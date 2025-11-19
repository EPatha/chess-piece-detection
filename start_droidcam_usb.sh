#!/bin/bash
# Quick Start DroidCam USB Mode

echo "🔌 DroidCam USB Quick Start"
echo "============================"
echo ""

# Check ADB
if ! command -v adb &> /dev/null; then
    echo "❌ ADB not installed"
    echo "Run: brew install android-platform-tools"
    exit 1
fi
echo "✅ ADB installed"

# Check device
echo ""
echo "📱 Checking USB connection..."
DEVICE_COUNT=$(adb devices | grep -c "device$")

if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "❌ No device connected!"
    echo ""
    echo "Checklist:"
    echo "  1. HP Android sudah dicolok USB?"
    echo "  2. USB Debugging enabled?"
    echo "     Settings → Developer Options → USB Debugging"
    echo "  3. Popup 'Allow USB Debugging' sudah OK?"
    echo "  4. DroidCam app running di HP?"
    exit 1
fi

echo "✅ Device connected:"
adb devices | grep "device$"

# Setup port forwarding
echo ""
echo "🔧 Setting up port forwarding..."
adb forward tcp:4747 tcp:4747
echo "✅ Port forwarding active: localhost:4747 → phone:4747"

# Test connection
echo ""
echo "🧪 Testing DroidCam connection..."
if curl -s -f -I http://localhost:4747/video > /dev/null 2>&1; then
    echo "✅ DroidCam accessible at http://localhost:4747/video"
else
    echo "⚠️  Cannot reach DroidCam"
    echo ""
    echo "Make sure:"
    echo "  1. DroidCam app is RUNNING on your phone"
    echo "  2. Camera permission granted"
    echo "  3. Try restarting DroidCam app"
    echo ""
    echo "Then run this script again"
    exit 1
fi

# Success
echo ""
echo "=" * 50
echo "🎉 DroidCam USB Ready!"
echo "=" * 50
echo ""
echo "📋 How to use:"
echo ""
echo "1. Run YOLO Detection UI:"
echo "   .venv/bin/python3 yolov_ui.py"
echo ""
echo "2. In the UI:"
echo "   - Source: http://localhost:4747/video"
echo "   - Model: runs/chess_detect/train3/weights/best.pt"
echo "   - Confidence: 0.15"
echo "   - Click Start"
echo ""
echo "3. Or test first:"
echo "   .venv/bin/python3 test_droidcam_usb.py"
echo ""
echo "💡 Tip: USB mode has ~50ms latency (WiFi ~200ms)"
echo ""
