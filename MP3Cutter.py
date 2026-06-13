from pydub import AudioSegment
import music_tag
import os


class TimeStampList:

    def __init__(self, file):
        self.mp3File = file
        self.songtitles = [] #a list where each entry is the title of one song in the file
        self.timestamps = [] #a list where each entry is the timestamp in seconds where the song of the same index begins

    def addTimeStamp(self, title, seconds):  #receives a title (string) and a timestamp (int) measured in seconds
        self.songtitles.append(title)
        self.timestamps.append(seconds*1000)  # stores the time in milliseconds

    def getListLength(self):
        if(len(self.songtitles) == len(self.timestamps)):
            return len(self.songtitles)
        else:
            log("ERROR: length of titles and timestamps is not of same length for file: ", self.mp3File)
            return 0

    def getListContent(self, index):
        if(index < 0 or len(self.songtitles) <= index):
            print(f"ERROR: {index} is not a valid index for list of {self.mp3File}")
            return None

        return (self.songtitles[index], self.timestamps[index])

    def printTimeStampList(self):
        print(self.mp3File)
        print(self.songtitles)
        print(self.timestamps)


def log(text):
    print("LOG:", text)
    return


def readSonglist(filename="songlist.txt"):
    try:
        log("trying to load file")
        with open(filename, "r") as f:
            lines = f.readlines()
        log("file loaded successfully")
    except FileNotFoundError:
        log(f"An Error occurred while trying to load the file {filename}")
        return None

    # evaluate line
    albumList = []

    log("starting songlist evaluation")
    for i in range(0, len(lines)):
        line = lines[i]

        if(line == "\n"):  #skip empty lines
            continue

        elif(line[0] == "#"):  #skip comment
            continue

        elif(line[:5] == "FILE:"):  #switch list the timestamps are added to
            if(line[-5:] != ".mp3\n"):
                log("ERROR: file is not a .mp3 file")
                return None
            albumList.append(TimeStampList(line[5:-1]))  #append the title of the file to the albumList without "FILE:" and without "\n"
            continue

        else:  #add timestamp to current list:
            #read timestamp from string
            minute, second, title = "", "", ""
            nextIndex = 0

            for i in range(0, len(line)):  #read the minute
                character = line[i]
                if(character == ":"):
                    nextIndex = i + 1
                    break
                minute = f"{minute}{character}"  #append the minute string by the next character

            for i in range(nextIndex, len(line)):  #read the second
                character = line[i]
                if(character == " "):
                    nextIndex = i + 1
                    break
                second = f"{second}{character}"

            for i in range(nextIndex, len(line)):  #read the title
                character = line[i]
                if (character == "\n"):
                    break
                title = f"{title}{character}"

            #add timestamps to list
            albumList[-1].addTimeStamp(title, int(minute) * 60 + int(second))
            continue

    log("songlist evaluation finished")
    return albumList


def storeMP3(song, songTitle, songTrackNumber, albumMetadata):
    albumTitle = albumMetadata["album"].first

    #create own folder for each album
    if(os.path.isdir(albumTitle) == False):
        try:
            os.mkdir(albumTitle)
            log(f"Directory '{albumTitle}' created successfully.")
        except PermissionError:
            log(f"Permission denied: Unable to create '{albumTitle}'.")
        except Exception as e:
            log(f"An error occurred: {e}")

    #export song as new mp3
    try:
        log(f"Trying to export song {songTitle}")
        song.export(f"{albumTitle}/{songTitle}.mp3", format="mp3")

        #set metadata of new song
        songMetaData = music_tag.load_file(f"{albumTitle}/{songTitle}.mp3")
        songMetaData["tracktitle"] = songTitle
        songMetaData["tracknumber"] = songTrackNumber
        for key in albumMetadata:
            songMetaData[key] = albumMetadata[key]
        songMetaData.save()

        log(f"Song {songTitle} exported successfully")
    except Exception as e:
        log(f"ERROR while exporting the song {songTitle}: {e}")


def cutMP3(timeStampList):
    try:
        log(f"trying to load audiofile for album {timeStampList.mp3File[:-4]}")

        album = AudioSegment.from_mp3(timeStampList.mp3File)  #import mp3 file as "list
        albumTitle = timeStampList.mp3File[:-4]

        #reading metadata of audiofile
        fullmetadata = music_tag.load_file(timeStampList.mp3File)

        #cut the relevant metadata from fullmetadata (there might be a more elegant way for this but i don't care)
        metadata = {}
        metadata["album"] = fullmetadata["album"]
        metadata["artist"] = fullmetadata["artist"]
        metadata["genre"] = fullmetadata["genre"]
        metadata["year"] = fullmetadata["year"]

        log(f"loading of audiofile for album {albumTitle} successfull")
    except FileNotFoundError:
        log(f"An Error occurred while trying to load the album {timeStampList.mp3File}")
        return

    if(timeStampList.getListLength() == 0):
        log(f"ERROR: the timestamp list is empty for file {timeStampList.mp3File}")

    #cut mp3 list into segments
    title, timestamp = timeStampList.getListContent(0)
    for i in range(0, timeStampList.getListLength()):
        if(i < (timeStampList.getListLength() - 1)):
            nextTitle, nextTimestamp = timeStampList.getListContent(i + 1)

            song = album[timestamp : nextTimestamp]
            storeMP3(song, title, i+1, metadata)

            title = nextTitle
            timestamp = nextTimestamp

        else:
            song = album[timestamp : ]
            storeMP3(song, title, i+1, metadata)



if __name__ == '__main__':
    albumList = readSonglist()
    for timeStampList in albumList:
        #timeStampList.printTimeStampList()
        cutMP3(timeStampList)

