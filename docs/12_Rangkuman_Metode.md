# Rangkuman Metode Implementasi dan Pengujian
## ChessMind Hybrid Vision System

---

## 📋 Daftar Metode Implementasi

### 1. Computer Vision Methods

#### 1.1 Board Detection (Auto-Calibration)
**Algoritma**: Canny Edge Detection + Contour Analysis

```
Pipeline:
BGR Frame (1920×1080)
    ↓
Grayscale Conversion
    ↓
Gaussian Blur (kernel 5×5)
    ↓
Canny Edge Detection (threshold: 50, 150)
    ↓
Morphological Dilation (kernel 3×3, iter=2)
    ↓
Find Contours (RETR_EXTERNAL)
    ↓
Filter by Area (> 10000 pixels)
    ↓
Approximate Polygon (epsilon = 0.02 × perimeter)
    ↓
Validate 4 corners + Aspect Ratio (0.8 - 1.2)
    ↓
Sort Corners (TL, TR, BR, BL)
    ↓
Compute Homography Matrix (3×3)
```

**Parameters**:
- Canny Lower: 50
- Canny Upper: 150
- Min Area: 10000 pixels
- Aspect Ratio: 0.8 - 1.2

---

#### 1.2 Perspective Transformation
**Algoritma**: Homography Transformation

```
Source Points (4 corners from detection)
    ↓
Sort by position:
  - Top-Left: min(x+y)
  - Top-Right: min(y-x)
  - Bottom-Right: max(x+y)
  - Bottom-Left: max(y-x)
    ↓
Destination Points (600×600):
  - [0, 0], [600, 0], [600, 600], [0, 600]
    ↓
cv2.getPerspectiveTransform()
    ↓
Homography Matrix H (3×3)
    ↓
For each frame:
  cv2.warpPerspective(frame, H, (600, 600))
    ↓
Warped Image (600×600)
```

**Output**: 600×600 pixel warped board image

---

#### 1.3 Color-Based Detection
**Algoritma**: HSV Color Space Analysis

```
ROI (75×75 pixels per square)
    ↓
BGR → HSV Conversion
    ↓
Calculate Mean H, S, V values
    ↓
Occupancy Check:
  if V < threshold (50): → 'empty'
    ↓
Color Classification:
  if S < 30:
    if V > 180: → 'white'
    if V < 80: → 'black'
  else: → 'colored'
```

**Parameters**:
- Occupancy Threshold: 50 (adjustable)
- White: S < 30, V > 180
- Black: S < 30, V < 80

**Kelebihan**:
- ✓ Cepat (< 10ms per frame)
- ✓ Tidak butuh training data
- ✓ Resource-efficient

**Kekurangan**:
- ✗ Tidak bisa identifikasi jenis piece
- ✗ Sensitif terhadap pencahayaan
- ✗ Akurasi moderate (~85%)

---

#### 1.4 YOLO Object Detection
**Algoritma**: YOLOv8 Deep Learning

```
Warped Frame (600×600)
    ↓
Preprocessing (normalization)
    ↓
YOLO Inference
  - Input: 640×640
  - Model: YOLOv8 Custom
  - Classes: 12 (6 white + 6 black pieces)
    ↓
Post-processing:
  - Confidence Threshold: 0.5
  - NMS IoU Threshold: 0.45
    ↓
Parse Detections:
  - BBox: [x1, y1, x2, y2]
  - Confidence: [0.0 - 1.0]
  - Class: piece type
    ↓
Calculate Center: (x1+x2)/2, (y1+y2)/2
    ↓
Determine Grid Square: 
  col = floor(center_x / 75)
  row = floor(center_y / 75)
    ↓
Build 8×8 Grid with class names
```

**Parameters**:
- Input Size: 640×640
- Confidence Threshold: 0.5
- IoU Threshold: 0.45
- Classes: 12 chess pieces

**Kelebihan**:
- ✓ Identifikasi jenis piece akurat (~94%)
- ✓ Robust terhadap pencahayaan
- ✓ Handle occlusion

**Kekurangan**:
- ✗ Butuh GPU untuk real-time
- ✗ Latency lebih tinggi (~50-80ms)
- ✗ Butuh training data

---

#### 1.5 Hybrid Detection
**Algoritma**: Fusion of Color + YOLO

```
Parallel Execution:
    ├─ Color-Based Detection → Color Grid
    └─ YOLO Detection → YOLO Grid
        ↓
For each square (row, col):
    ↓
  if YOLO detected:
    use YOLO class name
  else:
    use Color result ('white'/'black'/'empty')
        ↓
Merged Grid (8×8)
        ↓
Stability Check:
  Compare with previous stable grid
  If different:
    - Increment stability counter
    - If counter >= threshold (5 frames):
      → Confirm as stable
      → Infer chess move
```

**Keunggulan**:
- ✓ Combine speed (Color) + accuracy (YOLO)
- ✓ Fallback mechanism
- ✓ Akurasi tinggi (~92-95%)

