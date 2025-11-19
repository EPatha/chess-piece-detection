# 🚀 Quick Start - Chess Detection dengan Camera HP Android via USB

## ✅ CARA TERCEPAT (1 Command):

```bash
python3 run_detection.py
```

**Script ini OTOMATIS akan:**
- ✅ Check ADB terinstall
- ✅ Detect HP Android via USB
- ✅ Setup port forwarding (localhost:4747 → device:4747)
- ✅ Test koneksi DroidCam
- ✅ Launch detection UI dengan model chess
- ✅ Cleanup saat selesai

---

## 📱 Persiapan Satu Kali (Setup Awal):

### 1. Install ADB di Mac:
```bash
brew install android-platform-tools
```

### 2. Setup HP Android:

**a. Enable Developer Mode:**
```
Settings → About Phone → Tap "Build Number" 7 kali
(Akan muncul "You are now a developer!")
```

**b. Enable USB Debugging:**
```
Settings → Developer Options → USB Debugging (ON)
```

**c. Install DroidCam:**
```
Play Store → cari "DroidCam" → Install
```

### 3. Hubungkan USB:
```
1. Colok kabel USB HP ke Mac
2. Popup "Allow USB Debugging?" → Klik OK
3. Centang "Always allow from this computer"
```

---

## 🎮 Cara Pakai (Setiap Kali Mau Deteksi):

### Step 1: Buka DroidCam di HP
- Buka aplikasi DroidCam di HP Android
- **JANGAN minimize atau close app!**
- Biarkan app terbuka di foreground

### Step 2: Jalankan Script
```bash
python3 run_detection.py
```

### Output yang Diharapkan:
```
============================================================
  🚀 DroidCam USB + Chess Detection Launcher
============================================================

🔍 Checking requirements...

✅ ADB installed

📱 Checking Android device via USB...

✅ Android device connected: 4a1293620512

🔌 Setting up port forwarding...

✅ Port forwarding: localhost:4747 → device:4747

📸 Testing DroidCam connection...

✅ DroidCam is ready!

✅ Model ready: runs/chess_detect/train3/weights/best.pt

============================================================
  🎬 Launching Chess Detection UI
============================================================

📌 DroidCam URL: http://127.0.0.1:4747/video
📌 Model: runs/chess_detect/train3/weights/best.pt
📌 Confidence: 0.15 (optimal for chess)
📌 Device: Camera HP Android via USB

⌨️  UI window akan terbuka...
⌨️  Click 'Start' button untuk mulai detection
```

### Step 3: Mulai Detection
1. UI window akan terbuka otomatis
2. Settings sudah optimal:
   - Source: http://127.0.0.1:4747/video
   - Model: runs/chess_detect/train3/weights/best.pt
   - Confidence: 0.15
3. **Click "Start"** button
4. Arahkan camera HP ke papan catur
5. Model akan detect buah catur real-time!

---

## 🔧 Troubleshooting:

### Problem: "No Android device detected"
**Solution:**
```bash
# 1. Check USB connection
adb devices

# Output seharusnya:
# List of devices attached
# 4a1293620512    device

# Jika "unauthorized":
# - Di HP akan muncul popup lagi
# - Klik OK dan centang "Always allow"

# Jika tidak muncul sama sekali:
# - Coba kabel USB lain
# - Pastikan USB Debugging ON
# - Restart HP dan Mac
```

### Problem: "DroidCam not responding"
**Solution:**
1. **Pastikan DroidCam app TERBUKA di HP** (tidak minimize!)
2. Restart DroidCam app
3. Pastikan camera permission granted
4. Test manual:
   ```bash
   adb forward tcp:4747 tcp:4747
   curl -I http://127.0.0.1:4747/video
   # Harus muncul: HTTP/1.0 200 OK
   ```
5. Jalankan `python3 run_detection.py` lagi

### Problem: "ADB not installed"
**Solution:**
```bash
brew install android-platform-tools
```

### Problem: Detection kurang akurat
**Solution:**
- Adjust confidence threshold ke 0.10-0.15 di UI
- Pastikan pencahayaan terang dan merata
- Jarak camera 30-50 cm dari papan
- Background simple/polos lebih baik

---

## 📊 Performance:

| Metric | Value |
|--------|-------|
| Model | YOLOv8n (6 MB) |
| Classes | 13 chess pieces |
| mAP50 | 98.79% ⭐⭐⭐⭐⭐ |
| Latency | ~50ms (USB) vs ~200ms (WiFi) |
| FPS | 10-30 realtime |
| Connection | USB (stable & fast) |

---

## 💡 Tips Optimal:

1. **Pencahayaan:** Terang dan merata, hindari bayangan
2. **Jarak:** 30-50 cm dari papan catur
3. **Angle:** 30-45 derajat dari atas
4. **Background:** Polos lebih baik
5. **Confidence:** 0.10-0.20 untuk chess pieces
6. **USB Cable:** Gunakan kabel berkualitas bagus
7. **DroidCam App:** Jangan minimize saat detection

---

## 🎯 Alternative Methods:

### Method 1: Manual Setup
```bash
# Setup
adb devices
adb forward tcp:4747 tcp:4747

# Run
python3 yolov_ui.py
# Source sudah default: http://127.0.0.1:4747/video
```

### Method 2: Shell Script
```bash
./run_droidcam_usb.sh
```

### Method 3: Built-in Camera Mac (untuk testing)
```bash
python3 yolov_usb_ui.py
# Set Camera ID: 0
```

---

## ✨ Files Penting:

- **`run_detection.py`** ← **GUNAKAN INI!** (Auto setup DroidCam USB)
- **`yolov_ui.py`** - UI untuk MJPEG/DroidCam stream
- **`runs/chess_detect/train3/weights/best.pt`** - Model (mAP 98.79%)
- **`QUICK_START.md`** - Panduan ini

---

Selamat mencoba! 🎉

**Untuk HP Android via USB, cukup:**
1. Buka DroidCam app di HP
2. Run: `python3 run_detection.py`
3. Click "Start" di UI
4. Done! 🚀
