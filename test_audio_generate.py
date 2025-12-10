#!/usr/bin/env python3
"""
Test script for audio generation service
Calls /audio/generate/ endpoint with file upload and form parameters

Usage:
    python test_audio_generate.py
"""

import requests
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================
GENERATE_AUDIO_URL = "https://voiceclone-be.namitech.ai/audio/generate/"  # Update with actual service URL
JWT_URL = "https://voiceclone-be.namitech.ai/token"


# ============================================================================
# Main Function
# ============================================================================
def generate_audio(
    audio_file_path: str,
    gen_text: str,
    ref_lang: str = "vi",
    gen_lang: str = "vi",
    ref_text: str = None,
    is_upload: bool = False,
    is_translation: bool = False,
):
    """
    Call audio generation service

    Parameters:
        audio_file_path (str): Path to reference audio file
        gen_text (str): Text to generate audio for (required)
        ref_lang (str): Reference language - 'vi' (Vietnamese), 'en' (English), 'ja' (Japanese)
        gen_lang (str): Generation language - 'vi', 'en', 'ja'
        ref_text (str): Reference text (optional, ASR will auto-translate if not provided)
        is_upload (bool): Default False
        is_translation (bool): Default False

    Returns:
        dict: Response from the service
    """

    # Validate file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Prepare headers with JWT authentication
    JWT_TOKEN = get_token()
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}

    # Prepare form data
    form_data = {
        "gen_text": gen_text,
        "ref_lang": ref_lang,
        "gen_lang": gen_lang,
        "is_upload": str(is_upload).lower(),
        "is_translation": str(is_translation).lower(),
    }

    # Add optional ref_text if provided
    if ref_text is not None:
        form_data["ref_text"] = ref_text

    # Prepare file for upload
    files = {
        "file": (
            os.path.basename(audio_file_path),
            open(audio_file_path, "rb"),
            "audio/wav",  # Adjust MIME type if needed (audio/wav, audio/mp3, etc.)
        )
    }

    try:
        # Make POST request
        response = requests.post(
            GENERATE_AUDIO_URL,
            headers=headers,
            data=form_data,
            files=files,
            timeout=300,
        )

        # Close file
        files["file"][1].close()

        if response.status_code == 200:
            print("✅ Success!")
            try:
                response_data = response.content
                return response_data
            except json.JSONDecodeError:
                print("\n📦 Response (raw):")
                print(response.text)
                return {"raw_response": response.text}
        else:
            print(f"❌ Error: {response.status_code}")
            print("\n📦 Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return None

    except requests.exceptions.Timeout:
        print("❌ Request timeout - server took too long to respond")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - could not connect to server")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


def get_token():
    """
    Get JWT token
    """
    form_data = {
        "username": "demo",
        "password": "Namitech@2025",
    }
    response = requests.post(JWT_URL, data=form_data)
    return response.json()["access_token"]


# ============================================================================
# Example Usage
# ============================================================================
if __name__ == "__main__":
    # Example 1: Generate Vietnamese audio with Vietnamese reference
    print("Example 1: Vietnamese to Vietnamese")
    print("-" * 70)
    try:
        result = generate_audio(
            audio_file_path="008074.wav",  # Reference audio file
            gen_text="Xin chào, đây là văn bản cần tạo giọng nói",  # Text to generate
            ref_lang="vi",  # Reference is Vietnamese
            gen_lang="vi",  # Generate Vietnamese
            ref_text=None,  # Let ASR auto-detect
            is_upload=True,
            is_translation=False,
        )
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("   Please provide a valid audio file path")
