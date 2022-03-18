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
