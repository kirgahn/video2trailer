#!/usr/bin/env python

import random
from datetime import datetime, timedelta
import time
import mimetypes
import os
import sys
import argparse
import json
import math
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

def validate_string(test_str):
        allowed_chars="0123456789.:"
        return all(i in allowed_chars for i in test_str)

def time_input():
	#let's define some unicodes
	carriage_return='\x0d'
	backspace='\x7f'
	erase_line='\x1b[2K'
	cursor_up = '\x1b[1A'

	char_buffer=""
	while len(char_buffer)<12:
		try:
			char=getchar()
			if not char==carriage_return:
				if not char==backspace:
					if validate_string(char):
						if len(char_buffer)==2:
							char_buffer=char_buffer+":"
							print(":",end="",flush=True)
						if len(char_buffer)==5:
							char_buffer=char_buffer+":"
							print(":",end="",flush=True)
						#if len(char_buffer)==5:
						if len(char_buffer)==8:
							char_buffer=char_buffer+"."
							print(".",end="",flush=True)
						char_buffer=char_buffer+char
						print(char,end="",flush=True)
				else:
	                                if len(char_buffer)>=0:
	                                        char_buffer=char_buffer[:-1]
	                                        print(erase_line + cursor_up,flush=True)
	                                        print(char_buffer,end="",flush=True)
			else:
				print("\n")
				if char_buffer[-1:]=="." or char_buffer[-1:]==":":
					char_buffer=char_buffer[:-1]
				return(char_buffer)
		except (ValueError, OSError) as err:
			logger("Error: {0}".format(err))
			print("Error: {0}".format(err) + " (Press any key to continue)")
	print("\n")
	return(char_buffer)

def logger(logmessage):
	logfile="./v2t.log"
	now=datetime.now()
	now=now.strftime('%Y-%m-%d-%H:%M:%S.%f')[:-3]

	try:
		with open(logfile,mode='a', encoding='utf-8') as log_file:
			log_file.write("[" + now + "] - " + logmessage+"\n")
		log_file.close()
	except (ValueError, OSError) as err:
		print("Can't write log file!")
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

#### define getchar to get only a single char as input without waiting for a newline
def getchar():
	import termios
	import sys, tty
	def _getch():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch
	return _getch()

#### run video2filstrip ####
def video2filmstrip(sourcefile):
	try:
		logger("Running video2filmstrip")
		os.system("v2f" + " \'" + sourcefile + "\'")
	except OSError as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

#### open sourcefile with default player ####
def xdg_open(sourcefile):
	if sourcefile:
		try:
			logger("Playing media file with command: "+ player + " \'" + sourcefile + "\' &> /dev/null &")
			os.system(player + " \'" + sourcefile + "\' &> /dev/null &")
		except OSError as err:
			logger("Error: {0}".format(err))
			print("OS error: {0}".format(err))

#### create directory if not found
def check_path(path):
	if not os.path.exists(path):
		logger("Creating path: "+ path)
		os.makedirs(path)

#### convert seconds to hours (hh:mm:ss) ####
def convert_to_minutes(seconds):
	try:
		seconds=float(seconds)
		sec = timedelta(seconds=seconds)
		converted = datetime(1,1,1) + sec
		converted=converted.strftime('%H:%M:%S.%f')[:-3]
		return  converted
	except (ValueError) as err:
		logger("Unexpected error during conversion to minutes - Error: {0}".format(err))
		print("Error: {0}".format(err))
		print("Unexpected error during conversion to minutes. (Press any key to continue)")
		getchar()

#### convert hours (hh:mm:ss) to seconds ####
def convert_to_seconds(stime):
	try:
		msecs_found=False
		if stime.find(".") != -1: 
			(hours,msecs)=stime.split(".")
			msecs_found=True
		else:
			hours=stime
		secs=str(sum(int(x) * 60 ** i for i,x in enumerate(reversed(hours.split(":")))))
		
		if msecs_found:
				secs=secs + "." + msecs
		else:
				secs=secs + ".000"
		return secs
	except (ValueError) as err:
		logger("Unexpected error during conversion to seconds. - Error: {0}".format(err))
		print("Error: {0}".format(err))
		print("Unexpected error during conversion to seconds. (Press any key to continue)")
		getchar()

#### retrieve terminal size ####
def terminal_size():
	(columns,rows)=os.get_terminal_size()
	return (columns,rows)

#### draw title on top of each menu ####
def print_title():
	## let's clear the screen at first
	os.system('clear')
	(columns,rows)=terminal_size()
	decorators=int((columns/2 - len(title)/2))
	print(("=" * decorators) + title + ("=" * decorators))

