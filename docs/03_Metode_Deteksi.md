# Diagram Metode Deteksi

## 1. Metode Color-Based Detection

```mermaid
flowchart TD
    Start([ROI Square]) --> ConvertHSV[Convert BGR to HSV]
    ConvertHSV --> CalcMean[Hitung Mean HSV per Channel]
    
    CalcMean --> CheckOccupancy{V > Threshold?}
    CheckOccupancy -->|Tidak| Empty[Empty Square]
    CheckOccupancy -->|Ya| AnalyzeS[Analisis Saturation]
    
    AnalyzeS --> CheckS{S Value}
    CheckS -->|Low S + High V| White[White Piece]
    CheckS -->|Low S + Low V| Black[Black Piece]
    CheckS -->|High S| ColoredPiece[Colored Piece]
    
    White --> Return([Return: 'white'])
    Black --> Return([Return: 'black'])
    Empty --> ReturnEmpty([Return: 'empty'])
    ColoredPiece --> Return
    
    style Start fill:#4CAF50
    style ConvertHSV fill:#2196F3
    style CheckOccupancy fill:#FF9800
    style Return fill:#4CAF50
    style ReturnEmpty fill:#4CAF50
```

### Parameter Color Detection:
- **HSV Conversion**: BGR → HSV color space
- **Occupancy Threshold**: Default 50 (adjustable)
- **White Detection**: S < 30, V > 180
- **Black Detection**: S < 30, V < 80
- **Empty Detection**: V < Threshold

## 2. Metode YOLO Object Detection

```mermaid
flowchart TD
    Start([Warped Board Image]) --> Preprocess[Preprocessing]
    Preprocess --> RunModel[YOLO Inference]
    
    RunModel --> GetResults[Get Detection Results]
    GetResults --> LoopDetections[Loop Detections]
    
    LoopDetections --> CheckConf{Confidence >= 0.5?}
    CheckConf -->|Tidak| LoopDetections
    CheckConf -->|Ya| GetBBox[Get BBox Coordinates]
    
    GetBBox --> CalcCenter[Hitung Center Point]
    CalcCenter --> DetermineSquare[Tentukan Grid Square]
    
    DetermineSquare --> GetClass[Get Class Name]
    GetClass --> StoreDetection[Store Detection]
    
    StoreDetection --> MoreDetections{More?}
    MoreDetections -->|Ya| LoopDetections
    MoreDetections -->|Tidak| BuildGrid[Build 8x8 Grid]
    
    BuildGrid --> HandleOverlap{Multiple per Square?}
    HandleOverlap -->|Ya| UseHighestConf[Use Highest Confidence]
    HandleOverlap -->|Tidak| AssignDirect[Assign Directly]
    
    UseHighestConf --> Return([Return: YOLO Grid])
    AssignDirect --> Return
    
    style Start fill:#4CAF50
    style RunModel fill:#FF9800
    style BuildGrid fill:#2196F3
    style Return fill:#4CAF50
```

### YOLO Classes:
- white-pawn, white-rook, white-knight, white-bishop, white-queen, white-king
- black-pawn, black-rook, black-knight, black-bishop, black-queen, black-king

### Parameter YOLO Detection:
- **Model**: YOLOv8 Custom Trained
- **Input Size**: 640x640
- **Confidence Threshold**: 0.5 (adjustable)
- **NMS IoU Threshold**: 0.45

## 3. Metode Hybrid (Color + YOLO)

```mermaid
flowchart TD
    Start([Frame Input]) --> ParallelProcess{Run Both Methods}
    
    ParallelProcess -->|Path 1| ColorMethod[Color-Based Detection]
    ParallelProcess -->|Path 2| YOLOMethod[YOLO Detection]
    
    ColorMethod --> ColorGrid[Color Grid 8x8]
    YOLOMethod --> YOLOGrid[YOLO Grid 8x8]
    
    ColorGrid --> Merge[Merge Results]
    YOLOGrid --> Merge
    
    Merge --> LoopSquares[Loop Each Square]
    LoopSquares --> CheckYOLO{YOLO Detected?}
    
    CheckYOLO -->|Ya| UseYOLO[Use YOLO Class]
    CheckYOLO -->|Tidak| UseColor[Use Color Result]
    
    UseYOLO --> FinalGrid[Final Grid State]
    UseColor --> FinalGrid
    
    FinalGrid --> CompareStable{Compare with Stable Grid}
    CompareStable -->|Sama| NoChange[No State Change]
    CompareStable -->|Beda| CountStability[Increment Stability Counter]
    
    CountStability --> CheckThreshold{Counter >= Threshold?}
    CheckThreshold -->|Tidak| WaitMore[Wait More Frames]
    CheckThreshold -->|Ya| ConfirmChange[Confirm Board Change]
    
    ConfirmChange --> InferMove[Infer Chess Move]
    InferMove --> ValidateChess{Valid Chess Move?}
    
    ValidateChess -->|Tidak| RejectChange[Reject & Log Illegal]
    ValidateChess -->|Ya| UpdateGameState[Update Game State]
    
    UpdateGameState --> Return([Emit game_state_updated])
    RejectChange --> ReturnError([Emit illegal_move_attempted])
    NoChange --> ReturnNone([No Signal])
    WaitMore --> ReturnNone
    
    style Start fill:#4CAF50
    style Merge fill:#9C27B0
    style InferMove fill:#2196F3
    style Return fill:#4CAF50
```

### Hybrid Logic:
1. **Priority**: YOLO results take precedence when available
2. **Fallback**: Use color detection when YOLO fails or low confidence
3. **Stability**: Require N consecutive frames (default 5) with same state
4. **Validation**: All moves validated against chess.Board legal moves
