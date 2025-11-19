#!/usr/bin/env python3
"""
Automatic DroidCam USB Setup + Chess Detection Launcher
Setup camera HP Android via USB dan launch detection
"""
import subprocess
import sys
import os
import time
import urllib.request

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_command(cmd):
    """Check if command exists"""
    try:
        result = subprocess.run(
            ["which", cmd],
            capture_output=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


def get_adb_devices():
    """Get connected ADB devices"""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')[1:]
        devices = [line.split()[0] for line in lines if '\tdevice' in line]
        return devices
    except Exception:
        return []


def setup_port_forwarding():
    """Setup ADB port forwarding"""
    try:
        subprocess.run(
            ["adb", "forward", "tcp:4747", "tcp:4747"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def test_droidcam():
    """Test DroidCam connection"""
    try:
        req = urllib.request.Request("http://127.0.0.1:4747/video")
        response = urllib.request.urlopen(req, timeout=3)
        return response.getcode() == 200
    except Exception:
        return False


def main():
    print_header("🚀 DroidCam USB + Chess Detection Launcher")
    
    # Step 1: Check ADB
    print("🔍 Checking requirements...\n")
    if not check_command("adb"):
        print("❌ ADB not installed!")
        print("\n📦 Install dengan:")
        print("   brew install android-platform-tools")
        print("\nSetelah install, jalankan script ini lagi.")
        sys.exit(1)
    print("✅ ADB installed")
    
    # Step 2: Check Android device
    print("\n📱 Checking Android device via USB...\n")
    devices = get_adb_devices()
    
    if not devices:
        print("❌ No Android device detected!")
        print("\n📋 Checklist:")
        print("  1. HP Android sudah dicolok via USB ke Mac?")
        print("  2. USB Debugging sudah enabled?")
        print("     Settings → About Phone → Tap 'Build Number' 7x")
        print("     Settings → Developer Options → USB Debugging (ON)")
        print("  3. Popup 'Allow USB Debugging' sudah di-OK?")
        print("  4. DroidCam app sudah diinstall dari Play Store?")
        print("  5. DroidCam app sudah TERBUKA di HP?")
        print("\nSetelah fix, jalankan script ini lagi.")
        sys.exit(1)
    
    print(f"✅ Android device connected: {devices[0]}")
    
    # Step 3: Setup port forwarding
    print("\n🔌 Setting up port forwarding...\n")
    if not setup_port_forwarding():
        print("❌ Port forwarding failed!")
        sys.exit(1)
    print("✅ Port forwarding: localhost:4747 → device:4747")
    
    # Step 4: Test DroidCam
    print("\n📸 Testing DroidCam connection...\n")
    time.sleep(1)
    
    if not test_droidcam():
        print("⚠️  DroidCam not responding!")
        print("\n📋 Pastikan:")
        print("  1. DroidCam app TERBUKA di HP (jangan minimize!)")
        print("  2. Camera permission granted ke DroidCam")
        print("  3. App tidak di-force stop")
        print("\nMenunggu DroidCam ready...")
        
        # Retry 10x
        for i in range(10):
            time.sleep(2)
            if test_droidcam():
                print(f"\n✅ DroidCam connected!")
                break
            print(f"  Retry {i+1}/10...")
        else:
            print("\n❌ Cannot connect to DroidCam")
            print("\nTroubleshooting:")
            print("  1. Buka DroidCam app di HP")
            print("  2. Pastikan tidak ada error di app")
            print("  3. Coba restart DroidCam app")
            print("  4. Jalankan script ini lagi")
            sys.exit(1)
    else:
        print("✅ DroidCam is ready!")
    
    # Check model
    model_path = "runs/chess_detect/train3/weights/best.pt"
    if os.path.exists(model_path):
        print(f"\n✅ Model ready: {model_path}")
    else:
        print(f"\n⚠️  Warning: Model not found at {model_path}")
    
    # Launch UI
    print_header("🎬 Launching Chess Detection UI")
    print("📌 DroidCam URL: http://127.0.0.1:4747/video")
    print("📌 Model: runs/chess_detect/train3/weights/best.pt")
    print("📌 Confidence: 0.15 (optimal for chess)")
    print("📌 Device: Camera HP Android via USB")
    print("\n⌨️  UI window akan terbuka...")
    print("⌨️  Click 'Start' button untuk mulai detection")
    print("⌨️  Press Ctrl+C di terminal untuk stop\n")
    
    try:
        # Launch UI with DroidCam source
        venv_python = ".venv/bin/python3"
        subprocess.run([venv_python, "yolov_ui.py"])
    except KeyboardInterrupt:
        print("\n\n⏹  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            subprocess.run(
                ["adb", "forward", "--remove", "tcp:4747"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
        print("✅ Done!")


if __name__ == "__main__":
    main()
