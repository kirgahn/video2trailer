#!/usr/bin/env python

import random
from datetime import datetime, timedelta, time
import mimetypes
import os
import sys
import argparse
import json
import math
#from moviepy.editor import *
import subprocess

## Parse args
parser = argparse.ArgumentParser()
parser.add_argument("sourcefile", help="Source video file", type=str)
#parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )
parser.add_argument("-d", "--destfile", help="Destination video file, if unspecified append \"_trailer.webm\" to source filename", type=str)
parser.add_argument("-f", "--fps", help="Output videofile frames per second, if empty assumes source fps", type=int)
parser.add_argument("-w", "--width", help="Resolution width of the output file in pixels, if empty assumes source width", type=int)
parser.add_argument("-b", "--bitrate", help="Output videofile bitrate in \"x.x\" format, if empty assumes \"0.6M\"", type=float)
parser.add_argument("-t", "--threads", help="Number of threads to use when encoding", type=int)
parser.add_argument("-s", "--targetsize", help="Target size in MB for the final compressed video", type=int)

args = parser.parse_args()
	
#### Functions #####

#### run video2filstrip ####
def video2filmstrip(sourcefile):
	try:
		os.system("video2filmstrip" + " \'" + sourcefile + "\'")
	except OSError as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### run video2trailer-compress ####
#def compress(destfile,target_size):
def compress(destfile,target_size,fps,width,threads):
	try:
		print("Rencoding at selected quality, please wait...")
		os.system("video2trailer-compress -s " + str(target_size) + " -f " + str(fps) + " -r " + str(width) + " -t " + str(threads) + " \'" + destfile + "\'")
	except OSError as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

	#confirm=input("Would you like to watch the output file (y/n)")
	#if confirm == "y" or confirm == "Y" or confirm == "":
	#	xdg_open(destfile+"."+str(target_size)+"M.webm")
	input("Encoding completed (Press ENTER to continue)")

#### open sourcefile with default player ####
def xdg_open(sourcefile):
	if sourcefile:
		try:
			os.system(player + " \'" + sourcefile + "\' &> /dev/null &")
		except OSError as err:
			print("OS error: {0}".format(err))

#### convert seconds to hours (hh:mm:ss) ####
def convert_to_minutes(seconds):
	sec = timedelta(seconds=seconds)
	converted = datetime(1,1,1) + sec
	converted=converted.time()
	return  converted

#### convert hours (hh:mm:ss) to seconds ####
def convert_to_seconds(time):
	converted = sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":"))))
	return int(converted)

#### retrieve terminal size ####
def terminal_size():
	(columns,rows)=os.get_terminal_size()
	return (columns,rows)

#### draw title on top of each menu ####
def print_title():
	## let's clear the screen at first
	os.system('cls||clear')
	(columns,rows)=terminal_size()
	decorators=int((columns/2 - len(title)/2))
	print(("=" * decorators) + title + ("=" * decorators))

#### draw a separator ####
def print_separator():
	(columns,rows)=terminal_size()
	print("=" * columns)

#### generate random slices ####
#def generate_slices(video):
def generate_slices(sourceduration):
	# Initialize some variables - "steps" are slices position in percentage, where the overall source lenght is 100%
	slices = []

	try:
		print("Please select the overall duration for the clip in seconds")
		duration=int(input("# "))
	
		print("Please select the duration for each slice in seconds")
		sliceduration=int(input("# "))
	
		prevpos = 0
		cycles = duration/sliceduration
		step = 100/cycles
		s=1
		n=1
		
		#while n <= cycles and ((int(prevpos))+sliceduration < int(video.duration)):
		while n <= cycles and ((int(prevpos))+sliceduration < int(sourceduration)):
			s = random.randint(prevpos+sliceduration,round(int(sourceduration)/100*(n*step)))
			prevpos = s
			slices.append([s,s+sliceduration])
			n = n + 1
		return slices
	except (OSError, ValueError) as err:
		print("Error: {0}".format(err))
		input("Duration values can only be expressed in integers. (Press ENTER to continue)")


	
def print_slices(slices):
	(columns,rows)=os.get_terminal_size()
	menu_rows=20
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
		
