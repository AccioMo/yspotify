
# y-spotify

A Windows Python script to download Spotify playlists and songs and port them over to iTunes with lyrics and metadata using Genius and Spotify's API. Can also be used to download videos from YouTube.

1. Install dependencies:
```
pip install requests
pip install bs4
pip install yt_dlp
pip install lyricsgenius
pip install python-dotenv
```

2. Create .env file and add Spotify API Client ID and Secret Key:
```
SPOTIFY_CLIENT_ID=<YOUR-SPOTIFY-API-CLIENT-ID>
SPOTIFY_CLIENT_SECRET=<YOUR-SPOTIFY-API-CLIENT-SECRET>
```

3. Run:
```
python.exe main.py
```
