#!/usr/bin/env python3
"""
Chess Detection via USB Camera (HP Android as Webcam)
Zero delay - HP hanya sebagai camera, detection di laptop
"""
import cv2
import subprocess
import sys
import os


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def scan_cameras():
    """Scan semua camera devices yang tersedia"""
    print("🔍 Scanning available cameras...\n")
    
    available = []
    camera_info = {}
    
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                camera_info[i] = {
                    'width': w,
                    'height': h,
                    'fps': fps
                }
                
                # Try to get camera name (macOS)
                name = "Unknown"
                if i == 0:
                    name = "Built-in Camera (Mac)"
                else:
                    name = f"External Camera {i}"
                
                camera_info[i]['name'] = name
                available.append(i)
                
                print(f"  📷 Camera {i}: {name}")
                print(f"     Resolution: {w}x{h}")
                print(f"     FPS: {fps:.1f}\n")
            
            cap.release()
    
    return available, camera_info


def select_camera(available, camera_info):
    """Pilih camera yang akan digunakan"""
    if not available:
        print("❌ No cameras detected!")
        print("\n📋 Untuk HP Android via USB:")
        print("  1. Install app: Iriun Webcam (FREE)")
        print("     Download: https://iriun.com")
        print("  2. Di HP: Buka Iriun app")
        print("  3. Colok USB ke Mac")
        print("  4. HP akan muncul sebagai camera baru")
        print("\n  Alternative:")
        print("  - Cek HP support USB UVC/webcam mode")
        print("  - Atau pakai DroidCam: python3 run_detection.py")
        return None
    
    if len(available) == 1:
        cam_id = available[0]
        print(f"📷 Using camera {cam_id}: {camera_info[cam_id]['name']}")
        return cam_id
    
    # Multiple cameras - let user choose
    print("\n📋 Available cameras:")
    for cam_id in available:
        info = camera_info[cam_id]
        print(f"  [{cam_id}] {info['name']} - {info['width']}x{info['height']}")
    
    print(f"\n💡 Recommendations:")
    print(f"  - Camera 0: Built-in Mac camera")
    print(f"  - Camera 1+: External/USB camera (HP Android)")
    
    try:
        choice = input(f"\nPilih camera ID [0-{max(available)}]: ").strip()
        cam_id = int(choice)
        
        if cam_id in available:
            return cam_id
        else:
            print(f"❌ Invalid choice. Using camera {available[0]}")
            return available[0]
    except:
        print(f"❌ Invalid input. Using camera {available[0]}")
        return available[0]


def main():
    print_header("🚀 Chess Detection - USB Camera Mode")
    
    print("📱 Mode: HP Android sebagai USB Webcam")
    print("💻 Processing: YOLOv8 detection di Laptop")
    print("⚡ Zero Delay: Direct USB camera access\n")
    
    # Scan cameras
    available, camera_info = scan_cameras()
    
    if not available:
        sys.exit(1)
    
    # Select camera
    cam_id = select_camera(available, camera_info)
    
    if cam_id is None:
        sys.exit(1)
    
    # Check model
    model_path = "runs/chess_detect/train3/weights/best.pt"
    if not os.path.exists(model_path):
        print(f"\n⚠️  Warning: Model not found at {model_path}")
        print("Model will be downloaded on first run.")
    else:
        print(f"\n✅ Model ready: {model_path}")
    
    # Launch UI
    print_header("🎬 Launching Chess Detection UI")
    print(f"📌 Camera: ID {cam_id} ({camera_info[cam_id]['name']})")
    print(f"📌 Resolution: {camera_info[cam_id]['width']}x{camera_info[cam_id]['height']}")
    print(f"📌 Model: {model_path}")
    print(f"📌 Confidence: 0.15 (optimal)")
    print(f"📌 Processing: Laptop CPU/GPU")
    print("\n⌨️  UI window akan terbuka...")
    print("⌨️  Camera source akan di-set ke ID", cam_id)
    print("⌨️  Click 'Start' untuk mulai detection")
    print("⌨️  Press Ctrl+C untuk stop\n")
    
    try:
        # Launch UI with camera ID
        venv_python = ".venv/bin/python3"
        subprocess.run([venv_python, "yolov_usb_ui.py", str(cam_id)])
    except KeyboardInterrupt:
        print("\n\n⏹  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        print("\n✅ Done!")


if __name__ == "__main__":
    main()
