import aiohttp
import logging
import json
from app.config import settings

logger = logging.getLogger('uvicorn.error')

class DeepSeek:
    @staticmethod
    async def execute(content):
        logger.info("Starting DeepSeek request")

        headers = {
            'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }

        data = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [{"role": "user", "content": content}]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.DEEPSEEK_API_URL,
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return json.loads(result.get("choices", [{}])[0].get("message", {}).get("content", ""))
                    else:
                        response_text = await response.text()
                        raise Exception(
                            f"DeepSeek API Error: {response.status} - {response_text}"
                        )
        except Exception as e:
            logger.error(f"Error in DeepSeek: {str(e)}")
            raise e
