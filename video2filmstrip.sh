#!/bin/bash
# requires ffmpeg and imagemagick!
getopts "q" opt
if [ "$opt" == "q" ];
then
	quiet=true
	shift $((OPTIND-1))
fi

tot_frames=30
percentage=`echo 100/$tot_frames|bc`
progress=0
framelist=""
progressbar=""

duration_float=`ffprobe -i "$1" -show_format -v quiet | sed -n 's/duration=//p'`
duration=`echo "scale=2;$duration_float"|bc`
timegap=`echo "scale=2;$duration/$tot_frames;"|bc`

if [ "$quiet" != "true"  ];
then
	echo "video duration:" `date -u -d @${duration} +"%T"`
	echo "time gap between snapshots:" `date -u -d @${timegap} +"%T"`
fi

for i in $(seq 0 `echo $tot_frames-1|bc`);
do
	if [ "$i" == "0" ];
		then
			frametime=`echo $timegap/2|bc` 
		else
			frametime=`echo $i*$timegap|bc` 

	fi
	ffmpeg -v 0 -ss $frametime -y -i "$1" -t 1 -s 320x240 -f image2 _tmp$i.jpg; 
	frametimehours=`date -u -d @${frametime} +"%T"`
	progress=`echo $progress+$percentage|bc`
	progressbar=$progressbar##
	framelist=$framelist" _tmp$i.jpg"
	convert _tmp$i.jpg -fill black -gravity Southeast -pointsize 14 -annotate +0+0 $frametimehours _tmp$i.jpg
	convert _tmp$i.jpg -fill white -gravity Southeast -pointsize 14 -annotate +1+1 $frametimehours _tmp$i.jpg

	if [ "$quiet" != "true"  ];
	then
		echo -ne 'extracting frame at time '$frametimehours' ('$progress'%)' $progressbar' \r'
	fi
done; 

	if [ "$quiet" != "true"  ];
	then
		echo -ne '\n'
		echo "done, let's join those images!"
	fi

montage  -tile 5 -geometry +0+0  $framelist "$1".jpeg

	if [ "$quiet" != "true"  ];
	then
		echo "cleaning temp files.."
	fi

rm _tmp*

	if [ "$quiet" != "true"  ];
	then
		echo "done! output file is " "$1".jpeg
		echo "Press (q) to quit, (v) to view the file"
		read -n 1 -s viewfile
		
		if [ "$viewfile" == "v" ];
			then
				feh -F "$1".jpeg
		fi
	fi

exit 1
