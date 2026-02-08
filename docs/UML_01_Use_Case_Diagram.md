# UML Use Case Diagram
## ChessMind Hybrid Vision System

## 1. Use Case Diagram Utama

```mermaid
graph TB
    subgraph "ChessMind Hybrid System"
        UC1((Kalibrasi Papan))
        UC2((Deteksi Otomatis))
        UC3((Mulai Permainan))
        UC4((Deteksi Gerakan))
        UC5((Validasi Move))
        UC6((Analisis Engine))
        UC7((Export PGN))
        UC8((Konfigurasi Sistem))
        UC9((Load YOLO Model))
        UC10((Sinkronisasi Board))
        UC11((Undo Move))
        UC12((Audio Feedback))
    end
    
    User[👤 User/Pemain]
    System[🖥️ System]
    Engine[🤖 Stockfish Engine]
    Camera[📹 Camera Device]
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    
    UC1 --> Camera
    UC2 --> Camera
    UC4 --> Camera
    UC10 --> Camera
    
    UC3 --> UC4
    UC4 --> UC5
    UC5 --> UC6
    UC6 --> Engine
    UC5 --> UC12
    UC12 --> System
    
    UC9 --> System
    
    style User fill:#4CAF50
    style Engine fill:#9C27B0
    style Camera fill:#FF9800
    style System fill:#2196F3
```

## 2. Use Case: Kalibrasi Papan

```mermaid
graph LR
    subgraph "Kalibrasi Papan Catur"
        UC_Manual((Kalibrasi Manual))
        UC_Auto((Deteksi Otomatis))
    end
    
    User[👤 User] --> UC_Manual
    User --> UC_Auto
    
    UC_Manual --> Click1[Klik Sudut 1]
    UC_Manual --> Click2[Klik Sudut 2]
    UC_Manual --> Click3[Klik Sudut 3]
    UC_Manual --> Click4[Klik Sudut 4]
    
    Click4 --> Compute[Hitung Homography]
    
    UC_Auto --> Detect[Deteksi Edge]
    Detect --> Find[Cari Contour]
    Find --> Compute
    
    Compute --> Ready[Sistem Siap]
    
    style User fill:#4CAF50
    style Compute fill:#2196F3
    style Ready fill:#4CAF50
```

## 3. Use Case: Deteksi dan Validasi Move

```mermaid
graph TD
    subgraph "Deteksi Gerakan Buah Catur"
        UC_Detect((Deteksi Perubahan))
        UC_Stable((Cek Stabilitas))
        UC_Infer((Inferensi Move))
        UC_Validate((Validasi Move))
        UC_Apply((Apply Move))
    end
    
    Camera[📹 Camera] --> UC_Detect
    UC_Detect --> UC_Stable
    
    UC_Stable --> |Stabil| UC_Infer
    UC_Stable --> |Tidak Stabil| UC_Detect
    
    UC_Infer --> UC_Validate
    
    UC_Validate --> |Legal| UC_Apply
    UC_Validate --> |Illegal| Warning[Tampilkan Warning]
    
    UC_Apply --> UpdateUI[Update UI]
    UC_Apply --> EngineAnalysis[Analisis Engine]
    UC_Apply --> AudioFeed[Audio Feedback]
    
    Warning --> UC_Detect
    
    style Camera fill:#FF9800
    style UC_Apply fill:#4CAF50
    style Warning fill:#F44336
```

## 4. Use Case: Analisis Engine

```mermaid
graph LR
    subgraph "Analisis Posisi dengan Stockfish"
        UC_Send((Kirim FEN))
        UC_Analyze((Analisis))
        UC_Receive((Terima Hasil))
        UC_Display((Tampilkan))
    end
    
    User[👤 User] --> Enable[Enable Engine]
    Enable --> UC_Send
    
    UC_Send --> UC_Analyze
    UC_Analyze --> Engine[🤖 Stockfish]
    
    Engine --> UC_Receive
    UC_Receive --> Parse[Parse Evaluasi]
    Parse --> UC_Display
    
    UC_Display --> ShowEval[Tampilkan Evaluasi]
    UC_Display --> ShowBest[Highlight Best Move]
    
    style User fill:#4CAF50
    style Engine fill:#9C27B0
    style UC_Display fill:#2196F3
```

## 5. Use Case Diagram - Actor Interactions

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Pemain Catur" as Player
actor "Kamera" as Camera
actor "Stockfish Engine" as Engine

rectangle "ChessMind Hybrid System" {
    usecase "Kalibrasi Papan Manual" as UC1
    usecase "Deteksi Papan Otomatis" as UC2
    usecase "Mulai Permainan Baru" as UC3
    usecase "Deteksi Gerakan Buah" as UC4
    usecase "Validasi Legalitas Move" as UC5
    usecase "Update Game State" as UC6
    usecase "Analisis Posisi" as UC7
    usecase "Export ke PGN" as UC8
    usecase "Sinkronisasi Board" as UC9
    usecase "Load YOLO Model" as UC10
    usecase "Konfigurasi Sistem" as UC11
    usecase "Audio Announcement" as UC12
}

