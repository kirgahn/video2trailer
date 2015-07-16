#!/bin/bash

ffmpeg -v 0 -ss `echo 60*$2|bc` -y -i $1 -t 1 -s 1280x720 -f image2 _tmp.jpg ;  feh _tmp.jpg ; rm _tmp.jpg
