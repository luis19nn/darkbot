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

            filename = f"{settings.TMP_DIR}{filename}"
            with open(filename, "wb") as out:
                out.write(response.audio_content)
                print(f'Generated speech saved to "{filename}"')
        except Exception as e:
            logger.error(f"Error in Google: {str(e)}")
            raise e
