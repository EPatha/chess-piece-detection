# REVISED Project Management Document v2.1: ChessMind Hybrid Vision System

## UI/UX Specification Update Based on Reference Interface

---

## Document Update Summary

**Version:** 2.1 - UI/UX Enhancement  
**Date:** November 27, 2025  
**Changes:** Added comprehensive UI/UX specifications based on reference interface, migrated to Qt5 framework

---

## NEW SECTION: 15. User Interface Specification (Qt5)

### 15.1 UI Framework Decision

**Framework:** Qt5 (PyQt5)

**Rationale:**

- Native desktop performance (superior to Tkinter for complex UIs)
- Professional widget library with modern styling
- Excellent support for multi-window layouts
- Built-in threading for camera processing
- Cross-platform (Windows, macOS, Linux)
- Strong community and documentation

**Technology Stack Update:**

```bash
pip install PyQt5 opencv-python python-chess numpy scikit-image ultralytics
```

---

### 15.2 Main Dashboard Layout

Based on the reference interface, the system shall implement a **three-panel horizontal layout** with comprehensive control sidebar.

#### 15.2.1 Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Menu Bar: File | View | Settings | Help                                │
├──────────────┬──────────────┬──────────────┬────────────┬──────────────┤
│              │              │              │            │              │
│   RAW        │   CROPPED    │    BOARD     │  PIECES    │   LOG VIEW   │
│   CAMERA     │   CAMERA     │    VIEW      │  STATUS    │              │
│   VIEW       │   VIEW       │   (3D-ish)   │   LOG      │  [scrolling  │
│              │              │              │            │   console]   │
│  [live feed] │  [warped     │  [rendered   │ Ex         │              │
│              │   800x800]   │   board]     │ White:     │  Timestamps  │
│              │              │              │  ♙ Pawn1   │  Events      │
│              │   [overlay   │              │    Dead    │  Confidence  │
│              │    boxes]    │              │  ♖ Rook2   │              │
│              │              │              │    Alive   │              │
├──────────────┴──────────────┴──────────────┴────────────┴──────────────┤
│ CONTROL PANEL (Bottom or Right Sidebar)                                │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─ Camera ───────────────────┐  ┌─ Game Control ──────────────────┐   │
│ │ [SELECT CAMERA ID ▼]       │  │ [START GAME]  [STOP GAME]       │   │
│ │ [ROTATE 90°] [ROTATE -90°] │  │ [UNDO MOVE]                     │   │
│ └────────────────────────────┘  └─────────────────────────────────┘   │
│                                                                         │
│ ┌─ Calibration ──────────────┐  ┌─ Edge Detection ────────────────┐   │
│ │ [CALIBRATE CROPPED VIEW]   │  │ PARAMETER 1: [────●────]        │   │
│ └────────────────────────────┘  │ PARAMETER 2: [────●────]        │   │
│                                  │ PARAMETER 3: [────●────]        │   │
│ ┌─ Debug ────────────────────┐  └─────────────────────────────────┘   │
│ │ [DEBUG: IGNORE RULES]      │                                         │
│ │ [DEBUG: NO TURN MODE]      │  ┌─ Export ────────────────────────┐   │
│ └────────────────────────────┘  │ [EXPORT TO PGN]                 │   │
│                                  │ [EXPORT PGN TO LICHESS]         │   │
│                                  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 15.3 Detailed Panel Specifications

#### Panel 1: Raw Camera View

**Size:** 400x300 pixels (16:9 aspect ratio)  
**Purpose:** Show unprocessed camera feed for debugging

**Visual Elements:**

- Live video stream from webcam
- Semi-transparent overlay text: "RAW CAMERA VIEW"
- FPS counter (top-right corner)
- Camera status indicator (green dot = connected)

**User Interactions:**

- Click to select different camera (if multiple available)
- Right-click for camera properties menu

**Qt5 Implementation Notes:**

- Use `QLabel` with `QPixmap` updates
- Thread: Dedicated `QThread` for camera capture
- Update rate: 30 FPS (33ms timer)

---

#### Panel 2: Cropped Camera View (Warped Board)

**Size:** 400x400 pixels (1:1 aspect ratio, represents 800x800 internal processing)  
**Purpose:** Show perspective-corrected board with detection overlays

**Visual Elements:**

- Warped/homography-transformed board view
- Semi-transparent overlay text: "CROPPED CAMERA VIEW"
- Detection overlays:
  - **Green rectangles:** White piece detected
  - **Red rectangles:** Black piece detected
  - **Blue rectangles:** Occupied (color uncertain)
  - **Yellow rectangles:** Edge detection uncertainty