def calculate_height(width,sourcewidth,sourceheight):
	ratio=sourcewidth/sourceheight
	height=round(width/ratio)
	return height

#### draw a separator ####
def print_separator():
	(columns,rows)=terminal_size()
	print("=" * columns)

#### generate random slices ####
def generate_slices(sourceduration):
	slices = []
	try:
		print("Please select the overall duration for the clip in seconds")
		duration=int(input("# "))
	
		print("Please select the duration for each slice in seconds")
		sliceduration=int(input("# "))

		logger("Generating slices with overall clip duration of " + str(duration) + " secs and slice duration of " + str(sliceduration)+ " secs" )
	
		prevpos = 0
		cycles = duration/sliceduration
		step = 100/cycles
		s=1
		n=1
		
		while n <= cycles and ((int(prevpos))+sliceduration < int(sourceduration)):
			s = random.randint(prevpos+sliceduration,round(int(sourceduration)/100*(n*step)))
			prevpos = s
			slices.append([s,s+sliceduration])
			n = n + 1
		logger("Generated " + str(len(slices)) + " slices")
		return slices
	except (OSError, ValueError) as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err))
		print("Duration values can only be expressed in integers. (Press any key to continue)")
		getchar

def print_duration(slices):
	total_duration=0
	for i in range(len(slices)):
		(ss,se)=slices[i]
		diff=float(se)-float(ss)
		total_duration=total_duration+diff
	print("Total video lenght: " + str(convert_to_minutes(total_duration)) )
	
def print_slices(slices,show_info,show_slice_lenght):
	(columns,rows)=os.get_terminal_size()
	if show_info:
		menu_rows=23
	else:
		menu_rows=20

	available_rows=int(rows)-menu_rows
	slice_columns=math.ceil(len(slices)/available_rows)
	slices_per_column=math.ceil(len(slices)/slice_columns)

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
				if show_slice_lenght:
					print_str=print_str + "#" + str(num) + ")" + str(convert_to_minutes(ss)) + "-" + str(convert_to_minutes(se)) + "-len: " + str(round(float(se)-float(ss),2)) + separator
				else:
					print_str=print_str + "#" + str(num) + ")" + str(convert_to_minutes(ss)) + "-" + str(convert_to_minutes(se)) + separator
				num=num+(available_rows)
		print_out.append(print_str)

	for i in range(len(print_out)):
		if i <= available_rows:
			print(print_out[i])
		
def add_slice(slices,sourceduration):
	try:
		print("Please insert start time for the new subclip (hh:mm:ss.msc)",flush=True)
		ss=convert_to_seconds(time_input())

		print("Please insert end time for the new subclip (hh:mm:ss.msc)",flush=True)
		se=convert_to_seconds(time_input())

		if (float(ss) < sourceduration) and (float(se) < sourceduration):
			slices.append([ss,se])
		else:
			print("Slices can't start/end after the end of the source video. (Press any key to continue)")
			getchar()
	except:
		print("Specified time values are incorrect. (Press any key to continue)")
		getchar()

	return slices

#def insert_slice(slices,sourceduration):
#	try:
#
#		print("In which position would you like to add a new subclip?")
#		newpos=int(input("#"))
#	
#		if not (newpos > len(slices)):
#			print("Please insert start time for the new subclip (hh:mm:ss.msc)")
#			ss=convert_to_seconds(time_input())
#	
#			print("Please insert end time for the new subclip (hh:mm:ss.msc)")
#			se=convert_to_seconds(time_input())
#	
#			if (float(ss) < sourceduration) and (float(se) < sourceduration):
#				slices.insert(newpos,[ss,se])
#			else:
#				print("Slices can't start/end after the end of the source video. (Press any key to continue)")
#				getchar()
#		else:
#			print("Invalid slice position selected. (Press any key to continue)")
#			getchar()
#	
#	except ValueError as err:
#		logger("Error: {0}".format(err))
#		print("Error: {0}".format(err))
#		print("Either specified time values are incorrect or slice position is invalid. (Press any key to continue)")
#		getchar()
#	return slices
#
#def change_slice(slices,sourceduration):
#	try:
#		print("Which slice would you like to change?")
#		change_index=int(input("#"))
#		if not (change_index > len(slices)):
#
#			print("Please insert start time for the new subclip (hh:mm:ss.msc)")
#			ss=convert_to_seconds(time_input())
#	
#			print("Please insert end time for the new subclip (hh:mm:ss.msc)")
#			se=convert_to_seconds(time_input())
#	
#			if (float(ss) < sourceduration) or (float(se) < sourceduration):
#				slices[change_index]=(ss,se)
#			else:
#				print("Slices can't start/end after the end of the source video. (Press any key to continue)")
#				getchar()
#		else:
#			print("Invalid slice position selected. (Press any key to continue)")
#			getchar()
#
#	except ValueError as err:
#		logger("Error: {0}".format(err))
#		print("Error: {0}".format(err))
#		print("Either specified time values are incorrect or slice position is invalid. (Press any key to continue)")
#		getchar()
#	return slices