def add_slice(slices,sourceduration):
	try:
		print("Please insert start time for the new subclip (hh:mm:ss)")
		ss=convert_to_seconds(input("#"))

		print("Please insert end time for the new subclip (hh:mm:ss)")
		se=convert_to_seconds(input("#"))

		#if (ss < round(video.duration)) and (se < round(video.duration)):
		if (ss < round(sourceduration)) and (se < round(sourceduration)):
			slices.append([ss,se])
		else:
                	input("Slices can't start/end after the end of the source video. (Press ENTER to continue)")

	except ValueError as err:
                print("Error: {0}".format(err))
                input("Specified time values are incorrect. (Press ENTER to continue)")

	return slices

def insert_slice(slices,sourceduration):
	try:

		print("In which position would you like to add a new subclip?")
		newpos=int(input("#"))
	
		if not (newpos > len(slices)):
			print("Please insert start time for the new subclip (hh:mm:ss)")
			ss=convert_to_seconds(input("#"))
	
			print("Please insert end time for the new subclip (hh:mm:ss)")
			se=convert_to_seconds(input("#"))
	
			if (ss < round(sourceduration)) and (se < round(sourceduration)):
				slices.insert(newpos,[ss,se])
			else:
	                        input("Slices can't start/end after the end of the source video. (Press ENTER to continue)")
		else:
			input("Invalid slice position selected. (Press ENTER to continue)")
	
	except ValueError as err:
                print("Error: {0}".format(err))
                input("Either specified time values are incorrect or slice position is invalid. (Press ENTER to continue)")

	return slices

def change_slice(slices):
	try:
		print("Which slice would you like to change?")
		change_index=int(input("#"))
		if not (change_index > len(slices)):

			print("Please insert start time for the new subclip (hh:mm:ss)")
			ss=convert_to_seconds(input("#"))
	
			print("Please insert end time for the new subclip (hh:mm:ss)")
			se=convert_to_seconds(input("#"))
	
			if (ss < round(sourceduration)) or (se < round(sourceduration)):
				slices[change_index]=(ss,se)
			else:
	                        input("Slices can't start/end after the end of the source video. (Press ENTER to continue)")
		else:
                        input("Invalid slice position selected. (Press ENTER to continue)")

	except ValueError as err:
                print("Error: {0}".format(err))
                input("Either specified time values are incorrect or slice position is invalid. (Press ENTER to continue)")

	return slices

def remove_slice(slices):
	try:
		print("Which slice would you like to remove?")
		change_index=int(input("#"))
		if not (change_index > len(slices)):
			slices.pop(change_index)
		else:
                        input("Invalid slice position selected. (Press ENTER to continue)")

	except ValueError as err:
                print("Error: {0}".format(err))
                input("Slice position is invalid. (Press ENTER to continue)")
	return slices

