import requests

if __name__ == "__main__":

    url = "https://aft.namisense.ai/tts/offline"
    params = {
        "text": "Hôm nay tôi đi học",
        "accent": "01_default",
        "sample_rate": "16000",
        "audio_format": "wav",
    }

    try:
        resp = requests.get(url, params=params, timeout=20)

        # Print debug info
        print(f"Status Code: {resp.status_code}")
        print(f"Response Headers: {dict(resp.headers)}")

        resp.raise_for_status()

        # Kiểm tra Content-Type để chắc là audio
        content_type = resp.headers.get("Content-Type", "")
        if "audio" in content_type or resp.headers.get("Content-Disposition"):
            with open("output.wav", "wb") as f:
                f.write(resp.content)
            print("Saved output.wav")
        else:
            # Nếu không phải audio, in ra body (thường là JSON lỗi)
            print("Response Content-Type:", content_type)
            print(resp.text)
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        print(f"Response Headers: {dict(resp.headers)}")
    except requests.RequestException as e:
        print("Request failed:", e)
