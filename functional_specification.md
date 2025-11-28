# REVISED Project Management Document: ChessMind Hybrid Vision System

## Critical Updates Based on Technical Review

---

## ⚠️ CRITICAL CORRECTIONS TO ORIGINAL SPECIFICATION

This revised document addresses **five major technical contradictions** identified in the initial specification. These corrections are essential for project feasibility and honest stakeholder communication.

---

## Executive Summary

This document outlines the complete project specification for building a chess board tracking system that combines computer vision with chess logic. **IMPORTANT:** This system has fundamental limitations in Phase 1 that must be understood before development begins. The MVP will track board occupancy and infer moves through logic, but **cannot visually identify specific pieces without custom AI training.**

---

## 1. Project Overview

### 1.1 Project Name

**ChessMind Hybrid: Logic-First Chess Tracking System**

### 1.2 Revised Project Objectives

- Build a real-time chess board monitoring system that tracks **occupancy** and infers piece identity through **move logic**
- Combine basic object detection with classical computer vision (edge detection) for occupancy tracking
- Maintain legal game state through symbolic reasoning (python-chess engine)
- **Accept that visual piece classification requires Phase 2 custom training**
- Provide visual debugging dashboard for developers and users

### 1.3 Critical Understanding for Stakeholders

**This system does NOT "see" chess pieces like a human does.** Instead:

- It detects "something is here" vs. "nothing is here" (occupancy)
- It uses chess rules to deduce "if a piece left E2 and something appeared at E4, and E2→E4 is legal for a pawn, then it must be the pawn"
- **It will fail if:**
  - Players make illegal moves
  - Pieces are accidentally knocked over
  - Multiple pieces move simultaneously
  - The game state becomes desynchronized

---

## 2. System Architecture (CORRECTED)

### 2.1 Three-Layer Architecture

#### Layer 1: Perception Layer ("The Eye") - CORRECTED

**Responsibility:** Detect physical occupancy changes on the chess board

**Components:**

- Primary detector: Canny edge detection for occupancy verification
- Secondary detector: Generic object detection (YOLO trained on COCO dataset - detects "objects" not "chess pieces")
- Basic color detection: HSV color masking to distinguish white pieces from black pieces
- Camera calibration system for perspective correction

**CRITICAL LIMITATION:** This layer cannot identify "White Queen" vs "White Bishop." It can only report:

- "Square A1: Occupied by dark object"
- "Square E4: Occupied by light object"
- "Square H8: Empty"

**Input:** Raw camera feed  
**Output:**

- 8x8 occupancy grid (boolean: occupied/empty)
- 8x8 color grid (enum: white_piece/black_piece/empty)

#### Layer 2: Logic Layer ("The Brain") - ENHANCED

**Responsibility:** Maintain truth, validate changes, AND recover from errors

**Components:**

- State manager using python-chess library
- Move inference engine (deduces piece identity from legal moves)
- Legal move validator
- Debouncing system to filter noise
- **NEW: State desynchronization detector**
- **NEW: Manual correction interface**

**Input:** Occupancy grid changes + color information  
**Output:**

- Validated chess moves and updated board state
- Confidence score for current state
- Desynchronization alerts

#### Layer 3: Interface Layer ("The Face")

**Responsibility:** Display information and provide feedback

**Components:**

- Multi-window visualization system
- Real-time debugging overlays
- Console logging system with confidence indicators
- **NEW: Manual board correction UI**
- Optional: Text-to-speech move announcements
- Optional: Export functionality to spreadsheets

---

## 3. Functional Requirements (CORRECTED)

### 3.1 Core Features - Phase 1 (MVP)

**FR-1: Occupancy Detection System (CORRECTED)**

- System MUST use Canny edge detection as primary occupancy detector
- System MAY use generic YOLO as secondary verification (detecting "object" presence)
- System MUST use HSV color masking to distinguish white vs black pieces
- **REMOVED:** Piece classification capability (not possible with standard models)
- Acceptance Criteria: >90% accuracy on occupied/empty detection, >85% accuracy on color detection

**FR-2: Color Detection (NEW - CRITICAL FOR MVP)**

- System MUST implement HSV color space analysis for each occupied square
- Detect color ranges: White pieces (high value, low saturation), Black pieces (low value)
- Handle edge cases: Mixed colors, shadows, reflections
- Visual feedback: Color-coded rectangles (green=white piece, red=black piece, blue=unknown)
- Acceptance Criteria: >85% accuracy distinguishing white from black pieces

**FR-3: Perspective Calibration**

