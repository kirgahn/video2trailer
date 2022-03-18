# video2trailer
* v2t is a simple command line non-linear video editor used to edit a video file and generate webms (using VP8 for legacy reasons)
* v2f is a simple bash script used to generate a preview filmstrip out of a video file

dependecies(***):
* python3
* ffmpeg
* imagemagik
* mplayer
* feh
* youtube-dl

*** some dependencies might not be listed

# examples

- Autotrailer: generate a trailer that lasts 10 seconds and has 5 random slices called test.webm

v2t -a -l 10 -n 5 -d test.webm my_video.mp4

- Autotrailer with Scene Analyzer: generate a trailer that lasts 30 seconds using the Scene Analyzer algorithm to determine the slices. Scene Analyzer should employ a threshold equal to 0.1 to detect the biggest number of scenes.

v2t -a -l 30 -z -zt 0.1 -d test.webm my_video.mp4

- create a test pictures showing the scenes detected with the above settings:


- Autotrailer with lavfi scdet Scene Analyzer: generate a trailer that lasts 30 seconds - skipping the first 14 minutes and 20 seconds and ignoring the last 1 minute and 12 seconds - using the scdet Scene Analyzer (requires ffmpeg5) algorithm to determine the slices. Scdet Scene Analyzer requires a threshold between 1 and 100, with 10 being the default value.

v2t -a -l 30 -zd -zt 10 -zs 00:14:20 -ze 00:01:20 -d test.webm my_video.mp4

- create a test pictures showing the scenes detected with scdet and the above settings:
ffmpeg -f lavfi -ss 00:14:20 -to 00:26:40 -i "movie=my_video.mp4,scdet=s=1:t=10" -vf "scale=160:-1,tile=6x85" -frames:v 1 -qscale:v 3 preview.jpg
