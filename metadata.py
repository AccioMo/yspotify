import os
import json
import shutil
import requests
from lyricsgenius import Genius
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TS2, APIC, USLT, TALB, TRCK, TPE2

if not os.path.exists("data\History.json"):
	os.mkdir("data")
	with open("data\History.json", "w") as h:
		history = {
			"video_path": "C:\\Users\\PC\\Videos",
			"music_path": "C:\\Users\\PC\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes",
			"history": {}
		}
		history = json.dumps(history, indent=2)
		h.write(history)

with open("data\History.json", "r") as h:
    PLACE = json.load(h)
    VIDEO_PATH = PLACE["video_path"]
    MUSIC_PATH = PLACE["music_path"]

username = os.getlogin()
if not VIDEO_PATH:
    VIDEO_PATH = f"C:\\Users\\{username}\\Videos"
if not MUSIC_PATH:
    MUSIC_PATH = f"C:\\Users\\{username}\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes"

# No purpose for now.
def switchToALAC(name):
    os.system("ffmpeg -i %s.m4a-c:a alac %s.alac" %(name, name))

# No purpose for now.
def urlit(ut):
    return (ut).replace(" ", "+").replace("&", "%26").replace(":", "%3A")

# Make song and artist name shorter and more understandable to LyricsGenius in getLyrics().
def fixName(songName):
    try:
        try:
            iN = songName.index("-") - 1
            name = songName[:iN]
        except:
            iN = songName.index("&") - 1
            name = songName[:iN]
    except:
        try:
            iN = songName.index("(") - 1
            name = songName[:iN]
        except:
            name = songName
    return name

def getArtist(dictn):
    try:
        a2 = dictn["track"]["artists"][1]["name"]
        a1 = dictn["track"]["artists"][0]["name"]
        artists = f"{a1} & {a2}"
    except: 
        artists = dictn["track"]["artists"][0]["name"]
    return artists

def getLyrics(song):
    genius = Genius("Gx0pG5ohW_o_gENp8RGDtXD-k0cSxT1yDI8yPUJtscamGsNR1BRUzQN_ZnavcNdi")
    songName = fixName(song.name)
    songArtist = fixName(song.artist)
    try:
        songL = genius.search_song(songName, songArtist)
    except:
        songL = genius.search_song(songName)
    return songL.lyrics

def metadata(song, outS):
    print("metadata-ing...")
    recentSong = MP3(f"{outS}.mp3", ID3=ID3)
    r = requests.get(song.imageURL).content
    with open('image.jpg', 'wb') as image:
        image.write(r)
    image = open('image.jpg', 'rb').read()
    recentSong.tags.add(APIC(3, 'image/jpg', 3, 'Album Cover', image))
    recentSong.tags.add(TIT2(text=song.name))
    recentSong.tags.add(TPE2(text=song.albumartist))
    recentSong.tags.add(TS2(text=song.albumartist))
    recentSong.tags.add(TPE1(text=song.artist))
    recentSong.tags.add(TALB(text=song.album))
    recentSong.tags.add(TRCK(text=str(song.track)))
    for x in range(0,3):
        try:
            print(f"[{song.name}]: Getting Lyrics...", end="\r")
            recentSong.tags.add(USLT(lang='eng', desc='desc', text=getLyrics(song)))
            print(f"Lyrics Found: {song.name}!", end="\r")
            break
        except:
            print(f"Lyrics Not Found: {song.name}.", end="\r")
            pass

    recentSong.save()

def moveSong(outS):
    shutil.move(f'{outS}.mp3', f'{MUSIC_PATH}/{outS}.mp3')
    print("\nMoved to iTunes")

def moveVideo(outS):
    shutil.move(f'videos/{outS}.mp4', f'{VIDEO_PATH}/{outS}.mp4')
    print("\nMoved Video")

def askLyrics(recentSong, song):
    while True:
        try:
            recentSong.tags.add(USLT(lang='eng', desc='desc', text=getLyrics(song)))
            break
        except:
            yon = input(f"No lyrics found for {song.name}. Try again?(y/n)-")
            if yon.lower() == "y":
                pass
            else:
                break
