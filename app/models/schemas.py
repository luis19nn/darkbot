from pydantic import BaseModel, Field

class BotStartRequest(BaseModel):
    instances: int = Field(1, gt=0, example=2)
    config: dict
    
    class Config:
        schema_extra = {
            "example": {
                "instances": 2,
                "config": {
                    "source": "https://exemple.com/feed",
                    "credentials": {
                        "username": "user123",
                        "password": "pass123"
                    }
                }
            }
        }