def remove_slice(slices):
	try:
		print("Which slice would you like to remove?")
		change_index=int(input("#"))
		if not (change_index > len(slices)):
			slices.pop(change_index)
		else:
			print("Invalid slice position selected. (Press any key to continue)")
			getchar()

	except ValueError as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err))
		print("Slice position is invalid. (Press any key to continue)")
		getchar()
	return slices

def ffmpeg_write_vo(sourcefile,slices,destfile,sourcefps,sourcewidth,sourceheight,sourcebitrate,threads,keep_first_pass_log):
	try:
		#### encoder = either libx264 or libvpx
		encoder="libvpx"
		vo_slices = []
		quality_opts=" -quality good -cpu-used 0 -qmin 10 -qmax 42 -crf 10 -b:v " + str(sourcebitrate) + "k"

		#### with libvpx options
		ffmpeg_command="ffmpeg -stats -v quiet -i " + "\'" + sourcefile + "\'" + " -y -r " + str(sourcefps) + " -codec:v " + encoder + quality_opts + " -s " + str(sourcewidth) + "x" + str(sourceheight) + " -c:a libvorbis -q 0 -threads " + str(threads) + " -filter_complex \""

		for i in range(len(slices)):
			(ss,se)=slices[i]
			ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[v" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "

		for i in range(len(slices)):
			ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
	
		ffmpeg_command=ffmpeg_command + "concat=n=" + str(len(slices)) + ":v=1:a=1[out]\""
		ffmpeg_command_pass1=ffmpeg_command + " -an -pass 1 -map \"[out]\" -f webm " + "/dev/null"
		ffmpeg_command_pass2=ffmpeg_command + " -pass 2 -map \"[out]\" " + "-f webm \'" + destfile + "\'"

		logger("Enconding to: " + destfile)
		print("Enconding to: " + destfile)
		start_time=time.time()

		#### Skip first pass encoding if ffmpeg's first pass log is present. This should only happen when
		#### we're encoding both full and variable quality videos. This could create some race conditions 
		#### and who knows what will happen if ffmpeg makes a second pass with a corrupted first pass log!!
		if not os.path.isfile("ffmpeg2pass-0.log"):
			logger("Encoding to " + destfile + ", running first pass with command: " + ffmpeg_command_pass1)
			os.system(ffmpeg_command_pass1)
		else:
			logger("previous first pass log file found (ffmpeg2pass-0.log), skipping first pass encoding")

		logger("Encoding to " + destfile + ", running second pass with command: " + ffmpeg_command_pass2)
		os.system(ffmpeg_command_pass2)

		if not keep_first_pass_log:
			logger("Removing first pass log ffmpeg2pass-0.log")
			os.remove("ffmpeg2pass-0.log") 
		else:
			logger("keeping first pass log ffmpeg2pass-0.log for further encoding")

		end_time=time.time()
		elapsed_time=convert_to_minutes(end_time-start_time)
		logger("Encoding done, elapsed time with " + str(threads) + " threads is: " + elapsed_time)
		print("Time elapsed: " + elapsed_time)
		
	except (ValueError, OSError) as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

def write_all_slices(sourcefile,slices,destfile,sourcefps,sourcewidth,sourceheight,sourcebitrate):
	try:
		#### encoder = either libx264 or libvpx
		encoder="libvpx"
		start_time=time.time()

		vo_slices = []
		logger("Encoding " + str(len(slices)) + " slices, each slice as a separate ouput file")
		for i in range(len(slices)):
			outfile="\'" + destfile + "_" + str(i) + ".webm\'"

			(ss,se)=slices[i]

			#### with libvpx options
			ffmpeg_command="ffmpeg -stats -v quiet -i " + "\'" + sourcefile + "\'" + " -y -r " + str(sourcefps) + " -codec:v " + encoder + "  -quality good -cpu-used 0  -b:v " + str(sourcebitrate) + "k -qmin 10 -qmax 42 -s " + str(sourcewidth) + "x" + str(sourceheight) + " -c:a libvorbis -q 0 -threads " + str(threads) + " -filter_complex \""
	
			ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[v" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
		
			ffmpeg_command=ffmpeg_command + "concat=n=1:v=1:a=1[out]\" "
			ffmpeg_command=ffmpeg_command + "-map \"[out]\" " + outfile
	
			try:
				logger("Encoding slice #" + str(i) + " with filename " + outfile + ", using ffmpeg command: " + ffmpeg_command)
				print("Encoding slice #" + str(i) + " with filename: " + outfile)
				subprocess.call(ffmpeg_command,shell=True)
			
			except OSError as err:
				logger("Error: {0}".format(err))
				print("Error: {0}".format(err) + " (Press any key to continue)")
				getchar()

			end_time=time.time()
			elapsed_time=convert_to_minutes(end_time-start_time)
			logger("Encoding done, elapsed time with " + str(threads) + " threads is: " + elapsed_time)
			print("Elapsed time: " + elapsed_time)

	except (ValueError, OSError) as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

def write_preview(sourcefile,slices,destfile,fps,height,width,bitrate,threads):
	#### Encoders
	#### VP8:
	encoder="libvpx" ### either x264/mp4 or libvpx/webm
	audio_encoder="libvorbis"
	file_ext="webm"
	#### H264
	#encoder="libx264" ### either x264/mp4 or libvpx/webm
	#audio_encoder="aac"
	#file_ext="mp4"

	preview_file=destfile + "." + file_ext

	font="DejaVuSans-Bold.ttf"
	fontsize=100
	opts=" -cpu-used 8 -threads " + str(threads)
	#try:
	vo_slices = []

	ffmpeg_command="ffmpeg -stats -v quiet -i \'" + sourcefile + "\' -y -codec:v " + encoder + " -b:v " + str(bitrate) + " -s " + str(width) + "x" + str(height) + opts + " -c:a " + audio_encoder + " -q 0 -filter_complex \""
	for i in range(len(slices)):
		(ss,se)=slices[i]
		ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[todraw" + str(i) + "]; "
		ffmpeg_command=ffmpeg_command + "[todraw" + str(i) + "]drawtext=fontsize="+ str(fontsize) + ":fontcolor=black:fontfile=" + font + ":text=" + str(i) + "[v" + str(i) + "]; "
		ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "
	
	for i in range(len(slices)):
		ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
	
	ffmpeg_command=ffmpeg_command + "concat=n=" + str(len(slices)) + ":v=1:a=1[out]\" "
	ffmpeg_command=ffmpeg_command + "-map \"[out]\" " + "\'" + preview_file + "\'"

	start_time=time.time()

	logger("Encoding preview file \"" + preview_file + "\"" + " with ffmpeg command: " + ffmpeg_command)
	print("Encoding preview file: \"" + preview_file + "\"")

	subprocess.call(ffmpeg_command,shell=True)

	end_time=time.time()
	elapsed_time=convert_to_minutes(end_time-start_time)
	logger("Encoding preview file done, elapsed time with " + str(threads) + " threads is: " + elapsed_time)
	print("Time elapsed: " + elapsed_time)

	print("(p) to watch the preview file, (r) to remove the preview file, (q) to resume editing ")
	while True:
		confirm=getchar()
		if confirm == "p" or confirm == "P":
			xdg_open(preview_file)
		elif confirm == "r" or confirm == "R":
			os.system("rm " + "\'" + preview_file + "\'")
		elif confirm == "q" or confirm == "Q":
			break

def change_settings(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices,show_info):
	try:
		settings_loop=False
		while not settings_loop:
			## Settings Menu
			print_title()
			#print("show info: " + str(show_info))
			if show_info:
				print_source_info(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps)
				print_separator()
			print("")
			print("1) (o)utput Filename (" + destfile + ")")
			print("2) (f)ps (" + str(fps) + ")")
			print("3) (w)idth (" + str(width) + ") - height (" + str(calculate_height(width,sourcewidth,sourceheight)) + ")")
			print("4) (b)itrate (" + bitrate + ") - suggested (" + str(round((width*calculate_height(width,sourcewidth,sourceheight)*fps)/10000)) + ")")
			print("5) encoder (t)hreads (" + str(threads) + ")")
			print("6) f(u)ll quality video output (" + str(write_full_quality) + ")")
			print("7) (v)ariable bitrate video output (" + str(write_custom_quality) + ")")
			print("8) (s)lices output (" + str(write_slices) + ")")
			print("9) (q)uit to main menu")
			print("")
			print_separator()
	
			print("#",end="",flush=True)
			settings_choice=getchar()
	
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
			elif any(q in settings_choice for q in ["6","U","u"]):
				write_full_quality = not bool(write_full_quality)
			elif any(q in settings_choice for q in ["7","V","v"]):
				write_custom_quality = not bool(write_custom_quality)
			elif any(q in settings_choice for q in ["8","S","s"]):
				write_slices = not bool(write_slices)
			elif any(q in settings_choice for q in ["9","Q","q"]):
				settings_loop=True
		return (destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices)
	except (ValueError, OSError) as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()
		

#### Load State ####
def load_state(state_file_name):
	line_number = 0
	slices = []
	logger("Loading state file: " + state_file_name)

	try:
		with open(state_file_name, encoding='utf-8') as state_file:
			#### skip first two lines
			state_file.readline().strip()
			state_file.readline().strip()
			sourcefile = state_file.readline().rstrip()
				
			destfile = state_file.readline().rstrip()
			fps = int(state_file.readline().rstrip())
			bitrate = (state_file.readline().rstrip())
			width = int(state_file.readline().rstrip())
			threads = int(state_file.readline().rstrip())
			target_size = int(state_file.readline().rstrip())
			write_full_quality = bool(int(state_file.readline().rstrip()))
			write_custom_quality = bool(int(state_file.readline().rstrip()))
			write_slices = bool(int(state_file.readline().rstrip()))

			#### skip three lines
			state_file.readline().rstrip()
			state_file.readline().rstrip()
			state_file.readline().rstrip()
	
			for a_line in state_file:
				line_number += 1
				slice_line=a_line.rstrip()
				ss=convert_to_seconds(slice_line.split('-')[0])
				se=convert_to_seconds(slice_line.split('-')[1])
				slices.append([ss,se])

		logger("Loading state file succeeded")
		return (sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices)


	except (ValueError, OSError) as err:
		logger("Can't parse state file - " + "Error: {0}".format(err))
		print("Can't parse state file!")
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

#### Save State ####
def save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices):
	line_number = 0
	state_file_name=destfile + ".v2t"
	logger("Saving state file " + state_file_name)

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
			state_file.write(str(int(write_full_quality))+"\n")
			state_file.write(str(int(write_custom_quality))+"\n")
			state_file.write(str(int(write_slices))+"\n")
			
			state_file.write(""+"\n")
			state_file.write("slices"+"\n")
			state_file.write("-"*12+"\n")
	
			for a_line in range(len(slices)):
				(ss,se)=slices[a_line]
				ss=convert_to_minutes(ss)
				se=convert_to_minutes(se)
				state_file.write(str(ss)+"-"+str(se)+"\n")
				line_number += 1

			logger("Saving state file succeeded")
			print("State saved correctly (Press any key to continue)")
			getchar()

	except (ValueError, OSError) as err:
		logger("Can't write state file - " + "Error: {0}".format(err))
		print("Can't write state file!")
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

#### Edit slices with an external editor ####
def external_edit(slices,editor):
	state_path='./states/'
	check_path(state_path)
	tmpfile=state_path + destfile+str(random.randint(0,1024))+".edit.v2t"
	try:
		with open(tmpfile,mode='w', encoding='utf-8') as state_file:
						for i in range(len(slices)):
								(ss,se)=slices[i]
								ss=convert_to_minutes(ss)
								se=convert_to_minutes(se)
								state_file.write(str(i) + ")" +  str(ss)+"-"+str(se)+"\n")
								i += 1

		logger("Editing slices with external editor using command: " + editor + " " + tmpfile)
		subprocess.call(editor + " " + "\"" + tmpfile + "\"",shell=True)	

		slices=[]
		with open(tmpfile, encoding='utf-8') as state_file:
			for a_line in state_file:
					slice_line=a_line.rstrip()
					slice_line=slice_line.split(")")[1]
					ss=convert_to_seconds(slice_line.split('-')[0])
					se=convert_to_seconds(slice_line.split('-')[1])
					slices.append([ss,se])
		logger("Reloading slices edited with external editor succedeed")
		return(slices)

	except (ValueError, OSError) as err:
		logger("Can't write temporary state file - " + "Error: {0}".format(err))
		print("Can't write temporary state file!")
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

def youtube_dl_get_url(sourcefile):
	command='youtube-dl -q --no-warnings -f best -g \'' + sourcefile + '\''
	logger("Extracting video URL info with command: " + command)
	sourcefile = subprocess.getoutput(command)
	logger("Extracted video URL is: " + sourcefile)

	return(sourcefile)

def parse_ffprobe_info(sourcefile):
	#### Ask ffmpeg to provide a json with info about the video that we're going to parse
	command='ffprobe -v quiet -print_format json -show_format -show_streams \"' + sourcefile + "\""
	logger("Parsing video info with command: " + command)
	stream_info = subprocess.getoutput(command)
	j = json.loads(stream_info)
	logger("Dumping media info json file: " + str(j))
	
	#### ['streams'] is an array that includes audio and video streams
	#### therefore we look for the position of the first video stream
	for i  in range(len(j['streams'])):
			codec_type=j['streams'][i]['codec_type']
			if codec_type=='video':
					video_stream_pos=i
	
	sourcewidth=j['streams'][video_stream_pos]['width']
	sourceheight=j['streams'][video_stream_pos]['height']
	sourcefps=int(j['streams'][video_stream_pos]['r_frame_rate'][:2])
	sourcebitrate=int(j['format']['bit_rate'])/1000
	sourceduration=math.floor(float(j['format']['duration']))
	
	logger("Parsed info:")
	logger("Resolution is: " + str(sourcewidth) + "x" + str(sourceheight))
	logger("FPS is: " + str(sourcefps))
	logger("Bitrate is: " + str(sourcebitrate))
	logger("Source durations is: " + str(sourceduration))

	#### DEBUG :: UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 3714: ordinal not in range(128)
	#print(sourcewidth)
	#print(sourceheight)
	#print(str(sourcefps))
	#print(str(sourcebitrate))
	#print(str(sourceduration))
	#### DEBUG

	return (sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)

def print_source_info(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps):
	(columns,rows)=terminal_size()
	if len(sourcefile) > columns:
		sfilename=sourcefile[:(columns-23)] + "(...)"
	else:
		sfilename=sourcefile

	print("source file: \"" + sfilename + "\"") 
	print("resolution: " + str(sourcewidth) + "x" + str(sourceheight) + " - fps: " + str(fps) + " - bitrate: " + str(sourcebitrate) + "k - lenght: " + str(convert_to_minutes(sourceduration)))

def slices_menu(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps,show_info,show_slice_lenght):
	try:
		slices_loop=False
		while not slices_loop:
			## Slices Menu
			print_title()
			if show_info:
				print_source_info(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps)
				print_separator()
			print("")
			print("0) (g)enerate slices")
			print("1) (a)dd slice")
			#print("2) (i)nsert slice")
			#print("3) (c)hange slice")
			print("2) (r)emove slice")
			print("3) (d)elete all slices")
			print("4) (e)dit all slices")
			print("5) (s)lice preview")
			print("6) (p)review clip")
			print("7) (c)ustom slice")
			print("8) (w)rite destination file/s")
			print("9) (t)oggle slice lenght")
			print("10) (q)uit to main menu")
			print("")
			print_separator()
			
			if slices:
				print_duration(slices)
				print_slices(slices,show_info,show_slice_lenght)
	
			print("#",end="",flush=True)
			slices_choice=getchar()
	
			if any(q in slices_choice for q in ["0","G","g"]):
				new_slices=[]
				new_slices = generate_slices(sourceduration)
				if new_slices:
					slices = new_slices
			elif any(q in slices_choice for q in ["1","A","a"]):
				slices = add_slice(slices,sourceduration)
			#elif any(q in slices_choice for q in ["2","I","i"]):
			#	slices = insert_slice(slices,sourceduration)
			#elif any(q in slices_choice for q in ["3","C","c"]):
			#	if slices:
			#		slices = change_slice(slices,sourceduration)
			#	else:
			#		print("No defined slice! (Press any key to continue)")
			#		getchar()
			elif any(q in slices_choice for q in ["2","R","r"]):
				if slices:
					slices = remove_slice(slices)
				else:
					print("No defined slice! (Press any key to continue)")
					getchar()
			elif any(q in slices_choice for q in ["3","D","d"]):
				if slices:
					print("Confirm operation (y/n)")
					sure = getchar()
					if sure == "y" or sure == "Y" or sure == "":
						slices = []
				else:
					print("No defined slice! (Press any key to continue)")
					getchar()
			elif any(q in slices_choice for q in ["4","E","e"]):
				if slices:
					slices = external_edit(slices,editor)
				else:
					print("No defined slice! (Press anykey to continue)")
					getchar()
			elif any(q in slices_choice for q in ["5","S","s"]):
				if slices:
					try:
						print("which slice would you like to preview? (slice index)")
						which_slice=int(input("#"))
						subslice=[]
						subslice.append(slices[which_slice])
						tempfile=destfile+str(random.randint(0,1024))+".webm"

						write_preview(sourcefile,subslice,tempfile,20,180,320,"0.2M",threads)
					except (ValueError, OSError) as err:
						logger("Error: {0}".format(err))
						print("Error: {0}".format(err) + " (Press any key to continue)")
						getchar()
				else:
					print("No defined slice! (Press any key to continue)")
					getchar()
			elif any(q in slices_choice for q in ["6","P","p"]):
				if slices:
					try:
						ext=".webm" #either .mp4 or .webm
						path="./preview/"
						check_path(path)
						tempfile=path+destfile+str(random.randint(0,1024))+ext
						write_preview(sourcefile,slices,tempfile,20,180,320,"0.2M",threads)
					except (ValueError, OSError) as err:
						logger("Error: {0}".format(err))
						print("Error: {0}".format(err) + " (Press any key to continue)")
						getchar()
				else:
					print("No defined slice! (Press any key to continue)")
					getchar()

			elif any(q in slices_choice for q in ["7","C","c"]):
				custom_slice = []
				custom_slice_quality=""

				print("Please insert start time for the new custom slice (hh:mm:ss.msc)",flush=True)
				ss=convert_to_seconds(time_input())

				print("Please insert end time for the new custom slice (hh:mm:ss.msc)",flush=True)
				se=convert_to_seconds(time_input())

				if (float(ss) < sourceduration) and (float(se) < sourceduration):
					custom_slice.append([ss,se])
				else:
					print("Slices can't start/end after the end of the source video. (Press any key to continue)")
					getchar()

				print("Please insert a name for the output file")
				custom_name=input("#")

				print("Would you like to encode with full or variable quality? (f/v)")
				#while (custom_slice_quality != "f" or custom_slice_quality != "v"):
				custom_slice_quality=input("#")

				ext=".webm"
				path="./custom/"
				check_path(path)
				keep_first_pass_log=False

				custom_start=convert_to_minutes(ss)
				custom_start=custom_start.replace(':','.')
				padding=custom_start.count('.')
				for i in range(1,padding):
					custom_start=custom_start.lstrip("0")
					custom_start=custom_start.lstrip(".")
				custom_start=custom_start.rstrip("0")
				custom_start=custom_start.rstrip(".")

				custom_end=convert_to_minutes(se)
				custom_end=str(custom_end).replace(':','.')
				padding=custom_end.count('.')
				for i in range(1,padding):
					custom_end=custom_end.lstrip("0")
					custom_end=custom_end.lstrip(".")
				custom_end=custom_end.rstrip("0")
				custom_end=custom_end.rstrip(".")

				#### write the full quality webm
				if custom_slice_quality=="f":
					targetfile=path+custom_name+"_full_"+custom_start+"_"+custom_end+"_"+str(sourcewidth)+"x"+str(sourceheight)+ext
					ffmpeg_write_vo(sourcefile,custom_slice,targetfile,sourcefps,sourcewidth,sourceheight,sourcebitrate,threads,keep_first_pass_log)
				elif custom_slice_quality=="v":
					#### find correct height value given the priginl aspect ratio
					height=calculate_height(width,sourcewidth,sourceheight)
					targetfile=path+custom_name+"_variable_"+custom_start+"_"+custom_end+"_"+str(sourcewidth)+"x"+str(sourceheight)+ext
					ffmpeg_write_vo(sourcefile,custom_slice,targetfile,fps,width,height,bitrate,threads,keep_first_pass_log)

				#print("Encoding completed (Press any key to continue)")
				#getchar()
				print("(p) to watch the target file, (r) to remove the preview file, (q) to resume editing ")
				while True:
					confirm=getchar()
					if confirm == "p" or confirm == "P":
						xdg_open(targetfile)
					elif confirm == "r" or confirm == "R":
						os.system("rm " + "\'" + targetfile + "\'")
					elif confirm == "q" or confirm == "Q":
						break

			elif any(q in slices_choice for q in ["8","W","w"]):
				if slices:
					ext=".webm" 
					#### write the full quality webm
					if write_full_quality:
						path="./full/"
						check_path(path)
						targetfile=path+destfile.rsplit( "." ,1 )[0]+"_"+str(sourcewidth)+"x"+str(sourceheight)+ext
						if write_full_quality and write_custom_quality:
							keep_first_pass_log=True
						else:
							keep_first_pass_log=False
						ffmpeg_write_vo(sourcefile,slices,targetfile,sourcefps,sourcewidth,sourceheight,sourcebitrate,threads,keep_first_pass_log)
						keep_first_pass_log=False

					#### write the custom quality version
					if write_custom_quality:
						path="./variable/"
						check_path(path)
						#### find correct height value given the priginl aspect ratio
						height=calculate_height(width,sourcewidth,sourceheight)
						targetfile=path+destfile.rsplit( "." ,1 )[0]+"_"+str(width)+"x"+str(height)+".vbr"+str(bitrate)+"."+str(fps)+"fps"+ext
						keep_first_pass_log=False
						ffmpeg_write_vo(sourcefile,slices,targetfile,fps,width,height,bitrate,threads,keep_first_pass_log)

					#### write each slice as it's own webm
					if write_slices:
						path="./slices/"
						check_path(path)
						targetfile=path+destfile.rsplit( "." ,1 )[0]
						#write_all_slices(sourcefile,slices,targetfile,sourcefps,sourcewidth,sourceheight,sourcebitrate)
						write_all_slices(sourcefile,slices,targetfile,fps,width,height,bitrate,threads)

					print("Encoding completed (Press any key to continue)")
					getchar()
				else:
					print("No defined slice! (Press any key to continue)")
					getchar()
			elif any(q in slices_choice for q in ["9","T","t"]):
				show_slice_lenght=not show_slice_lenght
			elif any(q in slices_choice for q in ["10","Q","q"]):
				slices_loop=True
		return slices
	except (ValueError, OSError) as err:
		logger("Error: {0}".format(err))
		print("Error: {0}".format(err) + " (Press any key to continue)")
		getchar()

#################### BEGIN #########################

#### Parse arguments and load state eventually
title = "|| video2trailer ||"
#player="xdg-open"
#player="vlc"
player="mplayer -loop 0 -osd-fractions 1 -osdlevel 3"
editor="vim"

write_full_quality=True
write_custom_quality=True
write_slices=False

sourcefile = args.sourcefile

logger("Starting video2trailer, sourcefile is: " + sourcefile)

if not sourcefile[:4]=="http" and not os.path.isfile(sourcefile):
	logger("Can't open file \"" + sourcefile + "\" for reading! Quitting now.")
	raise SystemExit("Can't open file \"" + sourcefile + "\" for reading! Quitting now." )

if sourcefile.lower().endswith(('.v2t')):
	state_file_name=sourcefile
	(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices) = load_state(state_file_name)
	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)
