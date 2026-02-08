# Dokumentasi Implementasi dan Metode Pengujian
## ChessMind Hybrid Vision System

### 📚 Daftar Isi Dokumentasi

#### 1. [Arsitektur Sistem](./01_Arsitektur_Sistem.md)
Diagram arsitektur layer sistem, pola MVC, dan sistem event-driven menggunakan Signal-Slot pattern.

**Diagram yang tersedia:**
- Arsitektur Layer Sistem (UI, Core, Processing, Config)
- Arsitektur MVC (Model-View-Controller)
- Arsitektur Signal-Slot (Event-Driven)

#### 2. [Alur Kerja Sistem](./02_Alur_Kerja_Sistem.md)
Flowchart lengkap alur kerja utama aplikasi dari startup hingga deteksi move.

**Diagram yang tersedia:**
- Alur Kerja Utama (Main Workflow)
- Alur Deteksi Papan Otomatis
- Alur Pemrosesan Frame

#### 3. [Metode Deteksi](./03_Metode_Deteksi.md)
Detail metode deteksi buah catur menggunakan Color-Based dan YOLO Object Detection.

**Diagram yang tersedia:**
- Metode Color-Based Detection
- Metode YOLO Object Detection
- Metode Hybrid (Color + YOLO)

#### 4. [State Management & Game Logic](./04_Metode_State_Management.md)
Pengelolaan state permainan, inferensi move, dan mekanisme stabilitas.

**Diagram yang tersedia:**
- State Management Flow
- Move Inference Algorithm
- Stability Checking Mechanism

#### 5. [Metode Pengujian](./05_Metode_Pengujian.md)
Metodologi pengujian lengkap: Unit Testing, Integration Testing, Accuracy Testing, dan Performance Testing.

**Diagram yang tersedia:**
- Unit Testing Flow
- Integration Testing Flow
- Accuracy Testing (Detection)
- Performance Testing

#### 6. [Implementasi Kode](./06_Implementasi_Kode.md)
Struktur kode, design patterns yang digunakan, dan contoh implementasi.

**Diagram yang tersedia:**
- Struktur Kode Utama
- Pattern: Signal-Slot (Event-Driven)
- Pattern: Strategy Pattern (Detection Methods)
- Pattern: State Pattern (Game State)
- Pattern: Observer Pattern (Logging)

#### 7. [Computer Vision Pipeline](./07_Computer_Vision_Pipeline.md)
Pipeline pemrosesan gambar dari raw frame hingga grid state.

**Diagram yang tersedia:**
- Image Processing Pipeline
- Board Detection Pipeline
- Perspective Transformation
- Grid Division & ROI Extraction

#### 8. [Engine & Audio Integration](./08_Engine_Audio_Integration.md)
Integrasi Stockfish chess engine dan sistem audio feedback.

**Diagram yang tersedia:**
- Chess Engine Integration (Stockfish)
- Audio Feedback System
- Chess Clock System

#### 9. [Deployment & Configuration](./09_Deployment_Configuration.md)
Proses deployment, konfigurasi, instalasi, dan error handling.

**Diagram yang tersedia:**
- Deployment Architecture
- Configuration Flow
- Installation & Setup Process
- Error Handling & Logging

#### 10. [Data Persistence](./10_Data_Persistence.md)
Sistem penyimpanan data, PGN export, konfigurasi, dan statistik.

**Diagram yang tersedia:**
- Data Storage Architecture
- PGN Export Flow
- Configuration Management
- Statistics & Analytics

#### 11. [User Interface & Interaction](./11_User_Interface.md)
Hierarki komponen UI, user interaction flow, dan visual feedback.

**Diagram yang tersedia:**
- UI Component Hierarchy
- User Interaction Flow
- Control Panel Interactions
- Panel Update Flow
- Settings Dialog Flow
- Keyboard Shortcuts
- Visual Feedback System

#### 12. [Rangkuman Metode](./12_Rangkuman_Metode.md)
Rangkuman lengkap semua metode implementasi dan pengujian dengan detail algoritma.

**Konten:**
- Detail Algoritma Computer Vision
- Detail Algoritma Game State Management
- Detail Algoritma Engine Integration
- Detail Metode Pengujian dengan Code
- Expected Performance Results

---

## 🔬 Ringkasan Metode Pengujian

### 1. Unit Testing
- **YoloDetector**: Validasi model loading dan inference
- **ColorDetector**: Validasi konversi HSV dan klasifikasi warna
- **StateManager**: Validasi FEN parsing dan move validation
- **EngineManager**: Validasi koneksi Stockfish dan analysis

### 2. Integration Testing
- **Camera → Processing Flow**: Validasi pipeline frame processing
- **Processing → Hybrid Flow**: Validasi transmisi grid state
- **Hybrid → UI Flow**: Validasi signal emission ke UI
- **Engine Integration**: Validasi analisis posisi

### 3. Accuracy Testing
Menggunakan dataset test dengan ground truth:
- **Precision**: ≥ 90%
- **Recall**: ≥ 85%
- **F1-Score**: ≥ 87%
- **Accuracy**: ≥ 90%

Metrik yang diukur:
- True Positive (TP): Deteksi benar
- False Positive (FP): Deteksi salah
- False Negative (FN): Miss detection
- True Negative (TN): Empty square terdeteksi benar

