# ChessVision - Chess Position Tracking System

A real-time chess game tracker with **two versions**: one using AI-powered piece recognition (YOLOv8), and one using edge-based detection without AI. Both versions feature automatic move inference and beautiful Lichess-style visualization.

![ChessVision Demo](https://img.shields.io/badge/Status-Working-brightgreen)

## 📌 Two Versions Available

### 1. **AI Version** (`main.py`)

- Uses YOLOv8 neural network for piece detection
- Recognizes specific pieces (King, Queen, Rook, etc.)
- Requires pre-trained model (`chess_model.pt`)
- More accurate but requires more resources

### 2. **AI-Free Version** (`main_without_ai_refactored.py`)

- Uses edge-based occupancy detection
- No neural network required
- Lighter weight and faster
- **Recommended for most users**

## 🎯 Common Features (Both Versions)

- **Real-time Move Tracking**: Automatically detects and records chess moves
- **Material Gain Heuristic**: Intelligently resolves ambiguous captures
- **Lichess-Style Board**: Beautiful digital board visualization with Unicode pieces
- **PGN Export**: Save games in standard chess notation
- **Undo Functionality**: Quickly revert incorrect detections
- **Pawn Promotion**: Automatic promotion to Queen
- **Live Parameter Tuning**: Adjust edge detection thresholds in real-time
- **Voice Feedback**: Text-to-speech move announcements

## 📋 Requirements

### Hardware

- Webcam or external camera
- Physical chessboard (standard 8x8 with alternating colors)

### Software

- Python 3.7+
- macOS, Linux, or Windows

### Dependencies

```
opencv-python
numpy
python-chess
PyQt5
pyttsx3
Pillow
```

## 🚀 Installation

### 1. Clone or Download

```bash
cd /path/to/your/projects
git clone <your-repo-url>
cd ChessVision
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
# or manually:
pip install opencv-python numpy python-chess PyQt5 pyttsx3 Pillow ultralytics
```

### 4. Download AI Model (Only for AI Version)

If using `main.py` (AI version):

```bash
python download_model.py
# This downloads chess_model.pt (~6MB)
```

**Note**: Skip this step if using the AI-free version.

## 🎮 How to Run

### AI-Free Version (Recommended)

**Option 1**: Refactored (modular code)

```bash
./venv/bin/python main_without_ai_refactored.py
```

**Option 2**: Original (single file)

```bash
./venv/bin/python main_without_ai.py
```

### AI Version (Requires Model)

```bash
./venv/bin/python main.py
```

**Note**: Requires `chess_model.pt` (download via `download_model.py`)

## 📖 Usage Guide

### 1. Setup Your Board

- Place your physical chessboard in front of the camera
- Ensure good lighting
- Make sure the entire board is visible

### 2. Calibrate

1. Set up an **empty chessboard** (no pieces)
2. Click **"Calibrate (Empty Board)"**
3. Wait for "Calibrated Successfully" message
4. Use **"Rotate 90°"** if board orientation is wrong

### 3. Start Playing

1. Set up your pieces in starting position
2. Click **"Start Game"**
3. Make moves on the physical board
4. The system will detect and announce moves

### 4. Controls

- **Export PGN**: Save game to `.pgn` file
- **Undo Move**: Revert last detected move
- **Stop Game**: Reset and start over
- **Debug Mode**: Force moves (ignore chess rules)
- **No Turn Mode**: Allow any color to move

### 5. Parameter Tuning

Adjust sliders if detection is unreliable:

- **Edge Threshold**: Higher = less sensitive
- **Diff Threshold**: Difference from empty board
- **Canny Low/High**: Edge detection sensitivity
- **Blur Kernel**: Noise reduction

## 🤔 Which Version Should I Use?

### Use **AI-Free Version** if:

- ✅ You want quick setup (no model download)
- ✅ You have a standard chessboard with good lighting
- ✅ You prefer lightweight, fast processing
- ✅ You don't mind occasional ambiguity in captures

### Use **AI Version** if:

- ✅ You need precise piece identification
- ✅ You have complex lighting or board conditions
- ✅ You want to detect illegal positions
- ✅ You don't mind the extra setup

### Comparison Table

| Feature                    | AI Version              | AI-Free Version     |
| -------------------------- | ----------------------- | ------------------- |
| Setup Time                 | ~5 min (model download) | ~1 min              |
| Accuracy                   | Higher                  | Good (90%+)         |
| Speed                      | ~20 FPS                 | ~30 FPS             |
| Resource Usage             | Medium (GPU optional)   | Low                 |
| Piece Recognition          | Yes (K,Q,R,B,N,P)       | No (occupancy only) |
| Illegal Position Detection | Yes                     | No                  |
| Model Size                 | 6 MB                    | 0 MB                |

## 🏗️ Architecture

### Modular Structure (Refactored)

```
ChessVision/
├── core/
│   ├── chess_logic.py              # Game state & move inference
│   └── constants.py                # Configuration
├── gui/
│   └── widgets.py                  # Custom UI components
├── utils/
│   ├── audio.py                    # Text-to-speech
│   └── text.py                     # SAN to speech conversion
├── vision/
│   └── (future modules)            # Vision processing
├── main.py                         # AI version (YOLOv8)
├── main_without_ai.py              # AI-free original (monolithic)
├── main_without_ai_refactored.py  # AI-free refactored (modular)
├── download_model.py               # AI model downloader
└── chess_model.pt                  # YOLOv8 weights (after download)
```

### Core Components (Both Versions)

#### 1. **OccupancyChessSystem** (`core/chess_logic.py`)

- Manages game state using `python-chess`
- Infers moves from occupancy grid changes
- Handles special moves (castling, en passant, captures)
- Material Gain Heuristic for ambiguous captures

#### 2. **VisionWorker** (Vision Processing)

- Edge-based occupancy detection using OpenCV
- Camera calibration with chessboard corners
- Real-time frame processing (~30 FPS)

#### 3. **MainWindow** (GUI)

- PyQt5 interface with live video feeds
- Control buttons and parameter sliders
- Move logging and board visualization

## 🎯 How It Works

### Vision Pipeline

1. **Capture**: Read frame from camera
2. **Calibrate**: Detect chessboard corners, warp to 1000x1000 grid
3. **Edge Detection**: Apply Gaussian blur → Canny edge detection
4. **Occupancy**: Count edges per square, compare to empty reference
5. **Debounce**: Wait for stable state (1.5s)
6. **Inference**: Detect changes, infer move type

### Move Inference Logic

- **Standard Move**: 1 source empty + 1 target occupied
- **Capture**: 1 source empty + 0 targets changed (target stays occupied)
- **Castling**: 2 sources + 2 targets
- **En Passant**: 2 sources + 1 target

### Ambiguity Resolution

When multiple captures are possible (e.g., pawn can take left or right), the system chooses the move that captures the **highest value piece**:

- Queen = 9
- Rook = 5
- Bishop/Knight = 3
- Pawn = 1

## 🔧 Troubleshooting

### "Board not found" during calibration

- Ensure empty board is fully visible
- Check lighting (avoid shadows)
- Try adjusting camera angle

### Moves not detected

- Increase **Diff Threshold** slider
- Lower **Blur Kernel**
- Ensure pieces fully settle before moving next

### False detections ("ghost pieces")

- Increase **Edge Threshold**
- Increase **Canny High** threshold
- Recalibrate with empty board

### Ambiguous captures not resolved

- System logs "Ambiguous capture" with candidates
- If wrong piece chosen, use **Undo** and adjust position

## 📦 Files Overview

| File                            | Purpose                           |
| ------------------------------- | --------------------------------- |
| `main_without_ai_refactored.py` | Modular entry point (recommended) |
| `main_without_ai.py`            | Original monolithic version       |
| `core/chess_logic.py`           | Chess game logic                  |
| `core/constants.py`             | Edge thresholds, colors           |
| `utils/audio.py`                | TTS functionality                 |
| `utils/text.py`                 | SAN to speech                     |
| `gui/widgets.py`                | ClickableLabel                    |

## 🎨 Features in Detail

### Lichess-Style Board

- Light squares: `#F0D9B5`
- Dark squares: `#B58863`
- Unicode piece icons (♔♕♖♗♘♙ / ♚♛♜♝♞♟)
- Last move highlighting (yellow overlay)
- Turn indicator (White/Black)
- Detection dots (green = piece detected)

### PGN Export

Games are saved with:

- Standard chess notation
- Timestamp filename (`game_YYYYMMDD_HHMMSS.pgn`)
- Event: "BlindChess Vision Game"
- Compatible with chess.com, lichess.org

### Voice Feedback

Moves are announced in plain English:

- "Pawn to e4"
- "Knight captures f3"
- "Queen to h5 check"
- "Bishop captures f7 checkmate"

## 🐛 Known Limitations

- Requires clear visibility of entire board
- Sensitive to lighting changes
- May struggle with very fast moves
- Pawn promotion only supports Queen (no knight/rook/bishop choice)

## 📝 License

MIT License - feel free to modify and distribute.

## 🙏 Credits

- **python-chess**: Chess logic library
- **OpenCV**: Computer vision
- **PyQt5**: GUI framework
- **Lichess**: Color scheme inspiration

## 💡 Tips for Best Results

1. **Lighting**: Use consistent, diffuse lighting
2. **Camera**: Mount camera directly above or at 45° angle
3. **Board**: High-contrast squares work best
4. **Pieces**: Standard Staunton design recommended
5. **Movement**: Lift pieces cleanly, place firmly
6. **Calibration**: Recalibrate if you move camera

---

**Happy Chess Playing! ♟️**