- System MUST support 4-point manual calibration
- User clicks board corners in sequence: TL → TR → BR → BL
- System calculates homography matrix for perspective warping
- Warped output must be 800x800 pixels
- Acceptance Criteria: Successful calibration in under 30 seconds

**FR-4: Enhanced Occupancy Grid**

- System divides warped board into 8x8 grid (64 squares)
- Each square analyzed for:
  - Edge density (occupied vs empty)
  - Color information (white vs black)
- Threshold-based decisions with adjustable sensitivity
- Visual feedback: Color-coded rectangles on dashboard
- Acceptance Criteria: >90% accuracy on occupancy + color

**FR-5: Logic-Based Move Inference (CORRECTED)**

- Compare current occupancy+color vs. previous board state
- Detect changes: from-square (became empty) → to-square (became occupied)
- Use color information to narrow legal moves:
  - If white piece moved, only check white's legal moves
  - If black piece moved, only check black's legal moves
- **Handle ambiguity:** If multiple pieces could make the same move, request user clarification
- Acceptance Criteria: Correctly identify 80%+ of unambiguous standard moves

**FR-6: Move Validation (UNCHANGED)**

- All inferred moves MUST be checked against python-chess legal moves
- Illegal moves (noise, hand occlusion) MUST be discarded
- Only validated moves update the internal board state
- Acceptance Criteria: 100% legal game state maintained (until desync occurs)

**FR-7: State Persistence Through Logic (CORRECTED)**

- System maintains "last valid FEN" (Forsyth–Edwards Notation)
- Identity of pieces determined by **move inference**, not camera
- Example: If white piece moves E2→E4 and this is legal, system deduces it's a pawn
- **LIMITATION:** If the wrong piece is assumed, all subsequent logic corrupts
- Acceptance Criteria: Correct piece identity for straightforward move sequences

**FR-8: State Desynchronization Detection (NEW - CRITICAL)**

- System MUST track confidence in its internal board state
- Triggers for desynchronization:
  - Multiple consecutive "no legal move found" despite visible changes
  - Occupancy+color mismatch lasting >5 seconds
  - User manually flags incorrect state
- When desync detected, system MUST:
  - Alert user with visual/audio warning
  - Freeze board state updates
  - Offer manual correction interface
- Acceptance Criteria: Detect desync within 3 moves of occurrence

**FR-9: Manual State Correction (NEW - CRITICAL)**

- System MUST provide UI for manual board correction
- User can click squares to:
  - Set piece type (Pawn, Knight, Bishop, Rook, Queen, King)
  - Set piece color (White, Black)
  - Mark square as empty
- System re-synchronizes internal state with manual input
- Acceptance Criteria: Recovery from desync in <60 seconds

**FR-10: Visual Dashboard**

- Display raw camera feed in "Project Manager View" window
- Display warped board with detection overlays in "Dashboard" window
- Show occupancy detection as color-coded rectangles:
  - Green rectangle = White piece detected
  - Red rectangle = Black piece detected
  - Blue rectangle = Occupied but color unknown
  - No rectangle = Empty
- Print ASCII board state to console with confidence score
- **NEW:** Display desynchronization warnings prominently
- Acceptance Criteria: <200ms latency between detection and display

### 3.2 Advanced Features - Phase 2

**FR-11: Custom YOLO Training (ESSENTIAL FOR TRUE CLASSIFICATION)**

- Train YOLOv8 on chess-specific dataset (Roboflow or custom)
- Classes: 12 total (White: P,N,B,R,Q,K + Black: p,n,b,r,q,k)
- Dataset requirements: 2000+ labeled images, varied angles/lighting
- Replace logic-based inference with direct visual classification
- Acceptance Criteria: >90% accuracy on piece type identification

**FR-12: Debouncing System**

- Maintain occupancy+color history buffer (last 5 frames)
- Only register changes if consistent across 3+ frames
- Prevents flickering from temporary occlusions
- Acceptance Criteria: <1% false move registrations

**FR-13: Capture Detection (ENHANCED)**

- Use color change to detect captures: "white occupied → black occupied"
- Validate against legal capture moves
- Handle edge case: piece color mis-detected
- Acceptance Criteria: 85%+ capture detection accuracy

**FR-14: Special Move Handling**

- Castling: Detect 4-square simultaneous change (King + Rook)
- En passant: Detect 3-square change (pawn move + capture + empty diagonal)
- Promotion: Detect piece replacement at back rank + prompt user for choice
- Acceptance Criteria: 80%+ accuracy on special moves

**FR-15: Automatic State Recovery**

- If desync detected, system attempts automatic recovery:
  - Compare visible board to all possible game states
  - Calculate most likely board configuration
  - Prompt user: "Did you move [piece] from [square] to [square]?"
