#!/usr/bin/env python3
"""
Test Chessboard Grid Detection Model
"""
from ultralytics import YOLO
import cv2
import sys


def test_model(image_path=None, model_path="runs/chessboard_detect/chessboard_grid8/weights/best.pt"):
    """Test chessboard detection model"""
    
    print("\n" + "="*60)
    print("  🧪 Testing Chessboard Grid Detection Model")
    print("="*60)
    
    # Load model
    print(f"\n📥 Loading model: {model_path}")
    model = YOLO(model_path)
    
    # Print model info
    print(f"\n📊 Model Info:")
    print(f"   Classes: {model.names}")
    print(f"   Number of classes: {len(model.names)}")
    
    if image_path:
        # Test on image
        print(f"\n📷 Testing on image: {image_path}")
        
        results = model.predict(
            source=image_path,
            conf=0.25,
            save=True,
            project='runs/chessboard_detect',
            name='predict',
            show_labels=True,
            show_conf=True,
        )
        
        print(f"\n✅ Detection complete!")
        print(f"   Results saved to: runs/chessboard_detect/predict/")
        
        # Print detections
        for r in results:
            boxes = r.boxes
            print(f"\n🎯 Detections: {len(boxes)}")
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]
                print(f"   • {class_name}: {conf:.2f}")
    
    else:
        # Run validation on test set
        print(f"\n🧪 Running validation on test set...")
        
        results = model.val(
            data="Chessboard/data.yaml",
            split='test',
            save_json=True,
        )
        
        print(f"\n✅ Validation Results:")
        print(f"   mAP50: {results.box.map50:.4f}")
        print(f"   mAP50-95: {results.box.map:.4f}")
        print(f"   Precision: {results.box.mp:.4f}")
        print(f"   Recall: {results.box.mr:.4f}")
        
        # Per-class results
        print(f"\n📊 Per-Class Results:")
        for i, name in model.names.items():
            if i < len(results.box.maps):
                print(f"   {name}: mAP50={results.box.maps[i]:.4f}")
    
    print("\n" + "="*60)
    print("")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test on specific image
        test_model(sys.argv[1])
    else:
        # Run validation on test set
        print("Usage:")
        print("  python3 test_chessboard_model.py              # Validate on test set")
        print("  python3 test_chessboard_model.py image.jpg    # Test on image")
        print("")
        test_model()
