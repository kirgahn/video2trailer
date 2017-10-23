#!/bin/bash
# requires ffmpeg and imagemagick!

############################################
## Reads $1 and checks if there's "-q",   ##
## if so shift on the next parameter/arg  ##
############################################

getopts "q" opt
if [ "$opt" == "q" ];
then
	quiet=true
	shift $((OPTIND-1))
fi

############################################
## If no input file has been specified    ##
## just quit 				  ##
############################################

if [[ "$1" == "" ]];
then
	echo "No source file specified! Quitting..."
	exit 1
fi

############################################
## initialize variables and get duration  ##
## time in secs. tell something about it  ##
############################################

tot_frames=24
percentage=`echo 100/$tot_frames|bc`
progress=0
framelist=""
progressbar=""

duration_float=`ffprobe -i "$1" -show_format -v quiet | sed -n 's/duration=//p'`
duration=`echo "scale=2;$duration_float"|bc`
timegap=`echo "scale=2;$duration/$tot_frames;"|bc`
tmpdir=$(mktemp -d "/tmp/XXXXXXX")

if [ "$quiet" != "true"  ];
then
	echo "video duration:" `date -u -d @${duration} +"%T"`
	echo "time gap between snapshots:" `date -u -d @${timegap} +"%T"`
	echo "temporary directory: " $tmpdir
fi

################################################
## Generate a range as a sequence and loop.   ##
## Time gaps are defined as int of 	      ##
## duration/frames. Each frame will be        ##
## extracted at timegap*$i, except for the    ##
## first.                                     ##
################################################

for i in $(seq 0 `echo $tot_frames-1|bc`);
do
	if [ "$i" == "0" ];
		then
			frametime=`echo $timegap/2|bc` 
		else
			frametime=`echo $i*$timegap|bc` 

	fi
	ffmpeg -v 0 -ss $frametime -y -i "$1" -t 1 -s 320x180 -f image2 $tmpdir/_tmp$i.jpg;  

################################################
## Convert time to an understandable format   ##
## and stamp it on the frames. Do it twice    ##
## for black and white text.                  ##
## Show some progress.         		      ##
## extracted at timegap*$i, except for the    ##
## first.                                     ##
################################################

	frametimehours=`date -u -d @${frametime} +"%T"`
	progress=`echo $progress+$percentage|bc`

	for hastag in $percentage;
	do
		progressbar=$progressbar#
	done;

	framelist=$framelist"$tmpdir/_tmp$i.jpg "
	convert $tmpdir/_tmp$i.jpg -fill black -font /usr/share/fonts/TTF/DejaVuSans.ttf -gravity Southwest -pointsize 14 -annotate +0+0 $frametimehours $tmpdir/_tmp$i.jpg
	convert $tmpdir/_tmp$i.jpg -fill white -font /usr/share/fonts/TTF/DejaVuSans.ttf -gravity Southwest -pointsize 14 -annotate +1+1 $frametimehours $tmpdir/_tmp$i.jpg

	if [ "$quiet" != "true"  ];
	then
		echo -ne 'extracting frame at '$frametimehours' ('$progress'%)' $progressbar' \r'
	fi
done; 

	if [ "$quiet" != "true"  ];
	then
		echo -ne 'done extracting frames      (100%)' $progressbar' \r'
		echo -ne '\n'
		echo "done, let's join those images!"
	fi

################################################
## Create picture tile. 		      ##
## Remove temporary files.                    ##
## Offer to show results.                     ##
################################################

montage  -tile 6 -geometry +0+0 $framelist '$1'.jpeg

	if [ "$quiet" != "true"  ];
	then
		echo "cleaning temp files.."
	fi

rm -rf $tmpdir

	if [ "$quiet" != "true"  ];
	then
		echo "done! output file is " "$1".jpeg
		echo "Press (q) to quit, (v) to view the file"
		read -n 1 -s viewfile
		
		if [ "$viewfile" == "v" ];
			then
				#feh -F "$1".jpeg
				xdg-open "$1".jpeg &>/dev/null
		fi
	fi

exit 1
