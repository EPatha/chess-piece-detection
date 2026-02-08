# User Interface & Interaction

## 1. UI Component Hierarchy

```mermaid
graph TD
    Main[MainWindow] --> Top[Top Section]
    Main --> Bottom[Bottom Section]
    
    Top --> Left[Left Column]
    Top --> Center[Center Column]
    Top --> Right[Right Column]
    
    Left --> Raw[RawCameraPanel<br/>Live Camera Feed]
    Left --> Cropped[CroppedCameraPanel<br/>Warped Board View]
    
    Center --> Board[BoardViewPanel<br/>Chess Board Visualization]
    Center --> Status[PieceStatusPanel<br/>Game Info & Clock]
    
    Right --> History[HistoryPanel<br/>Move History PGN]
    Right --> Eval[EvaluationPanel<br/>Engine Analysis]
    
    Bottom --> Controls[Control Panel<br/>Buttons & Settings]
    Bottom --> Logs[LogViewPanel<br/>System Logs]
    
    style Main fill:#4CAF50
    style Board fill:#2196F3
    style Controls fill:#FF9800
```

## 2. User Interaction Flow

```mermaid
stateDiagram-v2
    [*] --> AppLaunch: Start Application
    
    AppLaunch --> CameraSelect: Select Camera
    CameraSelect --> Calibration: Calibrate Board
    
    Calibration --> ManualCalib: Manual Mode
    Calibration --> AutoCalib: Auto-Detect Mode
    
    ManualCalib --> ClickCorners: Click 4 Corners
    AutoCalib --> ProcessAuto: Auto-Find Board
    
    ClickCorners --> Calibrated: Homography Computed
    ProcessAuto --> Calibrated: Homography Computed
    
    Calibrated --> LoadModel: Load YOLO Model
    LoadModel --> ModelLoaded: Model Ready
    
    ModelLoaded --> GameSetup: Setup Game
    GameSetup --> StartGame: Click Start Game
    
    StartGame --> Playing: Game In Progress
    
    Playing --> MakeMove: User Moves Piece
    MakeMove --> Detecting: System Detecting
    Detecting --> Validating: Validating Move
    
    Validating --> Legal: Legal Move
    Validating --> Illegal: Illegal Move
    
    Legal --> UpdateBoard: Update Display
    Illegal --> ShowWarning: Show Warning
    
    ShowWarning --> Playing
    UpdateBoard --> CheckEnd: Check Game Status
    
    CheckEnd --> Playing: Game Continues
    CheckEnd --> GameOver: Checkmate/Draw
    
    GameOver --> SavePGN: Auto-Save PGN
    SavePGN --> ResetOption: Reset or Exit
    
    ResetOption --> GameSetup: New Game
    ResetOption --> [*]: Exit
```

## 3. Control Panel Interactions

```mermaid
flowchart TD
    Controls[Control Panel] --> CameraGroup[Camera Controls]
    Controls --> CalibGroup[Calibration Controls]
    Controls --> GameGroup[Game Controls]
    Controls --> DetectionGroup[Detection Controls]
    
    CameraGroup --> SelectCam[Select Camera Source]
    CameraGroup --> ToggleCam[Start/Stop Camera]
    
    CalibGroup --> ManualBtn[Manual Calibration]
    CalibGroup --> AutoBtn[Auto-Detect Board]
    CalibGroup --> ResetCalib[Reset Calibration]
    
    GameGroup --> StartGame[Start New Game]
    GameGroup --> ResetGame[Reset Game]
    GameGroup --> SavePGN[Export PGN]
    GameGroup --> SyncBoard[Sync from Camera]
    
    DetectionGroup --> LoadYOLO[Load YOLO Model]
    DetectionGroup --> ToggleYOLO[Enable/Disable YOLO]
    DetectionGroup --> ScanBoard[Scan Board]
    DetectionGroup --> ToggleEngine[Enable/Disable Engine]
    
    SelectCam --> Action1[Update Camera Source]
    ToggleCam --> Action2[Start/Stop Thread]
    
    ManualBtn --> Action3[Enable Click Mode]
    AutoBtn --> Action4[Start Auto-Detection]
    ResetCalib --> Action5[Clear Homography]
    
    StartGame --> Action6[Initialize Game State]
    ResetGame --> Action7[Reset to Start Position]
    SavePGN --> Action8[Export to File]
    SyncBoard --> Action9[Set Position from YOLO]
    
    LoadYOLO --> Action10[Load Model File]
    ToggleYOLO --> Action11[Switch Detection Mode]
    ScanBoard --> Action12[Run 30-Frame Scan]
    ToggleEngine --> Action13[Start/Stop Stockfish]
    
    style Controls fill:#4CAF50
    style CameraGroup fill:#2196F3
    style GameGroup fill:#FF9800
    style DetectionGroup fill:#9C27B0
```

