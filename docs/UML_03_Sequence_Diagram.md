# UML Sequence Diagram
## ChessMind Hybrid Vision System

## 1. Sequence Diagram - Aplikasi Startup

```mermaid
sequenceDiagram
    participant Main as main()
    participant App as QApplication
    participant MW as MainWindow
    participant CM as ConfigManager
    participant CT as CameraThread
    participant PT as ProcessingThread
    participant HM as HybridManager
    
    Main->>App: Create QApplication
    Main->>MW: Create MainWindow()
    
    MW->>CM: Create ConfigManager()
    CM->>CM: load_config()
    CM-->>MW: config loaded
    
    MW->>CT: Create CameraThread()
    MW->>PT: Create ProcessingThread()
    MW->>HM: Create HybridManager(game_mode=True)
    
    HM->>HM: Initialize StateManager
    HM->>HM: Initialize EngineManager
    HM->>HM: Start Stockfish Engine
    
    MW->>MW: setup_ui()
    MW->>MW: connect_signals()
    
    MW->>PT: start()
    Note over PT: ProcessingThread running
    
    MW->>MW: show()
    Main->>App: exec_()
    Note over App: Event Loop Running
```

## 2. Sequence Diagram - Kalibrasi Manual

```mermaid
sequenceDiagram
    participant User
    participant MW as MainWindow
    participant RP as RawCameraPanel
    participant PT as ProcessingThread
    
    User->>MW: Click "Manual Calibration"
    MW->>RP: Enable click mode
    Note over RP: Waiting for clicks
    
    User->>RP: Click point 1 (TL)
    RP->>RP: Store point 1
    User->>RP: Click point 2 (TR)
    RP->>RP: Store point 2
    User->>RP: Click point 3 (BR)
    RP->>RP: Store point 3
    User->>RP: Click point 4 (BL)
    RP->>RP: Store point 4
    
    RP->>PT: set_calibration_points([p1,p2,p3,p4])
    PT->>PT: Sort corners (TL,TR,BR,BL)
    PT->>PT: Compute homography matrix
    PT-->>MW: log_message("Calibration successful")
    
    Note over PT: Warping enabled
```

## 3. Sequence Diagram - Auto-Detect Board

```mermaid
sequenceDiagram
    participant User
    participant MW as MainWindow
    participant PT as ProcessingThread
    participant CV as OpenCV
    
    User->>MW: Click "Auto-Detect"
    MW->>PT: start_auto_detect()
    Note over PT: Auto-detection mode active
    
    loop Every frame
        PT->>PT: Latest frame available
        PT->>CV: cvtColor(GRAY)
        CV-->>PT: gray_frame
        PT->>CV: GaussianBlur()
        CV-->>PT: blurred
        PT->>CV: Canny(50, 150)
        CV-->>PT: edges
        PT->>CV: findContours()
        CV-->>PT: contours[]
        
        PT->>PT: Sort by area
        loop For each large contour
            PT->>CV: approxPolyDP()
            CV-->>PT: approx_polygon
            
            alt 4 corners found
                PT->>PT: Check aspect ratio
                alt Valid square shape
                    PT->>PT: set_calibration_points()
                    PT->>PT: stop_auto_detect()
                    PT-->>MW: log_message("Board detected")
                    Note over PT: Auto-detection stopped
                end
            end
        end
    end
```

## 4. Sequence Diagram - Frame Processing

```mermaid
sequenceDiagram
    participant CT as CameraThread
    participant PT as ProcessingThread
    participant CD as ColorDetector
    participant YD as YoloDetector
    participant HM as HybridManager
    
    CT->>CT: Read frame from camera
    CT->>PT: emit frame_ready(frame)
    
    PT->>PT: update_frame(frame)
    Note over PT: Latest frame stored
    
    PT->>PT: process_frame()
    
    alt Homography available
        PT->>PT: warpPerspective(frame)
        Note over PT: 600x600 warped
        
        par Color Detection
            loop 8x8 grid
                PT->>CD: detect(roi)
                CD->>CD: BGR→HSV
                CD->>CD: Calculate mean
                CD->>CD: Classify color
                CD-->>PT: 'white'/'black'/'empty'
            end
        and YOLO Detection
            alt YOLO enabled
                PT->>YD: detect(warped_frame)
                YD->>YD: YOLO inference
                YD->>YD: Parse detections
                YD->>YD: Assign to squares
                YD-->>PT: yolo_grid
            end
        end
        
        PT->>PT: Merge results
        PT->>HM: emit board_state_updated(grid)
        PT->>HM: emit yolo_state_updated(yolo_grid)
    end
```

## 5. Sequence Diagram - Move Detection & Validation