else:
	if sourcefile[:4]=="http":
		sourcefile=youtube_dl_get_url(sourcefile)

	state_file_name=sourcefile + ".v2t"
	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)

	try:
		with open(state_file_name,encoding='utf-8'):
			(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices) = load_state(state_file_name)
	except (ValueError, OSError):
		logger("No state file found, using default values")

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
			bitrate="400"
		else:
			bitrate=sourcebitrate
		if not args.threads:
			threads=3
		else:
			threads=args.threads
		if not args.targetsize:
			target_size=0
		else:
			target_size=args.targetsize

## MAIN LOOP BEGINS HERE
quit_loop=False
show_info=True
show_slice_lenght=True

try:
	while not quit_loop:
		## Main Menu
		print_title()
		if show_info:
			print_source_info(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps)
			print_separator()
		print("")
		print("1) (o)pen with default media player")
		print("2) (f)ilmstrip")
		print("3) (e)dit clip")
		print("4) (c)hange settings")
		print("5) (s)ave state file")
		print("6) show (i)nfo")
		print("7) (q)uit")
		print("")
		print_separator()

		print("#",end="",flush=True)
		choice=getchar()
		
		if any(q in choice for q in ["1","O","o"]):
			xdg_open(sourcefile)
		elif any(q in choice for q in ["2","F","f"]):
			print_separator()
			video2filmstrip(sourcefile)
		elif any(q in choice for q in ["3","E","e"]):
			slices = slices_menu(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps,show_info,show_slice_lenght)
		elif any(q in choice for q in ["4","c","c"]):
			(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices) = change_settings(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices,show_info)
		elif any(q in choice for q in ["5","i","i"]):
			show_info=not show_info
		elif any(q in choice for q in ["6","S","s"]):
			save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices)
		elif any(q in choice for q in ["6","Q","q"]):
			os.system('cls||clear')
			logger("Quitting video2trailer")
			quit_loop=True
except KeyboardInterrupt:
			os.system('cls||clear')
			logger("Quitting video2trailer")
			sys.exit()
except (ValueError, OSError) as err:
	logger("Error: {0}".format(err) )
	print("Error: {0}".format(err) + " (Press any key to continue)")
	getchar()
