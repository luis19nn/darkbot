import aiohttp
import aiofiles
import logging
from app.config import settings

logger = logging.getLogger('uvicorn.error')

class PexelsAPI:
    @staticmethod
    async def get_images(keyword, filename):
        logger.info(f"Searching image for keyword: {keyword}")

        headers = {'Authorization': settings.PEXELS_API_KEY}
        url = f"https://api.pexels.com/v1/search?query={keyword}&per_page=1"
        full_path = f"{settings.IMG_TMP_DIR}{filename}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["photos"]:
                            img_url = data["photos"][0]["src"]["original"]

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
                        logger.error(f"Pexels API error: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Error in PexelsAPI: {str(e)}")
            raise e