- Grid overlay (8x8, toggleable via settings)
- Calibration points (yellow dots, visible only during calibration)

**User Interactions:**

- **Calibration mode:** Click 4 corners (TL→TR→BR→BL) to set homography
- **Manual correction mode:** Click square to open piece editor dialog
- Right-click for context menu (recalibrate, save view, etc.)

**Qt5 Implementation Notes:**

- Use `QGraphicsView` + `QGraphicsScene` for overlay rendering
- Custom `QGraphicsRectItem` for detection boxes
- Color-coded based on detection confidence

---

#### Panel 3: Board View (3D-Rendered)

**Size:** 400x400 pixels  
**Purpose:** Display logical game state in attractive 3D visualization

**Visual Elements:**

- 3D-rendered chessboard (similar to chess.com/lichess style)
- Realistic piece models with shadows
- Optional: Last move highlighted (yellow arrow)
- Optional: Legal moves shown when piece selected
- Coordinate labels (a-h, 1-8)

**Rendering Options:**

1. **Simple (MVP):** Use chess piece Unicode symbols (♔♕♖♗♘♙) on 2D grid
2. **Advanced (Phase 2):** Use OpenGL or pre-rendered 3D sprites

**Qt5 Implementation Notes:**

- Simple: `QGraphicsView` with chess symbols
- Advanced: `QOpenGLWidget` for 3D rendering
- Update only when board state changes (not every frame)

---

#### Panel 4: Pieces Status Log

**Size:** 250x600 pixels  
**Purpose:** Show real-time piece status (alive/dead/unavailable)

**Layout:**

```
┌─ PIECES STATUS LOG ──────┐
│ Ex                        │
│ White:                    │
│   ♙ Pawn 1 - Dead         │
│   ♙ Pawn 2 - Alive        │
│   ♖ Rook 1 - Alive        │
│   ♖ Rook 2 - Alive        │
│   ♘ Knight 1 - Alive      │
│   ♘ Knight 2 - Dead       │
│   ♗ Bishop 1 - Alive      │
│   ♗ Bishop 2 - Alive      │
│   ♕ Queen - Alive         │
│   ♔ King - Alive          │
│                           │
│ Black:                    │
│   ♟ Pawn 1 - Unavailable │
│     (not deployed)        │
│   ♟ Pawn 2 - Alive        │
│   ...                     │
└───────────────────────────┘
```

**Status Colors:**

- **Green text:** Alive (on board)
- **Red text:** Dead (captured)
- **Gray text:** Unavailable (not yet on board, for starting position validation)

**Qt5 Implementation Notes:**

- Use `QListWidget` with custom item delegates
- Update dynamically when moves detected
- Icons: Use chess Unicode symbols

---

#### Panel 5: Log View (Console)

**Size:** 350x600 pixels  
**Purpose:** Scrolling event log with timestamps

**Log Entry Format:**

```
[HH:MM:SS] Event Type - Details
[HH:MM:SS.ms] Category: Message
```

**Log Categories:**

- **System:** Startup, shutdown, errors (white text)
- **Detection:** Occupancy changes, color detection (cyan text)
- **Move:** Valid moves, invalid moves (green/red text)
- **Warning:** Desync detected, low confidence (yellow text)
- **Debug:** Technical details (gray text, toggleable)

**Example Entries:**

```
[14:08:22] System: Application started
[14:08:25] System: Camera 0 connected (1920x1080)
[14:08:30] Calibration: 4 points captured
[14:08:31] System: Homography matrix calculated
[14:09:15] Detection: E2 became empty
[14:09:15] Detection: E4 became occupied (white piece)
[14:09:15] Move: Pawn E2→E4 (confidence: 0.95)
[14:09:16] Move: White Pawn moved to E4
[14:10:22] Warning: No legal move found for change at D5
[14:10:23] Warning: Desynchronization suspected (confidence: 0.42)
```

**Qt5 Implementation Notes:**

- Use `QPlainTextEdit` (read-only)
- Auto-scroll to bottom on new entries
- Color formatting with HTML/rich text
- Max buffer: 1000 lines (older entries auto-deleted)
- "Save Log" button to export to text file

---

### 15.4 Control Panel Components

#### 15.4.1 Camera Control Section

**SELECT CAMERA ID (Dropdown)**