```mermaid
sequenceDiagram
    participant PT as ProcessingThread
    participant HM as HybridManager
    participant SM as StateManager
    participant EM as EngineManager
    participant AM as AudioManager
    participant UI as UI Panels
    
    PT->>HM: board_state_updated(new_grid)
    
    HM->>HM: Compare with stable_grid
    
    alt Grid changed
        HM->>HM: Check stability
        alt Not stable (counter < 5)
            HM->>HM: Increment counter
            Note over HM: Wait for more frames
        else Stable (counter >= 5)
            HM->>HM: infer_move(old_grid, new_grid)
            HM->>HM: Analyze differences
            HM->>HM: Build UCI move
            
            HM->>SM: Validate move
            SM->>SM: chess.Board.is_legal(move)
            
            alt Legal move
                SM-->>HM: True
                HM->>SM: make_move(uci)
                SM->>SM: Apply move
                SM->>SM: Update FEN
                SM-->>HM: FEN string
                
                HM->>UI: emit game_state_updated(FEN, move)
                HM->>EM: analyze_position(FEN)
                HM->>AM: announce_move(uci, board)
                
                EM->>EM: Send to Stockfish
                EM->>EM: Parse response
                EM->>UI: emit evaluation_updated(eval)
                EM->>UI: emit best_move_found(move)
                
                AM->>AM: Build message
                AM->>AM: TTS speak
                
            else Illegal move
                SM-->>HM: False
                HM->>UI: emit illegal_move_attempted(uci)
                Note over UI: Show warning dialog
            end
        end
    end
```

## 6. Sequence Diagram - Engine Analysis

```mermaid
sequenceDiagram
    participant HM as HybridManager
    participant EM as EngineManager
    participant SF as Stockfish
    participant EP as EvaluationPanel
    participant BP as BoardPanel
    
    HM->>EM: analyze_position(fen, depth=15)
    
    EM->>SF: position fen {fen}
    EM->>SF: go depth 15
    
    Note over SF: Analyzing...
    
    loop Info updates
        SF-->>EM: info depth X score cp Y pv ...
        EM->>EM: Parse info line
    end
    
    SF-->>EM: bestmove e2e4
    
    EM->>EM: Parse evaluation
    EM->>EM: Format score
    
    alt Centipawn score
        EM->>EM: eval = "+1.25"
    else Mate score
        EM->>EM: eval = "M5"
    end
    
    EM->>EP: emit evaluation_updated(eval)
    EP->>EP: Update label
    EP->>EP: Update progress bar
    
    EM->>BP: emit best_move_found("e2e4")
    BP->>BP: Draw arrow on board
```

## 7. Sequence Diagram - Export PGN

```mermaid
sequenceDiagram
    participant User
    participant MW as MainWindow
    participant SM as StateManager
    participant PGN as chess.pgn
    participant FS as FileSystem
    
    User->>MW: Click "Export PGN"
    MW->>SM: get_pgn()
    
    SM->>PGN: Create Game()
    SM->>PGN: Set headers (Event, Date, etc.)
    
    loop For each move in history
        SM->>SM: Convert UCI to SAN
        SM->>PGN: Add variation(move)
    end
    
    SM->>PGN: str(game)
    PGN-->>SM: pgn_string
    
    SM->>SM: Generate filename
    Note over SM: game_YYYYMMDD_HHMMSS.pgn
    
    SM->>FS: Write file
    FS-->>SM: Success
    
    SM-->>MW: filename
    MW->>User: Show success message
```

## 8. Sequence Diagram - Complete Move Flow

```plantuml
@startuml
participant "Camera" as Camera
participant "ProcessingThread" as PT
participant "HybridManager" as HM
participant "StateManager" as SM
participant "EngineManager" as EM
participant "AudioManager" as AM
participant "UI Panels" as UI

Camera -> PT: Capture frame
PT -> PT: Warp perspective
PT -> PT: Detect pieces (Color/YOLO)
PT -> HM: board_state_updated(grid)

HM -> HM: Check stability
alt Stable (5 frames)
    HM -> HM: infer_move()
    HM -> SM: Validate move
    
    alt Legal
        SM -> SM: Apply move
        SM --> HM: FEN updated
        
        HM -> UI: game_state_updated(FEN, move)
        UI -> UI: Update displays
        
        HM -> EM: analyze_position(FEN)
        EM -> EM: Query Stockfish
        EM --> UI: evaluation_updated(eval)
        EM --> UI: best_move_found(move)
        
        HM -> AM: announce_move(uci)
        AM -> AM: TTS speak
        
    else Illegal
        HM -> UI: illegal_move_attempted(uci)
        UI -> UI: Show warning
    end
end

@enduml
```

## 9. Sequence Diagram - Clock Update

```mermaid
sequenceDiagram
    participant HM as HybridManager
    participant Clock as ChessClock
    participant SP as StatusPanel
    
    Note over Clock: Timer ticking every 100ms
    
    loop Every tick
        Clock->>Clock: Decrease active player time
        
        alt Time > 0
            Clock->>SP: emit time_updated(white, black)
            SP->>SP: Format time strings
            SP->>SP: Update labels
        else Time = 0
            Clock->>Clock: Stop timer
            Clock->>HM: emit flag_fall(is_white)
            HM->>HM: Handle time forfeit
            HM->>SP: Show game over message
        end
    end
    
    Note over HM: When move is made
    HM->>Clock: switch_turn()
    Clock->>Clock: Add increment
    Clock->>Clock: Switch active player
```
