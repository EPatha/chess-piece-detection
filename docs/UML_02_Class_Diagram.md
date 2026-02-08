# UML Class Diagram
## ChessMind Hybrid Vision System

## 1. Class Diagram - Core Components

```mermaid
classDiagram
    class MainWindow {
        -config_manager: ConfigManager
        -camera_thread: CameraThread
        -processing_thread: ProcessingThread
        -hybrid_manager: HybridManager
        -panels: List~Panel~
        +__init__()
        +setup_ui()
        +connect_signals()
        +setup_shortcuts()
        +toggle_camera()
        +new_game()
        +save_pgn()
    }
    
    class CameraThread {
        -cap: cv2.VideoCapture
        -running: bool
        -camera_index: int
        +frame_ready: Signal
        +log_message: Signal
        +run()
        +stop()
        +set_camera(index)
    }
    
    class ProcessingThread {
        -latest_frame: ndarray
        -homography_matrix: ndarray
        -color_detector: ColorDetector
        -yolo_detector: YoloDetector
        -use_yolo: bool
        +processed_frame_ready: Signal
        +board_state_updated: Signal
        +yolo_state_updated: Signal
        +run()
        +process_frame(frame)
        +detect_board(frame)
        +set_calibration_points(points)
    }
    
    class HybridManager {
        -state_manager: StateManager
        -engine_manager: EngineManager
        -audio_manager: AudioManager
        -clock: ChessClock
        -current_stable_grid: List
        -stability_counter: int
        +game_state_updated: Signal
        +evaluation_updated: Signal
        +best_move_found: Signal
        +update_board_state(grid)
        +infer_move(old_grid, new_grid)
        +reset_game()
        +sync_board_from_camera()
    }
    
    class StateManager {
        -board: chess.Board
        -move_history: List~str~
        +reset()
        +make_move(uci_move)
        +get_fen()
        +get_pgn()
        +set_custom_position(fen)
    }
    
    class EngineManager {
        -engine: chess.engine.SimpleEngine
        -engine_path: str
        +evaluation_updated: Signal
        +best_move_found: Signal
        +start_engine()
        +analyze_position(fen, depth)
        +stop_analysis()
        +shutdown()
    }
    
    class AudioManager {
        -enabled: bool
        -system: str
        +speak(text)
        +announce_move(move_uci, board)
        +play_sound(sound_type)
    }
    
    class ChessClock {
        -white_time: float
        -black_time: float
        -increment: float
        -is_white_turn: bool
        +time_updated: Signal
        +flag_fall: Signal
        +start_game(time_control, increment)
        +tick()
        +switch_turn()
        +stop()
    }
    
    class ColorDetector {
        -occupancy_threshold: int
        +detect(roi)
        -analyze_hsv(roi)
        -classify_color(hsv_mean)
    }
    
    class YoloDetector {
        -model: YOLO
        -model_path: str
        -class_names: dict
        +load_model(path)
        +detect(frame, conf_threshold)
    }
    
    class ConfigManager {
        -config: dict
        -config_path: str
        +config_changed: Signal
        +load_config()
        +save_config()
        +get(key, default)
        +set(key, value)
    }
    
    MainWindow --> CameraThread
    MainWindow --> ProcessingThread
    MainWindow --> HybridManager
    MainWindow --> ConfigManager
    
    ProcessingThread --> ColorDetector
    ProcessingThread --> YoloDetector
    
    HybridManager --> StateManager
    HybridManager --> EngineManager
    HybridManager --> AudioManager
    HybridManager --> ChessClock
```

## 2. Class Diagram - UI Panels

```mermaid
classDiagram
    class Panel {
        <<abstract>>
        #layout: QLayout
        +setup_ui()
        +update_display()
    }
    
    class RawCameraPanel {
        -image_label: QLabel
        -debug_points: List
        +update_frame(frame)
        +set_debug_points(points)
        -draw_debug_overlay(frame)
    }
    
    class CroppedCameraPanel {
        -image_label: QLabel
        +update_frame(warped)
    }
    
    class BoardViewPanel {
        -board_widget: QWidget
        -fen_label: QLabel
        -best_move_arrow: Arrow
        +update_fen(fen, move)
        +set_best_move(uci_move)
        -draw_board()
        -draw_pieces()
    }
    
    class PieceStatusPanel {
        -turn_label: QLabel
        -material_label: QLabel
        -white_clock: QLabel
        -black_clock: QLabel
        +update_game_info(fen)
        +update_clock(white_time, black_time)
        -calculate_material(fen)
    }
    
    class HistoryPanel {
        -moves_text: QTextEdit
        +update_history(pgn)
        -format_pgn(pgn)
    }
    
    class EvaluationPanel {
        -eval_label: QLabel
        -eval_bar: QProgressBar
        +update_evaluation(eval_str)
        -parse_evaluation(eval)
    }
    
    class LogViewPanel {
        -log_text: QTextEdit
        -filter_combo: QComboBox
        +add_entry(level, message)
        -get_color_for_level(level)
        -apply_filter(level)
    }
    
    Panel <|-- RawCameraPanel
    Panel <|-- CroppedCameraPanel
    Panel <|-- BoardViewPanel
    Panel <|-- PieceStatusPanel
    Panel <|-- HistoryPanel
    Panel <|-- EvaluationPanel
    Panel <|-- LogViewPanel
```

## 3. Class Diagram - Detection Strategy Pattern

