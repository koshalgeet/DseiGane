import os
import json
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

METADATA_FILE = 'songs_metadata.json'

def load_songs():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_songs(songs):
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=4)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KoshalWorld - Songs Collection</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }
        header { background-color: #000; color: #fff; text-align: center; padding: 15px; font-size: 24px; font-weight: bold; }
        .search-bar { text-align: center; margin: 20px 0; }
        .search-bar input { padding: 8px; width: 300px; }
        .search-bar button { padding: 8px 15px; background: #000; color: #fff; border: none; cursor: pointer; }
        .container { display: flex; max-width: 1100px; margin: 0 auto; gap: 20px; padding: 10px; }
        .sidebar { width: 250px; background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
        .categories { list-style: none; padding: 0; }
        .categories li a { display: block; padding: 8px; margin-bottom: 5px; background: #f9f9f9; text-decoration: none; color: #333; font-weight: bold; border-left: 4px solid #8E24AA; }
        .categories li a:hover { background: #8E24AA; color: #fff; }
        .main-content { flex: 1; background: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
        .song-card { border-bottom: 1px solid #ddd; padding: 15px 0; display: flex; align-items: center; gap: 15px; }
        .song-card img { width: 110px; height: 85px; object-fit: cover; border-radius: 6px; }
        .song-info { flex: 1; }
        audio { width: 100%; margin-top: 8px; height: 35px; }
        .download-btn { background: #8E24AA; color: white; padding: 8px 14px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 13px; display: inline-block; margin-top: 6px; }
        .download-btn:hover { background: #6A1B9A; }
        .admin-box { background: #fff3cd; border: 1px solid #ffeba2; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .admin-box input, .admin-box select { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
        .admin-box button { width: 100%; padding: 10px; background: #8E24AA; color: white; border: none; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <header>KoshalWorld</header>
    <div class="search-bar">
        <form method="GET" action="/">
            <input type="text" name="q" placeholder="Search Any Songs" value="{{ search_query }}">
            <button type="submit">Search</button>
        </form>
    </div>
    <div class="container">
        <div class="sidebar">
            {% if is_admin %}
            <div class="admin-box">
                ⚡ <b>Admin Uploader</b>
                <form method="POST" action="/admin">
                    <input type="text" name="song_title" placeholder="Song Title / Naam" required>
                    <input type="text" name="image_url" placeholder="Song Image / Thumbnail Link" required>
                    <input type="text" name="audio_url" placeholder="MP3 Audio Direct Link" required>
                    <select name="category" required>
                        <option value="">-- Select Category --</option>
                        {% for cat in categories %}
                        <option value="{{ cat }}">{{ cat }}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">Upload Song</button>
                </form>
            </div>
            {% endif %}
            
            <h3>📁 Categories</h3>
            <ul class="categories">
                {% for cat in categories %}
                <li><a href="/category/{{ cat }}">{{ cat }}</a></li>
                {% endfor %}
            </ul>
        </div>
        <div class="main-content">
            <h2>🎵 {{ current_title }}</h2>
            {% if songs %}
                {% for song in songs %}
                <div class="song-card">
                    <img src="{{ song.image_url }}" alt="Song Cover" onerror="this.src='https://via.placeholder.com/110x85?text=No+Image'">
                    <div class="song-info">
                        <strong>{{ song.title }}</strong><br>
                        <small style="color: #666;">Category: {{ song.category }}</small><br>
                        {% if song.audio_url %}
                        <audio controls preload="none">
                            <source src="{{ song.audio_url }}" type="audio/mpeg">
                        </audio><br>
                        <a href="{{ song.audio_url }}" download target="_blank" class="download-btn">⬇️ Direct Download MP3</a>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align:center; padding: 30px; color: #666;">Is category me koi song nahi hai.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

CATEGORIES = [
    "Hindi Song", "Odia Song", "Sambalpuri Song", "Punjabi Song", 
    "Bhojpuri Song", "Haryanvi Song", "Rajasthani Song", "Tamil Song", 
    "Telugu Song", "Malayalam Song", "Kannada Song", "Instagram Viral Song", "All Mix Song"
]

@app.route('/')
def home():
    songs = load_songs()
    search_query = request.args.get('q', '')
    if search_query:
        songs = [s for s in songs if search_query.lower() in s['title'].lower()]
    return render_template_string(
        HTML_LAYOUT, 
        songs=songs, 
        categories=CATEGORIES, 
        current_title="All Songs", 
        search_query=search_query,
        is_admin=False
    )

@app.route('/category/<cat_name>')
def category(cat_name):
    songs = load_songs()
    filtered_songs = [s for s in songs if s.get('category') == cat_name]
    return render_template_string(
        HTML_LAYOUT, 
        songs=filtered_songs, 
        categories=CATEGORIES, 
        current_title=cat_name, 
        search_query="",
        is_admin=False
    )

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    songs = load_songs()
    if request.method == 'POST':
        title = request.form.get('song_title')
        image_url = request.form.get('image_url')
        audio_url = request.form.get('audio_url')
        cat = request.form.get('category')
        
        new_song = {
            'title': title,
            'image_url': image_url,
            'audio_url': audio_url,
            'category': cat
        }
        songs.append(new_song)
        save_songs(songs)
            
        return redirect(url_for('admin'))
        
    return render_template_string(
        HTML_LAYOUT, 
        songs=songs, 
        categories=CATEGORIES, 
        current_title="Admin Panel (Songs List)", 
        search_query="",
        is_admin=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
