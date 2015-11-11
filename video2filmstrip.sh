#!/bin/bash
# requires ffmpeg and imagemagick!
tot_frames=20
percentage=`echo 100/$tot_frames|bc`
progress=0
framelist=""

duration_float=`ffprobe -i "$1" -show_format -v quiet | sed -n 's/duration=//p'`
duration=`echo "scale=2;$duration_float"|bc`
echo "video duration:" $duration

timegap=`echo "scale=2;$duration/20;"|bc`
echo "time gap between snapshots:" $timegap 
progressbar=""

for i in $(seq 0 `echo $tot_frames-1|bc`);
do
	if [ "$i" == "0" ];
		then
			ffmpeg -v 0 -ss `echo $timegap/2|bc` -y -i "$1" -t 1 -s 320x240 -f image2 _tmp$i.jpg; 
		else
			ffmpeg -v 0 -ss `echo $i*$timegap|bc` -y -i "$1" -t 1 -s 320x240 -f image2 _tmp$i.jpg; 
	fi
	#echo -ne 'extracting frame number' $i' \r'
	progress=`echo $progress+$percentage|bc`
	progressbar=$progressbar##
	echo -ne 'extracting frames ('$progress'%)' $progressbar' \r'
	framelist=$framelist" _tmp$i.jpg"
	#echo $framelist
done; 
echo -ne '\n'

echo "done, let's join those images!"
montage  -tile 5 -geometry +0+0  $framelist "$1".jpeg

echo "cleaning temp files.."
rm _tmp*

echo "done! output file is " "$1".jpeg
echo "Press (q) to quit, (v) to view the file"
read -n 1 -s viewfile

if [ "$viewfile" == "v" ];
	then
		feh -F "$1".jpeg
fi

exit 1
