from flask import Flask, render_template, request, send_file, jsonify
import subprocess
import os
import threading

app = Flask(__name__)

# Store progress status globally
progress = {"percentage": 0, "status": "Downloading..."}

def download_song(spotify_url):
    global progress
    # Reset progress
    progress["percentage"] = 0
    progress["status"] = "Downloading..."
    try:
        # Run spotdl command to download the song in the 'downloads' folder
        result = subprocess.run(['spotdl', spotify_url, '--output', 'downloads/'], check=True, capture_output=True, text=True)

        # Check if the download is successful and set progress to 100%
        downloaded_files = os.listdir('downloads')
        if any(file.endswith('.mp3') for file in downloaded_files):
            progress["percentage"] = 100
            progress["status"] = "Download Complete"
        else:
            raise Exception("Download file not found after completion")

    except subprocess.CalledProcessError:
        # If an error occurs, set progress to -1 and an error message
        progress["percentage"] = -1
        progress["status"] = "Error: Failed to download the song. Please check the URL and try again."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    spotify_url = request.form['url']

    if spotify_url:
        # Start download in a background thread
        thread = threading.Thread(target=download_song, args=(spotify_url,))
        thread.start()
        return jsonify({"status": "started"})

    return jsonify({"status": "error"})

@app.route('/progress')
def download_progress():
    return jsonify(progress)

@app.route('/get_file')
def get_file():
    # Get the most recently modified .mp3 file in the 'downloads' folder
    downloaded_files = [f for f in os.listdir('downloads') if f.endswith('.mp3')]
    
    if downloaded_files:
        latest_file = max(downloaded_files, key=lambda f: os.path.getmtime(os.path.join('downloads', f)))
        file_path = os.path.join('downloads', latest_file)
        return send_file(file_path, as_attachment=True)
    
    return "File not found", 404

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