```mermaid
classDiagram
    class DetectionStrategy {
        <<interface>>
        +detect(input)*
    }
    
    class ColorDetector {
        -occupancy_threshold: int
        -hsv_ranges: dict
        +detect(roi): str
        +set_threshold(value)
        -convert_to_hsv(roi)
        -calculate_mean(hsv)
        -classify(h, s, v): str
    }
    
    class YoloDetector {
        -model: YOLO
        -conf_threshold: float
        -iou_threshold: float
        -class_names: dict
        +detect(frame, conf): List
        +load_model(path): bool
        -preprocess(frame)
        -postprocess(results)
    }
    
    class HybridDetector {
        -color_detector: ColorDetector
        -yolo_detector: YoloDetector
        -priority: str
        +detect(frame): Grid
        -merge_results(color_grid, yolo_grid)
        -assign_to_grid(detections)
    }
    
    DetectionStrategy <|.. ColorDetector
    DetectionStrategy <|.. YoloDetector
    HybridDetector --> ColorDetector
    HybridDetector --> YoloDetector
```

## 4. Class Diagram - State Pattern

```mermaid
classDiagram
    class GameState {
        <<abstract>>
        +handle_input()*
        +update()*
    }
    
    class IdleState {
        +handle_input()
        +update()
    }
    
    class CalibratingState {
        -points_collected: int
        +handle_input()
        +update()
        +add_point(x, y)
    }
    
    class PlayingState {
        -is_monitoring: bool
        +handle_input()
        +update()
        +process_move()
    }
    
    class GameOverState {
        -result: str
        +handle_input()
        +update()
        +show_result()
    }
    
    class StateContext {
        -current_state: GameState
        +set_state(state)
        +handle_input()
        +update()
    }
    
    GameState <|-- IdleState
    GameState <|-- CalibratingState
    GameState <|-- PlayingState
    GameState <|-- GameOverState
    
    StateContext --> GameState
```

## 5. Class Diagram - Complete Architecture

```plantuml
@startuml
skinparam classAttributeIconSize 0

package "UI Layer" {
    class MainWindow {
        -config_manager: ConfigManager
        -camera_thread: CameraThread
        -processing_thread: ProcessingThread
        -hybrid_manager: HybridManager
        +__init__()
        +setup_ui()
        +connect_signals()
    }
    
    abstract class Panel {
        #layout: QLayout
        +setup_ui()
        +update_display()
    }
    
    class RawCameraPanel
    class CroppedCameraPanel
    class BoardViewPanel
    class PieceStatusPanel
    
    Panel <|-- RawCameraPanel
    Panel <|-- CroppedCameraPanel
    Panel <|-- BoardViewPanel
    Panel <|-- PieceStatusPanel
    
    MainWindow *-- Panel
}

package "Core Layer" {
    class HybridManager {
        -state_manager: StateManager
        -engine_manager: EngineManager
        -audio_manager: AudioManager
        -stability_counter: int
        +update_board_state(grid)
        +infer_move(old, new)
    }
    
    class StateManager {
        -board: chess.Board
        -move_history: List
        +make_move(uci)
        +get_fen(): str
    }
    
    class EngineManager {
        -engine: SimpleEngine
        +analyze_position(fen)
    }
    
    class AudioManager {
        +speak(text)
        +announce_move(uci)
    }
    
    class ChessClock {
        -white_time: float
        -black_time: float
        +tick()
        +switch_turn()
    }
    
    HybridManager *-- StateManager
    HybridManager *-- EngineManager
    HybridManager *-- AudioManager
    HybridManager *-- ChessClock
}

package "Processing Layer" {
    class CameraThread {
        -cap: VideoCapture
        +run()
        +stop()
    }
    
    class ProcessingThread {
        -color_detector: ColorDetector
        -yolo_detector: YoloDetector
        +process_frame(frame)
        +detect_board(frame)
    }
    
    class ColorDetector {
        +detect(roi): str
    }
    
    class YoloDetector {
        -model: YOLO
        +detect(frame): List
    }
    
    ProcessingThread *-- ColorDetector
    ProcessingThread *-- YoloDetector
}

package "Configuration Layer" {
    class ConfigManager {
        -config: dict
        +load_config()
        +save_config()
        +get(key): Any
        +set(key, value)
    }
}

MainWindow --> CameraThread
MainWindow --> ProcessingThread
MainWindow --> HybridManager
MainWindow --> ConfigManager

CameraThread --> ProcessingThread : frame_ready
ProcessingThread --> HybridManager : board_state_updated
HybridManager --> MainWindow : game_state_updated

@enduml
```

## 6. Relationship Summary

### Associations
- MainWindow **uses** CameraThread, ProcessingThread, HybridManager
- ProcessingThread **uses** ColorDetector, YoloDetector
- HybridManager **uses** StateManager, EngineManager, AudioManager, ChessClock

### Compositions
- MainWindow **contains** multiple Panels
- HybridManager **owns** StateManager, EngineManager, AudioManager, ChessClock
- ProcessingThread **owns** ColorDetector, YoloDetector

### Dependencies
- All components **depend on** ConfigManager for settings
- UI Panels **depend on** Signals from Core components
- StateManager **depends on** python-chess library

### Inheritance
- All Panel classes **inherit from** base Panel class
- ColorDetector, YoloDetector **implement** DetectionStrategy interface
- GameState classes **inherit from** GameState abstract class