- Acceptance Criteria: 60%+ successful auto-recovery

**FR-16: Export Functionality**

- Save game in PGN (Portable Game Notation) format
- Export move log to CSV or Google Sheets
- Include timestamps and confidence scores
- Acceptance Criteria: PGN importable into chess software

**FR-17: Audio Feedback**

- Text-to-speech announcement of moves (e.g., "Pawn to E4")
- Audio warnings for desynchronization
- Optional sound effects for captures, check, checkmate
- Acceptance Criteria: Clear announcements within 1 second of move

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

**NFR-1: Frame Rate**

- Minimum: 15 FPS on M1/M2 MacBook Air
- Target: 30 FPS on modern laptops
- **CORRECTED:** Edge detection + color masking is fast; generic YOLO adds overhead

**NFR-2: Latency**

- Detection-to-display latency: <200ms
- Move validation: <50ms
- Color detection: <30ms per frame
- Total system response time: <300ms

**NFR-3: Resource Usage**

- RAM: <2GB during operation (without YOLO), <3GB (with YOLO)
- CPU: <50% on single core (edge detection alone)
- GPU: Optional acceleration for YOLO; not required for MVP

### 4.2 Reliability Requirements

**NFR-4: Robustness (ADJUSTED EXPECTATIONS)**

- System MUST NOT crash on hand occlusion
- System MUST handle temporary camera disconnection
- System MUST recover from calibration errors
- **ADJUSTED:** System will desynchronize occasionally; must detect and allow recovery
- Uptime target: 95% during 2-hour chess session (allowing for manual corrections)

**NFR-5: Accuracy (REALISTIC TARGETS)**

- Occupancy detection: >90%
- Color detection: >85%
- Move inference (unambiguous): >80%
- Move inference (ambiguous): >50% (may require user input)
- Legal state maintenance: 100% (until desync occurs)
- Desync detection rate: >90%

**NFR-6: Lighting Tolerance**

- System should function in indoor lighting (300-800 lux)
- Color detection requires consistent lighting (no harsh shadows)
- Calibration should handle varied lighting conditions
- **NEW:** System should prompt user if lighting inadequate for color detection

### 4.3 Usability Requirements

**NFR-7: Setup Time**

- Complete installation: <10 minutes
- Environment setup: <5 minutes
- Board calibration: <30 seconds
- Color calibration (if needed): <2 minutes
- User should be able to start tracking within 20 minutes total

**NFR-8: Error Messages (ENHANCED)**

- Clear feedback when calibration fails
- Visual indication when model download is in progress
- Console warnings for suspicious detection patterns
- **NEW:** Prominent desynchronization alerts with recovery instructions
- **NEW:** Lighting quality feedback ("Too dark", "Too much glare")

**NFR-9: Honest User Expectations (NEW)**

- System MUST display disclaimer on startup:
  - "This system tracks occupancy and infers piece identity through chess rules"
  - "For best results, make one clear move at a time"
  - "If the system gets confused, use manual correction"
- User documentation must clearly explain limitations

---

## 5. Technical Specifications

### 5.1 Technology Stack (CORRECTED)

**Programming Language:** Python 3.8+

**Core Libraries:**

- `opencv-python` (Computer vision operations - PRIMARY TOOL)
- `python-chess` (Chess logic and validation - THE BRAIN)
- `numpy` (Numerical operations)
- `ultralytics` (OPTIONAL: Generic YOLO for object detection verification)

**NEW - Essential for MVP:**

- `scikit-image` or native OpenCV for color space conversions
- `tkinter` or `pygame` (Manual correction UI)

**Optional Libraries:**

- `pyttsx3` (Text-to-speech)
- `gspread` (Google Sheets export)
- `pandas` (Data processing)

### 5.2 Hardware Requirements

**Minimum:**

- Webcam: 720p, 30fps with **good color accuracy**
- Processor: Dual-core CPU
- RAM: 4GB
- Storage: 200MB (MVP without YOLO), 500MB (with YOLO)

**Recommended:**

- Webcam: 1080p, 60fps, auto-focus, **accurate color reproduction**
- Processor: M1/M2 Mac or equivalent Intel i5+
- RAM: 8GB
- **LED ring light** for consistent lighting (critical for color detection)

### 5.3 Camera Setup Guidelines (ENHANCED)

**Positioning:**

- Mount camera directly above board (0-30° angle, closer to 0° is better)
- Height: 60-80cm from board surface
- Ensure all 64 squares visible with minimal distortion

