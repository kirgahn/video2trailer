#!/bin/bash

#ffmpeg -v 0 -ss `echo 60*$2|bc` -y -i $1 -t 1 -s 1280x720 -f image2 _tmp.jpg ;  feh _tmp.jpg ; rm _tmp.jpg
duration_float=`ffprobe -i 192887.mp4.mp4 -show_format -v quiet | sed -n 's/duration=//p'`
duration=`echo "scale=2;$duration_float"|bc`
echo "video duration:" $duration

timegap=`echo "scale=2;$duration/16;"|bc`
echo "time gap between snapshots:" $timegap 

for i in {1..16}; 
	do ffmpeg -v 0 -ss `echo $i*$timegap|bc` -y -i $1 -t 1 -s 320x240 -f image2 _test$i.jpg; 
	echo "extracting frame number " $i
done; 

echo "done, let's join those images!"
montage  -tile 4 -geometry +0+0  _test* $1.jpeg

#feh testout.jpg
echo "cleaning temp files.."
rm _test*

echo "done! output file is " $1.jpeg

