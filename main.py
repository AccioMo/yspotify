import base64
from data import *
from dotenv import load_dotenv

# os.system('cls')

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

print("Type SP to switch to Spotify or PATH to change download folder.")
while True:
	# try:
		query = input("Enter link to video/playlist, or search: ")
		if query.find("youtube.com") != -1:
			if query.find("playlist") != -1: getPlaylist(query)
			else: downloadVideo(query)

		elif query.upper() == "PATH": VIDEO_PATH = input("Set a new download directory: ")

		elif query.upper() == "SP":
			if (not os.path.exists("data\DownloadedList.json")):
				open("data\DownloadedList.json", "w")
			with open("data\DownloadedList.json", "r") as b:
				DownloadedList = json.load(b)
			if (not os.path.exists("data\History.json")):
				with open("data\History.json", "w") as h:
					history = {
						"video_path": "C:\\Users\\PC\\Videos",
						"music_path": "C:\\Users\\PC\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes",
						"history": {}
					}
					histo = json.dumps(history, indent=2)
					h.write(histo)
			with open("data\History.json", "r") as h:
				history = json.load(h)
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
			url, title = searchYouTube(query)
			n = input(f"Found: {title} - (Y/N): ")
			if n.upper() != "N": downloadVideo(url)
			else: pass
		
	# except Exception as err: print(f"{err}")