**Lighting (CRITICAL FOR COLOR DETECTION):**

- Use diffuse lighting (LED ring light recommended)
- Avoid direct overhead shadows from pieces
- Minimize glare on glossy pieces
- Consistent color temperature (daylight 5000-6500K preferred)
- **Test color detection before starting game**

**Board Requirements:**

- High contrast between light and dark squares (recommended: white/black or cream/brown)
- Matte finish preferred over glossy
- Clear piece silhouettes (avoid elaborate piece designs)
- Recommended: Staunton-style pieces with distinct shapes

---

## 6. System Limitations (COMPREHENSIVE)

### 6.1 Fundamental Constraints (PHASE 1 MVP)

**L-1: NO Visual Piece Classification (CRITICAL)**

- Standard YOLO model is NOT trained on chess pieces
- System CANNOT distinguish "White Queen" vs "White Bishop" by vision alone
- System CAN ONLY detect:
  - Occupancy (something vs nothing)
  - Color (white piece vs black piece)
- Piece identity is INFERRED through move logic
- **Impact:** System assumes players make legal moves; illegal moves break the system
- **Mitigation:** Phase 2 requires custom YOLO training on chess dataset

**L-2: Logic-Over-Vision Creates Brittleness**

- System trusts its internal logic more than camera
- **Failure scenario:** If one move is mis-inferred, all subsequent moves may be rejected as "illegal"
- **Example:** System thinks White Bishop is at C1. User moves it to F4. Camera sees "white piece moved." System checks: "Is C1→F4 legal? No." System rejects move. Now system thinks Bishop is still at C1 (wrong). Game state is desynchronized.
- **Mitigation:** Desynchronization detection + manual correction interface

**L-3: Color Detection Unreliability**

- Lighting changes affect color detection accuracy
- Shadows can make white pieces appear black
- Glossy pieces create highlights that confuse color detection
- **Impact:** Wrong color → wrong legal move set → mis-inference → desynchronization
- **Mitigation:** Require good lighting; provide real-time color detection confidence display

**L-4: Cannot Handle Simultaneous Moves**

- System expects one move at a time with clear from→to transition
- Cannot handle:
  - Touch-move corrections (player moves piece back immediately)
  - Rapid exchanges (both players moving quickly)
  - Castling (requires special 4-square detection logic)
- **Impact:** System may register only part of the move or miss it entirely
- **Mitigation:** User discipline; debouncing system in Phase 2

**L-5: Ambiguous Move Resolution**

- If two pieces of same type can reach same square, system cannot determine which moved
- **Example:** Knights at B1 and F3 can both go to D4. Camera sees "white piece on D4." Which knight moved?
- Without piece classification, this is unsolvable
- **Mitigation:** Prompt user for clarification; use move history heuristics

### 6.2 Environmental Constraints

**L-6: Lighting Sensitivity**

- Requires consistent, diffuse lighting for color detection
- Direct sunlight or changing shadows cause false detections
- Very dark pieces on dark squares hard to detect
- **Mitigation:** Recommend LED ring light; display lighting quality warnings

**L-7: Board and Piece Requirements**

- Low-contrast boards (light wood on light squares) reduce detection accuracy
- Very small pieces or very large boards affect calibration
- Non-standard piece shapes (decorative sets) may confuse edge detection
- **Mitigation:** Provide board/piece recommendations in user guide

**L-8: Camera Quality Dependency**

- Cheap webcams with poor color reproduction reduce accuracy
- Auto-focus hunting causes frame drops
- Low resolution makes edge detection less precise
- **Mitigation:** Specify recommended camera models; allow manual focus lock

### 6.3 Capture and Special Move Constraints

**L-9: Capture Detection Limitations**

- Basic system sees: "white piece occupied → black piece occupied"
- But cannot always confirm capture occurred vs piece mis-detected
- En passant captures are particularly challenging (captured piece on different square)
- **Mitigation:** Require captured pieces removed from board; special handling in Phase 2

**L-10: Special Moves Require Enhanced Logic**

- Castling: 4-square change (King + Rook) difficult to track atomically
- Promotion: System cannot visually detect piece type change
- **Mitigation:** Prompt user when special move suspected; manual confirmation

### 6.4 Out of Scope (Phase 1 MVP)

- Automatic board corner detection
- Visual piece classification (requires Phase 2 training)
- Reliable capture detection
- Castling and en passant automatic handling
- Multiple board tracking
- Mobile app version
- Cloud synchronization
- Chess engine analysis integration
- Automatic state recovery without user input

---

## 7. Development Phases (REVISED)

### Phase 1: Basic Occupancy + Color Tracking (MVP)

