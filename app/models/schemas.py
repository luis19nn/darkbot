from pydantic import BaseModel, Field

class BotStartRequest(BaseModel):
    instances: int = Field(1, gt=0, example=2)
    config: dict

    class Config:
        json_schema_extra = {
            "example": {
                "instances": 2,
                "config": {
                    "credentials": [
                        {
                            "username": "user123",
                            "password": "pass123"
                        },
                        {
                            "username": "user456",
                            "password": "pass456"
                        }
                    ]
                }
            }
        }
