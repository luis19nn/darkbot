from google.oauth2 import service_account
import google.cloud.texttospeech as tts
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
