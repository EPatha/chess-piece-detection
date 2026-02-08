# Metode Pengujian (Testing Methods)

## 1. Unit Testing Flow

```mermaid
flowchart TD
    Start([Unit Test Suite]) --> TestDetector[Test YoloDetector]
    Start --> TestColor[Test ColorDetector]
    Start --> TestState[Test StateManager]
    Start --> TestEngine[Test EngineManager]
    
    TestDetector --> LoadModel[Load Test Model]
    LoadModel --> TestInference[Test Inference]
    TestInference --> ValidateOutput{Output Valid?}
    ValidateOutput -->|Ya| Pass1[✓ Pass]
    ValidateOutput -->|Tidak| Fail1[✗ Fail]
    
    TestColor --> TestHSV[Test HSV Conversion]
    TestHSV --> TestThreshold[Test Threshold Logic]
    TestThreshold --> ValidateColor{Classification Correct?}
    ValidateColor -->|Ya| Pass2[✓ Pass]
    ValidateColor -->|Tidak| Fail2[✗ Fail]
    
    TestState --> TestFEN[Test FEN Parsing]
    TestFEN --> TestMoves[Test Move Application]
    TestMoves --> TestValidation[Test Move Validation]
    TestValidation --> ValidateState{State Correct?}
    ValidateState -->|Ya| Pass3[✓ Pass]
    ValidateState -->|Tidak| Fail3[✗ Fail]
    
    TestEngine --> TestStockfish[Test Stockfish Connection]
    TestStockfish --> TestAnalysis[Test Position Analysis]
    TestAnalysis --> ValidateEval{Evaluation Valid?}
    ValidateEval -->|Ya| Pass4[✓ Pass]
    ValidateEval -->|Tidak| Fail4[✗ Fail]
    
    Pass1 --> Report[Generate Test Report]
    Pass2 --> Report
    Pass3 --> Report
    Pass4 --> Report
    Fail1 --> Report
    Fail2 --> Report
    Fail3 --> Report
    Fail4 --> Report
    
    Report --> End([Test Complete])
    
    style Start fill:#4CAF50
    style Pass1 fill:#4CAF50
    style Pass2 fill:#4CAF50
    style Pass3 fill:#4CAF50
    style Pass4 fill:#4CAF50
    style Fail1 fill:#F44336
    style Fail2 fill:#F44336
    style Fail3 fill:#F44336
    style Fail4 fill:#F44336
```

## 2. Integration Testing Flow

```mermaid
flowchart TD
    Start([Integration Test]) --> SetupEnv[Setup Test Environment]
    SetupEnv --> InitComponents[Initialize All Components]
    
    InitComponents --> TestCameraFlow[Test Camera → Processing Flow]
    TestCameraFlow --> MockCamera[Mock Camera Input]
    MockCamera --> CheckProcessing{Processing Thread Works?}
    CheckProcessing -->|Tidak| Fail1[✗ Integration Fail]
    CheckProcessing -->|Ya| TestHybridFlow[Test Processing → Hybrid Flow]
    
    TestHybridFlow --> MockGrid[Mock Grid State]
    MockGrid --> CheckHybrid{Hybrid Manager Works?}
    CheckHybrid -->|Tidak| Fail2[✗ Integration Fail]
    CheckHybrid -->|Ya| TestUIFlow[Test Hybrid → UI Flow]
    
    TestUIFlow --> CheckSignals{Signals Emitted?}
    CheckSignals -->|Tidak| Fail3[✗ Integration Fail]
    CheckSignals -->|Ya| TestEngineFlow[Test Engine Integration]
    
    TestEngineFlow --> MockFEN[Mock FEN Position]
    MockFEN --> CheckEngine{Engine Responds?}
    CheckEngine -->|Tidak| Fail4[✗ Integration Fail]
    CheckEngine -->|Ya| TestEndToEnd[End-to-End Test]
    
    TestEndToEnd --> SimulateGame[Simulate Full Game]
    SimulateGame --> CheckComplete{All Features Work?}
    CheckComplete -->|Ya| Pass[✓ All Integration Pass]
    CheckComplete -->|Tidak| Fail5[✗ Integration Fail]
    
    Fail1 --> Report[Test Report]
    Fail2 --> Report
    Fail3 --> Report
    Fail4 --> Report
    Fail5 --> Report
    Pass --> Report
    
    Report --> End([Test Complete])
    
    style Start fill:#4CAF50
    style Pass fill:#4CAF50
    style Fail1 fill:#F44336
    style Fail2 fill:#F44336
    style Fail3 fill:#F44336
    style Fail4 fill:#F44336
    style Fail5 fill:#F44336
```

## 3. Accuracy Testing (Detection)

