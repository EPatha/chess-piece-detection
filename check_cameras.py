#!/usr/bin/env python3
"""
Camera Detection Tool - Deteksi semua camera termasuk DroidCam
Supports: Built-in webcam, USB camera, DroidCam (USB/WiFi)
"""
import cv2
import platform
import sys

def check_cameras(max_cameras=10):
    """Scan camera ID dari 0 sampai max_cameras"""
    print(f"🔍 Scanning cameras (0-{max_cameras})...\n")
    print(f"💻 OS: {platform.system()} {platform.release()}")
    print(f"🐍 OpenCV Version: {cv2.__version__}\n")
    
    available_cameras = []
    
    for i in range(max_cameras):
        print(f"Testing camera ID {i}...", end=" ")
        
        # Coba buka camera
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            # Coba baca 1 frame untuk memastikan benar-benar berfungsi
            ret, frame = cap.read()
            
            if ret and frame is not None:
                # Dapatkan info camera
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                backend = cap.getBackendName()
                
                print(f"✅ FOUND")
                print(f"   └─ Resolution: {width}x{height}")
                print(f"   └─ FPS: {fps}")
                print(f"   └─ Backend: {backend}")
                
                # Detect camera type
                cam_type = "Unknown"
                if width == 1280 and height == 720:
                    cam_type = "Possibly DroidCam (720p)"
                elif width == 640 and height == 480:
                    cam_type = "Standard webcam or DroidCam (480p)"
                elif width >= 1920:
                    cam_type = "High-res USB/External camera"
                
                print(f"   └─ Type: {cam_type}")
                
                available_cameras.append({
                    'id': i,
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': backend,
                    'type': cam_type
                })
            else:
                print(f"❌ Opens but can't read frame")
            
            cap.release()
        else:
            print(f"❌ Not available")
    
    print("\n" + "="*60)
    
    if available_cameras:
        print(f"\n✅ Found {len(available_cameras)} camera(s):\n")
        for cam in available_cameras:
            print(f"   Camera ID {cam['id']}:")
            print(f"   - Resolution: {cam['resolution']}")
            print(f"   - FPS: {cam['fps']}")
            print(f"   - Backend: {cam['backend']}")
            print()
        
        print("💡 Tips:")
        print("   • Camera ID 0 biasanya built-in webcam (MacBook/laptop)")
        print("   • Camera ID 1+ biasanya external USB camera atau DroidCam")
        print("   • Untuk DroidCam via WiFi, gunakan URL: http://IP:4747/video")
        print("   • Untuk DroidCam via USB, biasanya muncul sebagai camera ID 1 atau 2")
    else:
        print("\n❌ No cameras found!")
        print("\n💡 Troubleshooting:")
        print("   1. Pastikan camera terhubung dengan baik")
        print("   2. Untuk DroidCam, pastikan aplikasi sudah running di HP")
        print("   3. Untuk USB, cek kabel dan izin akses camera")
        print("   4. Restart aplikasi DroidCam atau reconnect USB")
    
    return available_cameras


def test_camera_live(camera_id):
    """Test camera dengan preview langsung"""
    print(f"\n📹 Testing camera {camera_id} with live preview...")
    print("Press 'q' to quit preview\n")
    
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_id}")
        return False
    
    print(f"✅ Camera {camera_id} opened successfully!")
    print("Showing preview window...")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"❌ Failed to read frame {frame_count}")
            break
        
        frame_count += 1
        
        # Tampilkan info di frame
        cv2.putText(frame, f"Camera ID: {camera_id}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", (10, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow(f'Camera {camera_id} Preview', frame)
        
        # Press 'q' untuk quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Successfully captured {frame_count} frames")
    return True


if __name__ == "__main__":
    print("="*60)
    print("🎥 CAMERA DETECTION UTILITY")
    print("="*60 + "\n")
    
    # Scan semua camera
    cameras = check_cameras(max_cameras=10)
    
    # Jika ada camera, tanya user mau test atau tidak
    if cameras:
        print("\n" + "="*60)
        response = input("\n🎬 Test camera dengan live preview? (y/n): ").strip().lower()
        
        if response == 'y':
            camera_id = int(input("Enter camera ID to test: "))
            test_camera_live(camera_id)
    
    print("\n" + "="*60)
    print("Done! ✨")
    print("="*60)
