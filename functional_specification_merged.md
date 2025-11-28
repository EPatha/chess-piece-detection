# ChessMind Hybrid Vision System - Complete Specification

**Version:** 2.1 - Merged Technical + UI/UX Specification  
**Date:** November 27, 2025  
**Status:** Ready for Implementation

---

## Document Summary

This specification merges critical technical corrections with comprehensive UI/UX design using Qt5. It provides realistic expectations for an MVP chess tracking system that combines computer vision with chess logic.

---

## Executive Summary

This system tracks chess board occupancy using computer vision and infers piece identity through move logic. **Critical limitation:** Phase 1 MVP cannot visually identify specific pieces—it detects occupancy and color only. Visual piece classification requires Phase 2 custom YOLO training.

---

## 1. Project Overview

### 1.1 Project Name

**ChessMind Hybrid: Logic-First Chess Tracking System with Qt5 Interface**

### 1.2 Core Objectives

- Real-time chess board occupancy monitoring
- Color-based piece detection (white vs black)
- Move inference through chess rule validation
- Professional Qt5 desktop interface
- Desynchronization detection and manual correction
- PGN export functionality

### 1.3 System Capabilities & Limitations

**What It CAN Do:**

- Detect occupied vs empty squares (>90% accuracy)
- Distinguish white from black pieces (>85% accuracy)
- Infer piece identity from legal moves (>80% accuracy for unambiguous moves)
- Maintain legal game state
- Detect when system becomes confused
- Allow manual state correction

**What It CANNOT Do (Phase 1):**

- Visually identify piece types (requires Phase 2 training)
- Handle ambiguous moves without user input
- Recover from illegal moves automatically
- Track simultaneous piece movements
- Function reliably in poor lighting

---

## 2. System Architecture

### 2.1 Three-Layer Architecture

#### Layer 1: Perception (Computer Vision)

- **Primary:** Canny edge detection for occupancy
- **Secondary:** HSV color masking (white vs black)
- **Optional:** Generic YOLO for verification
- **Output:** 8×8 occupancy grid + color information

#### Layer 2: Logic (Chess Engine)

- **Engine:** python-chess library
- **Functions:** Move inference, validation, state management
- **New:** Desynchronization detection, confidence scoring
- **Output:** Validated moves, board state (FEN), alerts

#### Layer 3: Interface (Qt5 GUI)

- **Framework:** PyQt5
- **Components:** 5-panel dashboard, control sidebar, modal dialogs
- **Features:** Real-time visualization, parameter tuning, manual correction
- **Output:** Visual feedback, event logs, PGN export

---

## 3. User Interface Specification (Qt5)

### 3.1 Main Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Menu Bar: File | View | Settings | Help                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  RAW CAMERA  │   CROPPED    │  BOARD VIEW  │  PIECES STATUS +   │
│     VIEW     │  CAMERA VIEW │   (Logical)  │     LOG VIEW       │
│              │   [warped    │  [rendered   │                    │
│  [live feed] │    800×800]  │   board]     │  Status: Alive/    │
│              │   [overlay   │              │  Dead/Unavailable  │
│  FPS: 28     │    boxes]    │  Coordinates │                    │
│              │              │              │  [scrolling log]   │
│  400×300px   │   400×400px  │   400×400px  │    600×350px       │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│  CONTROL PANEL (Bottom/Right Sidebar)                          │
│  [Camera Selection] [Calibration] [Game Control] [Parameters]  │
│  [Debug Options] [Export Functions]                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Panel Specifications

**Panel 1: Raw Camera View** (400×300px)

- Unprocessed webcam feed
- FPS counter, camera status indicator
- Click to select camera source

**Panel 2: Cropped Camera View** (400×400px)

- Perspective-corrected board (homography transformed)
- Detection overlays: Green (white piece), Red (black), Blue (uncertain), Yellow (edge issues)
- 8×8 grid overlay (toggleable)
- Interactive calibration (click 4 corners)

**Panel 3: Board View** (400×400px)

- Logical game state visualization
- Chess Unicode symbols (♔♕♖♗♘♙)
- Last move highlighting
- Coordinate labels (a-h, 1-8)

**Panel 4: Pieces Status Log** (250×600px)

- Real-time piece tracking: White & Black
- Status per piece: Alive (green), Dead (red), Unavailable (gray)
- Example: "♙ Pawn 1 - Dead"

**Panel 5: Event Log** (350×600px)

- Scrolling console with timestamps
- Color-coded categories: System (white), Detection (cyan), Move (green/red), Warning (yellow), Debug (gray)
- Example: `[14:09:15] Move: Pawn E2→E4 (confidence: 0.95)`

