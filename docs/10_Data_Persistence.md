# Database & Data Persistence

## 1. Data Storage Architecture

```mermaid
flowchart TD
    subgraph "Data Sources"
        Game[Game State]
        Config[Configuration]
        History[Move History]
        Stats[Statistics]
    end
    
    subgraph "Storage Layer"
        PGNFiles[PGN Files]
        ConfigJSON[config.json]
        LogFiles[Log Files]
        CacheData[Cache Data]
    end
    
    subgraph "Persistence Manager"
        SaveGame[Save Game]
        LoadGame[Load Game]
        ExportPGN[Export PGN]
        SaveConfig[Save Config]
    end
    
    Game --> SaveGame
    History --> ExportPGN
    Config --> SaveConfig
    
    SaveGame --> PGNFiles
    ExportPGN --> PGNFiles
    SaveConfig --> ConfigJSON
    Stats --> LogFiles
    
    PGNFiles --> LoadGame
    ConfigJSON --> Config
    
    style Game fill:#4CAF50
    style SaveGame fill:#2196F3
    style PGNFiles fill:#FF9800
```

## 2. PGN Export Flow

```mermaid
flowchart TD
    Start([Game Finished]) --> BuildPGN[Build PGN Object]
    
    BuildPGN --> SetHeaders[Set Headers:<br/>- Event<br/>- Date<br/>- White<br/>- Black<br/>- Result]
    
    SetHeaders --> LoopMoves[Loop Move History]
    LoopMoves --> ConvertUCI[Convert UCI to SAN]
    ConvertUCI --> AddMove[Add Move to Game]
    
    AddMove --> MoreMoves{More Moves?}
    MoreMoves -->|Yes| LoopMoves
    MoreMoves -->|No| GenerateString[Generate PGN String]
    
    GenerateString --> CreateFilename[Create Filename:<br/>game_YYYYMMDD_HHMMSS.pgn]
    CreateFilename --> WriteFile[Write to File]
    
    WriteFile --> Success([PGN Saved])
    
    style Start fill:#4CAF50
    style GenerateString fill:#2196F3
    style Success fill:#4CAF50
```

### PGN File Format

```pgn
[Event "ChessMind Game"]
[Site "ChessMind Hybrid System"]
[Date "2025.01.26"]
[Round "1"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 
6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7
...
1-0
```

### Code: PGN Export

```python
import chess.pgn
from datetime import datetime

class PGNExporter:
    def __init__(self, state_manager):
        self.state_manager = state_manager
    
    def export_game(self, white_name="Player 1", black_name="Player 2"):
        """Export current game to PGN file"""
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = "ChessMind Game"
        game.headers["Site"] = "ChessMind Hybrid System"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["White"] = white_name
        game.headers["Black"] = black_name
        
        # Determine result
        board = self.state_manager.board
        if board.is_checkmate():
            result = "0-1" if board.turn == chess.WHITE else "1-0"
        elif board.is_stalemate() or board.is_insufficient_material():
            result = "1/2-1/2"
        else:
            result = "*"
        game.headers["Result"] = result
        
        # Add moves
        node = game
        board = chess.Board()
        for uci_move in self.state_manager.move_history:
            move = chess.Move.from_uci(uci_move)
            node = node.add_variation(move)
            board.push(move)
        
        # Generate PGN string
        pgn_string = str(game)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_{timestamp}.pgn"
        
        with open(filename, 'w') as f:
            f.write(pgn_string)
        
        return filename
```

## 3. Configuration Management

```mermaid
flowchart TD
    Start([Config Change]) --> ValidateInput{Valid Input?}
    
    ValidateInput -->|No| ShowError[Show Validation Error]
    ValidateInput -->|Yes| UpdateMemory[Update In-Memory Config]
    
    ShowError --> End([Rejected])
    
    UpdateMemory --> SerializeJSON[Serialize to JSON]
    SerializeJSON --> WriteFile[Write to config.json]
    
    WriteFile --> Success{Write Success?}
    Success -->|No| Rollback[Rollback to Previous]
    Success -->|Yes| EmitSignal[Emit config_changed Signal]
    
    Rollback --> ShowError
    EmitSignal --> ApplyChanges[Apply Changes to Components]
    
    ApplyChanges --> Complete([Config Updated])
    
    style Start fill:#4CAF50
    style UpdateMemory fill:#2196F3
    style Complete fill:#4CAF50
    style ShowError fill:#F44336
```

### Code: Config Manager

```python
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal

class ConfigManager(QObject):
    config_changed = pyqtSignal(str, object)  # key, value
    
    def __init__(self, config_path="config.json"):
        super().__init__()
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            # Create from example
            if os.path.exists(".config.json.example"):
                with open(".config.json.example", 'r') as f:
                    self.config = json.load(f)
                self.save_config()
            else:
                self.config = self.get_default_config()
                self.save_config()
        else:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set configuration value and save"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the correct nested level
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save and emit signal
        if self.save_config():
            self.config_changed.emit(key, value)
            return True
        
        return False
    
    def get_default_config(self):
        """Return default configuration"""
        return {
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
                "enabled": True,
                "voice": "default",
                "rate": 175
            },
            "features": {
                "game_mode": True,
                "auto_detect": False,
                "hybrid_mode": True,
                "show_debug": False
            },
            "processing": {
                "stability_threshold": 5,
                "occupancy_threshold": 50,
                "canny_lower": 50,
                "canny_upper": 150
            }
        }
```

## 4. Statistics & Analytics

```mermaid
flowchart TD
    Start([Game Session]) --> CollectData[Collect Session Data]
    
    CollectData --> TrackMetrics[Track Metrics:<br/>- Total Games<br/>- Win Rate<br/>- Average Time<br/>- Detection Accuracy]
    
    TrackMetrics --> UpdateStats[Update Statistics]
    UpdateStats --> CheckMilestone{Milestone Reached?}
    
    CheckMilestone -->|Yes| TriggerEvent[Trigger Achievement]
    CheckMilestone -->|No| Continue[Continue Tracking]
    
    TriggerEvent --> Continue
    Continue --> SessionEnd{Session End?}
    
    SessionEnd -->|No| CollectData
    SessionEnd -->|Yes| SaveStats[Save to stats.json]
    
    SaveStats --> GenerateReport[Generate Session Report]
    GenerateReport --> End([Session Complete])
    
    style Start fill:#4CAF50
    style TrackMetrics fill:#2196F3
    style End fill:#4CAF50
```

### Statistics Data Structure

```json
{
  "session_id": "uuid-here",
  "start_time": "2025-01-26T15:30:00",
  "end_time": "2025-01-26T16:45:00",
  "games_played": 5,
  "statistics": {
    "total_moves": 234,
    "average_move_time": 12.5,
    "detection_accuracy": 0.94,
    "false_positives": 3,
    "illegal_moves_attempted": 1,
    "engine_evaluations": 150
  },
  "performance": {
    "average_fps": 28.5,
    "average_latency_ms": 75,
    "peak_memory_mb": 420,
    "average_cpu_percent": 58
  }
}
```
