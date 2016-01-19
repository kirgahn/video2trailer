#!/bin/bash

#echo test "$@"
sliceduration=3
clipduration=60
width=800

for source in "$@";
do
	/usr/local/bin/video2trailer -v -s $sliceduration -dt $clipduration -w $width $source;
done

exit 0
