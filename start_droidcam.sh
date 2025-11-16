#!/bin/bash
# DroidCam USB Setup Helper for macOS

echo "🔧 DroidCam USB Setup Helper"
echo "================================"
echo ""

# Check if Homebrew installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install from: https://brew.sh"
    exit 1
fi
echo "✅ Homebrew installed"

# Check if ADB installed
if ! command -v adb &> /dev/null; then
    echo "📦 Installing Android Debug Bridge (ADB)..."
    brew install android-platform-tools
else
    echo "✅ ADB already installed"
fi

# Check if DroidCam client installed
if ! command -v droidcam-cli &> /dev/null; then
    echo "📦 Installing DroidCam client..."
    brew install droidcam
else
    echo "✅ DroidCam client already installed"
fi

echo ""
echo "================================"
echo "🔌 Connecting to Android Device"
echo "================================"
echo ""

# Start ADB server
echo "🚀 Starting ADB server..."
adb start-server
sleep 2

# Check connected devices
echo "📱 Checking connected devices..."
DEVICES=$(adb devices | grep -w "device" | wc -l)

if [ "$DEVICES" -eq 0 ]; then
    echo ""
    echo "❌ No device detected!"
    echo ""
    echo "📋 Checklist:"
    echo "  1. HP Android sudah dicolok via USB?"
    echo "  2. USB Debugging sudah enabled?"
    echo "     Settings → About Phone → Tap 'Build Number' 7x"
    echo "     Settings → Developer Options → Enable 'USB Debugging'"
    echo "  3. Popup 'Allow USB Debugging' sudah di-OK?"
    echo "  4. DroidCam app sudah running di HP?"
    echo ""
    exit 1
fi

echo "✅ Device connected!"
adb devices
echo ""

# Start DroidCam
echo "================================"
echo "🎥 Starting DroidCam"
echo "================================"
echo ""
echo "Starting DroidCam with 1280x720 resolution..."
echo "Press Ctrl+C to stop"
echo ""

# Start DroidCam client
droidcam-cli -v -size 1280x720 adb 4747
