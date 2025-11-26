import os
import requests

def download_model():
    model_name = "temp_exp1_last.pt"
    url = f"https://github.com/ChapponE/An-Object-Detection-Ramble-with-YOLOv8n-Application-to-Chess-Pieces/releases/download/v1.0.3/{model_name}"
    output_path = "chess_model.pt"
    
    print(f"Downloading {model_name} from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Model saved as {output_path}")
    except Exception as e:
        print(f"Error downloading model: {e}")

if __name__ == "__main__":
    download_model()
