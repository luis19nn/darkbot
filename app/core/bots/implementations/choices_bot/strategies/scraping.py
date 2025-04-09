from abc import ABC
import asyncio
import logging
from app.core.apis import (DeepSeek, Google, Image)

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
                "choices": [
                    {{
                        "option_1": {{"text": "...", "image_keywords": "...", "percentages": 60}},
                        "option_2": {{"text": "...", "image_keywords": "...", "percentages": 40}}
                    }}
                ]
            }}

            "choices" is a json list with several possible choices, I want it to have 5 different choices
            "text" has the choices, and "option_1" and "option_2" need to have some relationship that makes sense for the choice between the two options
            "image_keywords" has keywords to search for images on Wikimedia. Make sure to keep it as simple as possible, just the minimum. Keep only the main theme of the option. For example, if the option is about a character or organization from an anime, the keywords will only have the name of the anime
            "percentages" can be any, vary the percentages according to each choice

            I want the choices to be about just one topic: {theme}. Also, I want the choices to be interesting, fun, and controversial.

            Make sure each option has only one sentence.
            Make sure the image_keywords are not the same.
            Do not include the phrase "Would you rather" in the options.
            Remember to return only the json, don't use any markdown.
            I don't want any markdown or comments.
            """

            return await DeepSeek.execute(prompt)

        except Exception as e:
            raise e

    async def image(self, content):
        logger.info(f"Scraping image")

        try:
            tasks = []
            for idx, choice in enumerate(content['choices']):
                for option_key in ['option_1', 'option_2']:
                    keywords = choice[option_key]['image_keywords']
                    filename = f"choice_{idx}_{option_key}.jpg"
                    tasks.append(
                        Image.get_image(keywords, filename)
                    )

            results = await asyncio.gather(*tasks)

            index = 0
            for choice in content['choices']:
                for option_key in ['option_1', 'option_2']:
                    choice[option_key]['image_path'] = results[index]
                    index += 1

            return content

        except Exception as e:
            raise e

    async def text_to_speech(self, content):
        logger.info(f"Scraping text-to-speech content")

        try:
            tasks = []
            for idx, choice in enumerate(content['choices']):
                for option_key in ['option_1', 'option_2']:
                    option = choice[option_key]
                    filename = f"choice_{idx}_{option_key}.wav"
                    text = option.get('text')
                    if text:
                        tasks.append(
                            Google.text_to_speech(text, filename)
                        )

            results = await asyncio.gather(*tasks)

            index = 0
            for choice in content['choices']:
                for option_key in ['option_1', 'option_2']:
                    choice[option_key]['audio_path'] = results[index]
                    index += 1

            return content
        except Exception as e:
            raise e
