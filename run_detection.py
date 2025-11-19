#!/usr/bin/env python3
"""
Automatic DroidCam USB Setup + Chess Detection Launcher
Auto-install ADB jika belum terinstall, setup camera HP Android via USB
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


def install_homebrew():
    """Auto-install Homebrew"""
    print("📦 Installing Homebrew...\n")
    print("⏳ This may take a few minutes. Please wait...\n")
    
    try:
        # Install Homebrew
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = subprocess.run(
            install_cmd,
            shell=True,
            check=True,
            text=True
        )
        
        print("\n✅ Homebrew installed successfully!")
        
        # Add Homebrew to PATH for Apple Silicon Macs
        brew_path = "/opt/homebrew/bin/brew"
        if os.path.exists(brew_path):
            # Update current session PATH
            os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ['PATH']}"
            print("✅ Added Homebrew to PATH")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Homebrew installation failed: {e}")
        print("\n📋 Install manual:")
        print('   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def install_adb():
    """Auto-install ADB via Homebrew"""
    print("📦 Installing ADB (Android Platform Tools)...\n")
    
    # Check if Homebrew installed
    if not check_command("brew"):
        print("⚠️  Homebrew not found. Installing Homebrew first...\n")
        if not install_homebrew():
            return False
    
    print("✅ Homebrew ready. Installing android-platform-tools...\n")
    
    try:
        # Install ADB
        result = subprocess.run(
            ["brew", "install", "android-platform-tools"],
            check=True,
            text=True
        )
        
        print("\n✅ ADB successfully installed!")
        
        # Verify installation
        if check_command("adb"):
            # Get version
            version_result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True
            )
            print(f"\n{version_result.stdout.strip()}")
            return True
        else:
            print("⚠️  ADB installed but not found in PATH")
            print("Reloading environment...")
            # Try to find ADB in Homebrew path
            brew_adb = "/opt/homebrew/bin/adb"
            if os.path.exists(brew_adb):
                os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ['PATH']}"
                print("✅ ADB found and added to PATH")
                return True
            else:
                print("⚠️  Please restart terminal and run script again")
                return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ADB installation failed: {e}")
        print("\n📋 Install manual:")
        print("   brew install android-platform-tools")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
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
    
    # Step 1: Check & Install ADB
    print("🔍 Checking ADB installation...\n")
    
    if not check_command("adb"):
        print("⚠️  ADB not found. Installing automatically...\n")
        
        if not install_adb():
            print("\n❌ Auto-installation failed!")
            print("\n📋 Manual installation:")
            print("   1. Install Homebrew:")
            print('      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            print("   2. Install ADB:")
            print("      brew install android-platform-tools")
            print("\n💡 Jalankan script ini lagi setelah install.")
            sys.exit(1)
        
        print("\n✅ ADB installed successfully!")
    else:
        print("✅ ADB already installed")
        # Show version
        try:
            version = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True
            )
            print(f"   {version.stdout.splitlines()[0]}")
        except Exception:
            pass
    
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
        print("\n💡 Setelah fix, jalankan script ini lagi:")
        print("   python3 run_detection.py")
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
            print("\n💡 Troubleshooting:")
            print("  1. Buka DroidCam app di HP")
            print("  2. Pastikan tidak ada error di app")
            print("  3. Coba restart DroidCam app")
            print("  4. Test manual:")
            print("     curl -I http://127.0.0.1:4747/video")
            print("  5. Jalankan script ini lagi")
            sys.exit(1)
    else:
        print("✅ DroidCam is ready!")
    
    # Check model
    model_path = "runs/chess_detect/train3/weights/best.pt"
    if os.path.exists(model_path):
        print(f"\n✅ Model ready: {model_path}")
    else:
        print(f"\n⚠️  Warning: Model not found at {model_path}")
        print("Model will be downloaded on first run.")
    
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
