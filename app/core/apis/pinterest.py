import aiohttp
import aiofiles
import logging
from app.config import settings

logger = logging.getLogger('uvicorn.error')

class Pinterest:
    @staticmethod
    async def get_images(keyword: str, filename: str, image_size: str = "600x") -> str:
        logger.info(f"Searching Pinterest for keyword: {keyword}")

        headers = {
            'Authorization': f'Bearer {settings.PINTEREST_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        search_url = settings.PINTEREST_API_URL
        params = {
            'query': keyword,
            'fields': 'id,media',
            'limit': 1
        }

        full_path = f"{settings.IMG_TMP_DIR}{filename}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data.get("items") and len(data["items"]) > 0:
                            pin = data["items"][0]
                            img_url = pin["media"]["images"][image_size]["url"]

                            logger.info(f"Found image at: {img_url}")

                            async with session.get(img_url) as img_response:
                                if img_response.status == 200:
                                    async with aiofiles.open(full_path, 'wb') as f:
                                        await f.write(await img_response.read())
                                    logger.info(f"Image saved to {full_path}")
                                    return full_path
                                else:
                                    logger.error(f"Failed to download image: {img_url}")
                                    return None
                        else:
                            logger.warning(f"No images found for: {keyword}")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"Pinterest API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Error in Pinterest: {str(e)}")
            raise e
