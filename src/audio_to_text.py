import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

deepgram=None
def audio_initial_loader():
    global deepgram

    load_dotenv()

    API_KEY = os.getenv("DEEPGRAM_API_KEY")

    deepgram = DeepgramClient(api_key=API_KEY)

def audio_transcription(filepath):

    with open(filepath, "rb") as audio_file:
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_file.read(),
            model="nova-3"
        )
        return response.results.channels[0].alternatives[0].transcript


if __name__=='__main__':
    file='./temp/audio/recording.webm'
    audio_initial_loader()
    text=audio_transcription(file)
    print(text)