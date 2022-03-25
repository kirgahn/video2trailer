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
* pySceneDetect

*** some dependencies might not be listed

# examples

- interactively edit a video

```v2t my_video.mp4```

- Autotrailer: generate a trailer that lasts 10 seconds and has 5 random slices called test.webm

```v2t -a -l 10 -n 5 -d test.webm my_video.mp4```

- Autotrailer with Scene Analyzer: generate a trailer that lasts 30 seconds using the Scene Analyzer algorithm to determine the slices. Scene Analyzer should employ a threshold equal to 0.1 to detect the biggest number of scenes. A valid threshold goes from 0.1 to 1.

```v2t -a -l 30 -z 1 -zt 0.1 -d test.webm my_video.mp4```

- create a test pictures showing the scenes detected with the above settings:

```ffmpeg -i my_video.mp4 -vf select='gt(scene\,0.6)',scale=160:120,tile -frames:v 1 preview.jpg```

- Autotrailer with lavfi scdet Scene Analyzer: generate a trailer that lasts 30 seconds, skipping the first 14 minutes and 20 seconds and ignoring the last 1 minute and 12 seconds, using the scdet Scene Analyzer algorithm (requires ffmpeg5) to determine the slices. Scdet Scene Analyzer expects a threshold between 1 and 100, with 10 being the default value.

```v2t -a -l 30 -z 2 -zt 10 -zs 00:14:20 -ze 00:01:20 -d test.webm my_video.mp4```

- create a test pictures showing the scenes detected with scdet and the above settings:

```ffmpeg -f lavfi -ss 00:14:20 -to 00:26:40 -i "movie=my_video.mp4,scdet=s=1:t=10" -vf "scale=160:-1,tile=6x85" -frames:v 1 -qscale:v 3 preview.jpg```

- Autotrailer with pySceneDetect: generate a trailer that lasts 60 seconds, starting at 14 minutes and 20 seconds into the source video and ending at 48 minutes, with a bitrate of 1200Kbps and using 12 threads and a threshold that's equal to 20. Use double sampling (at 10% and 30%) for each scene found. In pySceneDetect the threshold refers to frame metric delta_hsv_avg in stats file that is generated the first time the
autotrailer runs, in v2t case under my_video.mp4.stats.csv.

```./v2t.py -a -l 60 -z 3 -zt 20 -zs 00:14:20 -ze 00:48:00 -zd -b 1200 -t 12 -d test.webm my_video.mp4```
