#!/usr/bin/env python

import random
from datetime import datetime, timedelta, time
import mimetypes
import os
import sys
import argparse
import math
from moviepy.editor import *

## Parse args
parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
#parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
parser.add_argument("-d", "--destfile", help="Destination video file, if unspecified append \"_trailer.webm\" to source filename", type=str)
parser.add_argument("-f", "--fps", help="Output videofile frames per second, if empty assumes source fps", type=int)
parser.add_argument("-w", "--width", help="Resolution width of the output file in pixels, if empty assumes 640", type=int)
parser.add_argument("-b", "--bitrate", help="Output videofile bitrate in \"x.x\" format, if empty assumes \"1.2M\"", type=float)

args = parser.parse_args()
sourcefile = args.sourcefile
video = VideoFileClip(sourcefile)
title = "|| video2trailer ||"

## Set default values whereas no argument was given
if not args.destfile:
        destfile=str(args.sourcefile)+'_trailer.webm'
else:
        destfile=args.destfile
if not args.fps:
        fps=int(video.fps)
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
#def show_info(sourcefile, destfile, fps, width, bitrate):
#		os.system('cls||clear')
#		print(("#" * 12) + " video2trailer " + ("#" * 12))
#		print("")
#		print("source file: " + sourcefile )
#		print("destination file: " + destfile)
#		#print("Configuration parameters")
#		print("-" * 24)
#		print("fps: "+ str(fps))
#		print("width: "+ str(width))
#		print("bitrate: "+ bitrate)
#		#print("-" * 24)
#		print("")
#		input("press ENTER go back to the pevious menu")

def video2filmstrip(sourcefile):
	os.system("video2filmstrip" + " " + sourcefile)

def xdg_open(sourcefile):
	os.system("xdg-open" + " " + sourcefile + " &> /dev/null &")

def convert_to_minutes(seconds):
	sec = timedelta(seconds=seconds)
	converted = datetime(1,1,1) + sec
	converted=converted.time()
	return  converted

def convert_to_seconds(time):
	converted = sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":"))))
	return int(converted)

def terminal_size():
	(columns,rows)=os.get_terminal_size()
	return (columns,rows)

def print_title():
	## let's clear the screen at first
	os.system('cls||clear')
	(columns,rows)=terminal_size()
	decorators=int((columns/2 - len(title)/2))
	print(("=" * decorators) + title + ("=" * decorators))

def print_separator():
	(columns,rows)=terminal_size()
	print("=" * columns)

def change_settings(destfile,fps,width,bitrate):
	settings_loop=False
	while not settings_loop:
		## Settings Menu
		print_title()
		print("")
		print("1) Change destination file (" + destfile + ")")
		print("2) Change fps (" + str(fps) + ")")
		print("3) Change width (" + str(width) + ")")
		print("4) Change bitrate (" + bitrate + ")")
		print("5) Back to main menu")
		print("")
		print_separator()

		settings_choice=input("# ")

		if settings_choice == "1":
			new_destfile = input("destination file: ")
			if new_destfile:
				destfile=new_destfile
		elif settings_choice == "2":
			new_fps = input("fps: ")
			if new_fps:
				fps=int(new_fps)
		elif settings_choice == "3":
			new_width = input("width: ")
			if new_width:
				width=int(new_width)
		elif settings_choice == "4":
			new_bitrate = input("bitrate: ")
			if new_bitrate:
				bitrate=new_bitrate
		elif settings_choice == "5":
			settings_loop=True
	return (destfile,fps,width,bitrate)

def generate_slices(video):
	# Initialize some variables - "steps" are slices position in percentage, where the overall source lenght is 100%
	slices = []
	
	print("Please select the overall duration for the clip in seconds")
	duration=int(input("# "))

	print("Please select the duration for each slice in seconds")
	sliceduration=int(input("# "))

	prevpos = 0
	cycles = duration/sliceduration
	step = 100/cycles
	s=1
	n=1
	
	while n <= cycles and ((int(prevpos))+sliceduration < int(video.duration)):
		s = random.randint(prevpos+sliceduration,round(int(video.duration)/100*(n*step)))
		#if args.verbose:
		#	sys.stdout.write("\r" + "generating slices -- slice:" + str(len(slices)) + " || slice position:" + str(s) + " || previous position:" + str(prevpos) + " || duration:" + str(v.duration) + " || percentage " + str(round(s/int(v.duration)*100))+"%" )
		#	sys.stdout.flush()
	
		prevpos = s
		slices.append([s,s+sliceduration])
		n = n + 1
	return slices
	
