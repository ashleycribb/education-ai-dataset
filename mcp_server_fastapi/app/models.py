from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field, validator

class ContextData(BaseModel):
    context_id: str = Field(alias="contextId")
    model_id: str = Field(alias="modelId")
    user_id: str = Field(alias="userId")
    context_payload: Dict[str, Any] = Field(alias="contextData")
    last_updated: datetime = Field(default_factory=datetime.utcnow, alias="lastUpdated")

    class Config:
        validate_by_name = True # Updated from allow_population_by_field_name
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Ensure that when Pydantic creates a model from data,
        # it uses the field names (e.g., context_id) if the alias (contextId) is not present.
        # And when serializing, it uses the alias.
        by_alias = True

    @validator('last_updated', pre=True, always=True)
    def set_last_updated(cls, v):
        return v or datetime.utcnow()

# Example usage (optional, for testing)
if __name__ == "__main__":
    data = {
        "contextId": "test_context_123",
        "modelId": "model_abc",
        "userId": "user_xyz",
        "contextData": {"setting": "test", "value": 42},
        # lastUpdated will be set by default_factory or validator
    }
    context_instance = ContextData(**data)
    print(context_instance.json(by_alias=True))

    context_instance_by_field_name = ContextData(
        context_id="test_context_456",
        model_id="model_def",
        user_id="user_uvw",
        context_payload={"setting": "prod", "value": 100}
    )
    print(context_instance_by_field_name.json(by_alias=True))
    print(context_instance_by_field_name.last_updated)
