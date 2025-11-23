# Chessboard Grid Detection - Training & Usage Guide

## 📋 Overview
Train YOLOv8 model untuk mendeteksi 64 kotak chessboard (grid A-H) beserta corners.

Dataset: `Chessboard/`
- Classes: A, B, C, D, E, F, G, H, chessboard-corners, chessfield, innerChessboard
- Total: 11 classes

---

## 🚀 Quick Start

### 1. Training Model

```bash
python3 train_chessboard.py
```

**Training Configuration:**
- Model: YOLOv8n (nano - fastest)
- Epochs: 100
- Image Size: 640x640
- Batch Size: 16
- Device: MPS (Apple Silicon GPU)
- Early Stopping: Patience 20

**Output:**
- Best model: `runs/chessboard_detect/chessboard_grid/weights/best.pt`
- Last model: `runs/chessboard_detect/chessboard_grid/weights/last.pt`
- Training plots: `runs/chessboard_detect/chessboard_grid/`

**Training Time:** ~30-60 minutes (tergantung hardware)

---

### 2. Test Model

#### A. Test on Image
```bash
python3 test_chessboard_model.py image.jpg
```

#### B. Validate on Test Set
```bash
python3 test_chessboard_model.py
```

**Expected Results:**
- mAP50: >0.90 (90%+)
- mAP50-95: >0.70 (70%+)

---

### 3. Real-time Detection with USB Camera

```bash
python3 chessboard_ui.py
```

**Or with specific camera:**
```bash
python3 chessboard_ui.py 0  # Camera ID 0
python3 chessboard_ui.py 1  # Camera ID 1 (HP Android via Iriun)
```

**UI Controls:**
- **Camera ID**: Pilih camera (0 = built-in, 1+ = external/USB)
- **Confidence**: Threshold deteksi (0.25 recommended)
- **Model**: Path ke model weights
- **Start/Stop**: Mulai/stop detection

---

## 📊 Dataset Info

**Structure:**
```
Chessboard/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── data.yaml
```

**Classes (11):**
1. A, B, C, D, E, F, G, H - Column markers
2. chessboard-corners - 4 corners of board
3. chessfield - Individual square
4. innerChessboard - Inner board area

---

## 🎯 Use Cases

### 1. Detect Chessboard Grid
Model akan deteksi:
- 8 kolom (A-H)
- 4 corners board
- 64 individual squares (chessfield)
- Inner board area

### 2. Integrate with Chess Piece Detection
Kombinasi dengan model chess piece detection:
```python
# 1. Detect chessboard grid
grid_model = YOLO("runs/chessboard_detect/chessboard_grid/weights/best.pt")
grid_results = grid_model(image)

# 2. Detect chess pieces
piece_model = YOLO("runs/chess_detect/train3/weights/best.pt")
piece_results = piece_model(image)

# 3. Map pieces to grid
# ... (mapping logic)
```

---

## 💡 Tips

### Training:
- Monitor loss curves di `runs/chessboard_detect/chessboard_grid/`
- Jika overfit: kurangi epochs atau tambah augmentation
- Jika underfit: tambah epochs atau pakai model lebih besar (yolov8s)

### Detection:
- Confidence 0.20-0.30 biasanya optimal
- Pastikan lighting cukup
- Board harus terlihat penuh (semua corners)
- Minimal background clutter

### Camera Setup:
- Posisi camera dari atas (bird's eye view) ideal
- Jarak ~50cm dari board
- Background kontras dengan board

---

## 🔧 Troubleshooting

### Error: "data.yaml not found"
```bash
# Check path
ls Chessboard/data.yaml
```

### Low mAP Score
- Training belum cukup epochs
- Data augmentation terlalu aggressive
- Image quality buruk

### Camera not detected
```bash
# Check available cameras
python3 << EOF
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        cap.release()
EOF
```

---

## 📈 Next Steps

1. **Train model** → `python3 train_chessboard.py`
2. **Test accuracy** → `python3 test_chessboard_model.py`
3. **Run UI** → `python3 chessboard_ui.py`
4. **Integrate** → Combine grid detection + piece detection

---

## 🎉 Expected Output

**Terminal:**
```
📊 Training Configuration:
   Model: yolov8n.pt
   Epochs: 100
   Image Size: 640
   Batch Size: 16

🚀 Starting training...

Epoch 1/100: loss=1.234, mAP50=0.567
Epoch 2/100: loss=0.987, mAP50=0.678
...
Epoch 50/100: loss=0.123, mAP50=0.945

✅ Training Complete!
   Best mAP50: 0.945
   Model: runs/chessboard_detect/chessboard_grid/weights/best.pt
```

**UI Window:**
- Real-time video dengan bounding boxes
- Label: A, B, C, D, E, F, G, H
- Corners detection
- Square detection
- FPS counter

---

Good luck! 🚀
