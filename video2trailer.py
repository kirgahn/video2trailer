#!/usr/bin/env python

import random
import datetime
import mimetypes
import os
import sys
import argparse
from moviepy.editor import *

parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
parser.add_argument("-s", "--sliceduration", help="Duration of each slice in seconds, if unpecified assume one second", type=int)
parser.add_argument("-dt", "--duration", help="Total duration of output file, if unspecified assume 30 seconds", type=int)
parser.add_argument("-d", "--destfile", help="Destination video file, if unspecified append \"_trailer.webm\" to source filename", type=str)
parser.add_argument("-f", "--fps", help="Output videofile frames per second, if empty assumes source fps", type=int)
parser.add_argument("-w", "--width", help="Resolution width of the output file in pixels, if empty assumes 640", type=int)
parser.add_argument("-b", "--bitrate", help="Output videofile bitrate in \"x.x\" format, if empty assumes \"1.2M\"", type=float)
parser.add_argument("-fs", "--finalslice", help="Additional final slice, good if you need to catch the last seconds; if empty assume no ", action="store_true" )

args = parser.parse_args()
sourcefile = args.sourcefile
v = VideoFileClip(sourcefile)

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

if args.verbose:
	print(("#" * 12) + " video2trailer " + ("#" * 12))
	print("source file: " + sourcefile + " - destination file: " + destfile)

if not args.fps:
        fps=int(v.fps)
        if args.verbose:
                print("Assuming FPS: " + str(v.fps))
else:
	fps=args.fps

if not args.width:
        width=640
        if args.verbose:
                print("Assuming bitrate: " + str(width))
else:
        width=args.width

if not args.bitrate:
        bitrate="1.2M"
        if args.verbose:
                print("Assuming bitrate: " + bitrate)
else:
        bitrate=str(args.bitrate)+"M"

if not args.finalslice:
        finalslice=False
else:
        finalslice=True

if args.verbose:
	print("Configuration parameters")
	print("-" * 24)
	print("Slice duration: "+str(sliceduration))
	print("Webm duration: "+str(duration))
	print("fps: "+ str(fps))
	print("width: "+ str(width))
	print("bitrate: "+ bitrate)
	print("Additional ending slice: " + str(finalslice))
	print("-" * 24)

slices = []
prevpos = 0
cycles = duration/sliceduration
step = 100/cycles
s=1
n=1

while n <= cycles and ((int(prevpos))+sliceduration < int(v.duration)):
	#s = random.randint(prevpos+1,round(int(v.duration)/100*(n*step)))
	s = random.randint(prevpos+sliceduration,round(int(v.duration)/100*(n*step)))
	if args.verbose:
		#print ("slice:", len(slices), "|| slice position:", s, "|| previous position:", prevpos, "|| duration:", int(v.duration), "|| percentage",str(round(s/int(v.duration)*100))+" % " )
		sys.stdout.write("\r" + "generating slices -- slice:" + str(len(slices)) + " || slice position:" + str(s) + " || previous position:" + str(prevpos) + " || duration:" + str(v.duration) + " || percentage " + str(round(s/int(v.duration)*100))+"%" )
		sys.stdout.flush()

	prevpos = s
	vo = v.subclip(s,s+sliceduration)
	vo = vo.resize(width=width)
	slices.append(vo)
	n = n + 1

# add last slice between prevpos + slice duration & total lenght - slice duration if possible
if finalslice and ((prevpos + sliceduration) <= (int(v.duration)-sliceduration)):
	# generates last slice - if it ends after the actual video ending just keep recalculating since prevpos + sliceduration < v.duration
	s = random.randint(prevpos + sliceduration,(int(v.duration)-sliceduration))
	#while s > int(v.duration-sliceduration):
	#	s = random.randint(prevpos + sliceduration,(int(v.duration)-sliceduration))

	prevpos = s

	if args.verbose:
		#print ("\nlast slice position:", s)			
		sys.stdout.write("\r" + "generating slices -- slice:" + str(len(slices)) + " || slice position:" + str(s) + " || previous position:" + str(prevpos) + " || duration:" + str(v.duration) + " || percentage 100%" )
		sys.stdout.write("\n")
	
	vo = v.subclip(s,s+sliceduration)
	vo = vo.resize(width=width)
	slices.append(vo)
else:
	sys.stdout.write("\n")

concatenate_videoclips(slices,method='compose').write_videofile(destfile, bitrate=bitrate, fps=fps)
