import os
import requests
import sys
import subprocess

GITHUB_RAW_URL = "https://raw.githubusercontent.com/vaporlite/fivem-trigger-py/refs/heads/main/triggerbot.py"
LOCAL_FILENAME = "atilla.py"

def download_latest():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            with open(LOCAL_FILENAME, "w", encoding="utf-8") as f:
                f.write(response.text)
            print("[+] Latest version downloaded.")
        else:
            print("[-] Failed to fetch latest script.")
    except Exception as e:
        print("[-] Error:", e)

def run_app():
    subprocess.run([sys.executable, LOCAL_FILENAME])

if __name__ == "__main__":
    download_latest()
    run_app()