#def write_vo(video,slices,destfile,sourcefps,fps,sourcewidth,width,bitrate,target_size):
#	try:
#		vo_slices = []
#		for i in range(len(slices)):
#			(ss,se)=slices[i]
#			vo = video.subclip(ss,se)
#			#### on first encoding pass we don't resize the video anymore 
#			#### that'll happen on pass2 (when calling video2trailer-compress)
#			#vo = vo.resize(width=width)
#			vo_slices.append(vo)
#
#		### Tell MoviePy to concatenate the selected subclips that are in the slices[] array.
#		concatenate_videoclips(vo_slices,method='compose').write_videofile(destfile,bitrate=bitrate,fps=sourcefps,threads=threads)
#		vo = ""
#
#
#		confirm=input("Would you like to watch the output file (y/n)")
#		if confirm == "y" or confirm == "Y" or confirm == "":
#			xdg_open(destfile)
#
#		if int(target_size) > 0:
#			compress(destfile,target_size,fps,width,threads)
#		
#	except (ValueError, OSError) as err:
#                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def ffmpeg_write_vo(sourcefile,slices,destfile,sourcefps,fps,sourcewidth,width,sourceheight,sourcebitrate,bitrate,target_size):
	try:
		#### encoder = either libx264 or libvpx
		encoder="libvpx"
		vo_slices = []

		#### with libvpx options
		ffmpeg_command="ffmpeg -stats -v quiet -i " + "\'" + sourcefile + "\'" + " -y -codec:v " + encoder + "  -quality good -cpu-used 0  -b:v " + str(sourcebitrate) + "k -qmin 10 -qmax 42 -s " + str(sourcewidth) + "x" + str(sourceheight) + " -threads " + str(threads) + " -filter_complex \""

		#### with libx264 options
		#### ffmpeg_command="ffmpeg -stats -v quiet -i " + "\'" + sourcefile + "\'" + " -y -codec:v " + encoder + " -b:v " + str(sourcebitrate) + "k -qmin 10 -qmax 42 -s " + str(sourcewidth) + "x" + str(sourceheight) + " -threads " + str(threads) + " -filter_complex \""

		for i in range(len(slices)):
			(ss,se)=slices[i]
			ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[v" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "

		for i in range(len(slices)):
			ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
	
		ffmpeg_command=ffmpeg_command + "concat=n=" + str(len(slices)) + ":v=1:a=1[out]\" "
		ffmpeg_command=ffmpeg_command + "-map \"[out]\" " + "\'" + destfile + "\'"
		#print("#### ffmpeg_command: " + "\"" + ffmpeg_command + "\"")

		try:
			os.system(ffmpeg_command)
		except OSError as err:
			input("Error: {0}".format(err) + " (Press ENTER to continue)")

#		confirm=input("Would you like to watch the output file (y/n)")
#		if confirm == "y" or confirm == "Y" or confirm == "":
#			xdg_open(destfile)

		if int(target_size) > 0:
			compress(destfile,target_size,fps,width,threads)
		
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

#def write_preview(video,slices,destfile,fps,width,bitrate):
#	try:
#		vo_slices = []
#		for i in range(len(slices)):
#			(ss,se)=slices[i]
#			subclip = video.subclip(ss,se)
#
#			txt_clip = TextClip(str(i),fontsize=30,color='black',stroke_color='black',stroke_width=2)
#			if int(subclip.duration) < 2:
#				txt_clip = txt_clip.set_pos(('left','top')).set_duration(1)
#			elif int(subclip.duration) < 3:
#				txt_clip = txt_clip.set_pos(('left','top')).set_duration(2)
#			else:
#				txt_clip = txt_clip.set_pos(('left','top')).set_duration(3)
#
#			subclip = subclip.resize(width=width)
#			vo = CompositeVideoClip([subclip, txt_clip])
#			vo_slices.append(vo)
#
#		### Tell MoviePy to concatenate the selected subclips that are in the slices[] array.
#		concatenate_videoclips(vo_slices,method='compose').write_videofile(destfile,bitrate=bitrate,fps=fps,threads=threads)
#		vo = ""
#		
#		confirm=input("Would you like to watch the output file (y/n)")
#		if confirm == "y" or confirm == "Y" or confirm == "":
#			xdg_open(destfile)
#			input("press enter to resume editing")
#		os.system("rm" + " " + "\'" + destfile + "\'" )
#
#	except (ValueError, OSError) as err:
#                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def write_preview(sourcefile,slices,destfile,fps,height,width,bitrate,threads):

	ext="mp4"
	#encoder="libx264" ### either x264/mp4 or libvpx/webm
	encoder="libvpx" ### either x264/mp4 or libvpx/webm
	font="DejaVuSans-Bold.ttf"
	fontsize=100
	opts="-cpu-used 8 -threads " + str(threads)
	#ffmpeg -i videoplayback.mp4 -filter_complex "drawtext=fontsize=50:fontcolor=black:fontfile=arial.ttf:text=yoyo[out]" -map "[out]" -f webm -cpu-used 8 -threads 4  drawtext.webm
	#try:
	vo_slices = []

#	for i in range(len(slices)):
#		(ss,se)=slices[i]
#		#ffmpeg -stats -v quiet 
#		cmd="ffmpeg -stats -v quiet -i \'" + sourcefile + "\' -y -codec:v " + encoder + " -b:v " + str(bitrate) + " -s " + str(width) + "x" + str(height) + " -threads " + str(threads) + " -filter_complex \"[0:v]trim="+ str(ss) 	+ ":" + str(se) + ",setpts=PTS-STARTPTS[todraw];[todraw]drawtext=fontsize=50:fontcolor=black:fontfile=arial.ttf:text=" + str(i) + "[out]\" -map \"[out]\" -f " + ext + " " + opts + " " + destfile + "_" + str(i) + "." + ext  
#
#		#DEBUG
#		#print(cmd)
#		print("Encoding tmp file #" + str(i) + ": \"" + destfile + "_" + str(i) + "." + ext+ "\"")
#		subprocess.call(cmd,shell=True)
#	
#	cmd="ffmpeg -stats -v quiet -i \"concat:"
#	for i in range(len(slices)):
#		cmd=cmd + destfile + "_" + str(i) + "." + ext + "|"
#		#### let's remove the last character added since it's uneeded after the last filename
#		cmd=cmd[:-1]
#		cmd=cmd + "\" -c copy -a copy " + destfile + "." + ext
#
#		### DEBUG 
#		print(cmd)
#		print("Encoding tmp file #" + str(i) + " \"" + destfile + "_" + str(i) + "." + ext+ "\"")
#		subprocess.call(cmd,shell=True)

	print("Encoding tmp file: \"" + destfile + "\"")
# 	"ffmpeg -stats -v quiet -i \"concat:"
	ffmpeg_command="ffmpeg -stats -v quiet -i \'" + sourcefile + "\' -y -codec:v " + encoder + " -b:v " + str(bitrate) + " -s " + str(width) + "x" + str(height) + " -threads " + str(threads) + " -filter_complex \""
	for i in range(len(slices)):
		(ss,se)=slices[i]
		ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[todraw" + str(i) + "]; "
		ffmpeg_command=ffmpeg_command + "[todraw" + str(i) + "]drawtext=fontsize="+ str(fontsize) + ":fontcolor=black:fontfile=" + font + ":text=" + str(i) + "[v" + str(i) + "]; "
		ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "
	
	for i in range(len(slices)):
		ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
	
	ffmpeg_command=ffmpeg_command + "concat=n=" + str(len(slices)) + ":v=1:a=1[out]\" "
	ffmpeg_command=ffmpeg_command + "-map \"[out]\" " + "\'" + destfile + "\'"

	subprocess.call(ffmpeg_command,shell=True)

#	### DEBUG 
#	print(ffmpeg_command)

	confirm=input("Would you like to watch the output file (y/n)")
	if confirm == "y" or confirm == "Y" or confirm == "":
		xdg_open(destfile)
		input("press enter to resume editing")
	os.system("rm" +  destfile)
#	os.system("rm" + " " + "\'" + destfile + "." + ext + "\'" )

#	except (ValueError, OSError) as err:
#                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def change_settings(destfile,fps,width,bitrate,threads,target_size):
	try:
		settings_loop=False
		while not settings_loop:
			## Settings Menu
			print_title()
			print("")
			print("1) (O)utput Filename (" + destfile + ")")
			print("2) (F)ps (" + str(fps) + ")")
			print("3) (W)idth (" + str(width) + ")")
			print("4) (B)itrate (" + bitrate + ")")
			print("5) encoder (T)hreads (" + str(threads) + ")")
			print("6) (C)ompressed video target size (0 means no further compression) (" + str(target_size) + ")")
			print("7) (Quit) to main menu")
			print("")
			print_separator()
	
			settings_choice=input("# ")
	
			if any(q in settings_choice for q in ["1","O","o"]):
				new_destfile = input("destination file: ")
				if new_destfile:
					destfile=new_destfile
			elif any(q in settings_choice for q in ["2","F","f"]):
				new_fps = input("fps: ")
				if new_fps:
					fps=int(new_fps)
			elif any(q in settings_choice for q in ["3","W","w"]):
				new_width = input("width: ")
				if new_width:
					width=int(new_width)
			elif any(q in settings_choice for q in ["4","B","b"]):
				new_bitrate = input("bitrate: ")
				if new_bitrate:
					bitrate=new_bitrate
			elif any(q in settings_choice for q in ["5","T","t"]):
				new_threads = input("threads: ")
				threads=new_threads
			elif any(q in settings_choice for q in ["6","C","c"]):
				new_target_size = input("target size: ")
				target_size=new_target_size
			elif any(q in settings_choice for q in ["7","Q","q"]):
				settings_loop=True
		return (destfile,fps,width,bitrate,threads,target_size)
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")
		
def slices_menu(sourcefile,slices):
	try:
		slices_loop=False
		while not slices_loop:
			## Slices Menu
			print_title()
			print("")
			print("0) (G)enerate slices")
			print("1) (A)dd slice")
			print("2) (I)nsert slice")
			print("3) (C)hange slice")
			print("4) (R)emove slice")
			print("5) (D)elete all slices")
			print("6) (S)lice preview")
			print("7) (P)review clip")
			print("8) (W)rite destination file")
			print("9) (Q)uit to main menu")
			print("")
			print_separator()
			
			if slices:
				print_slices(slices)
	
	
			slices_choice=input("# ")
	
			if any(q in slices_choice for q in ["0","G","g"]):
				new_slices=[]
				new_slices = generate_slices(sourceduration)
				if new_slices:
					slices = new_slices
			elif any(q in slices_choice for q in ["1","A","a"]):
				slices = add_slice(slices,sourceduration)
			elif any(q in slices_choice for q in ["2","I","i"]):
				slices = insert_slice(slices,sourceduration)
			elif any(q in slices_choice for q in ["3","C","c"]):
				if slices:
					slices = change_slice(slices,sourceduration)
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["4","R","r"]):
				if slices:
					slices = remove_slice(slices)
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["5","D","d"]):
				if slices:
					sure = input("Confirm operation (y/n)")
					if sure == "y" or sure == "Y" or sure == "":
						slices = []
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["6","S","s"]):
				if slices:
					try:
						print("which slice would you like to preview? (slice index)")
						which_slice=int(input("#"))
						subslice=[]
						subslice.append(slices[which_slice])
						tempfile=destfile+str(random.randint(0,1024))+".webm"
						write_preview(sourcefile,subslice,tempfile,20,240,320,"0.5M",threads)
					except (ValueError, OSError) as err:
				                input("Error: {0}".format(err) + " (Press ENTER to continue)")
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["7","P","p"]):
				if slices:
					try:
						tempfile=destfile+str(random.randint(0,1024))+".webm"
						write_preview(sourcefile,slices,tempfile,20,240,320,"0.5M",threads)
					except (ValueError, OSError) as err:
				                input("Error: {0}".format(err) + " (Press ENTER to continue)")
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["8","W","w"]):
				if slices:
					#### legacy call: write_vo(video,slices,destfile,sourcefps,fps,sourcewidth,width,bitrate,target_size)
					#### targetfile is destfile less the file extension (fir thing after "." starting from 
					#### the right plus resolution and extension: "_WIDTHxHEIGHT.webm"
					#### ext= either .mp4 or .webm
					ext=".webm" #either .mp4 or .webm
					targetfile=destfile.rsplit( "." ,1 )[0]+"_"+str(sourcewidth)+"x"+str(sourceheight)+ext
					print("targetfile: " +targetfile)
					ffmpeg_write_vo(sourcefile,slices,targetfile,sourcefps,fps,sourcewidth,width,sourceheight,sourcebitrate,bitrate,target_size)
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["9","Q","q"]):
				slices_loop=True
		return slices
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### Load State ####
def load_state(state_file_name):
	line_number = 0
	slices = []

	try:
		with open(state_file_name, encoding='utf-8') as state_file:
			## skip first two lines
			state_file.readline().strip()
			state_file.readline().strip()
			## the third line is to ignore the legacy video variable
			state_file.readline().strip()
				
			#video = VideoFileClip(state_file.readline().rstrip())
			destfile = state_file.readline().rstrip()
			fps = int(state_file.readline().rstrip())
			#bitrate = (state_file.readline().rstrip() + "M")
			bitrate = (state_file.readline().rstrip())
			width = int(state_file.readline().rstrip())
			threads = int(state_file.readline().rstrip())
			target_size = int(state_file.readline().rstrip())
			
			## skip three lines
			state_file.readline().rstrip()
			state_file.readline().rstrip()
			state_file.readline().rstrip()
	
			for a_line in state_file:
				line_number += 1
				slice_line=a_line.rstrip()
				ss=convert_to_seconds(slice_line.split('-')[0])
				se=convert_to_seconds(slice_line.split('-')[1])
				slices.append([ss,se])

		#return (video,destfile,fps,width,bitrate,threads,target_size,slices)
		return (destfile,fps,width,bitrate,threads,target_size,slices)

	except (ValueError, OSError) as err:
		print("Can't parse state file!")
		input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### Save State ####