**Duration:** 3-4 weeks

**Deliverables:**

- Manual calibration system
- Edge-based occupancy detection
- **HSV color detection** (white vs black pieces)
- Move inference with color information
- Basic validation via python-chess
- **Desynchronization detection**
- **Manual correction interface**
- Two-window visualization with color-coded overlays

**Success Criteria:**

- Can track a complete game of **simple, unambiguous moves**
- Maintains legal board state for **80%+ of typical game**
- Detects desynchronization within 3 moves
- User can manually correct state in <60 seconds
- Runs at 15+ FPS

**Known Limitations Accepted:**

- Cannot handle ambiguous moves (two knights to same square)
- Capture detection unreliable
- No special move handling
- Requires user intervention when confused

### Phase 2: Enhanced Detection + YOLO Training

**Duration:** 4-6 weeks

**Deliverables:**

- Custom YOLOv8 training on chess piece dataset
- Visual piece classification (12 classes)
- Debouncing system for stable detection
- Enhanced capture detection using piece type changes
- Special move detection (castling, en passant)
- Automatic state recovery attempts

**Success Criteria:**

- > 90% piece classification accuracy
- Can handle 95%+ of tournament game scenarios
- Ambiguous moves resolved visually
- Captures detected reliably
- Reduced user intervention to <5% of games

### Phase 3: User Experience + Export

**Duration:** 2-3 weeks

**Deliverables:**

- PGN export with confidence scores
- TTS announcements
- Configuration file for settings (thresholds, colors)
- Comprehensive error recovery
- Improved lighting quality feedback
- User documentation and video tutorials

**Success Criteria:**

- Non-technical users can set up system
- Games importable into chess analysis software
- Clear documentation of all limitations
- <10 support requests per 100 users on common issues

### Phase 4: Polish & Optimization

**Duration:** 1-2 weeks

**Deliverables:**

- Performance optimization (target 30 FPS)
- Comprehensive testing suite
- Edge case handling improvements
- Troubleshooting guide with photos
- Beta user feedback integration

**Success Criteria:**

- 30 FPS on target hardware
- Complete documentation with video walkthroughs
- <5 critical bugs
- > 4/5 user satisfaction rating

---

## 8. Testing Strategy (ENHANCED)

### 8.1 Unit Testing

**Component Tests:**

- Calibration: Verify homography matrix calculation
- Occupancy: Test edge detection threshold accuracy across lighting conditions
- **Color Detection: Test HSV masking on sample images (various lighting)**
- Move inference: Validate logic with known board states
- Desync detection: Trigger with intentionally corrupted states

### 8.2 Integration Testing

**System Tests:**

- End-to-end game tracking (simple opening, no captures)
- **Desynchronization recovery test** (introduce illegal move, verify detection + recovery)
- Color detection under varying light (morning, afternoon, artificial)
- Performance under load (60-minute game with thinking time)

### 8.3 Failure Mode Testing (NEW - CRITICAL)

**Deliberate Failure Scenarios:**

- **Illegal move test:** Make an illegal move, verify system rejects it
- **Ambiguous move test:** Create scenario where two pieces can reach same square
- **Lighting change test:** Turn lights on/off mid-game, measure impact
- **Rapid move test:** Make moves quickly, verify system can keep up or pauses
- **Piece knocked over:** Accidentally displace piece, verify desync detection

**Acceptance Criteria:**

- System never crashes, even under failure conditions
- Desync detected within 3 moves in 90%+ of failure scenarios
- User can always recover via manual correction

### 8.4 User Acceptance Testing

**Scenarios:**

- **Beginner game (20 moves, no captures):** Target 95%+ accuracy
- **Intermediate game (40 moves, 3-5 captures):** Target 80%+ accuracy, 1-2 manual corrections
- **Complex game (50+ moves, special moves):** Target 70%+ accuracy, 3-5 manual corrections
- **Stress test:** Multiple games back-to-back, different lighting conditions

**Metrics:**

- Setup time (target: <20 minutes)
- Move detection accuracy (target: 80%+ Phase 1, 95%+ Phase 2)
- Desync frequency (target: <1 per game Phase 1, <0.2 per game Phase 2)
- Recovery time from desync (target: <60 seconds)
- User satisfaction (target: 3.5/5 Phase 1, 4.5/5 Phase 2)

---

## 9. Risk Management (COMPREHENSIVE)

### 9.1 Technical Risks (UPDATED)

