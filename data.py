from __future__ import unicode_literals
from requests import get
import yt_dlp
from bs4 import *
from metadata import *

if not os.path.exists("data\DownloadedList.json"):
	with open("data\DownloadedList.json", "w") as h:
		DownloadedList = {}
		DownloadedList = json.dumps(DownloadedList, indent=2)
		h.write(DownloadedList)

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

class Song:
	def __init__(self, sData, datafex):
		self.id = sData["track"]["id"]
		self.name = sData["track"]["name"]
		self.album = sData["track"]["album"]["name"]
		self.artist = getArtist(sData)
		self.albumartist = datafex["name"]
		self.track = sData["track"]["track_number"]
		self.imageURL = sData["track"]["album"]["images"][0]["url"]

with open("data\DownloadedList.json", "r") as b:
	DownloadedList = json.load(b)

def getFromSpotify(headers, playlistID):
	pageURL = f"https://api.spotify.com/v1/playlists/{playlistID}"
	mainRes = requests.get(url=pageURL, headers=headers).json()
	pageURL = mainRes["tracks"]["next"]
	while pageURL:
		pageRes = requests.get(url=pageURL, headers=headers).json()
		for item in pageRes["items"]:
			(mainRes["tracks"]["items"]).append(item)
		pageURL = pageRes["next"]
	# upData = json.dumps(mainData, indent=2)
	return mainRes

# Takes song data from Spotify and gets it from YouTube.
def getFromYouTube(playlistID, datafex):
	for dictn in datafex["tracks"]["items"]:
		song = Song(dictn, datafex)
		fullTitle = f"{song.name} - {song.artist}"
		try:
			unexists = all(fullTitle != track for track in DownloadedList[playlistID]) # Checks for if already exists.
		except KeyError:
			DownloadedList[playlistID] = []
			unexists = all(fullTitle != track for track in DownloadedList[playlistID])
		finally: 
			if unexists:
				print(f"Name: {song.name}\nAlbum: {song.album}\nArtist: {song.artist}")
				executeSP(song)
				listingS(playlistID, fullTitle)
			else:
				pass
			

# Organizing function.
def executeSP(song):
	outS = (song.name).replace(("\ "[0]), "").replace("?", "").replace("|", "").replace("/", "").replace("\"", "").replace(":", "")
	try:
		urlSong, nameSong = searchYouTube(f"{song.name} by {song.artist}")
		downloadSong(urlSong, outS)
		metadata(song, outS)
		moveSong(outS)
	except IndexError:
		pass

# Search on Youtube.
def searchYouTube(arg):
	with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
		try:
			get(arg)
		except:
			videos_info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries']
			if videos_info:
				video = videos_info[0]
			else:
				video = ydl.extract_info(arg, download=False)
		else:
			video = ydl.extract_info(arg, download=False)
	idSong = video["id"]
	titleSong = video["title"]
	return f"https://www.youtube.com/watch?v={idSong}", titleSong

def getPlaylist(playlist_url):
	with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
		playlist = ydl.extract_info(url=playlist_url, download=False, process=False)
		with open("data\doc.json", "r") as l:
			vList = json.load(l)
		for vid in playlist["entries"]:
			video_id = vid["id"]
			if any(video_id == saved for saved in vList): continue
			downloadVideo(f"https://www.youtube.com/watch?v={video_id}")
			with open("data\doc.json", "w+") as h:
				vList.append(video_id)
				histo = json.dumps(vList, indent=2)
				h.write(histo)

# Download from YouTube.
def downloadSong(url, outS):
	boop = outS + '.%(ext)s'
	ydl_opts = {
		'format': 'bestaudio/best',
		'quality': '0',
		'outtmpl': boop,
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		ydl.download(url)
		print(ydl)

# Download from YouTube.
def downloadVideo(url):
	ydl_opts = {
		'format': 'bestvideo+bestaudio/best',
		'outtmpl': 'videos\\%(title)s.%(ext)s'
	}
	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])

def listingS(playlistID, fullTitle):
	DownloadedList[playlistID].append(fullTitle)
	upData = json.dumps(DownloadedList, indent=2)
	with open("data\DownloadedList.json", "w") as b:
		b.write(upData)

def countPages(headers, pageURL):
	tracks = 0
	while pageURL:
		pageRes = requests.get(url=pageURL, headers=headers).json()
		try:
			for item in pageRes["items"]: tracks += 1
			pageURL = pageRes["next"]
		except:
			for item in pageRes["tracks"]["items"]: tracks += 1
			pageURL = pageRes["tracks"]["next"]
	return tracks

def addToHistory(playlistid, playlist_name, history_doc):
	print("saving")
	try: del history_doc[playlistid]
	except KeyError: pass
	finally: 
		history_doc["history"][playlistid] = playlist_name
		history_doc["music_path"] = MUSIC_PATH
		history_doc["video_path"] = VIDEO_PATH
		history = json.dumps(history_doc, indent=2)
		with open("data\History.json", "w+") as h:
			h.write(history)
			print("saved")