def save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices):
	line_number = 0
	
	if sourcefile.find(".v2t")>0:
		state_file_name=sourcefile
		sourcefile=os.path.splitext(sourcefile)[0]
	else:
		state_file_name=sourcefile + ".v2t"

	try:
		with open(state_file_name,mode='w', encoding='utf-8') as state_file:
			state_file.write("settings"+"\n")
			state_file.write("-"*12 +"\n")

			state_file.write(sourcefile+"\n")
			state_file.write(destfile+"\n")
			state_file.write(str(fps)+"\n")
			state_file.write(bitrate+"\n")
			state_file.write(str(width)+"\n")
			state_file.write(str(threads)+"\n")
			state_file.write(str(target_size)+"\n")
			
			state_file.write(""+"\n")
			state_file.write("slices"+"\n")
			state_file.write("-"*12+"\n")
	
			for a_line in range(len(slices)):
				(ss,se)=slices[a_line]
				ss=convert_to_minutes(ss)
				se=convert_to_minutes(se)
				state_file.write(str(ss)+"-"+str(se)+"\n")
				line_number += 1

		#return (video,destfile,fps,width,bitrate,threads,slices)
		input("State saved correctly (Press ENTER to continue)")

	except (ValueError, OSError) as err:
		print("Can't parse state file!")
		input("Error: {0}".format(err) + " (Press ENTER to continue)")