| Risk                                                 | Impact       | Probability | Mitigation                                                                    | Phase |
| ---------------------------------------------------- | ------------ | ----------- | ----------------------------------------------------------------------------- | ----- |
| Color detection fails in varied lighting             | **CRITICAL** | **HIGH**    | Require LED ring light; display lighting warnings; extensive testing          | 1     |
| Logic-based inference creates frequent desyncs       | **HIGH**     | **HIGH**    | Implement robust desync detection; make manual correction easy                | 1     |
| Users make illegal moves, breaking system            | **HIGH**     | **MEDIUM**  | Clear UI warnings; "undo last move" feature; state snapshots                  | 1     |
| Ambiguous moves unsolvable without classification    | **MEDIUM**   | **HIGH**    | Accept limitation; prompt user; document clearly                              | 1-2   |
| Custom YOLO training fails to achieve >90% accuracy  | **HIGH**     | **MEDIUM**  | Acquire large, diverse dataset; consider transfer learning; budget extra time | 2     |
| Capture detection remains unreliable even in Phase 2 | **MEDIUM**   | **MEDIUM**  | Require captured pieces removed from board; document workaround               | 2     |
| YOLO model download slow/unavailable                 | **LOW**      | **LOW**     | Make YOLO optional in MVP; cache model locally; provide manual download       | 1     |

### 9.2 Project Risks (UPDATED)

| Risk                                                    | Impact       | Probability | Mitigation                                                                |
| ------------------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------------------- |
| Stakeholders expect piece classification in MVP         | **CRITICAL** | **HIGH**    | **This document explicitly sets realistic expectations**                  |
| Scope creep ("let's add Stockfish analysis!")           | **HIGH**     | **HIGH**    | Strict phase separation; MVP-first; feature freeze after Phase 1 approval |
| Insufficient testing with real users                    | **HIGH**     | **MEDIUM**  | Recruit 10+ beta testers; budget time for iteration                       |
| User hardware incompatibility (camera quality)          | **MEDIUM**   | **HIGH**    | Publish compatible camera list; provide diagnostic tool                   |
| Poor user experience due to frequent manual corrections | **MEDIUM**   | **MEDIUM**  | Make correction UI intuitive; add "undo" button; provide clear feedback   |

### 9.3 Communication Risks (NEW)

| Risk                                        | Impact       | Probability | Mitigation                                                                                  |
| ------------------------------------------- | ------------ | ----------- | ------------------------------------------------------------------------------------------- |
| Users blame system for their illegal moves  | **MEDIUM**   | **HIGH**    | Prominent disclaimer; log all moves with confidence; "replay mode" to show what system saw  |
| Marketing oversells capabilities            | **CRITICAL** | **MEDIUM**  | Review all marketing materials; require technical review approval; demo realistic scenarios |
| Bad reviews due to unrealistic expectations | **HIGH**     | **MEDIUM**  | Transparent documentation; tutorial video showing limitations; beta test with harsh critics |

---

## 10. Success Metrics (REALISTIC)

### 10.1 Technical KPIs - Phase 1 (MVP)

- **Occupancy detection accuracy:** >90% (not 95%)
- **Color detection accuracy:** >85% (under good lighting)
- **Move inference accuracy (unambiguous):** >80% (not 95%)
- **Desynchronization detection rate:** >90%
- **System crash rate:** <0.1% (1 crash per 1000 moves)
- **Frame rate:** >15 FPS (minimum)
- **Legal state maintenance:** 100% (until desync, which is expected occasionally)

### 10.2 Technical KPIs - Phase 2 (With YOLO)

- **Piece classification accuracy:** >90%
- **Move inference accuracy:** >95%
- **Capture detection accuracy:** >85%
- **Desynchronization frequency:** <0.2 per game
- **Frame rate:** >25 FPS (with YOLO running)

### 10.3 User Experience KPIs

**Phase 1:**

- Setup time: <20 minutes (adjusted from 15)
- Manual corrections per game: <3 (for 40-move game)
- Recovery time from desync: <60 seconds
- User satisfaction: >3/5 stars (realistic for MVP)
- Error rate: <1 missed move per 10 moves

**Phase 2:**

- Manual corrections per game: <1
- User satisfaction: >4/5 stars
- Error rate: <1 missed move per 50 moves

### 10.4 Project KPIs

- Phase 1 completion: On schedule (3-4 weeks)
- Phase 2 completion: On schedule (4-6 weeks after Phase 1)
- Bug count: <15 known issues at Phase 1 release (adjusted)
- Documentation completeness: 100% of features documented with limitations clearly stated
- Code coverage: >60% (realistic for vision projects)
- Beta tester satisfaction: >3.5/5 Phase 1, >4.5/5 Phase 2

---

