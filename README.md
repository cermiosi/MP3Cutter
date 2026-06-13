# Description
This is Python Script to extract Songs from a large MP3 file based on timestamps. It is useful to cut up legally downloaded full album streams.

It copies to following metadata from the original file to the newly created ones: Albumtitle, Contributing Artists, Year and Genre
It also stets the following metadata: Tracktitle (based on the title provided in songlist.txt), Tracknumber

It is just a quick-and-dirty script i wrote in one evening. I am sorry for the messy and unelegant code :)


# Usage
1. Install dependencies (see below) OR open as PyCharm project and use the attached python environment
2. copy all .mp3 files you want to cut into the same directory as MP3Cutter.py
3. fill songlist.txt with a list of the .mp3 files. Under each file, list the timestamps where cuts should be made and the title the cut file should have.
   Instructions on the formatting of songlist.txt can be found at the top of the file. It also contains an example.
4. Run MP3Cutter.py


# Dependencies:
`pip install pydub`
`pip install music-tag`
`pip install audioop-lts` (only necessary if using python 3.13 or above)
