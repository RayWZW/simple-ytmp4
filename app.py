from flask import Flask, request, render_template, send_from_directory, url_for
import yt_dlp as youtube_dl
import os
import threading
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'videos/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def cleanup_videos():
    while True:
        time.sleep(300)  # Wait for 5 minutes
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ytmp4', methods=['GET', 'POST'])
def convert_yt_mp4():
    download_link_mp4 = None
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return "URL is required", 400
        
        try:
            # Set up yt-dlp options
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(app.config['UPLOAD_FOLDER'], '%(id)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{info['id']}.mp4" if info['ext'] == 'mp4' else f"{info['id']}.{info['ext']}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            download_link_mp4 = url_for('download_file', filename=filename)
        
        except Exception as e:
            return f"An error occurred: {e}", 500

    return render_template('ytmp4.html', download_link_mp4=download_link_mp4)

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_videos, daemon=True)
    cleanup_thread.start()

    # Run the Flask app
    app.run(port=5444)