### 3.3 Control Panel Components

**Camera Control:**

- Camera ID dropdown
- Rotate 90°/-90° buttons
- Background: Yellow (#FFD95A)

**Game Control:**

- START GAME / STOP GAME
- UNDO MOVE
- Background: Yellow (#FFD95A)

**Calibration:**

- CALIBRATE CROPPED VIEW button
- Visual feedback during calibration

**Edge Detection Parameters:**

- Slider 1: Canny Lower Threshold (0-255, default 50)
- Slider 2: Canny Upper Threshold (0-255, default 150)
- Slider 3: Occupancy Threshold (0-500, default 50)
- Real-time parameter adjustment
- Background: Light Blue (#87CEEB)

**Debug Options:**

- DEBUG: IGNORE RULES (toggle)
- DEBUG: NO TURN MODE (toggle)
- Red border when active

**Export:**

- EXPORT TO PGN
- EXPORT PGN TO LICHESS

### 3.4 Modal Dialogs

**Manual Correction Dialog:**

- Select square to correct
- Radio buttons for all piece types (12 options + Empty)
- Apply/Cancel buttons

**Desynchronization Alert:**

- Warning message with causes
- Options: Undo Last Move, Manual Correction, Reset, Ignore

### 3.5 Color Scheme

**Primary Colors:**

- Buttons: #FFD95A (Yellow)
- Parameters: #87CEEB (Light Blue)
- Background: #2B2B2B (Charcoal)
- Log: #1E1E1E (Dark Gray)

**Text Colors:**

- Success: #00FF00, Warning: #FFFF00, Error: #FF0000, Info: #00FFFF

---

## 4. Functional Requirements

### 4.1 Core Features (Phase 1 MVP)

**FR-1: Occupancy Detection**

- Canny edge detection as primary method
- > 90% accuracy on occupied/empty detection

**FR-2: Color Detection (HSV Masking)**

- Distinguish white vs black pieces
- > 85% accuracy under good lighting
- Visual feedback with color-coded rectangles

**FR-3: Perspective Calibration**

- 4-point manual calibration (click corners)
- Homography transformation to 800×800px
- Completion time: <30 seconds

**FR-4: Move Inference with Color Information**

- Detect from-square → to-square changes
- Use color to narrow legal move set
- Handle ambiguous moves with user prompts
- > 80% accuracy for unambiguous moves

**FR-5: State Desynchronization Detection**

- Track confidence score
- Detect: repeated illegal moves, persistent mismatches, low confidence patterns
- Alert user within 3 moves of desync
- > 90% detection rate

**FR-6: Manual State Correction**

- UI for setting piece type/color per square
- Re-synchronize internal state
- Recovery time: <60 seconds

**FR-7: Qt5 User Interface**

- All 5 panels operational
- Real-time updates (>15 FPS)
- <50ms UI response time
- Window resizing and multi-monitor support

**FR-8: Real-Time Parameter Adjustment**

- Edge detection sliders with live preview
- Changes visible within 100ms
- Settings persist across sessions

**FR-9: Comprehensive Event Logging**

- Timestamp all events (<10ms delay)
- Color-coded categories
- Export log to text file
- 1000-entry buffer limit

**FR-10: Piece Status Tracking**

- Track all 32 pieces (alive/dead/unavailable)
- Real-time panel updates (<200ms delay)

### 4.2 Advanced Features (Phase 2)

**FR-11: Custom YOLO Training**

- Train on chess-specific dataset (12 classes)
- 2000+ labeled images required
- > 90% piece classification accuracy

**FR-12: Special Move Handling**

- Castling (4-square detection)
- En passant (3-square change)
- Promotion (user prompt)

**FR-13: Audio Feedback**

- TTS move announcements
- Audio warnings for desync

**FR-14: 3D Board Rendering**

- OpenGL visualization
- Realistic piece models with shadows

---

## 5. Technical Specifications

### 5.1 Technology Stack

**Programming Language:** Python 3.8+

**Core Libraries:**

- `PyQt5` - GUI framework (PRIMARY)
- `opencv-python` - Computer vision
- `python-chess` - Chess logic
- `numpy` - Numerical operations
- `scikit-image` - Color conversions

**Optional:**

- `ultralytics` - YOLO (Phase 2)
- `PyOpenGL` - 3D rendering (Phase 2)
- `pyttsx3` - Text-to-speech
- `pyperclip` - Clipboard operations

### 5.2 Qt5 Architecture

**Threading Model:**

- Main Thread: UI updates only
- Camera Thread: `QThread` for cv2.VideoCapture()
- Processing Thread: `QThread` for detection algorithms
- Communication: Qt signals/slots (thread-safe)

**File Structure:**

```
chess_hybrid/
├── chess_mind_app.py              # Entry point
├── ui/
│   ├── main_window.py             # QMainWindow
│   ├── panels/*.py                # 5 panel implementations
│   ├── dialogs/*.py               # Modal dialogs
│   └── styles.py                  # Qt stylesheets
├── core/
│   ├── camera_thread.py
│   ├── processing_thread.py
│   ├── hybrid_manager.py          # Core logic
│   ├── color_detector.py          # HSV detection
│   └── state_manager.py           # Board state + desync
├── utils/
│   ├── config.py, logger.py, pgn_exporter.py
└── config.json                    # User settings
```

### 5.3 Hardware Requirements

**Minimum:**

- Webcam: 720p, 30fps with good color accuracy
- CPU: Dual-core
- RAM: 4GB
- Storage: 500MB

**Recommended:**

- Webcam: 1080p, 60fps, accurate color reproduction
- CPU: M1/M2 Mac or Intel i5+
- RAM: 8GB
- LED ring light for consistent lighting

### 5.4 Camera Setup Guidelines

**Positioning:**

- Mount directly above board (0-30° angle)
- Height: 60-80cm
- All 64 squares visible

**Lighting (CRITICAL):**

- Diffuse lighting (LED ring recommended)
- Avoid shadows and glare
- Consistent color temperature (5000-6500K)
- Test color detection before starting

---

## 6. System Limitations

### 6.1 Fundamental Constraints (Phase 1)

**L-1: No Visual Piece Classification**

- Standard YOLO NOT trained on chess pieces
- Can only detect: occupancy + color
- Piece identity inferred through move logic
- Requires Phase 2 custom training

**L-2: Logic-Over-Vision Brittleness**

- System trusts internal logic over camera
- One mis-inference corrupts all subsequent moves
- Requires desync detection and manual correction

**L-3: Color Detection Unreliability**

- Lighting changes affect accuracy
- Shadows confuse white/black detection
- Glossy pieces create highlights

**L-4: Cannot Handle Simultaneous Moves**

- Expects one move at a time
- Cannot handle touch-move corrections or rapid exchanges

**L-5: Ambiguous Move Resolution**

- Two pieces of same type to same square: unsolvable without user input
- Example: Two knights can both reach D4

### 6.2 Environmental Constraints

**L-6: Lighting Sensitivity**

- Requires consistent, diffuse lighting
- Direct sunlight causes false detections

**L-7: Board/Piece Requirements**

- High contrast boards preferred (white/black)
- Matte finish over glossy
- Standard Staunton-style pieces recommended

---

## 7. Development Phases

### Phase 1: MVP with Complete UI (4-5 weeks)

**Week 1-2: Core Detection + UI Framework**

- Qt5 application skeleton
- 5-panel layout implementation
- Camera capture thread
- Basic edge detection

**Week 3: Logic + UI Integration**

- HSV color detection
- Move inference
- Board view with chess symbols
- Event logging

**Week 4-5: Polish + Testing**

- Interactive calibration
- Parameter sliders
- Desync detection
- Manual correction UI
- User testing

**Success Criteria:**

- All panels functional
- 80%+ accuracy on simple games
- Desync detection within 3 moves
- 15+ FPS with all panels active

### Phase 2: Enhanced Detection (4-6 weeks)

- Custom YOLOv8 training (12 classes)
- Visual piece classification (>90% accuracy)
- Debouncing system
- Special move handling
- 3D board rendering

### Phase 3: User Experience (2-3 weeks)

- Dark/light themes
- Customizable layouts
- Keyboard shortcuts
- Tutorial overlay
- Improved error messages

### Phase 4: Polish & Optimization (1-2 weeks)

- Performance optimization (30 FPS target)
- Testing suite
- Documentation with video tutorials

---

## 8. Testing Strategy

### 8.1 Unit Testing

- Calibration: Homography accuracy
- Occupancy: Edge detection across lighting
- Color: HSV masking validation
- Move inference: Known board states
- Desync: Intentional corruption tests

### 8.2 UI/UX Testing

- First-time setup (<20 minutes)
- Calibration ease (<3 failed attempts)
- Manual correction (<60 seconds)
- Parameter adjustment (no docs needed)

### 8.3 Failure Mode Testing

- Illegal move test
- Lighting change test
- Rapid move test
- Piece knocked over test
- Acceptance: No crashes, desync detected in 90%+ cases

### 8.4 User Acceptance

- Beginner game (20 moves): 95%+ accuracy
- Intermediate game (40 moves): 80%+ accuracy, 1-2 corrections
- Complex game (50+ moves): 70%+ accuracy, 3-5 corrections

---

## 9. Risk Management

### 9.1 Technical Risks

| Risk                                          | Impact   | Probability | Mitigation                               | Phase |
| --------------------------------------------- | -------- | ----------- | ---------------------------------------- | ----- |
| Color detection fails in varied lighting      | CRITICAL | HIGH        | Require LED light; display warnings      | 1     |
| Logic-based inference causes frequent desyncs | HIGH     | HIGH        | Robust desync detection; easy correction | 1     |
| Users make illegal moves                      | HIGH     | MEDIUM      | Clear warnings; undo feature             | 1     |
| Custom YOLO training fails                    | HIGH     | MEDIUM      | Large dataset; extra time budget         | 2     |

### 9.2 Communication Risks

| Risk                             | Impact   | Mitigation                                  |
| -------------------------------- | -------- | ------------------------------------------- |
| Unrealistic user expectations    | CRITICAL | Transparent documentation; demo limitations |
| Marketing oversells capabilities | CRITICAL | Technical review of all materials           |

---

## 10. Success Metrics

### 10.1 Phase 1 (MVP)

- Occupancy detection: >90%
- Color detection: >85%
- Move inference (unambiguous): >80%
- Desync detection: >90%
- Frame rate: >15 FPS
- Setup time: <20 minutes
- Manual corrections per game: <3

### 10.2 Phase 2 (With YOLO)

- Piece classification: >90%
- Move inference: >95%
- Desync frequency: <0.2 per game
- Frame rate: >25 FPS
- Manual corrections per game: <1

---

## 11. Deployment Instructions

### 11.1 Environment Setup

```bash
# Create virtual environment
python3 -m venv chess_hybrid
source chess_hybrid/bin/activate  # Mac/Linux

# Install dependencies
pip install PyQt5 opencv-python python-chess numpy scikit-image

# Optional
pip install ultralytics PyOpenGL pyttsx3 pyperclip

# Verify
python -c "from PyQt5.QtWidgets import QApplication; print('Qt5 OK')"
```

### 11.2 First Run

1. Run: `python chess_mind_app.py`
2. UI loads with all 5 panels
3. Select camera from dropdown
4. Check lighting quality in status bar
5. Click "CALIBRATE CROPPED VIEW" → click 4 corners
6. Verify warped board appears correctly
7. Click "START GAME"
8. Make moves one at a time

### 11.3 Troubleshooting

| Problem                  | Solution                                |
| ------------------------ | --------------------------------------- |
| "Poor lighting detected" | Add LED ring light; adjust camera angle |
| "No legal move found"    | Press 'R' for manual correction         |
| Frequent desyncs         | Make clearer moves; use undo button     |
| System slow              | Disable YOLO if running without GPU     |

---

## 12. Future Enhancements

### 12.1 Phase 2 Essential

- Custom YOLO training (12-class classification)
- Automatic ambiguous move resolution
- Reliable special move handling

### 12.2 Phase 3+ Quality of Life

- Automatic board corner detection (ArUco markers)
- Mobile app with cloud sync
- Chess engine analysis integration
- Support for chess variants (960, blitz timers)

---

## 13. Conclusion

This specification provides a **realistic, achievable** roadmap for building a chess tracking system. Key success factors:

1. **Honest Limitations:** MVP tracks occupancy + color, NOT piece types
2. **Recovery Mechanisms:** Desync detection and manual correction are essential
3. **Professional UI:** Qt5 provides robust, performant desktop interface
4. **Phased Approach:** MVP proves concept; Phase 2 enables production-ready system

### Next Steps

1. ✅ Stakeholder approval of realistic expectations
2. ✅ Acquire recommended hardware (webcam, LED light)
3. Build Qt5 UI skeleton (Week 1)
4. Prototype color detection (Week 2)
5. Integrate logic layer (Week 3-4)
6. Beta test with real users (Week 5+)

---

## Document Control

**Version:** 2.1 - MERGED SPECIFICATION  
**Status:** Ready for Implementation  
**Author:** Project Manager  
**Date:** November 27, 2025

**Change Log:**

- v1.0: Initial specification (FLAWED)
- v2.0: Critical technical corrections
- v2.1: Added comprehensive Qt5 UI/UX specification (THIS VERSION)

**Merged From:**

- `functional_specification.md` (Technical corrections, limitations, realistic metrics)
- `functional_specification2.md` (Qt5 UI/UX design, implementation patterns)

---

**CRITICAL NOTE:** This system has fundamental limitations in Phase 1. Success requires honest stakeholder communication, good lighting conditions, and user discipline in making clear legal moves.
