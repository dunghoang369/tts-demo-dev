import requests

NETSPEECH_API_URL = "http://115.79.192.192:19977/get_netspeech"
SNR_API_URL = "http://115.79.192.192:19977/get_snr"
TTS_API_KEY = "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu"


def send_audio_file_netspeech(audio_file_path):
    """
    Send an audio file to the API endpoint
    """
    try:
        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (  # API expects parameter named "file" not "audio_file"
                    "output.wav",  # filename
                    audio_file,  # file object
                    "audio/wav",  # mime type
                )
            }

            # Send POST request
            # NOTE: Do NOT set Content-Type manually when using files parameter
            # requests will automatically set it with the proper boundary
            headers = {
                "accept": "application/json",
                "api-key": TTS_API_KEY,
            }
            response = requests.post(NETSPEECH_API_URL, headers=headers, files=files)

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error response: {response.text}")
                return None

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def send_audio_file_snr(audio_file_path):
    """
    Send an audio file to the API endpoint
    """
    try:
        # Open and read the audio file
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (  # API expects parameter named "file" not "audio_file"
                    "output.wav",  # filename
                    audio_file,  # file object
                    "audio/wav",  # mime type
                )
            }

            # Send POST request
            # NOTE: Do NOT set Content-Type manually when using files parameter
            # requests will automatically set it with the proper boundary
            headers = {
                "accept": "application/json",
                "api-key": TTS_API_KEY,
            }
            response = requests.post(SNR_API_URL, headers=headers, files=files)

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error response: {response.text}")
                return None

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Send the output.wav file
    print("Sending audio file to API...")
    print(f"API URL: {NETSPEECH_API_URL}")
    print(f"Audio file: output.wav")

    result_netspeech = send_audio_file_netspeech("output.wav")
    result_snr = send_audio_file_snr("output.wav")
    import pdb

    pdb.set_trace()
    if result:
        print("\n✅ Success!")
        print(f"Result: {result}")
    else:
        print("\n❌ Failed to send audio")
