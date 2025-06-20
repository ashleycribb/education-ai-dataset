#!/usr/bin/env python3
"""
Interactive Quiz/Assessment Generator for AITA
AI-powered quiz generation based on conversation content and learning objectives
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import json
import uuid
import datetime
from enum import Enum
import random
import re

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    ORDERING = "ordering"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: QuestionType
    difficulty: DifficultyLevel
    question: str
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: Union[str, List[str]]  # Can be string or list for multiple answers
    explanation: str
    topic: str
    learning_objective: str
    points: int = 1
    time_limit: Optional[int] = None  # seconds

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    questions: List[QuizQuestion]
    total_points: int
    time_limit: Optional[int] = None  # total quiz time in minutes
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    created_by: str
    subject: str
    grade_level: Optional[int] = None

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    student_id: str
    answers: Dict[str, Any]  # question_id -> answer
    score: Optional[float] = None
    percentage: Optional[float] = None
    started_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    completed_at: Optional[datetime.datetime] = None
    time_taken: Optional[int] = None  # seconds

class QuizGenerationRequest(BaseModel):
    topic: str
    learning_objectives: List[str]
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    question_count: int = 5
    question_types: List[QuestionType] = [QuestionType.MULTIPLE_CHOICE]
    conversation_context: Optional[str] = None
    grade_level: Optional[int] = None

class QuizGenerator:
    def __init__(self):
        # Sample question templates and content
        self.question_templates = {
            QuestionType.MULTIPLE_CHOICE: [
                "What is {concept}?",
                "Which of the following best describes {concept}?",
                "In the context of {topic}, {concept} refers to:",
                "What happens when {action}?"
            ],
            QuestionType.TRUE_FALSE: [
                "{statement} is always true.",
                "{concept} is a type of {category}.",
                "In {topic}, {statement}."
            ],
            QuestionType.SHORT_ANSWER: [
                "Explain {concept} in your own words.",
                "Describe the relationship between {concept1} and {concept2}.",
                "What are the main characteristics of {concept}?"
            ],
            QuestionType.FILL_IN_BLANK: [
                "The {blank} is responsible for {function}.",
                "When {condition}, the result is {blank}.",
                "{concept} can be defined as {blank}."
            ]
        }
        
        # Sample content by subject
        self.content_database = {
            "mathematics": {
                "concepts": ["algebra", "geometry", "fractions", "equations", "variables"],
                "topics": ["linear equations", "quadratic functions", "geometric shapes", "probability"],
                "facts": [
                    "The Pythagorean theorem states that a² + b² = c²",
                    "A prime number is divisible only by 1 and itself",
                    "The area of a circle is π × r²"
                ]
            },
            "science": {
                "concepts": ["photosynthesis", "gravity", "atoms", "molecules", "energy"],
                "topics": ["biology", "chemistry", "physics", "earth science"],
                "facts": [
                    "Photosynthesis converts sunlight into chemical energy",
                    "Water boils at 100°C at sea level",
                    "The periodic table organizes elements by atomic number"
                ]
            },
            "english": {
                "concepts": ["metaphor", "simile", "protagonist", "theme", "plot"],
                "topics": ["literature", "grammar", "writing", "reading comprehension"],
                "facts": [
                    "A metaphor compares two things without using 'like' or 'as'",
                    "The protagonist is the main character in a story",
                    "A thesis statement presents the main argument of an essay"
                ]
            }
        }
    
    def generate_quiz(self, request: QuizGenerationRequest) -> Quiz:
        """Generate a quiz based on the request parameters"""
        questions = []
        
        # Determine subject from topic
        subject = self._identify_subject(request.topic)
        
        for i in range(request.question_count):
            question_type = random.choice(request.question_types)
            question = self._generate_question(
                question_type=question_type,
                topic=request.topic,
                learning_objectives=request.learning_objectives,
                difficulty=request.difficulty_level,
                subject=subject,
                context=request.conversation_context
            )
            questions.append(question)
        
        total_points = sum(q.points for q in questions)
        
        quiz = Quiz(
            title=f"Quiz: {request.topic.title()}",
            description=f"Assessment covering {', '.join(request.learning_objectives)}",
            questions=questions,
            total_points=total_points,
            created_by="AITA_System",
            subject=subject,
            grade_level=request.grade_level
        )
        
        return quiz
    
    def _identify_subject(self, topic: str) -> str:
        """Identify subject based on topic keywords"""
        topic_lower = topic.lower()
        
        math_keywords = ["math", "algebra", "geometry", "calculus", "equation", "number"]
        science_keywords = ["science", "biology", "chemistry", "physics", "experiment"]
        english_keywords = ["english", "literature", "writing", "reading", "grammar"]
        
        if any(keyword in topic_lower for keyword in math_keywords):
            return "mathematics"
        elif any(keyword in topic_lower for keyword in science_keywords):
            return "science"
        elif any(keyword in topic_lower for keyword in english_keywords):
            return "english"
        else:
            return "general"
    
    def _generate_question(self, question_type: QuestionType, topic: str, 
                          learning_objectives: List[str], difficulty: DifficultyLevel,
                          subject: str, context: Optional[str] = None) -> QuizQuestion:
        """Generate a single question"""
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return self._generate_multiple_choice(topic, learning_objectives[0], difficulty, subject)
        elif question_type == QuestionType.TRUE_FALSE:
            return self._generate_true_false(topic, learning_objectives[0], difficulty, subject)
        elif question_type == QuestionType.SHORT_ANSWER:
            return self._generate_short_answer(topic, learning_objectives[0], difficulty, subject)
        elif question_type == QuestionType.FILL_IN_BLANK:
            return self._generate_fill_in_blank(topic, learning_objectives[0], difficulty, subject)
        else:
            # Default to multiple choice
            return self._generate_multiple_choice(topic, learning_objectives[0], difficulty, subject)
    
    def _generate_multiple_choice(self, topic: str, objective: str, 
                                 difficulty: DifficultyLevel, subject: str) -> QuizQuestion:
        """Generate a multiple choice question"""
        
        if subject in self.content_database:
            concepts = self.content_database[subject]["concepts"]
            concept = random.choice(concepts)
        else:
            concept = topic
        
        # Generate question based on difficulty
        if difficulty == DifficultyLevel.EASY:
            question = f"What is {concept}?"
            correct = f"A fundamental concept in {subject}"
            options = [
                correct,
                f"A type of {random.choice(['tool', 'method', 'process'])}",
                f"An advanced {random.choice(['technique', 'theory', 'principle'])}",
                "None of the above"
            ]
        elif difficulty == DifficultyLevel.MEDIUM:
            question = f"Which statement best describes the relationship between {concept} and {topic}?"
            correct = f"{concept.title()} is a key component of {topic}"
            options = [
                correct,
                f"{concept.title()} is unrelated to {topic}",
                f"{concept.title()} contradicts {topic}",
                f"{concept.title()} is more important than {topic}"
            ]
        else:  # HARD
            question = f"In advanced {subject}, how does {concept} interact with other concepts in {topic}?"
            correct = f"It forms complex relationships that require deep understanding"
            options = [
                correct,
                "It operates independently without connections",
                "It only applies in basic scenarios",
                "It has been replaced by newer concepts"
            ]
        
        # Shuffle options
        random.shuffle(options)
        correct_index = options.index(correct)
        
        return QuizQuestion(
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=difficulty,
            question=question,
            options=options,
            correct_answer=chr(65 + correct_index),  # A, B, C, D
            explanation=f"This question tests understanding of {concept} in the context of {topic}.",
            topic=topic,
            learning_objective=objective,
            points=1 if difficulty == DifficultyLevel.EASY else 2 if difficulty == DifficultyLevel.MEDIUM else 3
        )
    
    def _generate_true_false(self, topic: str, objective: str, 
                           difficulty: DifficultyLevel, subject: str) -> QuizQuestion:
        """Generate a true/false question"""
        
        statements = [
            f"{topic.title()} is an important concept in {subject}",
            f"Understanding {topic} helps achieve {objective}",
            f"{topic.title()} requires no prior knowledge to master"
        ]
        
        statement = random.choice(statements)
        is_true = statement != statements[-1]  # Last statement is false
        
        return QuizQuestion(
            type=QuestionType.TRUE_FALSE,
            difficulty=difficulty,
            question=f"True or False: {statement}",
            correct_answer="True" if is_true else "False",
            explanation=f"This statement is {'true' if is_true else 'false'} because...",
            topic=topic,
            learning_objective=objective,
            points=1
        )
    
    def _generate_short_answer(self, topic: str, objective: str, 
                             difficulty: DifficultyLevel, subject: str) -> QuizQuestion:
        """Generate a short answer question"""
        
        question = f"Explain how {topic} relates to {objective}. Provide specific examples."
        
        return QuizQuestion(
            type=QuestionType.SHORT_ANSWER,
            difficulty=difficulty,
            question=question,
            correct_answer="Sample answer demonstrating understanding of the relationship",
            explanation="Look for clear explanation of concepts and relevant examples.",
            topic=topic,
            learning_objective=objective,
            points=3 if difficulty == DifficultyLevel.HARD else 2
        )
    
    def _generate_fill_in_blank(self, topic: str, objective: str, 
                              difficulty: DifficultyLevel, subject: str) -> QuizQuestion:
        """Generate a fill-in-the-blank question"""
        
        question = f"The concept of {topic} is important because it helps students _______ in {subject}."
        correct_answer = "understand fundamental principles"
        
        return QuizQuestion(
            type=QuestionType.FILL_IN_BLANK,
            difficulty=difficulty,
            question=question,
            correct_answer=correct_answer,
            explanation=f"The blank should be filled with a phrase that explains the importance of {topic}.",
            topic=topic,
            learning_objective=objective,
            points=2
        )
    
    def grade_quiz(self, quiz: Quiz, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Grade a quiz attempt"""
        total_points = 0
        earned_points = 0
        question_results = {}
        
        for question in quiz.questions:
            total_points += question.points
            student_answer = answers.get(question.id, "")
            
            is_correct = self._check_answer(question, student_answer)
            points_earned = question.points if is_correct else 0
            earned_points += points_earned
            
            question_results[question.id] = {
                "correct": is_correct,
                "points_earned": points_earned,
                "correct_answer": question.correct_answer,
                "student_answer": student_answer
            }
        
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        
        return {
            "total_points": total_points,
            "earned_points": earned_points,
            "percentage": percentage,
            "question_results": question_results,
            "grade": self._calculate_letter_grade(percentage)
        }
    
    def _check_answer(self, question: QuizQuestion, student_answer: str) -> bool:
        """Check if a student's answer is correct"""
        if question.type == QuestionType.MULTIPLE_CHOICE:
            return student_answer.upper() == question.correct_answer.upper()
        elif question.type == QuestionType.TRUE_FALSE:
            return student_answer.lower() == question.correct_answer.lower()
        elif question.type == QuestionType.FILL_IN_BLANK:
            # Simple keyword matching for fill-in-the-blank
            correct_keywords = question.correct_answer.lower().split()
            student_keywords = student_answer.lower().split()
            return any(keyword in student_keywords for keyword in correct_keywords)
        elif question.type == QuestionType.SHORT_ANSWER:
            # For demo purposes, assume 70% of short answers are correct
            # In production, this would use NLP/AI for evaluation
            return len(student_answer.strip()) > 10  # Basic length check
        else:
            return False
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

