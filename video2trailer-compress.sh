#!/bin/bash

##################################################################################
#### v2t-compress (re)encodes to a constant bitrate webm (VP8/9 - libvorbis)    ##
#### targeting a specific filesize 					      	##
##################################################################################

#### Set some default values
target_size=4
variable_bitrate=1
threads=4
fps=24
res=640

### Parse Options ####
while getopts "s:b:ct:f:r:" opt; do
	case $opt in
	s)
		#### target output filesize in MB
		target_size=$OPTARG
		;;
	b)
		#### forces target bitrate, completely ignores target filesize if passed
		target_bitrate=$OPTARG
		ignore_target_size=1
		;;
	c)
		#### use constant bitrate instead of variable 
		#### more precise on filesize, worse quality and optiomization
		variable_bitrate=0
		;;
	t)
		#### numer of encoding threads
		threads=$OPTARG
		;;
	f)
		#### FPS limit
		fps=$OPTARG
		;;
	r)
		#### target resolution
		res=$OPTARG
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

#### Moves after the options so that it correctly gets $1
shift $((OPTIND-1))

case $1 in
	"")
		echo "No source file specified" >&2
		exit 1
		;;
esac

source_file=$1

#### should we add a watermark?
watermark=0

#### choose encoder
## VP8
encoder=libvpx 	
## VP9
#encoder=libvpx-vp9

#### get video duration
duration_float=`ffprobe -i "$source_file" -show_format -v quiet | sed -n 's/duration=//p'`
source_duration=`echo "scale=2;$duration_float"|bc`

#### target size is expressed in Megabytes and then converted to Megabits
#### the outcome is then subtracted by the audio bitrate
#### the final target_bitrate is the constant bitrate that will be used 
#### to encode the video stream
#### audio bitrate is defined in quality tiers, we are using q0 (64kbps)
#### all the available quality tiers for libvorbis are available @
#### https://en.wikipedia.org/wiki/Vorbis#Technical_details
audio_bitrate=64

if [ ! $ignore_target_size ];then
	target_bitrate=$(echo $target_size*8192|bc)
	target_bitrate=$(echo $target_bitrate/$source_duration|bc)
	target_bitrate=$(echo $target_bitrate-$audio_bitrate|bc)
fi

#### DEBUG info
# echo "##################################"
# echo "target_bitrate:"$target_bitrate
# echo '$target_size:'$target_size
# echo "duration_float:"$duration_float
# echo "source_duration:"$source_duration

if [ $variable_bitrate -eq 1 ]; then
	#### Removes ffmpeg pass log
	if [ $(ls ffmpeg2pass-0.log) ];
	then 
		rm ffmpeg2pass-0.log;
	fi

	#### Variable bitrate test
	max_ratio="1.3"
	vbitrate=$(echo $target_bitrate/$max_ratio|bc)
	maxrate=$(echo $vbitrate+$vbitrate*25/100|bc)
	buffer_size=$(echo $maxrate*2|bc)

#### DEBUG info
# echo "max_ratio:"$max_ratio
# echo "vbitrate:"$vbitrate
# echo "maxrate:"$maxrate
# echo "bufsize:"$buffer_size

	#### First pass
	pass=1
	ffmpeg -stats -v quiet -i "$source_file" -y -r "$fps" -codec:v "$encoder" -quality good -cpu-used 0 -b:v "$vbitrate"k -qmin 10 -qmax 42 -maxrate "$maxrate"k -bufsize "$buffer_size"k -threads "$threads" -vf scale=-1:"$res" -an -pass $pass -f webm /dev/null

	#### Second pass
	pass=2
	ffmpeg -stats -v quiet -i "$source_file" -r "$fps" -codec:v "$encoder" -quality good -cpu-used 0 -b:v "$vbitrate"k -qmin 10 -qmax 42 -maxrate "$maxrate"k -bufsize "$buffer_size"k -threads "$threads" -vf scale=-1:"$res" -codec:a libvorbis -b:a "$audio_bitrate"k -pass "$pass" -threads "$threads" -f webm "$source_file".pass2."$vbitrate"-"$maxrate"k."$buffer_size"k."$fps"fps.w"$res".webm;

	#### Removes ffmpeg pass log
	rm ffmpeg2pass-0.log
else
	#### Constant bitrate
	if [[ ! $target_bitrate -gt 0 ]];
		then
			echo "target size $target_size is not enough to contain the video stream, got a negative bitrate of: $target_bitrate kbps";
			exit 1
	fi
	
	echo "estimated video bitrate for target size " $target_size"M: "$target_bitrate"k"
	echo "output file is: " "$source_file""."$target_size"M.webm"
	
	if [ $watermark == 1 ]; 
		then 
			ffmpeg -stats -v quiet -i "$source_file" -vf drawtext="fontfile=impact: text='K': fontcolor=white: fontsize=26: alpha=0.4: shadowcolor=black: shadowx=1: shadowy=1: x=10: y=(main_h-30):" -c:v $encoder -minrate $target_bitrate"k" -maxrate $target_bitrate"k" -b:v $target_bitrate"k" -c:a libvorbis -q 0 -threads 4 "$source_file""."$target_size"M.webm";
		else
			ffmpeg -stats -v quiet -i "$source_file" -c:v $encoder -minrate $target_bitrate"k" -maxrate $target_bitrate"k" -b:v $target_bitrate"k" -c:a libvorbis -q 0 -threads 4 "$source_file""."$target_size"M.webm";
	fi
fi
