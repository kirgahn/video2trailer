#!/bin/bash
# requires ffmpeg and imagemagick!

duration_float=`ffprobe -i "$1" -show_format -v quiet | sed -n 's/duration=//p'`
duration=`echo "scale=2;$duration_float"|bc`
echo "video duration:" $duration

timegap=`echo "scale=2;$duration/20;"|bc`
echo "time gap between snapshots:" $timegap 
framelist=""
for i in {0..19}; 
	do ffmpeg -v 0 -ss `echo $i*$timegap|bc` -y -i "$1" -t 1 -s 320x240 -f image2 _tmp$i.jpg; 
	echo "extracting frame number " $i
	framelist=$framelist" _tmp$i.jpg"
	#echo $framelist
done; 

echo "done, let's join those images!"
montage  -tile 5 -geometry +0+0  $framelist "$1".jpeg

#feh testout.jpg
echo "cleaning temp files.."
rm _tmp*

echo "done! output file is " "$1".jpeg

