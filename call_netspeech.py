import os
import requests

TTS_API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"


def audio_netspeech(file_path: str):
    """Forward audio file to NetSpeech API for quality analysis"""
    # Read file content
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Forward to NetSpeech API
    NETSPEECH_API_URL = "http://115.79.192.192:19977/get_netspeech"

    files = {
        "file": (
            os.path.basename(file_path),
            file_content,
            "audio/wav",
        )
    }
    headers = {"accept": "application/json", "api-key": TTS_API_KEY}

    response = requests.post(NETSPEECH_API_URL, files=files, headers=headers)

    return response.json()


if __name__ == "__main__":
    response = audio_netspeech("008074.wav")
    import pdb

    pdb.set_trace()