def print_slices(slices):
	(columns,rows)=os.get_terminal_size()
	menu_rows=15
	available_rows=int(rows)-menu_rows
	slice_columns=math.ceil(len(slices)/available_rows)
	slices_per_column=math.ceil(len(slices)/slice_columns)
	separator=" "*5

	print("Selected slices:")
	print("")
	
	available_rows=int(rows)-menu_rows
	slice_columns=math.ceil(len(slices)/available_rows)
	slices_per_column=math.ceil(len(slices)/slice_columns)
	separator="	"
	
#	print("slices: " + str(len(slices)))
#	print("rows: " + str(rows))
#	print("available rows: " + str(available_rows))
#	print("chars per row: " + str(columns))
#	print("number of pagination columns: " + str(slice_columns))
#	print("number of slices per column: " + str(slices_per_column))
	
	print_str=""
	print_out=[]
	
	for a in range(available_rows):
		print_str=""
		num=a

		for c in range(slice_columns):
			if num < len(slices):
				(ss,se)=slices[num]
				print_str=print_str + "#" + str(num) + " " + str(convert_to_minutes(ss)) + " - " + str(convert_to_minutes(se)) + separator
				num=num+(available_rows)
		print_out.append(print_str)

	for i in range(len(print_out)):
		if i <= available_rows:
			print(print_out[i])
		
		
def add_slice(slices):
	print("Please insert start time for the new subclip (hh:mm:ss)")
	ss=input("#")

	print("Please insert start time for the new subclip (hh:mm:ss)")
	se=input("#")

	slices.append([convert_to_seconds(ss),convert_to_seconds(se)])
	return slices
	
def change_slice(slices):
	print("Which slice would you like to change?")
	change_index=int(input("#"))

	print("Please insert start time for the new subclip (hh:mm:ss)")
	ss=input("#")

	print("Please insert start time for the new subclip (hh:mm:ss)")
	se=input("#")

	slices[change_index]=([convert_to_seconds(ss),convert_to_seconds(se)])
	return slices

def remove_slice(slices):
	print("Which slice would you like to remove?")
	change_index=int(input("#"))

	slices.pop(change_index)
	return slices
		
def slices_menu(video,slices):
	slices_loop=False
	while not slices_loop:
		## Slices Menu
		print_title()
		print("")
		print("1) Automagically generate slices")
		print("2) Add slice")
		print("3) Change slice")
		print("4) Remove slice")
		print("5) Remove all slices")
		print("6) Show preview")
		print("7) Back to main menu")
		print("")
		print_separator()
		
		if slices:
			print_slices(slices)


		slices_choice=input("# ")

		if slices_choice == "1":
			slices = generate_slices(video)
		elif slices_choice == "2":
			slices = add_slice(slices)
		elif slices_choice == "3":
			slices = change_slice(slices)
		elif slices_choice == "4":
			slices = remove_slice(slices)
		elif slices_choice  == "5":
			slices = []
		elif slices_choice  == "6":
			tempfile=destfile+str(random.randint(0,1024))+".webm"
			write_vo(video,slices,tempfile,12,240,"0.5M")
			input("press enter to resume editing")
			os.system("rm" + " " + tempfile)
			
		elif slices_choice == "7":
			slices_loop=True
	return slices

def write_vo(video,slices,destfile,fps,width,bitrate):
	vo_slices = []
	for i in range(len(slices)):
		(ss,se)=slices[i]
		vo = video.subclip(ss,se)
		vo = vo.resize(width=width)
		vo_slices.append(vo)
	
	### Tell MoviePy to concatenate the selected subclips that are in the slices[] array.
	concatenate_videoclips(vo_slices,method='compose').write_videofile(destfile, bitrate=bitrate, fps=fps)
	vo = ""
	
	if input("Would you like to watch the output file (y/n)") == "y":
		xdg_open(destfile)

## MAIN LOOP BEGINS HERE
subclip_num=1
quit_loop=False
slices = []

while not quit_loop:
	try:
		## Main Menu
		print_title()
		print("")
		print("1) Open with default media player")
		print("2) Create a video filmstrip")
		print("3) Edit clip")
		print("4) Write destination file")
		print("5) Change settings")
		print("6) Quit")
		print("")
		print_separator()
		
		choice=input("# ")
		
		if choice == "1":
			xdg_open(sourcefile)
		elif choice == "2":
			print("=" * 39)
			video2filmstrip(sourcefile)
		elif choice == "3":
			slices = slices_menu(video,slices)
		elif choice == "4":
			if slices:
				write_vo(video,slices,destfile,fps,width,bitrate)
			else:
				print("no defined slices!")
		#elif choice == "5":
			#show_info(sourcefile, destfile, fps, width, bitrate)
		elif choice == "5":
			(destfile,fps,width,bitrate) = change_settings(destfile,fps,width,bitrate)
		elif choice == "6" or choice == "Q" or choice == "q":
			os.system('cls||clear')
			quit_loop=True
	except KeyboardInterrupt:
			video = ""
			os.system('cls||clear')
			sys.exit()

#