# Create FastAPI app
quiz_app = FastAPI(
    title="AITA Quiz Generator",
    description="AI-powered quiz generation and assessment system",
    version="1.0.0"
)

# Add CORS middleware
quiz_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize quiz generator
generator = QuizGenerator()

# In-memory storage
quizzes_db = {}
attempts_db = {}

@quiz_app.post("/api/quizzes/generate", response_model=Quiz)
async def generate_quiz(request: QuizGenerationRequest):
    """Generate a new quiz based on the request parameters"""
    quiz = generator.generate_quiz(request)
    quizzes_db[quiz.id] = quiz
    return quiz

@quiz_app.get("/api/quizzes/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    """Get a quiz by ID"""
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quizzes_db[quiz_id]

@quiz_app.get("/api/quizzes", response_model=List[Quiz])
async def list_quizzes():
    """List all available quizzes"""
    return list(quizzes_db.values())

@quiz_app.post("/api/quizzes/{quiz_id}/attempt")
async def start_quiz_attempt(quiz_id: str, student_id: str):
    """Start a new quiz attempt"""
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        answers={}
    )
    
    attempts_db[attempt.id] = attempt
    
    return {"attempt_id": attempt.id, "message": "Quiz attempt started"}

@quiz_app.post("/api/attempts/{attempt_id}/submit")
async def submit_quiz_attempt(attempt_id: str, answers: Dict[str, Any]):
    """Submit answers for a quiz attempt"""
    if attempt_id not in attempts_db:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    attempt = attempts_db[attempt_id]
    quiz = quizzes_db[attempt.quiz_id]
    
    # Update attempt with answers
    attempt.answers = answers
    attempt.completed_at = datetime.datetime.now()
    attempt.time_taken = int((attempt.completed_at - attempt.started_at).total_seconds())
    
    # Grade the quiz
    grading_result = generator.grade_quiz(quiz, answers)
    
    attempt.score = grading_result["earned_points"]
    attempt.percentage = grading_result["percentage"]
    
    return {
        "attempt_id": attempt_id,
        "results": grading_result,
        "message": "Quiz submitted and graded successfully"
    }

@quiz_app.get("/api/attempts/{attempt_id}")
async def get_quiz_attempt(attempt_id: str):
    """Get quiz attempt details"""
    if attempt_id not in attempts_db:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    return attempts_db[attempt_id]

@quiz_app.get("/api/analytics/quiz/{quiz_id}")
async def get_quiz_analytics(quiz_id: str):
    """Get analytics for a specific quiz"""
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_attempts = [a for a in attempts_db.values() if a.quiz_id == quiz_id and a.completed_at]
    
    if not quiz_attempts:
        return {"message": "No completed attempts found"}
    
    scores = [a.percentage for a in quiz_attempts if a.percentage is not None]
    
    analytics = {
        "quiz_id": quiz_id,
        "total_attempts": len(quiz_attempts),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "highest_score": max(scores) if scores else 0,
        "lowest_score": min(scores) if scores else 0,
        "completion_rate": len(quiz_attempts) / len([a for a in attempts_db.values() if a.quiz_id == quiz_id]) * 100
    }
    
    return analytics

@quiz_app.get("/api/analytics/student/{student_id}")
async def get_student_quiz_analytics(student_id: str):
    """Get quiz analytics for a specific student"""
    student_attempts = [a for a in attempts_db.values() if a.student_id == student_id and a.completed_at]
    
    if not student_attempts:
        return {"message": "No completed attempts found for this student"}
    
    scores = [a.percentage for a in student_attempts if a.percentage is not None]
    
    analytics = {
        "student_id": student_id,
        "total_quizzes_taken": len(student_attempts),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "recent_attempts": sorted(student_attempts, key=lambda x: x.started_at, reverse=True)[:5]
    }
    
    return analytics

@quiz_app.get("/health")
async def health_check():
    """Health check for quiz system"""
    return {
        "status": "healthy",
        "total_quizzes": len(quizzes_db),
        "total_attempts": len(attempts_db),
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting AITA Quiz Generator...")
    uvicorn.run(quiz_app, host="0.0.0.0", port=8003)