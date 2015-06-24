#!/usr/bin/env python
# incremental version 0.1

#import glob
import random
import datetime
import mimetypes
import os
import argparse
from moviepy.editor import *

parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
parser.add_argument("-s", "--sliceduration", help="Duration of each slice in seconds, if unpecified assume one second", type=int)
parser.add_argument("-dt", "--duration", help="Total duration of output file, if unspecified assume 30 seconds", type=int)
parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
parser.add_argument("-d", "--destfile", help="Destination video file, if unspecified append \"_trailer.webm\" to source filename", type=str)

args = parser.parse_args()
sourcefile = args.sourcefile

if not args.destfile:
	destfile=str(args.sourcefile)+'_trailer.webm'
else:
	destfile=args.destfile

if not args.sliceduration:
	sliceduration=1
else:
	sliceduration=args.sliceduration	

if not args.duration:
	duration=30
else:
	duration=args.duration

#bitrate="'1.2M'"

if args.verbose:
	print("Configuration parameters")
	print("Source file: "+sourcefile)
	print("Destination file: "+destfile)
	print("Slice duration: "+str(sliceduration))
	print("Webm duration: "+str(duration))

v = VideoFileClip(sourcefile)
slices = []
prevpos = 0
cycles = duration/sliceduration
step = 100/cycles
s=1
n=1

while n <= cycles:
	if args.verbose:
		print ("slices:", len(slices), "step:", step, "n counter:", n, "slice position:", s, "previous position:", prevpos, "duration:", int(v.duration), "percentage",str(round(s/int(v.duration)*100))+"%" )

	s = random.randint(prevpos+1,round(int(v.duration)/100*(n*step)))
	prevpos = s
	vo = v.subclip(s,s+sliceduration)
	vo = vo.resize(width=640)
	slices.append(vo)
	n = n + 1

#last slice between lastpos & total lenght
s = random.randint(prevpos,int(v.duration))
prevpos = s

if args.verbose:
	print ("last slice position:", s)			

vo = v.subclip(s,s+sliceduration)
vo = vo.resize(width=720)
slices.append(vo)

concatenate_videoclips(slices,method='compose').write_videofile(destfile, bitrate='1.2M', fps=24)
