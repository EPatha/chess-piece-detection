import requests
import webbrowser

class LichessExporter:
    BASE_URL = "https://lichess.org/api/import"

    @staticmethod
    def upload_pgn(pgn_content):
        """
        Uploads PGN content to Lichess and opens the analysis board.
        Returns the URL of the imported game or None if failed.
        """
        try:
            print(f"Uploading PGN to Lichess: {pgn_content}")
            # Add headers to request JSON, otherwise Lichess might return HTML
            headers = {'Accept': 'application/json'}
            response = requests.post(LichessExporter.BASE_URL, data={'pgn': pgn_content}, headers=headers)
            
            print(f"Lichess Response Status: {response.status_code}")
            print(f"Lichess Response Body: {response.text}")

            if response.status_code == 200:
                result = response.json()
                url = result.get('url')
                if url:
                    print(f"Game uploaded to Lichess: {url}")
                    webbrowser.open(url)
                    return url
            
            print(f"Lichess Upload Failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"Lichess Export Error: {e}")
            return None