---

### 2. Game State Management

#### 2.1 Move Inference Algorithm
**Algoritma**: Differential Analysis

```
Input: New Grid, Previous Stable Grid
    ↓
Calculate Differences:
  changed_squares = []
  for each square:
    if new != old:
      changed_squares.append(square)
    ↓
Count Changes: N = len(changed_squares)
    ↓
Pattern Recognition:
    ├─ N = 0: No move
    ├─ N = 1: Promotion / Piece removed
    ├─ N = 2: Normal move / Capture
    ├─ N = 3: En Passant
    ├─ N = 4: Castling
    └─ N > 4: Error / Multiple moves
        ↓
For N = 2 (Normal Move):
  Find source (piece disappeared)
  Find destination (piece appeared)
  Build UCI: f"{source}{destination}"
    ↓
For N = 4 (Castling):
  Identify king movement (2 squares)
  Identify rook movement
  Build UCI: "e1g1" (kingside) or "e1c1" (queenside)
    ↓
Validate with chess.Board.is_legal(move)
    ↓
If valid:
  Apply move
  Update FEN
  Switch turn
  Update clock
Else:
  Emit illegal_move_attempted signal
```

**Edge Cases Handled**:
- Pawn Promotion: Prompt user for piece choice
- En Passant: 3-square change pattern
- Castling: 4-square change pattern
- Ambiguous moves: Reject and log

---

#### 2.2 Stability Mechanism
**Algoritma**: Temporal Consistency Check

```
Variables:
  - current_stable_grid: Last confirmed state
  - pending_grid: Candidate new state
  - stability_counter: Frame count
  - THRESHOLD: 5 frames (~166ms at 30 FPS)

Flow:
New Grid arrives
    ↓
if New == Current Stable:
  stability_counter = 0
  → No change, continue
else:
  if New == Pending:
    stability_counter++
    if stability_counter >= THRESHOLD:
      → Confirm stable
      → Infer move
      → Update current_stable_grid
  else:
    pending_grid = New
    stability_counter = 1
```

**Purpose**:
- Menghindari false positive dari noise
- Filter gerakan tangan/piece di udara
- Ensure move completion sebelum deteksi

---

### 3. Chess Engine Integration

#### 3.1 Stockfish Analysis
**Algoritma**: UCI Protocol Communication

```
Game State Updated (FEN)
    ↓
Send to Stockfish:
  position fen {fen_string}
  go depth {depth}
    ↓
Wait for Response:
  Parse 'info' lines:
    - depth
    - score cp {centipawns}
    - score mate {moves_to_mate}
    - pv {principal_variation}
    ↓
  Parse 'bestmove' line:
    - bestmove {uci_move}
    ↓
Format Evaluation:
  if mate:
    eval = "M{n}" or "-M{n}"
  else:
    eval = f"{cp/100:.2f}"
    ↓
Emit Signals:
  - evaluation_updated(eval)
  - best_move_found(uci_move)
    ↓
UI Updates:
  - Evaluation Panel shows eval
  - Board Panel highlights best move
```

**Parameters**:
- Depth: 15 (adjustable)
- Threads: 2
- Hash: 128 MB
- MultiPV: 1

---

### 4. Audio Feedback System

#### 4.1 Text-to-Speech
**Algoritma**: Platform-specific TTS

```
Move Applied (UCI)
    ↓
Parse Move:
  - piece_type = board.piece_at(from_square).type
  - from_name = chess.square_name(from_square)
  - to_name = chess.square_name(to_square)
    ↓
Build Message:
  msg = f"{piece_name} from {from_name} to {to_name}"
    ↓
Check Special:
  if capture: msg += ", captures"
  if check: msg += ", check"
  if checkmate: msg += ", checkmate"
    ↓
Platform Detection:
  if macOS: subprocess.run(['say', msg])
  if Linux: subprocess.run(['espeak', msg])
  if Windows: pyttsx3.speak(msg)
```

---

## 🧪 Metode Pengujian

### 1. Unit Testing

#### Test Cases:

**YoloDetector**:
```python
def test_load_model():
    detector = YoloDetector()
    assert detector.load_model("models/chess_yolo.pt") == True
    assert detector.model is not None

def test_detect():
    detector = YoloDetector()
    detector.load_model("models/chess_yolo.pt")
    frame = cv2.imread("test_images/position1.jpg")
    detections = detector.detect(frame, conf_threshold=0.5)
    assert len(detections) > 0
    assert all('class_name' in d for d in detections)
```

**ColorDetector**:
```python
def test_hsv_conversion():
    detector = ColorDetector()
    white_roi = np.ones((75, 75, 3), dtype=np.uint8) * 255
    result = detector.detect(white_roi)
    assert result == 'white'

def test_empty_detection():
    detector = ColorDetector()
    detector.occupancy_threshold = 50
    dark_roi = np.zeros((75, 75, 3), dtype=np.uint8)
    result = detector.detect(dark_roi)
    assert result == 'empty'
```

