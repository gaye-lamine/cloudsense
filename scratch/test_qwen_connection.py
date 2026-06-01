#!/usr/bin/env python3
"""
============================================================
  CloudSense — Qwen Cloud API Key Verification Sandbox
============================================================
  Use this lightweight script to test your Qwen Cloud API key
  and confirm full connectivity before turning on live mode
  in the FastAPI backend server.
============================================================
"""

import os
import sys
from openai import OpenAI


def test_qwen_connection():
    # 1. Retrieve API key from environment or prompt
    api_key = os.getenv("QWEN_API_KEY")

    if not api_key:
        print("❌ Error: QWEN_API_KEY environment variable is not set.")
        print("Please export it in your shell first:")
        print("   export QWEN_API_KEY=\"your_key_here\"")
        print("\nOr enter your key here to test it temporarily:")
        api_key = input("👉 Enter Qwen API Key: ").strip()

    if not api_key:
        print("❌ Error: No API key supplied. Exiting.")
        sys.exit(1)

    print("\n--- Connecting to Qwen Cloud Gateway ---")
    base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    model = "qwen-plus"

    print(f"Base URL: {base_url}")
    print(f"Model:    {model}")
    print("Sending test prompt...")

    try:
        # 2. Instantiate OpenAI-compatible client
        client = OpenAI(api_key=api_key, base_url=base_url)

        # 3. Create test completion request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful cloud assistant. Respond concisely.",
                },
                {
                    "role": "user",
                    "content": "Perform a connection verification test. Confirm you can read this and say hello!",
                },
            ],
            temperature=0.3,
            max_tokens=100,
        )

        reply = response.choices[0].message.content.strip()
        print("\n--- ✅ Connection Successful! ---")
        print(f"Qwen Reply: \"{reply}\"")
        print("\nTo activate live mode in CloudSense:")
        print("1. Open your '.env' file inside the cloudsense/ directory.")
        print(f"2. Paste your key: QWEN_API_KEY={api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")
        print("3. Restart your server. It will automatically switch from mock to live API mode!")

    except Exception as e:
        print("\n--- ❌ Connection Failed ---")
        print(f"Error Details: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your coupon was successfully activated by Alibaba Cloud.")
        print("2. Check if your API key was copied correctly from the console.")
        print("3. Ensure your network has internet access to dashscope-intl.aliyuncs.com.")


if __name__ == "__main__":
    test_qwen_connection()
