from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any, List, Optional

class ModerationService:
    """
    A service to check text for toxicity or other undesirable content using a
    Hugging Face text classification pipeline.
    """
    def __init__(self, model_name: str = "unitary/toxic-bert", logger: Optional[Any] = None):
        self.logger = logger
        self.model_name = model_name
        self.toxicity_threshold = 0.7  # Default threshold

        try:
            if self.logger:
                self.logger.info(f"ModerationService: Initializing text classification pipeline with model '{self.model_name}'.")
            
            # Some models, especially multi-label ones, might require explicit tokenizer and model loading
            # if the default pipeline("text-classification", model=model_name) doesn't handle them well.
            # For "unitary/toxic-bert", the standard pipeline should work.
            # return_all_scores=True is important for getting scores for all labels.
            self.pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name, # Explicitly providing tokenizer for clarity
                return_all_scores=True
            )
            if self.logger:
                self.logger.info(f"ModerationService: Pipeline for '{self.model_name}' initialized successfully.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"ModerationService: Failed to initialize Hugging Face pipeline for model '{self.model_name}'. Error: {e}", exc_info=True)
            # Fallback or re-raise, depending on desired robustness. For now, re-raise.
            raise RuntimeError(f"Failed to initialize moderation pipeline: {e}")

    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Checks the input text for toxicity or other flagged content.

        Returns:
            A dictionary containing:
            - "is_safe": bool (True if no category exceeds threshold, False otherwise)
            - "flagged_categories": List[str] (categories that exceeded the threshold)
            - "scores": Dict[str, float] (all returned labels and their scores)
            - "model_used": str (name of the moderation model)
        """
        is_safe = True
        flagged_categories: List[str] = []
        all_scores_dict: Dict[str, float] = {}
        
        # Model name to be returned in results, ensuring it reflects the actual model used by the pipeline
        # For pipelines initialized with a model object, pipeline.model.name_or_path might be more accurate.
        # If initialized with model name string, self.model_name is fine.
        model_identifier = self.model_name
        if hasattr(self.pipeline, 'model') and hasattr(self.pipeline.model, 'name_or_path'):
            model_identifier = self.pipeline.model.name_or_path


        try:
            if not text or text.isspace(): # Handle empty or whitespace-only input
                if self.logger:
                    self.logger.info("ModerationService: Input text is empty or whitespace. Considered safe.")
                return {
                    "is_safe": True,
                    "flagged_categories": [],
                    "scores": {},
                    "model_used": model_identifier,
                    "status": "empty_input"
                }

            if self.logger:
                self.logger.info(f"ModerationService: Checking text: '{text[:100]}...'") # Log snippet
            
            pipeline_output = self.pipeline(text)
            # The output of pipeline with return_all_scores=True is usually a list of lists of dicts,
            # e.g., [[{'label': 'toxic', 'score': 0.9}, {'label': 'severe_toxic', 'score': 0.1}, ...]]
            # We need to process this to get a flat dictionary of scores and check against the threshold.

            if pipeline_output and isinstance(pipeline_output, list) and isinstance(pipeline_output[0], list):
                scores_list = pipeline_output[0] # Assuming single string input, so take first element
                for item in scores_list:
                    label = item.get("label", "unknown_label")
                    score = item.get("score", 0.0)
                    all_scores_dict[label] = score
                    # Check if any of the predefined toxic labels exceed the threshold
                    # For "unitary/toxic-bert", labels are like 'toxic', 'severe_toxic', 'obscene', etc.
                    # We can either have a predefined list of "negative" labels or consider any high score as potentially unsafe
                    # For simplicity, let's assume any category score above threshold makes it "not safe" for now.
                    # A more nuanced approach might only consider specific labels as "unsafe".
                    if score > self.toxicity_threshold:
                        # This logic might need adjustment based on the specific model's labels.
                        # For toxic-bert, labels like 'toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate' are primary.
                        # Other models might have 'positive' and 'negative' labels.
                        # For this example, we'll flag any category that meets the threshold.
                        is_safe = False
                        flagged_categories.append(label)
                
                if self.logger:
                    self.logger.info(f"ModerationService: Scores for '{text[:50]}...': {all_scores_dict}, Is Safe: {is_safe}")

            else:
                if self.logger:
                    self.logger.error(f"ModerationService: Unexpected pipeline output format: {pipeline_output}")
                # Fallback to considering it unsafe if output format is not as expected
                is_safe = False 
                all_scores_dict = {"error": "unexpected_pipeline_output_format"}


        except Exception as e:
            if self.logger:
                self.logger.error(f"ModerationService: Error during text classification for '{text[:50]}...': {e}", exc_info=True)
            is_safe = False # Default to not safe in case of error
            all_scores_dict = {"error": str(e)}
            flagged_categories.append("pipeline_error")

        return {
            "is_safe": is_safe,
            "flagged_categories": flagged_categories,
            "scores": all_scores_dict,
            "model_used": model_identifier 
        }

if __name__ == '__main__':
    # Simple test for the ModerationService
    class SimpleLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg, exc_info=False): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")

    logger = SimpleLogger()
    logger.info("--- ModerationService Test ---")
    
    # This will download the model if not cached, might take time.
    # If running in an environment without internet, this needs pre-downloaded model.
    try:
        moderation_service = ModerationService(logger=logger)
        
        test_texts = [
            "I love this beautiful sunny day!",
            "This is a piece of junk and I hate it.", # Example that might trigger toxicity
            "You are an idiot.",
            "" # Empty string test
        ]

        for text in test_texts:
            results = moderation_service.check_text(text)
            logger.info(f"Text: \"{text}\"")
            logger.info(f"  Is Safe: {results['is_safe']}")
            logger.info(f"  Flagged Categories: {results['flagged_categories']}")
            logger.info(f"  Scores: {results['scores']}")
            logger.info(f"  Model: {results['model_used']}")
            logger.info("-" * 20)
            
    except Exception as e:
        logger.error(f"Could not run ModerationService test: {e}", exc_info=True)
        logger.error("This might be due to model download issues if run for the first time without internet,")
        logger.error("or if the Hugging Face model Hub is unavailable.")
        logger.error("Ensure 'transformers' and 'torch' (or 'tensorflow'/'jax') are installed.")
