from flask import Flask, request, render_template_string, send_from_directory
import yt_dlp
import os
import json

app = Flask(__name__)

MUSIC_FOLDER = 'uploaded_songs'
METADATA_FILE = 'songs_metadata.json'

os.makedirs(MUSIC_FOLDER, exist_ok=True)

CATEGORIES = [
    "Hindi Song", "Odia Song", "Sambalpuri Song", "Punjabi Song",
    "Bhojpuri Song", "Haryanvi Song", "Rajasthani Song", "Tamil Song",
    "Telugu Song", "Malayalam Song", "Kannada Song", "Instagram Viral Song", "All Mix Song"
]

def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_metadata(data):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KoshalWorld - MP3 Songs Download</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { background-color: #f5f5f5; color: #333; }
        .top-header { background-color: #000; padding: 15px 0; text-align: center; border-bottom: 3px solid #7B1FA2; }
        .logo-text { color: #fff; font-size: 32px; font-weight: bold; text-decoration: none; }
        .search-container { background: #e8e8e8; padding: 15px 10px; text-align: center; margin-bottom: 20px; }
        .search-box { display: inline-flex; width: 100%; max-width: 500px; }
        .search-box input { flex: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 3px 0 0 3px; font-size: 14px; outline: none; }
        .search-box button { background: #000; color: #fff; border: none; padding: 8px 18px; border-radius: 0 3px 3px 0; font-weight: bold; cursor: pointer; }
        .main-container { max-width: 1000px; margin: 0 auto; padding: 0 10px 30px 10px; display: flex; gap: 15px; flex-wrap: wrap; }
        .left-sidebar { flex: 1; min-width: 260px; max-width: 320px; }
        .right-content { flex: 2; min-width: 300px; }
        .admin-card { background: #fff3bf; border: 1px solid #ffe066; padding: 12px; border-radius: 4px; margin-bottom: 15px; }
        .admin-card h4 { color: #856404; font-size: 14px; margin-bottom: 8px; }
        .admin-form { display: flex; flex-direction: column; gap: 8px; }
        .admin-form input, .admin-form select { padding: 8px 10px; font-size: 13px; border: 1px solid #ffd43b; border-radius: 3px; width: 100%; outline: none; }
        .admin-form button { background: #7B1FA2; color: white; border: none; padding: 8px 12px; font-size: 13px; font-weight: bold; border-radius: 3px; cursor: pointer; }
        .purple-title { background: #8E24AA; color: white; padding: 8px 12px; font-size: 14px; font-weight: bold; border-radius: 3px 3px 0 0; }
        .categories-list { background: white; border: 1px solid #ddd; border-top: none; margin-bottom: 15px; border-radius: 0 0 3px 3px; }
        .category-item { display: block; padding: 9px 12px; color: #333; text-decoration: none; font-size: 13px; border-bottom: 1px solid #f0f0f0; font-weight: 500; }
        .category-item:hover { background: #f0f0f0; color: #7B1FA2; }
        .telegram-btn { background: #8E24AA; color: white; text-align: center; padding: 10px; display: block; text-decoration: none; font-weight: bold; font-size: 13px; border-radius: 3px; margin-bottom: 15px; }
        .songs-box { background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 3px 3px; }
        .song-card { display: flex; align-items: center; padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }
        .song-thumb { width: 50px; height: 50px; border-radius: 4px; object-fit: cover; margin-right: 12px; flex-shrink: 0; background: #eee; }
        .song-details { flex: 1; overflow: hidden; }
        .song-title-text { font-size: 14px; font-weight: bold; color: #222; margin-bottom: 2px; }
        .song-artist-text { font-size: 12px; color: #777; }
        .song-cat-badge { display: inline-block; background: #e1bee7; color: #4a148c; font-size: 10px; padding: 2px 6px; border-radius: 3px; margin-top: 3px; font-weight: bold; }
        .dl-icon-btn { background: #8E24AA; color: white; text-decoration: none; padding: 6px 12px; border-radius: 3px; font-size: 12px; font-weight: bold; }
        @media (max-width: 600px) { .main-container { flex-direction: column; } .left-sidebar { max-width: 100%; } }
    </style>
</head>
<body>
    <div class="top-header">
        <a href="/" class="logo-text">KoshalWorld</a>
    </div>

    <div class="search-container">
        <div class="search-box">
            <input type="text" placeholder="Search Any Songs">
            <button>Search</button>
        </div>
    </div>

    <div class="main-container">
        <div class="left-sidebar">
            <div class="admin-card">
                <h4>⚡ Admin YouTube Uploader</h4>
                <form action="/admin-upload" method="post" class="admin-form">
                    <input type="text" name="url" placeholder="YouTube URL paste karein" required>
                    <select name="category" required>
                        <option value="" disabled selected>-- Select Category --</option>
                        {% for cat in categories %}
                            <option value="{{ cat }}">{{ cat }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">Upload Song</button>
                </form>
                {% if message %}
                    <p style="font-size:11px; color:green; margin-top:5px; font-weight:bold;">{{ message }}</p>
                {% endif %}
            </div>

            <div class="purple-title">📁 Categories</div>
            <div class="categories-list">
                {% for cat in categories %}
                    <a href="/category/{{ cat }}" class="category-item">📁 {{ cat }}</a>
                {% endfor %}
            </div>

            <a href="#" class="telegram-btn">Join Our Telegram Channel</a>
        </div>

        <div class="right-content">
            <div class="purple-title">🎵 {{ selected_category if selected_category else 'New Release' }}</div>
            <div class="songs-box">
                {% if songs %}
                    {% for song in songs %}
                    <div class="song-card">
                        <img src="{{ song.thumbnail }}" class="song-thumb" alt="thumb">
                        <div class="song-details">
                            <div class="song-title-text">{{ song.title }}</div>
                            <div class="song-artist-text">{{ song.uploader }}</div>
                            <span class="song-cat-badge">{{ song.category }}</span>
                        </div>
                        <a href="/download/{{ song.file }}" class="dl-icon-btn" download>Download MP3</a>
                    </div>
                    {% endfor %}
                {% else %}
                    <div style="padding: 30px; text-align: center; color: #888; font-size: 13px;">
                        Is category me koi song nahi hai.<br>Upar Admin Box se YouTube link upload karein!
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    songs = load_metadata()
    return render_template_string(HTML_TEMPLATE, songs=songs, categories=CATEGORIES, selected_category=None)

@app.route('/category/<cat_name>')
def category_view(cat_name):
    all_songs = load_metadata()
    filtered_songs = [s for s in all_songs if s.get('category') == cat_name]
    return render_template_string(HTML_TEMPLATE, songs=filtered_songs, categories=CATEGORIES, selected_category=cat_name)

@app.route('/admin-upload', methods=['POST'])
def admin_upload():
    url = request.form.get('url')
    category = request.form.get('category')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{MUSIC_FOLDER}/%(title)s.%(ext)s',
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = os.path.basename(ydl.prepare_filename(info))
            
            song_data = {
                "title": info.get('title', 'Unknown Track'),
                "uploader": info.get('uploader', 'Unknown Artist'),
                "thumbnail": info.get('thumbnail', 'https://via.placeholder.com/150'),
                "category": category,
                "file": filename
            }
            
            songs = load_metadata()
            songs.insert(0, song_data)
            save_metadata(songs)
            
        return render_template_string(HTML_TEMPLATE, songs=songs, categories=CATEGORIES, selected_category=None, message="✅ Song Uploaded & Categorized Successfully!")
    except Exception as e:
        songs = load_metadata()
        return render_template_string(HTML_TEMPLATE, songs=songs, categories=CATEGORIES, selected_category=None, message=f"❌ Error: {str(e)}")

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(MUSIC_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)