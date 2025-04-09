import aiofiles
import aiohttp
import logging
import random
from app.config import settings

logger = logging.getLogger('uvicorn.error')

class Image:
    @staticmethod
    async def get_image(query, filename):
        try:
            logger.info("Starting Image.get_image request")

            full_path = f"{settings.IMG_TMP_DIR}{filename}"

            headers = {
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json"
            }

            params = {
                "q": query,
                "num": 20,
                "tbm": "isch"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.SERPER_API_URL,
                    headers=headers,
                    json=params
                ) as response:
                    if not response.ok:
                        logger.error(f"Got {response.status} error from serper: {response.reason}")
                        raise
                    
                    data = await response.json()

                if not data.get("images"):
                    logger.warning("No images found")
                    raise
                
                valid_images = [img for img in data["images"] if img.get("imageWidth", 0) > 300 and img.get("imageHeight", 0) > 300]
                
                if not valid_images:
                    logger.warning("No valid images found")
                    raise

                selected_image = random.choice(valid_images)
                image_url = selected_image["imageUrl"]

                async with session.get(image_url) as img_response:
                    async with aiofiles.open(full_path, "wb") as f:
                        await f.write(await img_response.read())

                    logger.info(f"Image saved to {full_path}")
                    return full_path

        except Exception as e:
            logger.error(f"Error in Image.get_image: {str(e)}")
            return await Image.get_image2(query, filename)

    @staticmethod
    async def get_image2(query, filename):
        try:
            logger.info("Starting Image.get_image2 request")

            full_path = f"{settings.IMG_TMP_DIR}{filename}"

            params = {
                "method": "flickr.photos.search",
                "api_key": settings.FLICKR_API_KEY,
                "text": query,
                "orientation": "landscape, portrait, square",
                "dimension_search_mode": "min",
                "height": 640,
                "width": 640,
                "content_types": "0, 2",
                "media": "photos",
                "sort": "relevance",
                "format": "json",
                "nojsoncallback": 1,
                "extras": "url_o"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(settings.FLICKR_API_URL, params=params) as response:
                    data = await response.json()

                    if data["stat"] != "ok" or not data["photos"]["photo"]:
                        logger.warning("No images found")
                        return None

                    photo = data["photos"]["photo"][0]
                    image_url = photo['url_o']

                    async with session.get(image_url) as img_response:
                        async with aiofiles.open(full_path, "wb") as f:
                            await f.write(await img_response.read())

                        logger.info(f"Image saved to {full_path}")
                        return full_path

            return None

        except Exception as e:
            logger.error(f"Error in Image.get_image2: {str(e)}")
            raise e
