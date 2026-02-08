# Deployment & Configuration

## 1. Deployment Architecture

```mermaid
flowchart TD
    subgraph "Development Environment"
        Dev[Developer Machine]
        Git[Git Repository]
        Dev --> Git
    end
    
    subgraph "Build Process"
        Clone[Clone Repository]
        InstallDeps[Install Dependencies]
        ConfigSetup[Setup Configuration]
        TestRun[Run Tests]
        
        Git --> Clone
        Clone --> InstallDeps
        InstallDeps --> ConfigSetup
        ConfigSetup --> TestRun
    end
    
    subgraph "Production Deployment"
        App[ChessMind Application]
        Camera[Camera Device]
        Stockfish[Stockfish Engine]
        ModelFile[YOLO Model File]
        
        TestRun --> App
        Camera --> App
        Stockfish --> App
        ModelFile --> App
    end
    
    subgraph "User Environment"
        macOS[macOS System]
        Linux[Linux System]
        
        App --> macOS
        App --> Linux
    end
    
    style Dev fill:#4CAF50
    style App fill:#2196F3
    style macOS fill:#9C27B0
    style Linux fill:#FF9800
```

## 2. Configuration Flow

```mermaid
flowchart TD
    Start([Application Start]) --> CheckConfig{config.json exists?}
    
    CheckConfig -->|No| CreateDefault[Create from .config.json.example]
    CheckConfig -->|Yes| LoadConfig[Load config.json]
    
    CreateDefault --> ParseConfig[Parse Configuration]
    LoadConfig --> ParseConfig
    
    ParseConfig --> ValidateConfig{Valid Config?}
    ValidateConfig -->|No| ShowError[Show Error Dialog]
    ValidateConfig -->|Yes| ApplySettings[Apply Settings]
    
    ShowError --> UseDefaults[Use Default Settings]
    UseDefaults --> ApplySettings
    
    ApplySettings --> InitCamera[Initialize Camera:<br/>- camera.source<br/>- camera.resolution<br/>- camera.fps]
    
    InitCamera --> InitYOLO[Initialize YOLO:<br/>- yolo.model_path<br/>- yolo.confidence_threshold]
    
    InitYOLO --> InitEngine[Initialize Engine:<br/>- engine.path<br/>- engine.threads<br/>- engine.depth]
    
    InitEngine --> InitAudio[Initialize Audio:<br/>- audio.enabled<br/>- audio.voice]
    
    InitAudio --> InitFeatures[Initialize Features:<br/>- game_mode<br/>- auto_detect<br/>- hybrid_mode]
    
    InitFeatures --> Ready([Application Ready])
    
    style Start fill:#4CAF50
    style ApplySettings fill:#2196F3
    style Ready fill:#4CAF50
```

### Configuration File Structure

```json
{
  "camera": {
    "source": 0,
    "resolution": [1920, 1080],
    "fps": 30
  },
  "yolo": {
    "model_path": "models/chess_yolo.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45
  },
  "engine": {
    "path": "/usr/local/bin/stockfish",
    "threads": 2,
    "hash": 128,
    "depth": 15
  },
  "audio": {
    "enabled": true,
    "voice": "default",
    "rate": 175
  },
  "features": {
    "game_mode": true,
    "auto_detect": false,
    "hybrid_mode": true,
    "show_debug": false
  },
  "processing": {
    "stability_threshold": 5,
    "occupancy_threshold": 50,
    "canny_lower": 50,
    "canny_upper": 150
  }
}
```

## 3. Installation & Setup Process

