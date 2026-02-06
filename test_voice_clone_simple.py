#!/usr/bin/env python3
"""
Test script for the audio_voice_clone_simple endpoint
Tests the simple Vietnamese-only voice clone API proxy
"""

import requests
import sys
import os
from pathlib import Path
import base64


def test_voice_clone_simple(
    audio_file_path: str,
    text: str,
    api_url: str = "http://localhost:8000/api/audio/voice-clone-simple",
    output_file: str = "test_output_simple.wav",
):
    """
    Test the simple voice clone endpoint

    Args:
        audio_file_path: Path to the reference audio file (.wav or .mp3)
        text: Vietnamese text to generate
        api_url: API endpoint URL (default: localhost)
        output_file: Output file path for generated audio
    """

    print("=" * 60)
    print("Testing Simple Voice Clone API")
    print("=" * 60)

    # Check if audio file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Error: Audio file not found: {audio_file_path}")
        return False

    print(f"\n📁 Audio file: {audio_file_path}")
    print(f"📝 Text: {text}")
    print(f"🌐 API URL: {api_url}")

    try:
        # Prepare the file for upload
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (os.path.basename(audio_file_path), audio_file, "audio/wav")
            }

            # Query parameters: use "base64" so "audio" field contains base64-encoded WAV
            # (with "url", the API returns a URL string; base64-decoding that produces invalid audio)
            params = {"text": text, "return_type": "url"}

            # Headers
            headers = {
                "accept": "application/json",
                "api-key": "zNBVyiatKn5eTvC2CEvDg1msgOCHrTZ55zZ0qfsu",
            }

            print(f"\n🚀 Sending request to {api_url}...")
            print(f"   Parameters: {params}")

            # Make the POST request
            response = requests.post(
                api_url,
                files=files,
                params=params,
                timeout=300,  # 5 minute timeout for generation
                headers=headers,
            )

            print(f"\n📊 Response Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Content-Length: {len(response.content)} bytes")

            # Check response
            if response.status_code == 200:
                data = response.json()
                audio_field = data.get("audio")
                # Assume base64-encoded audio
                audio_bytes = base64.b64decode(audio_field)

                with open(output_file, "wb") as f:
                    f.write(audio_bytes)

                print(f"\n✅ Success! Audio generated and saved to: {output_file}")
                print(f"   File size: {os.path.getsize(output_file)} bytes")
                return True
            else:
                print(f"\n❌ Error: API returned status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Response text: {response.text[:500]}")
                return False

    except requests.exceptions.Timeout:
        print("\n❌ Error: Request timed out (>5 minutes)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Could not connect to {api_url}")
        print("   Make sure the API server is running")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function to run tests"""

    print("\n" + "=" * 60)
    print("Voice Clone Simple API Test Suite")
    print("=" * 60)

    # Configuration
    # Update these paths according to your setup
    TEST_AUDIO = "output.wav"  # Default test audio in the repo
    TEST_TEXT = "Hôm nay là thứ sáu có phải không nhỉ?"
    API_URL = "http://115.79.192.192:19977/voice_clone"
    OUTPUT_FILE = "test_voice_clone_simple_output.wav"

    success = test_voice_clone_simple(
        audio_file_path=TEST_AUDIO,
        text=TEST_TEXT,
        api_url=API_URL,
        output_file=OUTPUT_FILE,
    )

    # Print summary
    print("\n" + "=" * 60)
    if success:
        print("✅ Test PASSED")
        print(f"   Generated audio saved to: {OUTPUT_FILE}")
        print(f"   You can play the audio to verify the result")
    else:
        print("❌ Test FAILED")
        print("   Check the error messages above for details")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
    # import json

    # with open("response_1770362439572.json") as f:
    #     data = json.load(f)
    #     audio_bytes = base64.b64decode(data["audio"])
    #     with open("test_voice_clone_simple_output2.wav", "wb") as f:
    #         f.write(audio_bytes)