## 4. Panel Update Flow

```mermaid
sequenceDiagram
    participant U as User
    participant CameraThread
    participant ProcessingThread
    participant HybridManager
    participant RawPanel
    participant CroppedPanel
    participant BoardPanel
    participant StatusPanel
    participant EvalPanel
    participant LogPanel
    
    U->>CameraThread: Start Camera
    
    loop Every Frame
        CameraThread->>RawPanel: frame_ready signal
        RawPanel->>RawPanel: Update Display
        
        CameraThread->>ProcessingThread: frame_ready signal
        ProcessingThread->>ProcessingThread: Process Frame
        ProcessingThread->>CroppedPanel: processed_frame_ready
        CroppedPanel->>CroppedPanel: Update Warped View
        
        ProcessingThread->>HybridManager: board_state_updated
        HybridManager->>HybridManager: Check Stability
        
        alt Move Detected
            HybridManager->>HybridManager: Infer & Validate Move
            HybridManager->>BoardPanel: game_state_updated
            BoardPanel->>BoardPanel: Update FEN Display
            
            HybridManager->>StatusPanel: game_state_updated
            StatusPanel->>StatusPanel: Update Turn & Material
            
            HybridManager->>EvalPanel: evaluation_updated
            EvalPanel->>EvalPanel: Update Engine Eval
            
            HybridManager->>LogPanel: log_message
            LogPanel->>LogPanel: Add Log Entry
        end
    end
```

## 5. Settings Dialog Flow

```mermaid
flowchart TD
    Open[Open Settings] --> LoadCurrent[Load Current Settings]
    LoadCurrent --> DisplayTabs[Display Tabs:<br/>- Camera<br/>- Detection<br/>- Engine<br/>- Audio<br/>- Advanced]
    
    DisplayTabs --> UserEdit{User Edits?}
    UserEdit -->|No Change| Cancel[Cancel]
    UserEdit -->|Changed| Validate[Validate Input]
    
    Validate --> Valid{Valid?}
    Valid -->|No| ShowError[Show Error Message]
    Valid -->|Yes| Preview[Show Preview/Test]
    
    ShowError --> UserEdit
    Preview --> UserConfirm{Confirm Changes?}
    
    UserConfirm -->|No| Cancel
    UserConfirm -->|Yes| Apply[Apply Settings]
    
    Apply --> SaveConfig[Save to config.json]
    SaveConfig --> RestartComponents[Restart Affected Components]
    
    RestartComponents --> Success[Show Success Message]
    Success --> Close[Close Dialog]
    Cancel --> Close
    
    Close --> End([Settings Updated])
    
    style Open fill:#4CAF50
    style Apply fill:#2196F3
    style End fill:#4CAF50
    style ShowError fill:#F44336
```

## 6. Keyboard Shortcuts

```mermaid
graph TD
    Shortcuts[Keyboard Shortcuts] --> Camera[Camera Controls]
    Shortcuts --> Game[Game Controls]
    Shortcuts --> Detection[Detection Controls]
    Shortcuts --> View[View Controls]
    
    Camera --> C1["Space: Start/Stop Camera"]
    Camera --> C2["C: Cycle Camera Source"]
    
    Game --> G1["N: New Game"]
    Game --> G2["R: Reset Game"]
    Game --> G3["S: Save PGN"]
    Game --> G4["U: Undo Move"]
    
    Detection --> D1["A: Auto-Detect Board"]
    Detection --> D2["M: Manual Calibration"]
    Detection --> D3["Y: Toggle YOLO"]
    Detection --> D4["E: Toggle Engine"]
    
    View --> V1["F11: Fullscreen"]
    View --> V2["L: Toggle Logs"]
    View --> V3["D: Toggle Debug"]
    View --> V4["H: Show Help"]
    
    style Shortcuts fill:#4CAF50
    style Camera fill:#2196F3
    style Game fill:#FF9800
    style Detection fill:#9C27B0
    style View fill:#795548
```

