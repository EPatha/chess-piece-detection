# Diagram State Management & Game Logic

## 1. State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Initializing: App Start
    Initializing --> Idle: Components Ready
    
    Idle --> Calibrating: Manual/Auto Calibration
    Calibrating --> Idle: Calibration Complete
    
    Idle --> GameReady: Load YOLO Model
    GameReady --> Playing: Start Game
    
    Playing --> WaitingMove: Stable Board
    WaitingMove --> DetectingChange: Board Changed
    DetectingChange --> ValidatingMove: Change Stable (5 frames)
    
    ValidatingMove --> WaitingMove: Valid Move
    ValidatingMove --> ErrorState: Illegal Move
    ErrorState --> WaitingMove: User Corrects
    
    WaitingMove --> Analyzing: Engine Analysis
    Analyzing --> WaitingMove: Analysis Complete
    
    WaitingMove --> GameOver: Checkmate/Stalemate
    GameOver --> Idle: Reset Game
    
    Playing --> Idle: Stop Game
    Idle --> [*]: Exit App
```

## 2. Move Inference Algorithm

```mermaid
flowchart TD
    Start([New Grid State]) --> ComparePrev[Compare dengan Previous Grid]
    ComparePrev --> FindDiff[Temukan Perbedaan]
    
    FindDiff --> CountChanges{Jumlah Perubahan?}
    CountChanges -->|0| NoMove([No Move])
    CountChanges -->|1| OneChange[1 Square Changed]
    CountChanges -->|2| TwoChanges[2 Squares Changed]
    CountChanges -->|>2| MultiChange[Multi-Square Change]
    
    OneChange --> CheckNewPiece{Piece Muncul/Hilang?}
    CheckNewPiece -->|Muncul| Promotion[Pawn Promotion]
    CheckNewPiece -->|Hilang| Capture[Piece Captured]
    
    TwoChanges --> AnalyzePattern[Analisis Pattern]
    AnalyzePattern --> CheckEmpty{Satu Empty, Satu Filled?}
    CheckEmpty -->|Ya| NormalMove[Normal Move]
    CheckEmpty -->|Tidak| SpecialMove{Special Move?}
    
    SpecialMove --> CheckCastling{Castling Pattern?}
    SpecialMove --> CheckEnPassant{En Passant Pattern?}
    
    CheckCastling -->|Ya| Castling[Castling Move]
    CheckCastling -->|Tidak| Unknown1[Unknown Pattern]
    
    CheckEnPassant -->|Ya| EnPassant[En Passant Capture]
    CheckEnPassant -->|Tidak| Unknown2[Unknown Pattern]
    
    MultiChange --> CheckFour{4 Squares?}
    CheckFour -->|Ya| CastlingCheck[Verify Castling]
    CheckFour -->|Tidak| CheckThree{3 Squares?}
    
    CheckThree -->|Ya| EnPassantCheck[Verify En Passant]
    CheckThree -->|Tidak| UnknownMulti[Complex Change]
    
    NormalMove --> BuildUCI[Build UCI Move]
    Capture --> BuildUCI
    Promotion --> PromptUser[Prompt for Piece]
    Castling --> BuildUCI
    EnPassant --> BuildUCI
    
    PromptUser --> BuildUCI
    BuildUCI --> ValidateChess{chess.Board.is_legal?}
    
    ValidateChess -->|Ya| ApplyMove[Apply Move]
    ValidateChess -->|Tidak| Illegal[Illegal Move]
    
    ApplyMove --> UpdateFEN[Update FEN]
    UpdateFEN --> SwitchTurn[Switch Turn]
    SwitchTurn --> ClockUpdate[Update Clock]
    ClockUpdate --> Success([Move Applied])
    
    Illegal --> EmitError([Emit Error Signal])
    Unknown1 --> EmitError
    Unknown2 --> EmitError
    UnknownMulti --> EmitError
    
    style Start fill:#4CAF50
    style BuildUCI fill:#2196F3
    style ValidateChess fill:#FF9800
    style Success fill:#4CAF50
    style EmitError fill:#F44336
```

## 3. Stability Checking Mechanism

```mermaid
flowchart TD
    NewGrid([New Grid State]) --> Compare{Same as Current Stable?}
    
    Compare -->|Ya| ResetCounter[Reset Stability Counter = 0]
    Compare -->|Tidak| CheckPending{Same as Pending Grid?}
    
    CheckPending -->|Tidak| SetPending[Set as Pending Grid]
    CheckPending -->|Ya| IncrementCounter[Stability Counter++]
    
    SetPending --> Counter1[Counter = 1]
    Counter1 --> Wait([Wait Next Frame])
    
    IncrementCounter --> CheckThreshold{Counter >= Threshold?}
    CheckThreshold -->|Tidak| Wait
    CheckThreshold -->|Ya| ConfirmStable[Confirm Stable State]
    
    ConfirmStable --> UpdateStable[Update Current Stable Grid]
    UpdateStable --> InferMove[Infer Chess Move]
    InferMove --> ResetCounter
    
    ResetCounter --> End([Continue Processing])
    Wait --> End
    
    style NewGrid fill:#4CAF50
    style ConfirmStable fill:#2196F3
    style InferMove fill:#FF9800
    style End fill:#4CAF50
```

### Stability Parameters:
- **Stability Threshold**: 5 frames (default)
- **Purpose**: Menghindari false positive dari noise/gerakan tangan
- **Frame Rate**: ~30 FPS, jadi ~166ms delay
