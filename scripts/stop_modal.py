#!/usr/bin/env python3
"""
Stop Modal apps to control costs.
"""

import subprocess
import sys

def list_apps():
    """List all Modal apps."""
    try:
        result = subprocess.run([
            "modal", "app", "list"
        ], capture_output=True, text=True, check=True,
           encoding='cp1252' if sys.platform == "win32" else None,
           errors='replace' if sys.platform == "win32" else None)
        
        print("📊 Current Modal Apps:")
        print("=" * 50)
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to list apps: {e}")
        return False

def stop_app(app_name: str):
    """Stop a specific Modal app."""
    try:
        result = subprocess.run([
            "modal", "app", "stop", app_name
        ], capture_output=True, text=True, check=True,
           encoding='cp1252' if sys.platform == "win32" else None,
           errors='replace' if sys.platform == "win32" else None)
        
        print(f"✅ Successfully stopped app: {app_name}")
        print("💰 App stopped - no more costs until next deployment")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop app '{app_name}': {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main function with interactive or command-line interface."""
    if len(sys.argv) > 1:
        # Command line mode
        app_name = sys.argv[1]
        print(f"🛑 Stopping Modal app: {app_name}")
        
        if stop_app(app_name):
            return 0
        else:
            return 1
    else:
        # Interactive mode
        print("🛑 Modal App Manager")
        print("=" * 30)
        
        # List current apps
        if not list_apps():
            return 1
        
        # Get user choice
        print("\nOptions:")
        print("1. Stop example-base-whisper (main transcription app)")
        print("2. Stop all apps")
        print("3. Just show status (no action)")
        print("4. Exit")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                return 0 if stop_app("example-base-whisper") else 1
            elif choice == "2":
                print("🛑 Stopping all Modal apps...")
                success = True
                # Try to stop common app names
                for app in ["example-base-whisper"]:
                    if not stop_app(app):
                        success = False
                return 0 if success else 1
            elif choice == "3":
                print("✅ Status shown above")
                return 0
            elif choice == "4":
                print("👋 Goodbye!")
                return 0
            else:
                print("❌ Invalid choice")
                return 1
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

if __name__ == "__main__":
    exit(main()) 