# UML Activity Diagram
## ChessMind Hybrid Vision System

## 1. Activity Diagram - Main Application Flow

```plantuml
@startuml
start

:Initialize Application;
:Load Configuration;
:Create Main Window;

fork
  :Start Camera Thread;
fork again
  :Start Processing Thread;
fork again
  :Start Hybrid Manager;
end fork

:Display UI;

repeat
  :Wait for User Action;
  
  if (Action Type?) then (Calibrate Board)
    if (Manual or Auto?) then (Manual)
      :Click 4 Corners;
    else (Auto)
      :Auto-Detect Board;
    endif
    :Compute Homography;
    
  elseif (Load YOLO Model) then
    :Select Model File;
    :Load YOLO;
    :Enable YOLO Detection;
    
  elseif (Start Game) then
    :Reset Game State;
    :Start Clock;
    :Enable Monitoring;
    
    repeat
      :Capture Frame;
      :Process Frame;
      :Detect Board State;
      
      if (State Changed?) then (Yes)
        :Wait for Stability;
        if (Stable?) then (Yes)
          :Infer Move;
          if (Legal?) then (Yes)
            :Apply Move;
            :Update UI;
            :Analyze Position;
            :Announce Move;
          else (No)
            :Show Warning;
          endif
        endif
      endif
      
    repeat while (Game Active?) is (Yes)
    
  elseif (Export PGN) then
    :Generate PGN;
    :Save to File;
    
  elseif (Settings) then
    :Open Settings Dialog;
    :Edit Configuration;
    :Save & Apply;
  endif

repeat while (Continue?) is (Yes)

:Cleanup Resources;
:Stop Threads;
:Save Configuration;

stop
@enduml
```

## 2. Activity Diagram - Board Detection Process

```mermaid
flowchart TD
    Start([Start Auto-Detection]) --> InitParams[Initialize Detection Parameters]
    InitParams --> CaptureLoop{Capture Loop Active}
    
    CaptureLoop -->|Yes| GetFrame[Get Frame from Camera]
    GetFrame --> Grayscale[Convert to Grayscale]
    Grayscale --> Blur[Apply Gaussian Blur]
    Blur --> Canny[Canny Edge Detection]
    Canny --> Morphology[Morphological Operations]
    
    Morphology --> FindContours[Find Contours]
    FindContours --> SortContours[Sort by Area Descending]
    
    SortContours --> LoopContours{For Each Large Contour}
    LoopContours -->|Next| AreaCheck{Area > Threshold?}
    
    AreaCheck -->|No| LoopContours
    AreaCheck -->|Yes| ApproxPoly[Approximate Polygon]
    
    ApproxPoly --> VertexCheck{4 Vertices?}
    VertexCheck -->|No| LoopContours
    VertexCheck -->|Yes| AspectCheck{Aspect Ratio OK?}
    
    AspectCheck -->|No| LoopContours
    AspectCheck -->|Yes| FoundBoard[Board Found!]
    
    FoundBoard --> SortCorners[Sort Corners TL,TR,BR,BL]
    SortCorners --> ComputeH[Compute Homography Matrix]
    ComputeH --> StoreH[Store Matrix]
    StoreH --> Success([Detection Success])
    
    LoopContours -->|No More| Timeout{Timeout?}
    Timeout -->|No| CaptureLoop
    Timeout -->|Yes| Failed([Detection Failed])
    
    CaptureLoop -->|No| Cleanup[Cleanup]
    Cleanup --> End([End])
    
    Success --> End
    Failed --> End
    
    style Start fill:#4CAF50
    style Success fill:#4CAF50
    style Failed fill:#F44336
```

## 3. Activity Diagram - Frame Processing

```plantuml
@startuml
|CameraThread|
start
:Capture Frame;

|ProcessingThread|
:Receive Frame;

if (Homography Available?) then (Yes)
  :Warp Perspective;
  :Divide into 8x8 Grid;
  
  fork
    |ColorDetector|
    :Process with Color Detection;
    repeat
      :Extract ROI for Square;
      :Convert BGR to HSV;
      :Calculate Mean HSV;
      if (V < Threshold?) then (Yes)
        :Mark as Empty;
      else (No)
        if (Bright?) then (Yes)
          :Mark as White;
        else (No)
          :Mark as Black;
        endif
      endif
    repeat while (All 64 Squares Done?) is (No)
    :Build Color Grid;
    
  fork again
    |YoloDetector|
    if (YOLO Enabled?) then (Yes)
      :Run YOLO Inference;
      :Parse Detections;
      :Filter by Confidence;
      repeat
        :Get BBox;
        :Calculate Center;
        :Determine Square;
        :Store Class;
      repeat while (All Detections Done?) is (No)
      :Build YOLO Grid;
    endif
  end fork
  
  |ProcessingThread|
  :Merge Color & YOLO Grids;
  :Emit board_state_updated;
  
else (No)
  :Display Raw Frame;
endif

stop
@enduml
```