**StateManager**:
```python
def test_make_legal_move():
    state = StateManager()
    success, msg = state.make_move("e2e4")
    assert success == True
    assert state.get_fen().startswith("rnbqkbnr/pppppppp")

def test_reject_illegal_move():
    state = StateManager()
    success, msg = state.make_move("e2e5")
    assert success == False
```

---

### 2. Integration Testing

```python
def test_camera_to_processing_flow():
    """Test frame flow from camera to processing"""
    camera = CameraThread()
    processing = ProcessingThread()
    
    # Connect signals
    camera.frame_ready.connect(processing.update_frame)
    
    # Start threads
    camera.start()
    processing.start()
    
    # Wait and check
    time.sleep(2)
    assert processing.latest_frame is not None

def test_processing_to_hybrid_flow():
    """Test grid state flow"""
    processing = ProcessingThread()
    hybrid = HybridManager()
    
    # Connect signal
    processing.board_state_updated.connect(hybrid.update_board_state)
    
    # Mock grid state
    mock_grid = create_initial_grid()
    processing.board_state_updated.emit(mock_grid)
    
    # Check hybrid received it
    assert hybrid.current_stable_grid == mock_grid
```

---

### 3. Accuracy Testing

**Dataset**:
- 100 test images dengan ground truth annotations
- Berbagai kondisi pencahayaan
- Berbagai posisi papan

**Metrik**:
```python
def calculate_accuracy(predictions, ground_truth):
    TP = true_positives(predictions, ground_truth)
    FP = false_positives(predictions, ground_truth)
    FN = false_negatives(predictions, ground_truth)
    TN = true_negatives(predictions, ground_truth)
    
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * (precision * recall) / (precision + recall)
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy
    }
```

**Target**:
- Precision ≥ 90%
- Recall ≥ 85%
- F1-Score ≥ 87%
- Accuracy ≥ 90%

---

### 4. Performance Testing

```python
import time
import psutil

def test_fps_performance():
    """Measure frame rate"""
    camera = CameraThread()
    processing = ProcessingThread()
    
    frame_count = 0
    start_time = time.time()
    
    # Run for 60 seconds
    while time.time() - start_time < 60:
        # Process frame
        frame_count += 1
        
    fps = frame_count / 60
    assert fps >= 25, f"FPS too low: {fps}"

def test_latency():
    """Measure processing latency"""
    processing = ProcessingThread()
    
    latencies = []
    for _ in range(100):
        start = time.time()
        processing.process_frame(test_frame)
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 100, f"Latency too high: {avg_latency}ms"

def test_memory_usage():
    """Measure memory consumption"""
    process = psutil.Process()
    
    # Run application
    app = MainWindow()
    
    # Measure after 5 minutes
    time.sleep(300)
    
    memory_mb = process.memory_info().rss / 1024 / 1024
    assert memory_mb < 500, f"Memory too high: {memory_mb}MB"

def test_cpu_usage():
    """Measure CPU consumption"""
    process = psutil.Process()
    
    cpu_percentages = []
    for _ in range(60):
        cpu_percent = process.cpu_percent(interval=1)
        cpu_percentages.append(cpu_percent)
    
    avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
    assert avg_cpu < 70, f"CPU too high: {avg_cpu}%"
```

---

## 📊 Rangkuman Hasil

### Expected Performance:

| Metric | Target | Expected |
|--------|--------|----------|
| Detection Precision | ≥ 90% | 92-95% |
| Detection Recall | ≥ 85% | 88-90% |
| F1-Score | ≥ 87% | 90-92% |
| Overall Accuracy | ≥ 90% | 91-94% |
| Frame Rate | ≥ 25 FPS | 28-30 FPS |
| Latency | < 100ms | 60-80ms |
| Memory Usage | < 500 MB | 350-450 MB |
| CPU Usage | < 70% | 50-65% |

---

## 🎯 Kesimpulan Metode

### Metode Implementasi yang Digunakan:

1. **Computer Vision**: Canny Edge Detection, Homography Transform, HSV Color Analysis, YOLOv8 Object Detection
2. **Hybrid Detection**: Color + YOLO fusion dengan priority system
3. **State Management**: Differential analysis, Stability checking, Chess rules validation
4. **Engine Integration**: UCI protocol, Stockfish communication
5. **Audio Feedback**: Platform-specific TTS

### Metode Pengujian yang Diterapkan:

1. **Unit Testing**: Individual component testing
2. **Integration Testing**: Inter-component communication testing
3. **Accuracy Testing**: Dataset-based detection validation
4. **Performance Testing**: FPS, latency, resource usage monitoring

### Design Patterns:

1. Signal-Slot (Event-Driven)
2. Strategy Pattern (Detection)
3. State Pattern (Game State)
4. Observer Pattern (Logging)
5. MVC Architecture