```mermaid
flowchart TD
    Start([Accuracy Test]) --> PrepareDataset[Prepare Test Dataset]
    PrepareDataset --> LoadImages[Load 100 Test Images]
    
    LoadImages --> LoadGroundTruth[Load Ground Truth Annotations]
    LoadGroundTruth --> InitMetrics[Initialize Metrics: TP, FP, FN, TN]
    
    InitMetrics --> LoopImages[Loop Each Image]
    LoopImages --> RunDetection[Run Detection Algorithm]
    
    RunDetection --> CompareResults[Compare with Ground Truth]
    CompareResults --> CountMetrics[Count TP, FP, FN, TN]
    
    CountMetrics --> MoreImages{More Images?}
    MoreImages -->|Ya| LoopImages
    MoreImages -->|Tidak| Calculate[Calculate Metrics]
    
    Calculate --> CalcPrecision[Precision = TP/(TP+FP)]
    CalcPrecision --> CalcRecall[Recall = TP/(TP+FN)]
    CalcRecall --> CalcF1[F1-Score = 2×(P×R)/(P+R)]
    CalcF1 --> CalcAccuracy[Accuracy = (TP+TN)/Total]
    
    CalcAccuracy --> CheckTarget{Accuracy >= Target?}
    CheckTarget -->|Ya, >= 90%| Pass[✓ Test Pass]
    CheckTarget -->|Tidak, < 90%| Fail[✗ Test Fail - Needs Improvement]
    
    Pass --> GenerateReport[Generate Detailed Report]
    Fail --> GenerateReport
    
    GenerateReport --> SaveReport[Save Report & Confusion Matrix]
    SaveReport --> End([Test Complete])
    
    style Start fill:#4CAF50
    style Pass fill:#4CAF50
    style Fail fill:#F44336
    style Calculate fill:#2196F3
```

### Metrics Definition:
- **True Positive (TP)**: Deteksi benar, piece yang terdeteksi sesuai ground truth
- **False Positive (FP)**: Deteksi salah, mendeteksi piece yang tidak ada
- **False Negative (FN)**: Miss detection, piece ada tapi tidak terdeteksi
- **True Negative (TN)**: Kotak kosong terdeteksi dengan benar

### Target Metrics:
- **Precision**: ≥ 90%
- **Recall**: ≥ 85%
- **F1-Score**: ≥ 87%
- **Accuracy**: ≥ 90%

## 4. Performance Testing

```mermaid
flowchart TD
    Start([Performance Test]) --> SetupMonitor[Setup Performance Monitor]
    SetupMonitor --> TestFPS[Test Frame Rate]
    
    TestFPS --> RunCamera[Run Camera Thread]
    RunCamera --> MeasureFPS[Measure FPS for 60s]
    MeasureFPS --> CheckFPS{FPS >= 25?}
    CheckFPS -->|Ya| PassFPS[✓ FPS OK]
    CheckFPS -->|Tidak| FailFPS[✗ FPS Low]
    
    PassFPS --> TestLatency[Test Detection Latency]
    FailFPS --> TestLatency
    
    TestLatency --> MeasureTime[Measure Processing Time]
    MeasureTime --> CheckLatency{Latency < 100ms?}
    CheckLatency -->|Ya| PassLatency[✓ Latency OK]
    CheckLatency -->|Tidak| FailLatency[✗ Latency High]
    
    PassLatency --> TestMemory[Test Memory Usage]
    FailLatency --> TestMemory
    
    TestMemory --> MonitorRAM[Monitor RAM Usage]
    MonitorRAM --> CheckMemory{Memory < 500MB?}
    CheckMemory -->|Ya| PassMemory[✓ Memory OK]
    CheckMemory -->|Tidak| FailMemory[✗ Memory High]
    
    PassMemory --> TestCPU[Test CPU Usage]
    FailMemory --> TestCPU
    
    TestCPU --> MonitorCPU[Monitor CPU %]
    MonitorCPU --> CheckCPU{CPU < 70%?}
    CheckCPU -->|Ya| PassCPU[✓ CPU OK]
    CheckCPU -->|Tidak| FailCPU[✗ CPU High]
    
    PassCPU --> Report[Generate Performance Report]
    FailCPU --> Report
    
    Report --> End([Test Complete])
    
    style Start fill:#4CAF50
    style PassFPS fill:#4CAF50
    style PassLatency fill:#4CAF50
    style PassMemory fill:#4CAF50
    style PassCPU fill:#4CAF50
    style FailFPS fill:#F44336
    style FailLatency fill:#F44336
    style FailMemory fill:#F44336
    style FailCPU fill:#F44336
```

### Performance Targets:
- **Frame Rate**: ≥ 25 FPS
- **Processing Latency**: < 100ms per frame
- **Memory Usage**: < 500 MB
- **CPU Usage**: < 70% (average)