- Lists all available cameras: "Camera 0", "Camera 1", etc.
- Auto-detect on startup
- Live preview updates when selection changes

**ROTATE 90° / ROTATE -90° (Buttons)**

- Rotates raw camera feed before processing
- Useful for cameras mounted sideways
- Persists rotation setting in config file

**Visual Design:**

- Yellow background (#FFD95A)
- Black text, rounded corners
- Grouped in box with header "Camera"

---

#### 15.4.2 Game Control Section

**START GAME (Button)**

- Validates starting position (32 pieces detected)
- Initializes `chess.Board()` object
- Enables move detection
- Changes to "RESUME GAME" if paused
- Green border when active

**STOP GAME (Button)**

- Pauses move detection
- Preserves current board state
- Useful for taking breaks
- Red border when stopped

**UNDO MOVE (Button)**

- Reverts last move in `chess.Board()`
- Useful for correcting false detections
- Shows confirmation dialog: "Undo [move]? (Y/N)"
- Disabled if no moves to undo

**Visual Design:**

- Yellow background (#FFD95A)
- Black text, rounded corners
- Grouped in box with header "Game Control"

---

#### 15.4.3 Calibration Section

**CALIBRATE CROPPED VIEW (Button)**

- Activates calibration mode
- Instruction overlay appears: "Click 4 corners: TL → TR → BR → BL"
- Button text changes to "CALIBRATING..." (disabled)
- Green checkmark appears when complete

**Visual Design:**

- Yellow background (#FFD95A)
- Black text, rounded corners

---

#### 15.4.4 Edge Detection Parameters Section

**PARAMETER 1: Canny Lower Threshold (Slider)**

- Range: 0-255
- Default: 50
- Label shows current value in real-time
- Affects edge detection sensitivity

**PARAMETER 2: Canny Upper Threshold (Slider)**

- Range: 0-255
- Default: 150
- Auto-updates processed view

**PARAMETER 3: Occupancy Threshold (Slider)**

- Range: 0-500
- Default: 50 (pixel count)
- Determines "occupied" vs "empty"

**Visual Design:**

- Light blue background (#87CEEB)
- White text on header
- Sliders with visible track and handle
- Real-time value labels (e.g., "Param 1: 50")

**Qt5 Implementation:**

- `QSlider` with horizontal orientation
- `valueChanged` signal triggers immediate reprocessing
- Values saved to config file on change

---

#### 15.4.5 Debug Section

**DEBUG: IGNORE RULES (Toggle Button)**

- When enabled: System accepts all moves (no `chess.Board()` validation)
- Useful for testing detection without playing legal games
- Red border when active (warning state)

**DEBUG: NO TURN MODE (Toggle Button)**

- When enabled: Allows both colors to move any time (no turn enforcement)
- Useful for testing
- Red border when active

**Visual Design:**

- Yellow background (#FFD95A)
- Black text
- Toggle state: Pressed appearance when active

---

#### 15.4.6 Export Section

**EXPORT TO PGN (Button)**

- Opens file save dialog
- Exports game as `.pgn` file
- Includes metadata: Date, Event, White/Black (placeholder), Result

**EXPORT PGN TO LICHESS (Button)**

- Copies PGN to clipboard with instructions
- Opens browser to lichess.org/paste (optional)
- Shows toast notification: "PGN copied to clipboard!"

**Visual Design:**

- Yellow background (#FFD95A)
- Black text, rounded corners

---

### 15.5 Additional UI Features

#### 15.5.1 Menu Bar

**File Menu:**

- New Game (Ctrl+N)
- Load Game from PGN (Ctrl+O)
- Save Game (Ctrl+S)
- Exit (Ctrl+Q)

**View Menu:**

- Toggle Grid Overlay
- Toggle FPS Counter
- Toggle Debug Panel
- Full Screen (F11)

**Settings Menu:**

- Camera Settings (resolution, exposure, etc.)
- Color Detection Thresholds
- Audio Settings (TTS enable/disable)
- Theme (Light/Dark mode)

**Help Menu:**

- Quick Start Guide
- Troubleshooting
- About

#### 15.5.2 Status Bar (Bottom)

```
[System Status: ●READY]  |  [Board: Synchronized]  |  [Confidence: 0.95]  |  [FPS: 28]
```

**Status Indicators:**

- **System Status:** READY (green) | CALIBRATING (yellow) | ERROR (red)
- **Board:** Synchronized (green) | Desynced (red) | Unknown (gray)
- **Confidence:** 0.00-1.00 (color-coded: >0.8 green, 0.5-0.8 yellow, <0.5 red)
- **FPS:** Current frame rate

---

#### 15.5.3 Modal Dialogs

**Manual Correction Dialog (triggered by right-click on square):**

```
┌─ Correct Square E4 ──────────────────┐
│                                       │
│ Current: Empty                        │
│ Set to:                               │
│   ○ Empty                             │
│   ○ White Pawn                        │
│   ○ White Knight                      │
│   ○ White Bishop                      │
│   ○ White Rook                        │
│   ○ White Queen                       │
│   ○ White King                        │
│   ○ Black Pawn                        │
│   ○ Black Knight                      │
│   ... (all 12 piece types)            │
│                                       │
│        [APPLY]         [CANCEL]       │
└───────────────────────────────────────┘
```

**Desynchronization Alert Dialog:**

```
┌─ Warning: Board State Desynchronized ─┐
│                                        │
│ The system detected inconsistencies    │
│ between camera view and internal       │
│ board state.                           │
│                                        │
│ Possible causes:                       │
│  • Illegal move was made              │
│  • Piece was accidentally moved       │
│  • Lighting changed significantly     │
│                                        │
│ Options:                               │
│  [UNDO LAST MOVE]                     │
│  [MANUAL CORRECTION]                  │
│  [RESET TO CURRENT CAMERA VIEW]       │
│  [IGNORE (Continue Anyway)]           │
│                                        │
└────────────────────────────────────────┘
```

---

### 15.6 Color Scheme & Styling

#### Color Palette (Based on Reference UI)

**Primary Colors:**

- Control Buttons: `#FFD95A` (Bright Yellow)
- Parameter Section: `#87CEEB` (Light Blue)
- Status Section: `#FF69B4` (Pink/Magenta)
- Log Background: `#1E1E1E` (Dark Gray)
- Main Background: `#2B2B2B` (Charcoal)

**Text Colors:**

- Primary: `#000000` (Black) on light backgrounds
- Primary: `#FFFFFF` (White) on dark backgrounds
- Success: `#00FF00` (Bright Green)
- Warning: `#FFFF00` (Yellow)
- Error: `#FF0000` (Red)
- Info: `#00FFFF` (Cyan)

**Border/Accent:**

- Active elements: 2px solid `#FFD95A`
- Inactive: 1px solid `#555555`
- Hover: 2px solid `#FFFFFF`

#### Qt5 Stylesheet Example

```python
STYLESHEET = """
QMainWindow {
    background-color: #2B2B2B;
}

QPushButton {
    background-color: #FFD95A;
    color: #000000;
    border: 2px solid #000000;
    border-radius: 8px;
    padding: 10px;
    font-size: 12pt;
    font-weight: bold;
}

QPushButton:hover {
    border: 2px solid #FFFFFF;
}

QPushButton:pressed {
    background-color: #FFC000;
}

QPushButton:disabled {
    background-color: #808080;
    color: #404040;
}

QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px;
    background: #FFFFFF;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #FFD95A;
    border: 2px solid #000000;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QLabel {
    color: #FFFFFF;
    font-size: 10pt;
}

QPlainTextEdit {
    background-color: #1E1E1E;
    color: #00FF00;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    border: 1px solid #555555;
}
"""
```

---

### 15.7 Responsive Layout Behavior

**Window Minimum Size:** 1600x900 pixels  
**Recommended:** 1920x1080 (Full HD)

**Resize Behavior:**

- Panels scale proportionally
- Control panel can collapse to icon-only mode
- Log view can be hidden via View menu
- Board views maintain aspect ratio (no distortion)

**Multi-Monitor Support:**

- Panels can be "popped out" to separate windows
- Useful for dual-monitor setups (camera on one, board on other)

---

## UPDATED SECTION: 3. Functional Requirements

### 3.1 Core Features - Phase 1 (MVP) - UPDATED WITH UI

**FR-11: Qt5 User Interface (NEW)**

- System MUST implement all UI panels as specified in Section 15
- System MUST provide real-time visual feedback on all panels
- System MUST update views at >15 FPS without UI lag
- System MUST support window resizing and multi-monitor setups
- Acceptance Criteria: All panels functional, <50ms UI response time

**FR-12: Real-Time Parameter Adjustment (NEW)**

- System MUST allow edge detection parameters to be adjusted via sliders
- System MUST apply parameter changes immediately (live preview)
- System MUST save parameter values to config file
- Acceptance Criteria: Changes visible within 100ms, settings persist across sessions

**FR-13: Interactive Calibration (NEW)**

- System MUST provide visual feedback during calibration (yellow dots on corners)
- System MUST validate calibration (check for convex quadrilateral)
- System MUST allow re-calibration without restarting application
- Acceptance Criteria: Calibration completable in <30 seconds with clear visual guidance

**FR-14: Comprehensive Logging (NEW)**

- System MUST log all events with timestamps to Log View panel
- System MUST color-code log entries by category
- System MUST support log export to text file
- System MUST limit log buffer to 1000 entries (performance)
- Acceptance Criteria: All significant events logged with <10ms delay

**FR-15: Piece Status Tracking (NEW)**

- System MUST maintain and display status for all 32 pieces
- System MUST update Pieces Status Log panel in real-time
- System MUST color-code piece status (alive/dead/unavailable)
- Acceptance Criteria: Status updates within 200ms of move detection

---

## UPDATED SECTION: 5. Technical Specifications

### 5.1 Technology Stack (UPDATED FOR UI)

**Programming Language:** Python 3.8+

**Core Libraries:**

- `PyQt5` (GUI framework - PRIMARY UI TOOL)
- `opencv-python` (Computer vision operations)
- `python-chess` (Chess logic and validation)
- `numpy` (Numerical operations)
- `scikit-image` (Color space conversions)

**Optional Libraries:**

- `ultralytics` (YOLO for Phase 2)
- `PyOpenGL` (3D board rendering for Phase 2)
- `pyttsx3` (Text-to-speech)
- `pyperclip` (Clipboard operations for PGN export)

### 5.2 Qt5 Architecture

**Main Application Structure:**

```
ChessMindApp (QMainWindow)
├── CameraThread (QThread) - Captures frames
├── ProcessingThread (QThread) - Runs detection algorithms
├── UIUpdateThread (QThread) - Updates displays
└── Panels (QWidget subclasses)
    ├── RawCameraPanel
    ├── CroppedCameraPanel (QGraphicsView)
    ├── BoardViewPanel (QGraphicsView or QOpenGLWidget)
    ├── PieceStatusPanel (QListWidget)
    └── LogViewPanel (QPlainTextEdit)
```

**Threading Model:**

- **Main Thread:** UI updates only (Qt requirement)
- **Camera Thread:** cv2.VideoCapture() loop
- **Processing Thread:** Edge detection, color detection, move inference
- Communication: Qt signals/slots (thread-safe)

---

## UPDATED SECTION: 7. Development Phases

### Phase 1: MVP with Complete UI (UPDATED)

**Duration:** 4-5 weeks (increased from 3-4 due to UI complexity)

**Week 1-2: Core Detection + UI Framework**

- Set up Qt5 application skeleton
- Implement 5-panel layout
- Camera capture thread with Raw Camera View
- Basic edge detection with Cropped Camera View
- Control panel buttons (non-functional stubs)

**Week 3: Logic + UI Integration**

- HSV color detection
- Move inference logic
- Board View panel with chess symbols
- Pieces Status Log updates
- Log View with event logging

**Week 4-5: Polish + Testing**

- Interactive calibration with visual feedback
- Parameter sliders with live updates
- Desync detection + alert dialogs
- Manual correction UI
- Comprehensive testing with real users

**Success Criteria (Updated):**

- All UI panels functional and responsive
- Can track simple games with 80%+ accuracy
- Desync detection works reliably
- Users can calibrate and correct manually without external help
- Application runs at 15+ FPS with all panels active

---

### Phase 2: Enhanced Detection (UNCHANGED TIMELINE)

**Duration:** 4-6 weeks

**Additional UI Features:**

- 3D board rendering (OpenGL)
- Advanced piece status (show confidence scores)
- Move history timeline (scrubber to review past moves)
- Export to multiple formats (PGN, FEN, GIF animation)

---

### Phase 3: User Experience (UPDATED)

**Duration:** 2-3 weeks

**UI Enhancements:**

- Dark/Light theme toggle
- Customizable panel layouts (drag-and-drop)
- Keyboard shortcuts for all functions
- Tutorial overlay (first-run experience)
- Settings persistence across sessions
- Improved error messages with screenshots

---

## UPDATED SECTION: 8. Testing Strategy

### 8.1 UI/UX Testing (NEW)

**Usability Tests:**

- First-time user setup (target: <20 minutes)
- Calibration ease-of-use (target: <3 failed attempts)
- Manual correction workflow (target: <60 seconds)
- Parameter adjustment intuitiveness (target: no documentation needed)

**Performance Tests:**

- UI responsiveness during processing (target: <50ms lag)
- Memory usage with all panels active (target: <500MB)
- Frame rate stability over 2-hour session (target: >15 FPS sustained)

**Visual Tests:**

- Color contrast (WCAG AA compliance)
- Readability of log text
- Panel scaling on different resolutions (1080p, 1440p, 4K)

---

## UPDATED SECTION: 11. Deployment Instructions

### 11.1 Environment Setup (UPDATED)

```bash
# Create virtual environment
python3 -m venv chess_hybrid
source chess_hybrid/bin/activate  # Mac/Linux

# Install dependencies (UPDATED with Qt5)
pip install PyQt5 opencv-python python-chess numpy scikit-image

# Optional: Install advanced features
pip install ultralytics PyOpenGL pyttsx3 pyperclip

# Verify Qt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('Qt5 OK')"
```

### 11.2 First Run (UPDATED)

1. Run: `python chess_mind_app.py`
2. **UI loads:** All 5 panels appear, control buttons visible
3. **Select camera:** Use dropdown to choose camera (if multiple)
4. **Lighting check:** Status bar shows lighting quality
5. **Calibration:** Click "CALIBRATE CROPPED VIEW", then click 4 corners
6. **Verify:** Cropped Camera View should show warped board
7. **Start game:** Click "START GAME"
8. **Play:** Make moves one at a time, observe Log View for feedback

---

## UPDATED SECTION: 16. Qt5 Implementation Guide (NEW)

### 16.1 File Structure

```
chess_hybrid/
├── chess_mind_app.py          # Main application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # QMainWindow subclass
│   ├── panels/
│   │   ├── raw_camera_panel.py
│   │   ├── cropped_camera_panel.py
│   │   ├── board_view_panel.py
│   │   ├── piece_status_panel.py
│   │   └── log_view_panel.py
│   ├── dialogs/
│   │   ├── manual_correction_dialog.py
│   │   └── desync_alert_dialog.py
│   └── styles.py              # Qt stylesheets
├── core/
│   ├── __init__.py
│   ├── camera_thread.py       # QThread for camera capture
│   ├── processing_thread.py   # QThread for detection
│   ├── hybrid_manager.py      # Core logic (updated from original)
│   ├── color_detector.py      # HSV color detection
│   └── state_manager.py       # Board state + desync detection
├── utils/
│   ├── __init__.py
│   ├── config.py              # Settings management
│   ├── logger.py              # Event logging
│   └── pgn_exporter.py        # PGN export functions
├── resources/
│   ├── icons/                 # Button icons
│   └── chess_pieces/          # SVG or PNG piece images
├── config.json                # User settings (auto-generated)
└── requirements.txt           # Python dependencies
```

### 16.2 Key Implementation Patterns

#### Pattern 1: Camera Thread with Qt Signals

```python
# core/camera_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import cv2

class CameraThread(QThread):
    frame_ready = pyqtSignal(object)  # Emits numpy array

    def __init__(self, camera_id=0):
        super().__init__()
        self.camera_id = camera_id
        self.running = False

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(33)  # ~30 FPS

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
```

#### Pattern 2: Panel Base Class

```python
# ui/panels/base_panel.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class BasePanel(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title overlay
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-size: 14pt;
            font-weight: bold;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        self.setLayout(layout)
```

#### Pattern 3: Signal/Slot Communication

```python
# ui/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create threads
        self.camera_thread = CameraThread(camera_id=0)
        self.processing_thread = ProcessingThread()

        # Connect signals
        self.camera_thread.frame_ready.connect(self.on_frame_ready)
        self.processing_thread.move_detected.connect(self.on_move_detected)

        # Start threads
        self.camera_thread.start()
        self.processing_thread.start()

    def on_frame_ready(self, frame):
        # Update Raw Camera Panel
        self.raw_panel.update_frame(frame)
        # Send to processing
        self.processing_thread.process_frame(frame)

    def on_move_detected(self, move_data):
        # Update Board View
        self.board_panel.update_board(move_data['fen'])
        # Update Log
        self.log_panel.add_entry(f"Move: {move_data['san']}")
```

### 16.3 Configuration Management

```python
# utils/config.py
import json
import os

class Config:
    DEFAULT_CONFIG = {
        "camera_id": 0,
        "camera_rotation":
```
