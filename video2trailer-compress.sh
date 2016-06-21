#!/bin/bash

##################################################################################
#### v2t-compress (re)encodes to a constant bitrate webm (VP8/9 - libvorbis)    ##
#### targeting a specific filesize 					      	##
##################################################################################

### Parse Options ####
target_size=4
while getopts ":s:" opt; do
	case $opt in
	s)
		target_size=$OPTARG
		shift $((OPTIND-1))
		;;
	\?)
		echo "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	:)
		echo "Option -$OPTARG requires an argument." >&2
		exit 1
		;;
	esac
done

case $1 in
	"")
		echo "No source file specified" >&2
		exit 1
		;;
esac

#### should we add a watermark?
watermark=1

#### choose encoder
## VP8
encoder=libvpx 	
## VP9
#encoder=libvpx-vp9


#### get video duration
duration_float=`ffprobe -i "$1" -show_format -v quiet | sed -n 's/duration=//p'`
source_duration=`echo "scale=2;$duration_float"|bc`

#### target size is expressed in Megabytes the converted to Megabits
#### the outcome is then subtracted by the audio bitrate
#### the final target_bitrate is the constant bitrate that will be used 
#### to encode the video stream
#### audio bitrate is defined in quality tiers, we are using q0 (64kbps)
#### all the available quality tiers for libvorbis are available @
#### https://en.wikipedia.org/wiki/Vorbis#Technical_details
audio_bitrate=64
threads=4

target_bitrate=$(echo $target_size*8192|bc)
target_bitrate=$(echo $target_bitrate/$source_duration|bc)
target_bitrate=$(echo $target_bitrate-$audio_bitrate|bc)

if [[ ! $target_bitrate -gt 0 ]];
	then
		echo "target size $target_size is not enough to contain the video stream, got a negative bitrate of: $target_bitrate kbps";
		exit 1
fi

echo "estimated video bitrate for target size " $target_size"M: "$target_bitrate"k"
echo "output file is: " $1"."$target_size"M.webm"

#ffmpeg -i $1 -c:v libvpx-vp9 -minrate $target_bitrate"k" -maxrate $target_bitrate"k" -b:v $target_bitrate"k" -c:a libvorbis -q 0 -threads 4 $1"."$target_size"M.webm"

if [ $watermark == 1 ]; 
	then ffmpeg -stats  -v quiet -i $1 -vf drawtext="fontfile=impact: text='K': fontcolor=white: fontsize=26: alpha=0.4: shadowcolor=black: shadowx=1: shadowy=1: x=10: y=(main_h-30):" -c:v $encoder -minrate $target_bitrate"k" -maxrate $target_bitrate"k" -b:v $target_bitrate"k" -c:a libvorbis -q 0 -threads 4 $1"."$target_size"M.webm";
else
	ffmpeg -stats -v quiet -i $1 -c:v $encoder -minrate $target_bitrate"k" -maxrate $target_bitrate"k" -b:v $target_bitrate"k" -c:a libvorbis -q 0 -threads 4 $1"."$target_size"M.webm";
fi