#### Info Menu ####
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

def parse_ffprobe_info(sourcefile):
	#### Ask ffmpeg to provide a json with info about the video that we're going to parse
	stream_info = subprocess.getoutput('ffprobe -v quiet -print_format json -show_format -show_streams \'' + sourcefile + "\'")
	print(stream_info)
	j = json.loads(stream_info)
	
	#### ['streams'] is an array that includes audio and video streams
	#### therefre we look for the position of the first video stream
	for i  in range(len(j['streams'])):
	        codec_type=j['streams'][i]['codec_type']
	        if codec_type=='video':
	                video_stream_pos=i
	
	sourcewidth=j['streams'][video_stream_pos]['width']
	sourceheight=j['streams'][video_stream_pos]['height']
	sourcefps=int(j['streams'][video_stream_pos]['r_frame_rate'][:2])
	sourcebitrate=int(j['format']['bit_rate'])/1000
	sourceduration=math.floor(float(j['format']['duration']))
	
	return (sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)

#### Parse arguments and load state eventually
title = "|| video2trailer ||"
#player="xdg-open"
#player="vlc"
player="mplayer"

sourcefile = args.sourcefile

if sourcefile.lower().endswith(('.v2t')):
	state_file_name=sourcefile
	(destfile,fps,width,bitrate,threads,target_size,slices) = load_state(state_file_name)
	sourcefile=os.path.splitext(sourcefile)[0]
	
	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)

