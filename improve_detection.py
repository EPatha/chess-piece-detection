#!/usr/bin/env python3
"""
Analyze and improve chess detection performance

This script helps diagnose why detection might seem poor despite good training metrics:
1. Checks model predictions on test set with various confidence thresholds
2. Visualizes detections to identify issues
3. Provides recommendations for improvement
"""

import argparse
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


def analyze_detections(
    model_path: str = "runs/chess_detect/train3/weights/best.pt",
    test_images_dir: str = "Chess Pieces Detection Dataset/test/images",
    conf_thresholds: list = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50],
    save_dir: str = "detection_analysis",
):
    """Analyze detection performance at different confidence thresholds."""
    
    print("🔍 Chess Detection Analysis")
    print("=" * 60)
    
    # Load model
    model = YOLO(model_path)
    print(f"✅ Model loaded: {model_path}")
    print(f"   Classes: {list(model.names.values())}")
    
    # Get test images
    test_images = list(Path(test_images_dir).glob("*.jpg")) + list(Path(test_images_dir).glob("*.png"))
    print(f"✅ Found {len(test_images)} test images")
    
    if len(test_images) == 0:
        print("❌ No test images found!")
        return
    
    # Create output directory
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True, parents=True)
    
    # Test on first 5 images with different confidence thresholds
    sample_images = test_images[:5]
    
    print("\n" + "=" * 60)
    print("Testing different confidence thresholds:")
    print("=" * 60)
    
    results_summary = {}
    
    for conf in conf_thresholds:
        print(f"\n🎯 Confidence threshold: {conf:.2f}")
        total_detections = 0
        
        for i, img_path in enumerate(sample_images):
            # Run inference
            results = model.predict(
                source=str(img_path),
                conf=conf,
                iou=0.45,
                save=False,
                verbose=False,
            )
            
            result = results[0]
            num_detections = len(result.boxes)
            total_detections += num_detections
            
            # Save annotated image for conf=0.15 (recommended)
            if conf == 0.15:
                annotated = result.plot()
                output_path = save_path / f"sample_{i+1}_conf{conf:.2f}.jpg"
                cv2.imwrite(str(output_path), annotated)
            
            if num_detections > 0:
                print(f"   Image {i+1}: {num_detections} pieces detected")
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf_score = float(box.conf[0])
                    cls_name = model.names[cls_id]
                    print(f"      - {cls_name}: {conf_score:.3f}")
            else:
                print(f"   Image {i+1}: No detections")
        
        avg_detections = total_detections / len(sample_images)
        results_summary[conf] = avg_detections
        print(f"   Average: {avg_detections:.1f} pieces per image")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("📊 RECOMMENDATIONS")
    print("=" * 60)
    
    best_conf = max(results_summary, key=results_summary.get)
    print(f"\n✅ Best confidence threshold: {best_conf:.2f}")
    print(f"   (Detected avg {results_summary[best_conf]:.1f} pieces per image)")
    
    print(f"\n💡 To improve detection in real-time UI:")
    print(f"   1. Lower confidence threshold to 0.10-0.20 in yolov_ui.py")
    print(f"   2. Ensure good lighting (no harsh shadows)")
    print(f"   3. Camera distance: 30-50cm from board")
    print(f"   4. Stable camera (use tripod or mount)")
    print(f"   5. Plain background (avoid busy patterns)")
    
    print(f"\n📁 Sample detections saved to: {save_dir}/")
    print(f"   Check these images to see detection quality!")
    
    # Check if model is detecting but confidence is too low
    if results_summary[0.10] > results_summary[0.25] * 1.5:
        print(f"\n⚠️  ISSUE FOUND: Many detections at low confidence!")
        print(f"   This suggests:")
        print(f"   - Training data may need more diversity")
        print(f"   - OR test images are different from training")
        print(f"   - OR need more training epochs")
    
    print("\n" + "=" * 60)


def create_improved_training_script():
    """Create an improved training configuration."""
    
    script_content = """#!/usr/bin/env python3
'''
Improved Chess Detection Training
- More epochs for better convergence
- Optimized hyperparameters
- Better augmentation
'''

from ultralytics import YOLO

# Use larger model for better accuracy
model = YOLO("yolov8s.pt")  # Small model (better than nano)

# Train with improved settings
results = model.train(
    data="Chess Pieces Detection Dataset/data.yaml",
    epochs=150,  # More epochs
    imgsz=640,
    batch=8,
    device="cpu",  # Stable, no MPS bug
    patience=30,  # More patience for convergence
    
    # Optimized learning rate
    lr0=0.001,  # Lower initial LR for fine-tuning
    lrf=0.001,  # Lower final LR
    
    # Better augmentation for chess pieces
    hsv_h=0.01,  # Minimal hue change (chess pieces have consistent colors)
    hsv_s=0.3,   # Moderate saturation
    hsv_v=0.2,   # Moderate brightness
    degrees=5.0,    # Small rotation (chess boards are usually aligned)
    translate=0.1,  # Small translation
    scale=0.3,      # Moderate scale
    fliplr=0.5,     # Horizontal flip OK
    flipud=0.0,     # No vertical flip (chess pieces have orientation)
    mosaic=1.0,     # Use mosaic augmentation
    mixup=0.1,      # Small mixup
    
    # Detection settings
    conf=0.15,  # Lower confidence for validation
    iou=0.5,    # Standard IoU threshold
    
    # Callbacks
    project="runs/chess_detect_improved",
    name="train",
    save=True,
    save_period=10,
    plots=True,
    val=True,
    verbose=True,
)

print("\\n✅ Training complete!")
print(f"   Best model: runs/chess_detect_improved/train/weights/best.pt")
"""
    
    with open("train_improved.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created: train_improved.py")
    print("   Run with: .venv/bin/python3 train_improved.py")


def main():
    parser = argparse.ArgumentParser(description="Analyze chess detection performance")
    parser.add_argument("--model", type=str, default="runs/chess_detect/train3/weights/best.pt",
                        help="Path to trained model")
    parser.add_argument("--test-dir", type=str, default="Chess Pieces Detection Dataset/test/images",
                        help="Test images directory")
    parser.add_argument("--save-dir", type=str, default="detection_analysis",
                        help="Output directory for analysis")
    parser.add_argument("--create-improved-training", action="store_true",
                        help="Create improved training script")
    
    args = parser.parse_args()
    
    if args.create_improved_training:
        create_improved_training_script()
    else:
        analyze_detections(
            model_path=args.model,
            test_images_dir=args.test_dir,
            save_dir=args.save_dir,
        )


if __name__ == "__main__":
    main()