## 4. Activity Diagram - Move Inference

```mermaid
flowchart TD
    Start([New Grid State]) --> Compare[Compare with Stable Grid]
    Compare --> Different{Grids Different?}
    
    Different -->|No| Reset[Reset Stability Counter]
    Reset --> Wait([Wait Next Frame])
    
    Different -->|Yes| CheckPending{Same as Pending?}
    CheckPending -->|No| SetPending[Set as Pending Grid]
    SetPending --> Counter1[Set Counter = 1]
    Counter1 --> Wait
    
    CheckPending -->|Yes| Increment[Increment Counter]
    Increment --> CheckThreshold{Counter >= 5?}
    
    CheckThreshold -->|No| Wait
    CheckThreshold -->|Yes| Stable[Confirmed Stable]
    
    Stable --> CountChanges[Count Changed Squares]
    CountChanges --> Analyze{Number of Changes?}
    
    Analyze -->|0| NoMove[No Move Detected]
    Analyze -->|1| OneSquare[Single Square Change]
    Analyze -->|2| TwoSquares[Two Squares Changed]
    Analyze -->|3| ThreeSquares[Three Squares Changed]
    Analyze -->|4| FourSquares[Four Squares Changed]
    Analyze -->|>4| Error[Too Many Changes]
    
    TwoSquares --> NormalMove[Identify Source & Dest]
    NormalMove --> BuildUCI[Build UCI Move String]
    
    ThreeSquares --> EnPassant[Check En Passant Pattern]
    EnPassant --> BuildUCI
    
    FourSquares --> Castling[Check Castling Pattern]
    Castling --> BuildUCI
    
    OneSquare --> Promotion[Check Promotion]
    Promotion --> BuildUCI
    
    BuildUCI --> Validate{Legal Move?}
    Validate -->|Yes| Apply[Apply Move]
    Validate -->|No| Illegal[Emit Illegal Move]
    
    Apply --> UpdateFEN[Update FEN]
    UpdateFEN --> SwitchTurn[Switch Turn]
    SwitchTurn --> UpdateClock[Update Clock]
    UpdateClock --> EmitState[Emit game_state_updated]
    EmitState --> Success([Move Applied])
    
    NoMove --> Wait
    Error --> Illegal
    Illegal --> RejectMove([Move Rejected])
    
    style Start fill:#4CAF50
    style Success fill:#4CAF50
    style RejectMove fill:#F44336
    style Illegal fill:#F44336
```

## 5. Activity Diagram - Engine Analysis

```plantuml
@startuml
|HybridManager|
start

if (Engine Enabled?) then (Yes)
  :Get Current FEN;
  
  |EngineManager|
  :Send Position to Stockfish;
  :Send 'go depth 15' Command;
  
  |Stockfish|
  :Start Analysis;
  
  repeat
    :Calculate Evaluation;
    :Find Best Line;
    |EngineManager|
    :Receive Info Line;
    :Parse Depth, Score, PV;
  repeat while (Target Depth Reached?) is (No)
  
  |Stockfish|
  :Return Best Move;
  
  |EngineManager|
  :Parse Best Move;
  
  fork
    :Format Evaluation;
    if (Mate Score?) then (Yes)
      :Format as "M5" or "-M3";
    else (No)
      :Format as "+1.25" or "-0.50";
    endif
    :Emit evaluation_updated;
    
  fork again
    :Extract Best Move UCI;
    :Emit best_move_found;
  end fork
  
  |UI Panels|
  :Update Evaluation Display;
  :Highlight Best Move Arrow;
  
else (No)
  :Skip Analysis;
endif

stop
@enduml
```

## 6. Activity Diagram - Game Session