## 11. Deployment Instructions (ENHANCED)

### 11.1 Environment Setup

```bash
# Create virtual environment
python3 -m venv chess_hybrid
source chess_hybrid/bin/activate  # Mac/Linux
# chess_hybrid\Scripts\activate  # Windows

# Install core dependencies (MVP)
pip install opencv-python python-chess numpy scikit-image

# Optional: Install YOLO (adds overhead)
pip install ultralytics

# Optional: Install UI/export tools
pip install pygame pyttsx3
```

### 11.2 Pre-Flight Checklist

- [ ] Webcam connected and functioning
- [ ] Chess board with high contrast (white/black preferred)
- [ ] LED ring light or consistent overhead lighting
- [ ] Camera positioned 60-80cm above board
- [ ] All 64 squares visible in camera view
- [ ] No harsh shadows or glare on board

### 11.3 First Run

1. Run: `python hybrid_manager.py`
2. **Lighting check:** System displays color detection confidence
   - Green: Good lighting
   - Yellow: Marginal, adjust lighting
   - Red: Insufficient, add light source
3. **Calibration:** Click 4 board corners (TL→TR→BR→BL)
4. **Color calibration:** System analyzes starting position
   - Confirms white pieces in rows 1-2
   - Confirms black pieces in rows 7-8
5. **Start playing:** Make one clear move at a time
6. **If system gets confused:** Press 'R' for manual correction UI

### 11.4 Troubleshooting (COMPREHENSIVE)

| Problem                      | Likely Cause                                   | Solution                                                                |
| ---------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------- |
| "Poor lighting detected"     | Insufficient/uneven lighting                   | Add LED ring light; close curtains; test with desk lamp                 |
| "Color detection unreliable" | Shadows, glare, or camera quality              | Adjust camera angle; use matte pieces; test color masking thresholds    |
| "No legal move found"        | Desynchronization occurred                     | Press 'R' for manual correction; review last 3 moves                    |
| Frequent desyncs             | Player making illegal moves or ambiguous moves | Review move carefully; use "undo" if available; make clearer moves      |
| Pieces not detected          | Low contrast between pieces and squares        | Use darker pieces on light squares; increase edge detection sensitivity |
| System very slow             | Running YOLO without GPU                       | Disable YOLO in settings (config.json); rely on edge detection          |
| Board warped incorrectly     | Calibration points inaccurate                  | Recalibrate; ensure camera is steadily mounted                          |

---

## 12. Future Enhancements

### 12.1 Essential (Phase 2)

- Custom YOLO training on chess dataset (12-class classification)
- Automatic ambiguous move resolution
- Reliable capture and special move handling
- Smart state recovery suggestions

### 12.2 Quality of Life (Phase 3+)

- Automatic board corner detection (ArUco markers or computer vision)
- Mobile app with cloud sync
- PGN export with timestamps
- Integration with chess engines for analysis
- Support for chess variants (960, blitz timers)

### 12.3 Research Opportunities (Future)

- Temporal models (LSTM) for predictive move detection
- 3D board reconstruction from single camera
- Gesture recognition for move confirmation
- Federated learning for model improvement without privacy concerns
- Multi-board tournament management system

---

## 13. Conclusion (REVISED)

This project represents a **pragmatic** fusion of computer vision with symbolic reasoning. Unlike the original specification, this revised document acknowledges the fundamental limitations of Phase 1 and provides realistic success criteria.

### Key Success Factors (CORRECTED):

1. **The system "trusts logic over pixels" - WITH CAVEATS:**

   - This works for straightforward games where players make legal moves
   - This breaks when moves are ambiguous, illegal, or mis-detected
   - Recovery mechanisms are essential, not optional

2. **Honest Communication:**

   - Stakeholders must understand: MVP tracks occupancy + color, not piece identity
   - Users must be warned: system requires disciplined play and occasional corrections
   - Marketing must avoid overselling: "AI-powered" ≠ "foolproof"
     powered" ≠ "foolproof"

3. **Phase 2 is Critical:**
   - Custom YOLO training is not a "nice-to-have" - it's required for robust operation
   - MVP is a proof-of-concept, not a production system
   - Budget and timeline must reflect this reality

### What Makes This Specification Better:

- ✅ **Eliminates the YOLO Paradox:** MVP uses edge detection + color, not piece classification
- ✅ **Adds Color Detection:** Essential HSV masking for distinguishing white/black pieces
- ✅ **Addresses State Recovery:** Desync detection + manual correction interface
- ✅ **Realistic Success Metrics:** 80% accuracy for MVP, not 95%
- ✅ **Honest About Limitations:** Multiple sections on failure modes and constraints
- ✅ **Failure Mode Testing:** Deliberately tests how system breaks, not just how it works

