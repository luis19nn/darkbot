from abc import ABC
import asyncio
import logging
from app.core.apis import (DeepSeek, Pinterest, PexelsAPI, Google)

logger = logging.getLogger('uvicorn.error')

class ChoicesScrapingStrategy(ABC):
    async def scrape(self, config):
        logger.info(f"Choices scraping")
        try:
            text_scraping = await self.text(config["theme"])
            image_scraping = await self.image(text_scraping)
            return await self.text_to_speech(image_scraping)
        except Exception as e:
            raise e

    async def text(self, theme):
        logger.info(f"Scraping text")

        try:
            prompt = f"""
            I want you to return a json "Would you rather..." in the following format:
            {{
                "or": "or",
                "choices": [
                    {{
                        "option_1": {{"text": "...", "image_keywords": "...", "percentages": 60}},
                        "option_2": {{"text": "...", "image_keywords": "...", "percentages": 40}}
                    }}
                ]
            }}

            "choices" is a json list with several possible choices, I want it to have 4 different choices
            "text" has the choices, and "option_1" and "option_2" need to have some relationship that makes sense for the choice between the two options
            "image_keywords" has keywords to search on the internet for images related to the options present in the equivalent "text"
            "percentages" can be any, vary the percentages according to each choice
 
            I want the choices to be about just one topic: {theme}. Also, I want the choices to be interesting, fun, and controversial.

            Remember to return only the json
            I also don't want any markdown or comments.
            Make sure each option has only one sentence.
            """

            return await DeepSeek.execute(prompt)

        except Exception as e:
            raise e

    async def image(self, content):
        logger.info(f"Scraping image")

        try:
            pexels_tasks = []
            for idx, choice in enumerate(content['choices']):
                for option_key in ['option_1', 'option_2']:
                    keywords = choice[option_key]['image_keywords']
                    filename = f"choice_{idx}_{option_key}.jpg"
                    pexels_tasks.append(
                        PexelsAPI.get_images(keywords, filename)
                    )

            pexels_results = await asyncio.gather(*pexels_tasks)

            index = 0
            for choice in content['choices']:
                for option_key in ['option_1', 'option_2']:
                    choice[option_key]['image_path'] = pexels_results[index]
                    index += 1

            return content

        except Exception as e:
            raise e

    async def text_to_speech(self, content):
        logger.info(f"Scraping text-to-speech content")

        try:
            google_tasks = []
            for idx, choice in enumerate(content['choices']):
                for option_key in ['option_1', 'option_2']:
                    option = choice[option_key]
                    filename = f"choice_{idx}_{option_key}.wav"
                    text = option.get('text')
                    if text:
                        google_tasks.append(
                            Google.text_to_speech(text, filename)
                        )

            google_results = await asyncio.gather(*google_tasks)

            index = 0
            for choice in content['choices']:
                for option_key in ['option_1', 'option_2']:
                    choice[option_key]['audio_path'] = google_results[index]
                    index += 1

            return content
        except Exception as e:
            raise e