```mermaid
flowchart TD
    Start([Start Installation]) --> CheckPython{Python 3.8+ installed?}
    
    CheckPython -->|No| InstallPython[Install Python 3.8+]
    CheckPython -->|Yes| CloneRepo[Clone Git Repository]
    
    InstallPython --> CloneRepo
    CloneRepo --> CreateVenv[Create Virtual Environment:<br/>python3 -m venv venv]
    
    CreateVenv --> ActivateVenv[Activate venv:<br/>source venv/bin/activate]
    ActivateVenv --> InstallReq[Install Requirements:<br/>pip install -r requirements.txt]
    
    InstallReq --> CheckOS{Operating System?}
    
    CheckOS -->|macOS| InstallStockfishMac[Install Stockfish:<br/>brew install stockfish]
    CheckOS -->|Linux| InstallStockfishLinux[Install Stockfish:<br/>apt install stockfish]
    
    InstallStockfishMac --> DownloadModel[Download YOLO Model]
    InstallStockfishLinux --> DownloadModel
    
    DownloadModel --> SetupConfig[Setup Configuration:<br/>cp .config.json.example config.json]
    SetupConfig --> EditConfig[Edit config.json:<br/>Set paths and parameters]
    
    EditConfig --> TestCamera[Test Camera:<br/>python check_cameras.py]
    TestCamera --> CameraOK{Camera Working?}
    
    CameraOK -->|No| FixCamera[Fix Camera Permissions]
    CameraOK -->|Yes| TestModel[Test YOLO Model:<br/>python test_chess_model.py]
    
    FixCamera --> TestCamera
    TestModel --> ModelOK{Model Loading?}
    
    ModelOK -->|No| RedownloadModel[Re-download Model]
    ModelOK -->|Yes| RunApp[Run Application:<br/>python chess_mind_app.py]
    
    RedownloadModel --> TestModel
    RunApp --> Success([Installation Complete])
    
    style Start fill:#4CAF50
    style Success fill:#4CAF50
    style InstallReq fill:#2196F3
    style RunApp fill:#9C27B0
```

### Installation Commands

```bash
# 1. Clone Repository
git clone https://github.com/your-repo/chess-mind-hybrid.git
cd chess-mind-hybrid/chess_hybrid

# 2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Stockfish
# macOS:
brew install stockfish

# Linux:
sudo apt update
sudo apt install stockfish

# 5. Download YOLO Model
python download_model.py

# 6. Setup Configuration
cp .config.json.example config.json
# Edit config.json as needed

# 7. Test Components
python check_cameras.py
python test_chess_model.py

# 8. Run Application
python chess_mind_app.py
```

## 4. Error Handling & Logging

```mermaid
flowchart TD
    Error([Error Occurred]) --> Classify{Error Type?}
    
    Classify -->|Camera Error| CameraHandle[Handle Camera Error]
    Classify -->|Model Error| ModelHandle[Handle Model Error]
    Classify -->|Engine Error| EngineHandle[Handle Engine Error]
    Classify -->|Runtime Error| RuntimeHandle[Handle Runtime Error]
    
    CameraHandle --> LogError[Log to File]
    ModelHandle --> LogError
    EngineHandle --> LogError
    RuntimeHandle --> LogError
    
    LogError --> CheckSeverity{Severity?}
    
    CheckSeverity -->|Critical| ShowDialog[Show Error Dialog]
    CheckSeverity -->|Warning| LogOnly[Log Only]
    CheckSeverity -->|Info| LogOnly
    
    ShowDialog --> OfferRetry{Recoverable?}
    OfferRetry -->|Yes| Retry[Offer Retry Option]
    OfferRetry -->|No| Shutdown[Graceful Shutdown]
    
    Retry --> UserChoice{User Retries?}
    UserChoice -->|Yes| RetryOperation[Retry Operation]
    UserChoice -->|No| Continue[Continue with Degraded Mode]
    
    RetryOperation --> Success{Success?}
    Success -->|Yes| Resume([Resume Normal Operation])
    Success -->|No| ShowDialog
    
    LogOnly --> Resume
    Continue --> Resume
    
    style Error fill:#F44336
    style LogError fill:#FF9800
    style Resume fill:#4CAF50
    style Shutdown fill:#F44336
```

### Log Format

```python
# Log Entry Format
[TIMESTAMP] [LEVEL] [COMPONENT] Message

# Example:
[2025-01-26 15:30:45] [INFO] [CameraThread] Camera initialized successfully
[2025-01-26 15:30:46] [WARNING] [YoloDetector] Model confidence below threshold
[2025-01-26 15:30:50] [ERROR] [EngineManager] Failed to connect to Stockfish
[2025-01-26 15:31:00] [DEBUG] [HybridManager] Stability counter: 3/5
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures that don't stop the app)
- **CRITICAL**: Critical errors (app must shut down)
