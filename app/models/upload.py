from pydantic import BaseModel, Field

class UploadStartRequest(BaseModel):
    instances: int = Field(1, gt=0, example=2)
    config: dict

    class Config:
        json_schema_extra = {
            "example": {
                "instances": 2,
                "config": {
                    "instances": [
                        {
                            "account": ["account_01"],
                            "credentials": {
                                "tiktok": {
                                    "username": "tiktok123",
                                    "password": "tiktok123"
                                },
                                "youtube": {
                                    "username": "yt123",
                                    "password": "yt123"
                                },
                                "instagram": {
                                    "username": "insta123",
                                    "password": "insta123"
                                }
                            }
                        },
                        {
                            "account": ["account_02"],
                            "credentials": {
                                "tiktok": {
                                    "username": "tiktok456",
                                    "password": "tiktok456"
                                },
                                "youtube": {
                                    "username": "yt456",
                                    "password": "yt456"
                                },
                                "instagram": {
                                    "username": "insta456",
                                    "password": "insta456"
                                }
                            }
                        }
                    ]
                }
            }
        }
