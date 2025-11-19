#!/bin/bash
# DroidCam USB Auto-Setup & Run YOLOv8 Detection UI

echo "🚀 DroidCam USB + YOLOv8 Detection Launcher"
echo "==========================================="
echo ""

# Check ADB installed
if ! command -v adb &> /dev/null; then
    echo "❌ ADB not installed! Run: brew install android-platform-tools"
    exit 1
fi
echo "✅ ADB installed"

# Check device connected
echo "🔍 Checking USB devices..."
DEVICES=$(adb devices | grep -w "device" | grep -v "List" | wc -l | xargs)

if [ "$DEVICES" -eq "0" ]; then
    echo "❌ No Android device detected!"
    echo ""
    echo "📋 Checklist:"
    echo "  1. HP Android sudah dicolok USB?"
    echo "  2. USB Debugging enabled? (Settings → Developer Options)"
    echo "  3. Allow USB Debugging popup sudah OK?"
    echo "  4. DroidCam app running di HP?"
    exit 1
fi

echo "✅ Android device connected:"
adb devices | grep -v "List"
echo ""

# Setup port forwarding
echo "🔌 Setting up port forwarding..."
adb forward tcp:4747 tcp:4747
echo "✅ Port forwarding: localhost:4747 → device:4747"
echo ""

# Test DroidCam
echo "📱 Testing DroidCam connection..."
sleep 1
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:4747/video --connect-timeout 3)

if [ "$RESPONSE" != "200" ]; then
    echo "⚠️  DroidCam not responding (HTTP $RESPONSE)"
    echo "Make sure DroidCam app is OPEN on your phone!"
    echo ""
    read -p "Press Enter after opening DroidCam app..."
fi

echo "✅ DroidCam ready"
echo ""

# Launch UI
echo "🎬 Launching YOLOv8 Detection UI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 DroidCam URL: http://127.0.0.1:4747/video"
echo "📌 Model: runs/chess_detect/train3/weights/best.pt"
echo "📌 Confidence: 0.15 (optimal for chess)"
echo ""

.venv/bin/python3 yolov_ui.py

# Cleanup
echo ""
echo "🧹 Cleaning up..."
adb forward --remove tcp:4747 2>/dev/null || true
echo "✅ Done!"
