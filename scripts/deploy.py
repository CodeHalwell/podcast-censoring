#!/usr/bin/env python3
"""
Deploy Modal app for podcast transcription.
"""

import subprocess
import sys
import time
from pathlib import Path

def main():
    """Deploy the Modal app."""
    print("🚀 Deploying Modal app for podcast transcription...")
    
    # Path to the modal client
    modal_client_path = Path("src/podcast_transcription/modal_client.py")
    
    if not modal_client_path.exists():
        print(f"❌ Modal client not found at {modal_client_path}")
        return 1
    
    try:
        # Deploy the app
        result = subprocess.run([
            "modal", "deploy", str(modal_client_path)
        ], capture_output=True, text=True, check=True,
           encoding='cp1252' if sys.platform == "win32" else None,
           errors='replace' if sys.platform == "win32" else None)
        
        print("✅ Modal app deployed successfully!")
        print("\n📋 Deployment Details:")
        print("=" * 50)
        print(result.stdout)
        
        # Check app status
        print("\n🔍 Checking app status...")
        status_result = subprocess.run([
            "modal", "app", "list"
        ], capture_output=True, text=True,
           encoding='cp1252' if sys.platform == "win32" else None,
           errors='replace' if sys.platform == "win32" else None)
        
        if status_result.returncode == 0:
            print("📊 Current Modal Apps:")
            print(status_result.stdout)
        
        print("\n✅ Deployment complete!")
        print("💡 You can now use the transcription pipeline")
        print("💰 The app will auto-scale to zero when not in use (no cost)")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 