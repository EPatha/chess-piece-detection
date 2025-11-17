#!/bin/bash
# Quick Test Camera Script

echo "🎥 Quick Camera Test"
echo "===================="
echo ""

# Check Python
if ! .venv/bin/python3 --version &> /dev/null; then
    echo "❌ Virtual environment not found"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "✅ Python environment ready"
echo ""

# Test camera permission dengan simple script
echo "📹 Testing camera access..."
.venv/bin/python3 << 'PYTHON_CODE'
import cv2
import sys

print("Attempting to open camera 0 (built-in)...")
cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("✅ Camera 0 opened successfully!")
    ret, frame = cap.read()
    if ret:
        h, w = frame.shape[:2]
        print(f"   Resolution: {w}x{h}")
        print(f"   FPS: {cap.get(cv2.CAP_PROP_FPS)}")
        print("")
        print("🎉 Camera is working! You can now run:")
        print("   .venv/bin/python3 yolov_usb_ui.py")
        cap.release()
        sys.exit(0)
    else:
        print("❌ Camera opened but cannot read frames")
        cap.release()
        sys.exit(1)
else:
    print("❌ Cannot open camera!")
    print("")
    print("🔧 Troubleshooting:")
    print("   1. Grant camera permission in System Preferences")
    print("      System Preferences → Security & Privacy → Camera")
    print("      ✅ Check 'Terminal' or 'iTerm'")
    print("")
    print("   2. Restart Terminal completely")
    print("")
    print("   3. If using external camera, try:")
    print("      .venv/bin/python3 check_cameras.py")
    sys.exit(1)
PYTHON_CODE
