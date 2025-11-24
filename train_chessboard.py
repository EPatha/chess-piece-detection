#!/usr/bin/env python3
"""
Train YOLOv8 for Chessboard Grid Detection
Detects 64 squares (A-H columns) and chessboard corners
"""
from ultralytics import YOLO
import os


def train_chessboard_model():
    """Train YOLOv8 model for chessboard grid detection"""
    
    print("\n" + "="*60)
    print("  🎯 Training Chessboard Grid Detection Model")
    print("="*60)
    
    # Model configuration
    model_name = "yolov8n.pt"  # Nano model (fastest)
    # Alternative: yolov8s.pt (small), yolov8m.pt (medium)
    
    epochs = 50
    img_size = 640
    batch_size = 16
    
    # Data configuration
    data_yaml = "Chessboard/data.yaml"
    
    # Check if data.yaml exists
    if not os.path.exists(data_yaml):
        print(f"❌ Error: {data_yaml} not found!")
        return
    
    print(f"\n📊 Training Configuration:")
    print(f"   Model: {model_name}")
    print(f"   Epochs: {epochs}")
    print(f"   Image Size: {img_size}")
    print(f"   Batch Size: {batch_size}")
    print(f"   Dataset: {data_yaml}")
    
    # Load model
    print(f"\n📥 Loading YOLOv8 model...")
    model = YOLO(model_name)
    
    # Train model
    print(f"\n🚀 Starting training...\n")
    
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        name='chessboard_grid',
        project='runs/chessboard_detect',
        
        # Optimization parameters
        patience=20,           # Early stopping patience
        save=True,             # Save checkpoints
        save_period=10,        # Save every 10 epochs
        
        # Augmentation
        hsv_h=0.015,          # HSV-Hue augmentation
        hsv_s=0.7,            # HSV-Saturation augmentation
        hsv_v=0.4,            # HSV-Value augmentation
        degrees=10.0,         # Rotation augmentation
        translate=0.1,        # Translation augmentation
        scale=0.5,            # Scale augmentation
        shear=0.0,            # Shear augmentation
        perspective=0.0,      # Perspective augmentation
        flipud=0.0,           # Vertical flip
        fliplr=0.5,           # Horizontal flip
        mosaic=1.0,           # Mosaic augmentation
        mixup=0.0,            # Mixup augmentation
        
        # Performance
        device='mps',         # Use Apple Silicon GPU (or 'cpu')
        workers=8,            # Number of workers
        
        # Verbosity
        verbose=True,
        plots=True,           # Generate plots
    )
    
    print("\n" + "="*60)
    print("  ✅ Training Complete!")
    print("="*60)
    
    # Print results
    print(f"\n📊 Training Results:")
    print(f"   Best mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   Best mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    
    # Model save location
    best_model = "runs/chessboard_detect/chessboard_grid/weights/best.pt"
    last_model = "runs/chessboard_detect/chessboard_grid/weights/last.pt"
    
    print(f"\n💾 Model saved to:")
    print(f"   Best: {best_model}")
    print(f"   Last: {last_model}")
    
    print("\n📈 Training plots saved to:")
    print(f"   runs/chessboard_detect/chessboard_grid/")
    
    # Validation
    print(f"\n🧪 Running validation on best model...")
    model_best = YOLO(best_model)
    val_results = model_best.val()
    
    print(f"\n✅ Validation Results:")
    print(f"   mAP50: {val_results.box.map50:.4f}")
    print(f"   mAP50-95: {val_results.box.map:.4f}")
    print(f"   Precision: {val_results.box.mp:.4f}")
    print(f"   Recall: {val_results.box.mr:.4f}")
    
    print("\n" + "="*60)
    print("  🎉 Ready to use!")
    print("="*60)
    print("\n💡 Next steps:")
    print(f"   1. Test model: python3 test_chessboard_model.py")
    print(f"   2. Use in UI: Update yolov_ui.py model path")
    print(f"   3. Detect from image: python3 detect_chessboard.py image.jpg")
    print("")


if __name__ == "__main__":
    train_chessboard_model()