### Next Steps for Implementation:

1. **Stakeholder approval** of this REVISED specification with realistic expectations
2. **Acquire recommended hardware** (good webcam, LED ring light)
3. **Prototype color detection** first (1 week) to validate feasibility
4. **Build MVP** with desync detection as core feature
5. **Beta test with 10+ real users** who understand limitations
6. **Gather data for Phase 2** YOLO training during beta period

---

## 14. Appendix: Technical Deep Dives

### A. Color Detection Algorithm (HSV Masking)

**Why HSV instead of RGB:**

- HSV separates color (Hue) from brightness (Value)
- More robust to lighting variations
- Easier to define "white" and "black" ranges

**Implementation Sketch:**

```
For each occupied square:
  1. Convert ROI to HSV color space
  2. Calculate average V (Value/Brightness)
  3. Calculate average S (Saturation)
  4. Classify:
     - If V > 180 and S < 50: White piece
     - If V < 100: Black piece
     - Else: Unknown (flag for review)
```

**Challenges:**

- Shadows reduce Value, making white pieces appear black
- Glossy pieces create highlights (high V spots)
- Wooden pieces have mid-range values (neither white nor black)

**Mitigation:**

- Use median Value instead of average (reduces highlight impact)
- Analyze histogram, not just single value
- Allow user to manually set color thresholds during calibration

### B. Desynchronization Detection Logic

**Trigger Conditions:**

1. **No legal move found:** Camera sees change, but no legal move matches
2. **Persistent mismatch:** Occupancy+color disagrees with logic for >5 seconds
3. **Confidence decay:** Multiple low-confidence inferences in a row
4. **User flag:** Manual desync report

**Confidence Scoring:**

```
Confidence = 1.0 (start)
For each move:
  If move unambiguous: confidence += 0.1 (max 1.0)
  If move ambiguous: confidence -= 0.2
  If color detection uncertain: confidence -= 0.1
  If took >5 seconds to detect: confidence -= 0.1
If confidence < 0.5: Trigger desync warning
```

**Recovery Strategy:**

1. Freeze state updates
2. Show user: Current logical board vs Camera view
3. Highlight differences
4. Offer: "Undo last N moves" or "Manual correction"

### C. Custom YOLO Training Requirements (Phase 2)

**Dataset Specification:**

- Minimum: 2000 labeled images
- Recommended: 5000+ images
- Classes: 12 (wP, wN, wB, wR, wQ, wK, bP, bN, bB, bR, bQ, bK)
- Images must include:
  - Various angles (0-45°)
  - Different lighting conditions
  - Multiple chess sets (wooden, plastic, weighted)
  - Different board materials
  - Occlusions (hands partially visible)

**Data Sources:**

- Roboflow Chess Pieces Dataset (public)
- Chess.com/Lichess streamed games (with permission)
- Self-collected data from beta testers
- Synthetic data generation (render 3D chess models)

**Training Parameters:**

- Model: YOLOv8n or YOLOv8s (balance speed/accuracy)
- Epochs: 100-200
- Batch size: 16-32 (GPU dependent)
- Augmentation: Rotation, brightness, blur, zoom
- Expected training time: 4-8 hours on modern GPU

**Success Criteria:**

- mAP@0.5: >90%
- Inference time: <50ms per frame
- Real-world testing: >90% accuracy on unseen chess set

---

## Document Control

**Version:** 2.0 - MAJOR REVISION  
**Date:** November 27, 2025  
**Status:** Ready for Critical Review  
**Author:** Project Manager  
**Reviewed By:** Technical Lead (Self-Review)  
**Approved By:** [Pending Stakeholder Approval]

**Change Log:**

- v1.0: Initial specification (FLAWED - DO NOT USE)
- v2.0: **CRITICAL CORRECTIONS** addressing five major technical contradictions:
  1. Eliminated YOLO piece classification from Phase 1
  2. Added HSV color detection as essential MVP feature
  3. Added state desynchronization detection + recovery
  4. Corrected fallback logic (occupancy only, not classification)
  5. Adjusted success metrics to realistic levels (80% not 95%)
  6. Added comprehensive failure mode testing
  7. Expanded limitations section with honest assessment
  8. Enhanced risk management with communication risks

**CRITICAL NOTE FOR STAKEHOLDERS:**  
This document represents a complete revision of the original specification. The changes are not cosmetic - they address fundamental technical impossibilities in the original plan. Any decisions based on v1.0 should be reconsidered in light of this corrected specification.
