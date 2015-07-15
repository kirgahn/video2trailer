#!/usr/bin/env python
# converts/extracts slices from videos to webm format
# incremental version 0.7

import os
import argparse
from moviepy.editor import *

parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
parser.add_argument("destfile", help="Destination video file", type=str)
parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
parser.add_argument("-s", "--starttime", help="Begin to cut video file at this time given a \"00:00:00\" time format. If empty assume \"00:00:00\"", type=str)
parser.add_argument("-e", "--endtime", help="Cut video file from starttime to this time given a \"00:00:00\" time format. If empty assume video ending", type=str)
parser.add_argument("-r", "--resolution", help="Output videofile width in pixels, if empty assumes 640", type=int) 
parser.add_argument("-f", "--fps", help="Output videofile frames per second, if empty assumes source fps", type=int)
parser.add_argument("-b", "--bitrate", help="Output videofile bitrate in \"x.x\" format, if empty assumes \"1.2M\"", type=float)
parser.add_argument("-m", "--mute", help="Removes audio from videoclip, if not specified keeps audio", action="store_true")

args = parser.parse_args()

sourcefile=args.sourcefile
destfile=args.destfile
resolution=args.resolution
fps=args.fps

v = VideoFileClip(sourcefile)

if not args.starttime:
	starttime=0
	if args.verbose:
		print("Assuming starttime is beginning of source file")
else:
	starttime=sum(int(x) * 60 ** i for i,x in enumerate(reversed(args.starttime.split(":"))))
		
if not args.endtime:
	endtime=v.duration
	if args.verbose:
		print("Assuming endtime is ending of source file")
else:
	endtime=sum(int(x) * 60 ** i for i,x in enumerate(reversed(args.endtime.split(":"))))
  
if not args.resolution:
	resolution=720
	if args.verbose:
		print("Assuming resolution width of: " + str(resolution))

if not args.fps:
	fps=v.fps
	if args.verbose:
		print("Assuming FPS: " + str(v.fps))

if not args.bitrate:
	bitrate="1.2M"
	if args.verbose:
		print("Assuming bitrate: " + bitrate)
else:
	bitrate=str(args.bitrate)+"M"

if args.verbose:
	print("sourcefile: "+ sourcefile)
	print("starttime: "+ str(starttime))
	print("endtime: "+ str(args.endtime))
	print("destfile: "+ args.destfile+".webm")
	print("resolution: "+ str(resolution))
	print("fps: "+ str(fps))
	print("bitrate: "+ bitrate)


vo = v.subclip(starttime,endtime)
vo = vo.resize(width=resolution)

if args.mute:
	#print("no audio")
	vo = vo.without_audio()

vo.write_videofile(destfile+".webm",fps=fps, bitrate=bitrate)

############################################################