### 4. Performance Testing
Target performance:
- **Frame Rate**: ≥ 25 FPS
- **Processing Latency**: < 100ms per frame
- **Memory Usage**: < 500 MB
- **CPU Usage**: < 70% (average)

---

## 🏗️ Ringkasan Metode Implementasi

### 1. Computer Vision Methods

#### a. Color-Based Detection
```
Input: ROI (75×75 pixels)
↓
BGR → HSV Conversion
↓
Calculate Mean H, S, V
↓
Occupancy Check (V > Threshold)
↓
Color Classification:
- White: S < 30, V > 180
- Black: S < 30, V < 80
- Empty: V < Threshold
↓
Output: 'white' | 'black' | 'empty'
```

#### b. YOLO Object Detection
```
Input: Warped Frame (600×600)
↓
YOLO Inference (YOLOv8)
↓
Detect 12 Classes:
- white-pawn, rook, knight, bishop, queen, king
- black-pawn, rook, knight, bishop, queen, king
↓
Parse Bounding Boxes
↓
Assign to Grid Squares
↓
Output: 8×8 Grid with class names
```

#### c. Hybrid Method
```
Run Both Methods in Parallel
↓
Merge Results (YOLO has priority)
↓
Stability Check (5 frames)
↓
Infer Chess Move
↓
Validate with chess.Board
↓
Update Game State
```

### 2. Image Processing Pipeline

#### a. Board Detection (Auto-Calibration)
```
Camera Frame
↓
Grayscale Conversion
↓
Gaussian Blur (5×5)
↓
Canny Edge Detection (50, 150)
↓
Find Contours
↓
Filter by Area & Shape
↓
Approximate Polygon (4 corners)
↓
Validate Aspect Ratio
↓
Compute Homography Matrix
```

#### b. Perspective Transformation
```
4 Corner Points
↓
Sort: TL, TR, BR, BL
↓
Destination: [0,0], [W,0], [W,H], [0,H]
↓
cv2.getPerspectiveTransform()
↓
Homography Matrix 3×3
↓
cv2.warpPerspective()
↓
Warped Image 600×600
```

### 3. Game Logic Methods

#### a. Move Inference
```
Compare New Grid with Previous Grid
↓
Count Changed Squares
↓
Pattern Recognition:
- 1 change: Promotion/Capture
- 2 changes: Normal Move
- 3 changes: En Passant
- 4 changes: Castling
↓
Build UCI Move
↓
Validate: chess.Board.is_legal()
↓
Apply or Reject Move
```

#### b. Stability Mechanism
```
New Grid State
↓
Compare with Current Stable Grid
↓
If Different:
  - Compare with Pending Grid
  - If Same: Increment Counter
  - If Different: Reset Counter, Set New Pending
↓
If Counter >= Threshold (5):
  - Confirm as Stable
  - Infer Move
  - Update State
```

### 4. Design Patterns Used

1. **Signal-Slot Pattern** (Event-Driven Architecture)
   - PyQt5 signals for loose coupling
   - Observer pattern for events

2. **Strategy Pattern** (Detection Methods)
   - ColorDetector
   - YoloDetector
   - Switchable at runtime

3. **State Pattern** (Game State Management)
   - StateManager handles game state transitions
   - chess.Board for validation

4. **Observer Pattern** (Logging System)
   - Multiple log observers (UI, File)
   - Central log emission

5. **MVC Pattern** (Overall Architecture)
   - Model: StateManager, ConfigManager
   - View: UI Panels
   - Controller: HybridManager, ProcessingThread

---

## 📊 Teknologi dan Library yang Digunakan

### Core Technologies
- **Python 3.8+**: Bahasa pemrograman utama
- **PyQt5**: GUI framework
- **OpenCV (cv2)**: Computer vision
- **Ultralytics YOLOv8**: Object detection
- **python-chess**: Chess logic dan validasi

### Supporting Libraries
- **NumPy**: Array operations
- **Stockfish**: Chess engine untuk analysis
- **pyttsx3/say**: Text-to-speech
- **subprocess**: Process management

### Development Tools
- **VS Code**: IDE
- **Git**: Version control
- **pytest**: Testing framework

---

## 📈 Hasil Pengujian (Expected)

### Accuracy Metrics
- Precision: 92-95%
- Recall: 88-90%
- F1-Score: 90-92%
- Overall Accuracy: 91-94%

### Performance Metrics
- Frame Rate: 28-30 FPS
- Detection Latency: 60-80ms
- Memory Usage: 350-450 MB
- CPU Usage: 50-65%

### Stability Metrics
- False Positive Rate: < 5%
- Move Detection Success Rate: > 95%
- Illegal Move Rejection: 100%

---

## 🎯 Kesimpulan

Sistem ChessMind Hybrid Vision mengimplementasikan:

1. **Dual Detection System**: Color-based + YOLO untuk akurasi maksimal
2. **Robust State Management**: Stability checking untuk menghindari false positive
3. **Comprehensive Testing**: Unit, Integration, Accuracy, dan Performance testing
4. **Modern Design Patterns**: Signal-Slot, Strategy, State, Observer, MVC
5. **Real-time Processing**: < 100ms latency untuk user experience yang smooth

Dokumentasi ini mencakup semua aspek implementasi dari arsitektur sistem, metode deteksi, pipeline pemrosesan, hingga metode pengujian yang komprehensif.