### Code: Keyboard Shortcuts Implementation

```python
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

class MainWindow(QMainWindow):
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Camera Controls
        QShortcut(QKeySequence(Qt.Key_Space), self, self.toggle_camera)
        QShortcut(QKeySequence("C"), self, self.cycle_camera)
        
        # Game Controls
        QShortcut(QKeySequence("N"), self, self.new_game)
        QShortcut(QKeySequence("R"), self, self.reset_game)
        QShortcut(QKeySequence("S"), self, self.save_pgn)
        QShortcut(QKeySequence("U"), self, self.undo_move)
        
        # Detection Controls
        QShortcut(QKeySequence("A"), self, self.auto_detect)
        QShortcut(QKeySequence("M"), self, self.manual_calibration)
        QShortcut(QKeySequence("Y"), self, self.toggle_yolo)
        QShortcut(QKeySequence("E"), self, self.toggle_engine)
        
        # View Controls
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("L"), self, self.toggle_logs)
        QShortcut(QKeySequence("D"), self, self.toggle_debug)
        QShortcut(QKeySequence("H"), self, self.show_help)
```

## 7. Visual Feedback System

```mermaid
flowchart TD
    Event[User Action / System Event] --> Type{Event Type?}
    
    Type -->|Success| Green[Green Highlight]
    Type -->|Warning| Yellow[Yellow Highlight]
    Type -->|Error| Red[Red Highlight]
    Type -->|Info| Blue[Blue Highlight]
    
    Green --> Flash1[Flash Animation]
    Yellow --> Flash2[Flash Animation]
    Red --> Flash3[Flash Animation]
    Blue --> Flash4[Flash Animation]
    
    Flash1 --> Sound1{Sound Enabled?}
    Flash2 --> Sound2{Sound Enabled?}
    Flash3 --> Sound3{Sound Enabled?}
    Flash4 --> Sound4{Sound Enabled?}
    
    Sound1 -->|Yes| PlaySuccess[Play Success Sound]
    Sound2 -->|Yes| PlayWarning[Play Warning Sound]
    Sound3 -->|Yes| PlayError[Play Error Sound]
    Sound4 -->|Yes| PlayInfo[Play Info Sound]
    
    Sound1 -->|No| Visual
    Sound2 -->|No| Visual
    Sound3 -->|No| Visual
    Sound4 -->|No| Visual
    
    PlaySuccess --> Visual[Visual Feedback Complete]
    PlayWarning --> Visual
    PlayError --> Visual
    PlayInfo --> Visual
    
    Visual --> Log[Add to Log Panel]
    Log --> End([Feedback Complete])
    
    style Event fill:#4CAF50
    style Green fill:#4CAF50
    style Yellow fill:#FFC107
    style Red fill:#F44336
    style Blue fill:#2196F3
```

### Visual Feedback Examples:

1. **Move Detected (Success)**
   - Board square highlights in green
   - Success sound plays
   - Log: "[INFO] Move detected: e2e4"

2. **Illegal Move (Error)**
   - Board square highlights in red
   - Error sound plays
   - Dialog shows: "Illegal move attempted"
   - Log: "[ERROR] Illegal move: e2e5"

3. **Board Calibrated (Success)**
   - Raw camera panel border turns green
   - Success sound plays
   - Log: "[INFO] Board calibrated successfully"

4. **Model Loading (Info)**
   - Progress bar shows loading
   - Info sound plays
   - Log: "[INFO] Loading YOLO model..."

5. **Engine Analysis (Info)**
   - Evaluation panel updates
   - Log: "[INFO] Engine evaluation: +0.52"