```mermaid
flowchart TD
    Start([User Starts Game]) --> ResetState[Reset Game State]
    ResetState --> ResetClock[Reset Chess Clock]
    ResetClock --> InitBoard[Initialize Board Position]
    
    InitBoard --> GameLoop{Game Active?}
    
    GameLoop -->|Yes| WaitMove[Wait for Physical Move]
    WaitMove --> DetectChange[Detect Board Change]
    DetectChange --> Stable{Stable?}
    
    Stable -->|No| WaitMove
    Stable -->|Yes| InferMove[Infer Move]
    
    InferMove --> ValidMove{Valid?}
    ValidMove -->|No| ShowWarning[Show Illegal Move Warning]
    ShowWarning --> WaitMove
    
    ValidMove -->|Yes| ApplyMove[Apply Move to Board]
    ApplyMove --> UpdateUI[Update All UI Panels]
    UpdateUI --> CheckStatus{Check Game Status}
    
    CheckStatus -->|Checkmate| GameOver[Declare Winner]
    CheckStatus -->|Stalemate| GameOver
    CheckStatus -->|Draw| GameOver
    CheckStatus -->|Time Up| GameOver
    CheckStatus -->|Continue| SwitchClock[Switch Clock]
    
    SwitchClock --> EngineAnalyze{Engine Enabled?}
    EngineAnalyze -->|Yes| RunAnalysis[Run Engine Analysis]
    EngineAnalyze -->|No| AudioAnnounce
    
    RunAnalysis --> ShowEval[Show Evaluation]
    ShowEval --> AudioAnnounce{Audio Enabled?}
    
    AudioAnnounce -->|Yes| Speak[Announce Move]
    AudioAnnounce -->|No| GameLoop
    Speak --> GameLoop
    
    GameOver --> SavePGN[Auto-save PGN]
    SavePGN --> ShowResult[Show Game Result]
    ShowResult --> UserChoice{Play Again?}
    
    UserChoice -->|Yes| Start
    UserChoice -->|No| End([Exit Game])
    
    GameLoop -->|No| End
    
    style Start fill:#4CAF50
    style GameOver fill:#FF9800
    style End fill:#F44336
```

## 7. Activity Diagram - Configuration Management

```plantuml
@startuml
start

:User Opens Settings;

partition "Settings Dialog" {
  :Load Current Config;
  :Display in Tabs;
  
  repeat
    :User Edits Settings;
    
    if (Input Valid?) then (Yes)
      :Update Preview;
    else (No)
      :Show Validation Error;
    endif
    
  repeat while (User Confirms?) is (No)
}

:Validate All Settings;

if (All Valid?) then (Yes)
  :Save to config.json;
  
  fork
    if (Camera Settings Changed?) then (Yes)
      :Restart Camera Thread;
    endif
  fork again
    if (YOLO Settings Changed?) then (Yes)
      :Reload YOLO Model;
    endif
  fork again
    if (Engine Settings Changed?) then (Yes)
      :Restart Stockfish;
    endif
  fork again
    if (Processing Settings Changed?) then (Yes)
      :Update Processing Parameters;
    endif
  end fork
  
  :Emit config_changed Signal;
  :Show Success Message;
  
else (No)
  :Show Error Dialog;
  :Revert Changes;
endif

stop
@enduml
```

## 8. Activity Diagram - Error Handling

```mermaid
flowchart TD
    Error([Error Occurs]) --> Classify{Error Type?}
    
    Classify -->|Camera Error| CameraError[Camera Error Handler]
    Classify -->|Model Error| ModelError[Model Error Handler]
    Classify -->|Engine Error| EngineError[Engine Error Handler]
    Classify -->|Move Error| MoveError[Move Error Handler]
    Classify -->|Config Error| ConfigError[Config Error Handler]
    
    CameraError --> CamRetry{Camera Available?}
    CamRetry -->|Yes| ReinitCam[Reinitialize Camera]
    CamRetry -->|No| ShowCamError[Show Error Dialog]
    ShowCamError --> UserFixCam{User Fixes?}
    UserFixCam -->|Yes| ReinitCam
    UserFixCam -->|No| DisableCam[Disable Camera Features]
    
    ModelError --> ModelRetry{Model File Exists?}
    ModelRetry -->|Yes| ReloadModel[Reload Model]
    ModelRetry -->|No| ShowModelError[Show Error Dialog]
    ShowModelError --> UserSelectModel{User Selects New?}
    UserSelectModel -->|Yes| ReloadModel
    UserSelectModel -->|No| DisableYOLO[Disable YOLO, Use Color]
    
    EngineError --> EngineRetry{Stockfish Available?}
    EngineRetry -->|Yes| RestartEngine[Restart Engine]
    EngineRetry -->|No| ShowEngineError[Show Error Dialog]
    ShowEngineError --> UserFixEngine{User Fixes?}
    UserFixEngine -->|Yes| RestartEngine
    UserFixEngine -->|No| DisableEngine[Disable Engine Analysis]
    
    MoveError --> LogMove[Log Illegal Move]
    LogMove --> ShowMoveWarning[Show Warning to User]
    ShowMoveWarning --> RejectMove[Reject Move]
    
    ConfigError --> UseDefaults[Use Default Config]
    UseDefaults --> ShowConfigWarning[Show Warning]
    
    ReinitCam --> LogSuccess[Log Recovery]
    ReloadModel --> LogSuccess
    RestartEngine --> LogSuccess
    DisableCam --> LogDegraded[Log Degraded Mode]
    DisableYOLO --> LogDegraded
    DisableEngine --> LogDegraded
    RejectMove --> LogDegraded
    ShowConfigWarning --> LogDegraded
    
    LogSuccess --> Resume([Resume Operation])
    LogDegraded --> Resume
    
    style Error fill:#F44336
    style Resume fill:#4CAF50
    style LogSuccess fill:#4CAF50
```
