import base64
from data import *
from dotenv import load_dotenv

# os.system('cls')

if not os.path.exists("config.json"):
	with open("config.json", "w") as h:
		config = {
			"video_path": f"./Downloads/video/",
			"audio_path": f"./Downloads/audio/",
		}
		histo = json.dumps(config, indent=2)
		h.write(histo)
with open("config.json", "r") as h:
	config = json.load(h)

VIDEO_PATH = config["video_path"]
MUSIC_PATH = config["audio_path"]

GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

video = True

print("Type AUDIO to download audio, VIDEO to download video, or SP to download Spotify playlist.")
while True:
	try:
		print(f"[ {GREEN + 'VIDEO' + RESET if video else BLUE + 'AUDIO' + RESET} ]", end="  ")
		query = input("Enter link to video/playlist, or search youtube: " + BLUE)
		print(RESET, end="\r")
		if query.find("youtube.com") != -1:
			if query.find("playlist") != -1: getPlaylist(query)
			elif video: downloadVideo(query, VIDEO_PATH)
			else: downloadAudio(query, MUSIC_PATH)

		elif query.upper() == "AUDIO" or query.upper() == "A":
			video = False
		elif query.upper() == "VIDEO" or query.upper() == "V":
			video = True
		
		elif query.upper() == "VPATH": VIDEO_PATH = input("Set a new video download directory: ")
		elif query.upper() == "APATH": MUSIC_PATH = input("Set a new audio download directory: ")

		elif query.upper() == "SP":
			url = "https://accounts.spotify.com/api/token"
			headers = {}
			data = {}

			load_dotenv()
			clientID = os.environ.get("SPOTIFY_CLIENT_ID")
			clientSecret = os.environ.get("SPOTIFY_CLIENT_SECRET")

			msgBytes = f"{clientID}:{clientSecret}".encode('ascii')
			msgBytes64 = base64.b64encode(msgBytes)
			msg64 = msgBytes64.decode('ascii')

			headers['Authorization'] = f"Basic {msg64}"
			data['grant_type'] = "client_credentials"
			r = requests.post(url, headers=headers, data=data)

			token = r.json()['access_token']

			headers = {
				"Authorization": "Bearer " + token
			}
			if (not os.path.exists("data\DownloadedList.json")):
				open("data\DownloadedList.json", "w")
			with open("data\DownloadedList.json", "r") as b:
				DownloadedList = json.load(b)
			if (not os.path.exists("data\History.json")):
				with open("data\History.json", "w") as h:
					history = {
						"video_path": f"./Spotify/video/",
						"music_path": f"./Spotify/music/",
						"history": {}
					}
					histo = json.dumps(history, indent=2)
					h.write(histo)
			with open("data\History.json", "r") as h:
				history = json.load(h)
			VIDEO_PATH = history["video_path"]
			MUSIC_PATH = history["music_path"]
			print("Recently Played:")
			no = 0
			recent_searches = [0]
			reversed_history = dict(reversed(list(history["history"].items())))
			for pid in reversed_history:
				no += 1
				name = reversed_history[pid]
				pageURL = f"https://api.spotify.com/v1/playlists/{pid}"
				no_of_songs = countPages(headers, pageURL)
				if pid in DownloadedList:
					songs_added = no_of_songs - len(DownloadedList[pid])
				else: songs_added = no_of_songs
				print(f"  {no}- {pid}: {name}, {no_of_songs} Songs (+{songs_added} Added)")
				recent_searches.append(pid)
				if no >= 3: break
			
			query = input("Input Playlist ID or choose from Recents:- ")
			if query.upper() == "PATH": MUSIC_PATH = input("Set a new download directory: ")
			try: query = int(query)

			except: pass

			else: query = recent_searches[query]

			finally: 
				playlist_data = getFromSpotify(headers, query)
				addToHistory(query, playlist_data["name"], history)
				getFromYouTube(query, playlist_data)
		
		else:
			video = searchYouTube(query)
			if video:
				title = video["title"]
				seconds = video["duration"]
				minutes = seconds // 60
				hours = seconds // 3600
				duration = f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}"
				views = video["view_count"]
				likes = video["like_count"]
				print("[yspotify]", BOLD + BLUE + f"{title}" + RESET)
				print(f"[yspotify]", BOLD + BLUE + "👁 " + f"{views:,} views" + RESET)
				print(f"[yspotify]", BOLD + BLUE + "⧖ " + f"{duration}" + RESET)
				print(f"[yspotify]", BOLD + BLUE + "🖒 " + f"{likes:,} likes" + RESET)
				n = input("[yspotify] Download? (y/n) " + BOLD + BLUE)
				print(RESET, end="\r")
				if n.upper() != "N":
					video_id = video["id"]
					url = f"https://www.youtube.com/watch?v={video_id}"
					if video: downloadVideo(url, VIDEO_PATH)
					else: downloadAudio(url, MUSIC_PATH)
			else:
				print("No results found.")
				continue
		
	except Exception as e:
		print(f"[yspotify] Error: {e}")
		print(RESET, end="\r")
		continue
