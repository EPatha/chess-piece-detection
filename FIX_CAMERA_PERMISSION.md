# 🔐 Fix macOS Camera Permission

## ❌ Problem: "not authorized to capture video"

macOS memblokir akses camera untuk Python/Terminal karena privacy settings.

## ✅ Solution

### Metode 1: Via System Preferences (GUI)

1. **Buka System Preferences**
   ```
   Apple Menu → System Preferences → Security & Privacy
   ```

2. **Ke tab Privacy**
   - Scroll ke "Camera" di sidebar kiri
   - Klik lock icon (🔒) di kiri bawah untuk unlock
   - Masukkan password Mac

3. **Enable Camera Access**
   - Centang ✅ **Terminal** (jika menjalankan dari Terminal)
   - Centang ✅ **Python** (jika ada)
   - Centang ✅ **iTerm** (jika pakai iTerm)

4. **Restart Terminal**
   - Close semua Terminal windows
   - Buka lagi dan test: `.venv/bin/python3 check_cameras.py`

---

### Metode 2: Via Terminal (Command Line)

**⚠️ Metode ini memerlukan System Administrator privileges**

```bash
# Reset camera permissions untuk Terminal
sudo tccutil reset Camera com.apple.Terminal

# Atau untuk iTerm
sudo tccutil reset Camera com.googlecode.iterm2

# Restart Terminal dan run lagi
.venv/bin/python3 check_cameras.py
```

Saat run lagi, macOS akan popup asking untuk permission. Klik **"OK"** atau **"Allow"**.

---

### Metode 3: Temporary Workaround (System Integrity Protection)

**⚠️ NOT RECOMMENDED - Hanya untuk development/debugging**

Jika metode di atas tidak work dan urgent:

1. Restart Mac dan hold **Cmd+R** saat booting (Recovery Mode)
2. Buka Terminal di Recovery Mode
3. Run: `csrutil disable`
4. Restart Mac normally
5. Grant camera permissions
6. **IMPORTANT**: Re-enable SIP dengan `csrutil enable` setelah selesai

---

## 🧪 Test Camera Access

Setelah grant permission:

```bash
# Method 1: Check cameras dengan script
.venv/bin/python3 check_cameras.py

# Method 2: Quick test dengan Python
.venv/bin/python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera OK' if cap.isOpened() else '❌ Camera Failed'); cap.release()"
```

Expected output setelah berhasil:
```
✅ Camera OK
```

---

## 📱 Setup DroidCam (Setelah Permission Fixed)

### Quick Setup:

1. **Install DroidCam di HP Android**
   - Download dari Play Store
   - Buka app dan catat IP address (contoh: 192.168.1.100)

2. **Install DroidCam Client di Mac**
   ```bash
   # Via Homebrew
   brew install droidcam android-platform-tools
   
   # Atau download manual: https://www.dev47apps.com/droidcam/mac/
   ```

3. **Connect via USB** (Recommended - minimal latency)
   ```bash
   # Enable USB Debugging di HP:
   # Settings → About Phone → Tap "Build Number" 7x
   # Settings → Developer Options → Enable "USB Debugging"
   
   # Colok USB ke Mac
   # Run:
   ./start_droidcam.sh
   ```

4. **Connect via WiFi** (Alternative - jika USB tidak work)
   ```bash
   # Pastikan HP dan Mac di WiFi yang sama
   # Check IP di DroidCam app
   # Test koneksi:
   curl http://192.168.1.100:4747/video
   ```

5. **Check Camera ID**
   ```bash
   .venv/bin/python3 check_cameras.py
   
   # Output akan show:
   # ✅ Found 2 camera(s):
   #    Camera ID 0: Built-in (640x480)
   #    Camera ID 1: DroidCam (1280x720)  ← Use this!
   ```

6. **Use in yolov_usb_ui.py**
   - Buka UI: `.venv/bin/python3 yolov_usb_ui.py`
   - Set Camera ID to 1 (atau ID yang terdetect)
   - Click Start
   - Enjoy real-time detection! 🎉

---

## 🐛 Troubleshooting

### Problem: Permission granted tapi masih error

**Solution 1**: Restart Terminal completely (close all windows)

**Solution 2**: Logout/Login dari macOS

**Solution 3**: Check Python permission separately:
```bash
# Add Python interpreter to Camera access
which python3
# Copy path, then add manually di System Preferences → Camera
```

### Problem: DroidCam tidak terdetect sebagai camera

**Solution**: 
```bash
# Stop dan restart DroidCam client
killall droidcam-cli
./start_droidcam.sh

# Dalam terminal lain:
.venv/bin/python3 check_cameras.py
```

### Problem: USB Debugging not working

**Check ADB connection:**
```bash
adb devices

# Should show:
# List of devices attached
# XXXXXXXXXX    device

# If shows "unauthorized":
adb kill-server
adb start-server
# Check HP, popup akan muncul, centang "Always allow"
```

---

## ✅ Final Verification

Setelah semua setup:

```bash
# 1. Check cameras
.venv/bin/python3 check_cameras.py

# 2. Run detection UI
.venv/bin/python3 yolov_usb_ui.py

# 3. Test with chess pieces!
```

Expected: Real-time chess detection dengan confidence ~0.7-0.9+ 🎯
