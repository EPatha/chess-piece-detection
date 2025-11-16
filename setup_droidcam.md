# Setup DroidCam untuk Akses Camera HP via USB

## 📱 Persiapan di Android

### 1. Install DroidCam App
- Download dari Play Store: https://play.google.com/store/apps/details?id=com.dev47apps.droidcam
- Install dan buka aplikasi

### 2. Enable USB Debugging
```
Settings → About Phone → Tap "Build Number" 7x
Settings → Developer Options → Enable "USB Debugging"
```

### 3. Hubungkan ke Mac via USB
- Colok kabel USB
- Izinkan "USB Debugging" saat popup muncul
- Pastikan muncul "USB Connected" di DroidCam app

---

## 💻 Setup di macOS

### 1. Install DroidCam Client (macOS)

**Via Homebrew:**
```bash
brew install droidcam
```

**Manual Download:**
- Download dari: https://www.dev47apps.com/droidcam/mac/
- Extract dan install

### 2. Install ADB (Android Debug Bridge)
```bash
brew install android-platform-tools
```

### 3. Test Koneksi ADB
```bash
# Check device terhubung
adb devices

# Output seharusnya:
# List of devices attached
# XXXXXXXXXX    device
```

### 4. Start DroidCam via USB
```bash
# Start DroidCam client
droidcam-cli -v adb 4747

# Atau dengan resolusi custom:
droidcam-cli -v -size 1280x720 adb 4747
```

---

## 🎥 Akses di OpenCV Python

### Metode 1: Via Video Device (Recommended)
```python
import cv2

# DroidCam biasanya muncul sebagai video device di macOS
# Check index dengan script check_cameras.py
cap = cv2.VideoCapture(1)  # Bisa 1, 2, atau 3 tergantung system

if cap.isOpened():
    print("✅ DroidCam connected!")
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('DroidCam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
```

### Metode 2: Via IP (WiFi fallback)
```python
import cv2

# Jika USB tidak work, pakai WiFi
# Check IP di DroidCam app: WiFi IP section
DROIDCAM_URL = "http://192.168.1.100:4747/video"

cap = cv2.VideoCapture(DROIDCAM_URL)
```

---

## 🔧 Troubleshooting

### Problem: `adb devices` shows "unauthorized"
**Solution:**
```bash
# Revoke dan re-authorize
adb kill-server
adb start-server
adb devices

# Di HP akan muncul popup lagi, centang "Always allow" dan OK
```

### Problem: DroidCam not detected as camera
**Solution:**
```bash
# Restart DroidCam client
killall droidcam-cli
droidcam-cli -v adb 4747

# Check system camera devices
ls -la /dev/video*
```

### Problem: Permission denied on macOS
**Solution:**
```
System Preferences → Security & Privacy → Camera
→ Allow Terminal/Python
```

---

## 🚀 Quick Start Script

Jalankan ini untuk auto-detect DroidCam:

```bash
# 1. Start ADB
adb start-server

# 2. Check device
adb devices

# 3. Start DroidCam
droidcam-cli -v -size 1280x720 adb 4747

# 4. Dalam window Python lain, run:
python3 check_cameras.py  # Untuk cek camera ID

# 5. Gunakan ID yang terdetect di yolov_usb_ui.py
```

---

## 📊 Performance Tips

### Untuk Real-time dengan Minimal Delay:

1. **Use USB** bukan WiFi (lebih stabil, latency rendah)
2. **Lower resolution** untuk FPS tinggi:
   ```bash
   droidcam-cli -v -size 640x480 adb 4747
   ```
3. **Disable camera effects** di HP (HDR, beauty mode, dll)
4. **Close other apps** di HP yang pakai camera

### Recommended Settings:
- Resolution: 1280x720 (balance antara quality & speed)
- FPS: 30
- Connection: USB (latency ~50ms vs WiFi ~200ms)

---

## ✅ Verification Checklist

- [ ] USB Debugging enabled di HP
- [ ] ADB installed di Mac (`adb devices` shows device)
- [ ] DroidCam app running di HP
- [ ] DroidCam client running di Mac (`droidcam-cli -v adb 4747`)
- [ ] Camera permission granted di macOS
- [ ] Test dengan `check_cameras.py` atau `yolov_usb_ui.py`

---

## 🎯 Integration dengan YOLOv8 UI

Setelah DroidCam jalan:

1. Run script check:
   ```bash
   .venv/bin/python3 check_cameras.py
   ```

2. Note camera ID (contoh: Camera 2)

3. Buka `yolov_usb_ui.py` dan set Camera ID ke 2

4. Start detection! 🚀
