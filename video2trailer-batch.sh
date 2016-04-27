#!/bin/bash

#echo test "$@"
#sliceduration=3
#clipduration=60
#width=800

sliceduration=2
clipduration=29
width=720

for source in "$@";
do
	/usr/local/bin/video2trailer -v -s $sliceduration -dt $clipduration -w $width -fs "$source";
done
exit 0
