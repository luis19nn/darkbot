import aiofiles
import aiohttp
from google.oauth2 import service_account
import google.cloud.texttospeech as tts
from bs4 import BeautifulSoup
import numpy as np
from PIL import Image
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import logging
from app.config import settings

logger = logging.getLogger('uvicorn.error')

class Google:
    @staticmethod
    async def text_to_speech(content, filename):
        try:
            text_input = tts.SynthesisInput(text=content)
            voice_params = tts.VoiceSelectionParams(
                language_code="en-US", name="en-US-Chirp3-HD-Orus"
            )
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

            credentials = service_account.Credentials.from_service_account_info({
                "type": settings.GOOGLE_PROJECT_TYPE,
                "project_id": settings.GOOGLE_PROJECT_ID,
                "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
                "private_key": settings.GOOGLE_PRIVATE_KEY.replace('\\n', '\n'),
                "client_email": settings.GOOGLE_CLIENT_EMAIL,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "token_uri": settings.GOOGLE_TOKEN_URI,
            })

            client = tts.TextToSpeechClient(credentials=credentials)
            response = client.synthesize_speech(
                input=text_input,
                voice=voice_params,
                audio_config=audio_config,
            )

            full_path = f"{settings.AUDIOS_TMP_DIR}{filename}"
            with open(full_path, "wb") as out:
                out.write(response.audio_content)
                logger.info(f"Generated speech saved to {full_path}")
                return full_path
        except Exception as e:
            logger.error(f"Error in Google.text_to_speech: {str(e)}")
            raise e

    @staticmethod
    async def get_image(query, filename, theme):
        try:
            full_path = f"{settings.IMG_TMP_DIR}{filename}"
            search_url = f"https://www.google.com/search?q={query}&tbm=isch"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    img_tags = soup.find_all("img")

                    if img_tags:
                        img_url = img_tags[1]["src"]

                        async with session.get(img_url) as img_response:
                            async with aiofiles.open(full_path, "wb") as f:
                                await f.write(await img_response.read())
                            logger.info(f"Image saved to {full_path}")
                        
                        Google.resize_image(full_path, theme)
                        return full_path
            return None
        except Exception as e:
            logger.error(f"Error in Google.get_images: {str(e)}")
            raise e
    
    @staticmethod
    def resize_image(image_path: str, theme: str = None):
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

            if theme == 'anime':
                model_params = {
                    'num_in_ch': 3,
                    'num_out_ch': 3,
                    'num_feat': 64,
                    'num_block': 6,
                    'num_grow_ch': 32,
                    'scale': 4
                }
                model_path = f'{settings.MISC_DIR}RealESRGAN_x4plus_anime_6B.pth'
            else:
                model_params = {
                    'num_in_ch': 3,
                    'num_out_ch': 3,
                    'num_feat': 64,
                    'num_block': 23,
                    'num_grow_ch': 32,
                    'scale': 4
                }
                model_path = f'{settings.MISC_DIR}RealESRGAN_x4plus.pth'

            model = RRDBNet(**model_params)
            state_dict = torch.load(model_path, map_location=device)
            
            if 'params_ema' in state_dict:
                model.load_state_dict(state_dict['params_ema'])
            else:
                model.load_state_dict(state_dict)

            upsampler = RealESRGANer(
                scale=4,
                model_path=model_path,
                model=model,
                device=device,
                pre_pad=0
            )

            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)

            output, _ = upsampler.enhance(img_array, outscale=4)
            Image.fromarray(output).save(image_path)
            return True

        except Exception as e:
            logger.error(f"Error on resize_image: {str(e)}")
            raise e
