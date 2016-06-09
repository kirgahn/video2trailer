#!/usr/bin/env python

import random
import datetime
import mimetypes
import os
import sys
import argparse
from moviepy.editor import *

## Parse args
parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
#parser.add_argument("-s", "--sliceduration", help="Duration of each slice in seconds, if unpecified assume one second", type=int)
#parser.add_argument("-dt", "--duration", help="Total duration of output file, if unspecified assume 30 seconds", type=int)
parser.add_argument("-d", "--destfile", help="Destination video file, if unspecified append \"_trailer.webm\" to source filename", type=str)
parser.add_argument("-f", "--fps", help="Output videofile frames per second, if empty assumes source fps", type=int)
parser.add_argument("-w", "--width", help="Resolution width of the output file in pixels, if empty assumes 640", type=int)
parser.add_argument("-b", "--bitrate", help="Output videofile bitrate in \"x.x\" format, if empty assumes \"1.2M\"", type=float)
#parser.add_argument("-fs", "--finalslice", help="Additional final slice, good if you need to catch the last seconds; if empty assume no ", action="store_true" )

args = parser.parse_args()
sourcefile = args.sourcefile
v = VideoFileClip(sourcefile)

## Set default values whereas no argument was given
if not args.destfile:
        destfile=str(args.sourcefile)+'_trailer.webm'
else:
        destfile=args.destfile
if not args.fps:
        fps=int(v.fps)
else:
        fps=args.fps
if not args.width:
        width=640
else:
        width=args.width
if not args.bitrate:
        bitrate="1.2M"
else:
        bitrate=str(args.bitrate)+"M"

## Define Functions
def show_info(sourcefile, destfile, fps, width, bitrate):
		os.system('cls||clear')
		print(("#" * 12) + " video2trailer " + ("#" * 12))
		print("")
		print("source file: " + sourcefile )
		print("destination file: " + destfile)
		#print("Configuration parameters")
		print("-" * 24)
		print("fps: "+ str(fps))
		print("width: "+ str(width))
		print("bitrate: "+ bitrate)
		#print("-" * 24)
		print("")
		input("press ENTER go back to the pevious menu")

def video2filmstrip(sourcefile):
	os.system("video2filmstrip" + " " + sourcefile)

def xdg_open(sourcefile):
	os.system("xdg-open" + " " + sourcefile + "&> /dev/null &")

def change_settings(destfile,fps,width,bitrate):
	settings_loop=False
	while not settings_loop:
		## Settings Menu
		os.system('cls||clear')
		print(("=" * 12) + "<|| video2trailer ||> " + ("=" * 12))
		#print("")
		#print ("\"" + sourcefile + "\"")
		#print("")
		#print("=" * 39)
		print("")
		print("1) Change destination file (" + destfile + ")")
		print("2) Change fps (" + str(fps) + ")")
		print("3) Change width (" + str(width) + ")")
		print("4) Change bitrate (" + bitrate + ")")
		print("5) Back to main menu")
		print("")
		print("=" * 39)

		settings_choice=input("# ")

		if settings_choice == "1":
			new_destfile = input("destination file: ")
			if new_destfile:
				destfile=new_destfile
		elif settings_choice == "2":
			new_fps = input("fps: ")
			if new_fps:
				fps=new_fps
		elif settings_choice == "3":
			new_width = input("width: ")
			if new_width:
				width=new_width
		elif settings_choice == "4":
			new_bitrate = input("bitrate: ")
			if new_bitrate:
				bitrate=new_bitrate
		elif settings_choice == "5":
			settings_loop=True
	return (destfile,fps,width,bitrate)

