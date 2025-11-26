# Quick Start Guide

## For First-Time Users

### 1. Install Dependencies

```bash
cd ChessVision
python3 -m venv venv
source venv/bin/activate
pip install opencv-python numpy python-chess PyQt5 pyttsx3 Pillow
```

### 2. Run the Application

```bash
./venv/bin/python main_without_ai_refactored.py
```

### 3. Calibrate

- Set up **empty** chessboard
- Click **"Calibrate (Empty Board)"**
- Wait for success message

### 4. Play Chess

- Set up pieces in starting position
- Click **"Start Game"**
- Make moves!

## Common Issues

**Problem**: Camera not detected
**Solution**: Check `CAMERA_ID` in code (try 0, 1, or 2)

**Problem**: No moves detected
**Solution**: Increase "Diff Threshold" slider

**Problem**: Too many false detections
**Solution**: Increase "Edge Threshold" slider

## Export Your Game

Click **"Export PGN"** to save game as `.pgn` file for analysis or sharing.