Player --> UC1
Player --> UC2
Player --> UC3
Player --> UC8
Player --> UC9
Player --> UC10
Player --> UC11

Camera --> UC4
UC4 --> UC5
UC5 --> UC6
UC6 --> UC7
UC7 --> Engine
UC6 --> UC12

UC3 ..> UC4 : <<include>>
UC4 ..> UC5 : <<include>>
UC5 ..> UC6 : <<include>>
UC6 ..> UC7 : <<extend>>
UC6 ..> UC12 : <<extend>>

@enduml
```

## 6. Deskripsi Use Cases

### UC1: Kalibrasi Papan Manual
- **Aktor**: Pemain Catur
- **Precondition**: Kamera aktif, papan catur terlihat
- **Flow**:
  1. User klik tombol "Manual Calibration"
  2. User klik 4 sudut papan catur (TL, TR, BR, BL)
  3. Sistem menghitung homography matrix
  4. Sistem menampilkan warped board
- **Postcondition**: Papan catur terkalibrasi

### UC2: Deteksi Papan Otomatis
- **Aktor**: Pemain Catur, Kamera
- **Precondition**: Kamera aktif
- **Flow**:
  1. User klik tombol "Auto-Detect"
  2. Sistem melakukan edge detection
  3. Sistem mencari contour berbentuk persegi
  4. Sistem menghitung homography matrix
- **Postcondition**: Papan catur terkalibrasi otomatis

### UC3: Mulai Permainan Baru
- **Aktor**: Pemain Catur
- **Precondition**: Papan terkalibrasi
- **Flow**:
  1. User klik "Start New Game"
  2. Sistem reset game state ke posisi awal
  3. Sistem start chess clock
  4. Sistem mulai monitoring perubahan board
- **Postcondition**: Permainan dimulai

### UC4: Deteksi Gerakan Buah
- **Aktor**: Kamera
- **Precondition**: Game sedang berjalan
- **Flow**:
  1. Kamera capture frame
  2. Sistem deteksi dengan Color/YOLO
  3. Sistem build 8x8 grid state
  4. Sistem cek stabilitas (5 frames)
  5. Sistem inferensi move dari perbedaan grid
- **Postcondition**: Move terdeteksi

### UC5: Validasi Legalitas Move
- **Aktor**: System (chess.Board)
- **Precondition**: Move terdeteksi
- **Flow**:
  1. Sistem build UCI move string
  2. Sistem validasi dengan chess.Board.is_legal()
  3. Jika legal, lanjut ke UC6
  4. Jika illegal, tampilkan warning
- **Postcondition**: Move tervalidasi

### UC6: Update Game State
- **Aktor**: System
- **Precondition**: Move valid
- **Flow**:
  1. Sistem apply move ke board
  2. Sistem update FEN
  3. Sistem switch turn
  4. Sistem update clock
  5. Sistem update UI panels
- **Postcondition**: Game state terupdate

### UC7: Analisis Posisi
- **Aktor**: Stockfish Engine
- **Precondition**: Engine enabled, move applied
- **Flow**:
  1. Sistem kirim FEN ke Stockfish
  2. Stockfish analisis posisi (depth 15)
  3. Stockfish return evaluasi dan best move
  4. Sistem tampilkan di Evaluation Panel
- **Postcondition**: Evaluasi ditampilkan

### UC8: Export ke PGN
- **Aktor**: Pemain Catur
- **Precondition**: Game telah dimulai
- **Flow**:
  1. User klik "Export PGN"
  2. Sistem build PGN object dengan headers
  3. Sistem konversi move history ke SAN
  4. Sistem save ke file .pgn
- **Postcondition**: Game tersimpan dalam format PGN

### UC9: Sinkronisasi Board
- **Aktor**: Pemain Catur
- **Precondition**: YOLO model loaded
- **Flow**:
  1. User klik "Sync from Camera"
  2. Sistem ambil current YOLO grid state
  3. Sistem build board dari deteksi YOLO
  4. Sistem set sebagai current position
- **Postcondition**: Board tersinkronisasi dengan kamera

### UC10: Load YOLO Model
- **Aktor**: Pemain Catur
- **Precondition**: Model file tersedia
- **Flow**:
  1. User klik "Load YOLO Model"
  2. User pilih file model (.pt)
  3. Sistem load model dengan Ultralytics
  4. Sistem enable YOLO detection
- **Postcondition**: YOLO detection aktif

### UC11: Konfigurasi Sistem
- **Aktor**: Pemain Catur
- **Precondition**: -
- **Flow**:
  1. User buka Settings Dialog
  2. User edit parameter (camera, YOLO, engine, dll)
  3. User klik Apply
  4. Sistem validate dan save ke config.json
  5. Sistem restart affected components
- **Postcondition**: Konfigurasi terupdate

### UC12: Audio Announcement
- **Aktor**: System (TTS)
- **Precondition**: Audio enabled, move applied
- **Flow**:
  1. Sistem parse move UCI
  2. Sistem build natural language message
  3. Sistem speak dengan TTS (say/espeak/pyttsx3)
- **Postcondition**: Move diumumkan secara audio