def generate_slices():
	# Initialize some variables - "steps" are slices position in percentage, where the overall source lenght is 100%
	slices = []
	prevpos = 0
	cycles = duration/sliceduration
	step = 100/cycles
	s=1
	n=1
	
	## One loop for each cycle IF the next estimated slice position doesn't end after the overall clip duration.
	## If that happens, MoviePy will complain and quit, leaving temp files behind.
	## stdout.write and stdout.flush are used with \r (return at the beginning of the line) to write info on the
	## same line. 
	## vo (video out) is composed of source video subclips defined by the randomized  start of a slice (s) plus
	## the defined slice duration.
	while n <= cycles and ((int(prevpos))+sliceduration < int(v.duration)):
		s = random.randint(prevpos+sliceduration,round(int(v.duration)/100*(n*step)))
		if args.verbose:
			sys.stdout.write("\r" + "generating slices -- slice:" + str(len(slices)) + " || slice position:" + str(s) + " || previous position:" + str(prevpos) + " || duration:" + str(v.duration) + " || percentage " + str(round(s/int(v.duration)*100))+"%" )
			sys.stdout.flush()
	
		prevpos = s
		vo = v.subclip(s,s+sliceduration)
		vo = vo.resize(width=width)
		slices.append(vo)
		n = n + 1
	
	## Add last slice between the (previous postion + slice duration) & (total lenght - slice duration). 
	## If that isn't possible becuse the slice would end after the source file ending then just skip the 
	## thing altogether. If that happens, the logged "percentage" never reaches 100%. 
	## Also, stdout.write a newline (\n) to avoid MoviePy messages be appended to the previous line.
	if finalslice and ((prevpos + sliceduration) <= (int(v.duration)-sliceduration)):
		s = random.randint(prevpos + sliceduration,(int(v.duration)-sliceduration))
		if args.verbose:
			sys.stdout.write("\r" + "generating slices -- slice:" + str(len(slices)) + " || slice position:" + str(s) + " || previous position:" + str(prevpos) + " || duration:" + str(v.duration) + " || percentage 100%" )
			sys.stdout.write("\n")
		
		vo = v.subclip(s,s+sliceduration)
		vo = vo.resize(width=width)
		slices.append(vo)
	else:
		sys.stdout.write("\n")

def slices_menu(slices):
	slices_loop=False
	while not slices_loop:
		## Slices Menu
		os.system('cls||clear')
		print(("=" * 12) + "<|| video2trailer ||> " + ("=" * 12))
		#print("")
		#print ("\"" + sourcefile + "\"")
		#print("")
		#print("=" * 39)
		print("")
		print("1) Automagically generate slices")
		print("2) Add slice")
		print("3) Change slice")
		print("4) Remove slice")
		print("5) Show preview")
		print("6) Back to main menu")
		print("")
		print("=" * 39)
		
		if slices:
			print("Selected slices:")
			print("")
			
			#i = 0
			#for i in len(slices):
				#print("#" + str(i) + ": " slices[i]

		#slices_choice=input("# ")

		#if slices_choice == "1":
		#elif slices_choice == "2":
		#elif slices_choice == "3":
		#elif settings_choice == "4":
		#elif settings_choice == "5":
		#elif settings_choice == "6":
			#slices_loop=True
	return (destfile,fps,width,bitrate)

## MAIN LOOP BEGINS HERE
subclip_num=1
quit_loop=False
slices = []

while not quit_loop:
	try:
		## let's clear the screen at first
		os.system('cls||clear')
	
		## Main Menu
		print(("=" * 12) + "<|| video2trailer ||> " + ("=" * 12))
		print("")
		print("1) Open with default media player")
		print("2) Create a video filmstrip")
		print("3) Edit clip")
		print("4) Write destination file")
		print("5) Show output video info")
		print("6) Change video settings")
		print("7) Quit")
		print("")
		print("=" * 39)
		
		choice=input("# ")
		
		if choice == "1":
			xdg_open(sourcefile)
		elif choice == "2":
			print("=" * 39)
			video2filmstrip(sourcefile)
		elif choice == "3":
			#slice_start = input("enter start time for subclip number " + str(subclip_num) + ": ")
			#slice_end = input("enter end time for subclip number " + str(subclip_num) + ": ")
			slices = slices_menu(slices)
		elif choice == "4":
			print("STUB")
		elif choice == "5":
			print("STUB")
		elif choice == "6":
			show_info(sourcefile, destfile, fps, width, bitrate)
		elif choice == "7":
			(destfile,fps,width,bitrate) = change_settings(destfile,fps,width,bitrate)
		elif choice == "8" or choice == "Q" or choice == "q":
			os.system('cls||clear')
			quit_loop=True
	except KeyboardInterrupt:
			v = ""
			os.system('cls||clear')
			sys.exit()

#
### Tell MoviePy to concatenate the selected subclips that are in the slices[] array.
#concatenate_videoclips(slices,method='compose').write_videofile(destfile, bitrate=bitrate, fps=fps)