else:
	state_file_name=sourcefile + ".v2t"
	#video = VideoFileClip(sourcefile)
	#sourcewidth=int(video.w)
	#sourceheight=int(video.h)
	#sourcefps=int(video.fps)

	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)

	try:
		with open(state_file_name,encoding='utf-8'):
			#(video,destfile,fps,width,bitrate,threads,target_size,slices) = load_state(state_file_name)
			(destfile,fps,width,bitrate,threads,target_size,slices) = load_state(state_file_name)
	except (ValueError, OSError):

		slices = []

		## Set default values whereas no argument was given
		if not args.destfile:
		        destfile=str(args.sourcefile)+'_trailer.webm'
		else:
		        destfile=args.destfile
		if not args.fps:
		        fps=sourcefps
		else:
		        fps=args.fps
		if not args.width:
			width=sourcewidth
		else:
		        width=args.width
		if not args.bitrate:
		        bitrate="0.6M"
		else:
		        bitrate=sourcebitrate+"M"
		
		if not args.threads:
			threads=4
		else:
			threads=args.threads

		if not args.targetsize:
			target_size=4
		else:
			target_size=args.targetsize


## MAIN LOOP BEGINS HERE
#subclip_num=1
quit_loop=False

try:
	while not quit_loop:
	
		## Main Menu
		print_title()
		print("")
		print("1) (O)pen with default media player")
		print("2) (F)ilmstrip")
		print("3) (E)dit clip")
		#print("4) Write destination file")
		print("4) (C)hange settings")
		print("5) (S)ave state file")
		print("6) co(M)press destination file")
		print("7) (Q)uit")
		print("")
		print_separator()
		

		choice=input("# ")
		
		if any(q in choice for q in ["1","O","o"]):
			xdg_open(sourcefile)
		elif any(q in choice for q in ["2","F","f"]):
			print_separator()
			video2filmstrip(sourcefile)
		elif any(q in choice for q in ["3","E","e"]):
			slices = slices_menu(sourcefile,slices)
		elif any(q in choice for q in ["4","c","c"]):
			(destfile,fps,width,bitrate,threads,target_size) = change_settings(destfile,fps,width,bitrate,threads,target_size)
		elif any(q in choice for q in ["5","S","s"]):
			save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices)
		elif any(q in choice for q in ["6","M","m"]):
			compress(destfile)
		elif any(q in choice for q in ["7","Q","q"]):
			os.system('cls||clear')
			quit_loop=True
except KeyboardInterrupt:
			#video = ""
			os.system('cls||clear')
			sys.exit()
except (ValueError, OSError) as err:
	input("Error: {0}".format(err) + " (Press ENTER to continue)")
