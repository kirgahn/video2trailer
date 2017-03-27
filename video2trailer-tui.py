#!/usr/bin/env python

import random
#from datetime import datetime, timedelta, time
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

#### run video2filstrip ####
def video2filmstrip(sourcefile):
	try:
		os.system("video2filmstrip" + " \'" + sourcefile + "\'")
	except OSError as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### open sourcefile with default player ####
def xdg_open(sourcefile):
	if sourcefile:
		try:
			os.system(player + " \'" + sourcefile + "\' &> /dev/null &")
		except OSError as err:
			print("OS error: {0}".format(err))

#### create directory if not found
def check_path(path):
	if not os.path.exists(path):
	    os.makedirs(path)

#### convert seconds to hours (hh:mm:ss) ####
def convert_to_minutes(seconds):
	seconds=float(seconds)
	sec = timedelta(seconds=seconds)
	converted = datetime(1,1,1) + sec
	#converted=converted.time()
	converted=converted.strftime('%H:%M:%S.%f')[:-3]
	return  converted

#### convert hours (hh:mm:ss) to seconds ####
def convert_to_seconds(stime):
	#converted = sum(int(x) * 60 ** i for i,x in enumerate(reversed(time.split(":"))))
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
		return slices
	except (OSError, ValueError) as err:
		print("Error: {0}".format(err))
		input("Duration values can only be expressed in integers. (Press ENTER to continue)")

def print_duration(slices):
	total_duration=0
	for i in range(len(slices)):
		(ss,se)=slices[i]
		diff=float(se)-float(ss)
		total_duration=total_duration+diff
	print("Total video lenght: " + str(convert_to_minutes(total_duration)) )
	
def print_slices(slices,show_info):
	(columns,rows)=os.get_terminal_size()
	if show_info:
		menu_rows=23
	else:
		menu_rows=20

	available_rows=int(rows)-menu_rows
	slice_columns=math.ceil(len(slices)/available_rows)
	slices_per_column=math.ceil(len(slices)/slice_columns)
	#separator=" "*5

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
				#print_str=print_str + "#" + str(num) + " " + str(convert_to_minutes(ss)) + " - " + str(convert_to_minutes(se)) + separator
				print_str=print_str + "#" + str(num) + ")" + str(convert_to_minutes(ss)) + "-" + str(convert_to_minutes(se)) + separator
				#print_str=print_str + "|#" + str(num) + " " + str(convert_to_minutes(ss)) + " - " + str(convert_to_minutes(se)) + " - len: " + str(convert_to_minutes(float(se)-float(ss))) + separator
				num=num+(available_rows)
		print_out.append(print_str)

	for i in range(len(print_out)):
		if i <= available_rows:
			print(print_out[i])
		
def add_slice(slices,sourceduration):
	try:
		print("Please insert start time for the new subclip (hh:mm:ss.msc)")
		ss=convert_to_seconds(input("#"))

		print("Please insert end time for the new subclip (hh:mm:ss.msc)")
		se=convert_to_seconds(input("#"))

		if (float(ss) < sourceduration) and (float(se) < sourceduration):
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
			print("Please insert start time for the new subclip (hh:mm:ss.msc)")
			ss=convert_to_seconds(input("#"))
	
			print("Please insert end time for the new subclip (hh:mm:ss.msc)")
			se=convert_to_seconds(input("#"))
	
			if (float(ss) < sourceduration) and (float(se) < sourceduration):
				slices.insert(newpos,[ss,se])
			else:
	                        input("Slices can't start/end after the end of the source video. (Press ENTER to continue)")
		else:
			input("Invalid slice position selected. (Press ENTER to continue)")
	
	except ValueError as err:
                print("Error: {0}".format(err))
                input("Either specified time values are incorrect or slice position is invalid. (Press ENTER to continue)")

	return slices

def change_slice(slices,sourceduration):
	try:
		print("Which slice would you like to change?")
		change_index=int(input("#"))
		if not (change_index > len(slices)):

			print("Please insert start time for the new subclip (hh:mm:ss.msc)")
			ss=convert_to_seconds(input("#"))
	
			print("Please insert end time for the new subclip (hh:mm:ss.msc)")
			se=convert_to_seconds(input("#"))
	
			if (float(ss) < sourceduration) or (float(se) < sourceduration):
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

def ffmpeg_write_vo(sourcefile,slices,destfile,sourcefps,sourcewidth,sourceheight,sourcebitrate,threads,constant_bitrate=0,crf_factor=30):
	try:
		#### encoder = either libx264 or libvpx
		encoder="libvpx"
		vo_slices = []
		if constant_bitrate==0:
			quality_opts=" -quality good -cpu-used 0 -qmin 10 -qmax 42 -crf 10 -b:v " + str(sourcebitrate) + "k"
		else:
			#### constant bitrate encoding... sucks, but it's precise because it forces a specific bitrate. 
			#### Used for chan_renderer to respect the calculated optimal bitrate.
			print("Encoding with constant bitrate of: " + str(sourcebitrate) + "kbps, crf_factor: " + str(crf_factor))
			quality_opts=" -deadline good -cpu-used 0  -bufsize " + str(sourcebitrate*1000) + " -b:v "+ str(sourcebitrate) + "k -minrate "+ str(sourcebitrate) + "k -maxrate " + str(sourcebitrate) + "k -qmin " + str(crf_factor)+ " -qmax " + str(crf_factor) + " -error-resilient 1  -rc_buf_aggressivity 0.5 -crf "  + str(crf_factor)

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

		#### DEBUG
		#print("#"*30)
		#print("### 1:\'" + ffmpeg_command_pass1 + "\'")
		#print("")
		#print("### 2:\'" + ffmpeg_command_pass2 + "\'")
		#print("#"*30)

		print("Enconding to: " + destfile)
		start_time=time.time()

		os.system(ffmpeg_command_pass1)
		os.system(ffmpeg_command_pass2)
		os.remove("ffmpeg2pass-0.log")

		end_time=time.time()
		elapsed_time=convert_to_minutes(end_time-start_time)
		print("Time elapsed: " + elapsed_time)
		
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def chan_renderer(sourcefile,slices,destfile,targetsize,targetfps,sourcewidth,sourceheight,threads):
	#### the idea is to calculate the target size for the stream given that we know
	#### both the target size and the clip duration.
	#### we then proceed try several resolutions until we find the right combo
	#### of resolution and bitrate given that we know how many bits_per_pixel 
	#### we whish to allocate.
	#### bits_per_pixel is a quality coefficient and should be around 0.1.
	#### lower values like 0.03 mean horrible picture quality, while higher values 
	#### mean that we are wasting data

	#### let's find how long the final clip will last
	total_duration=0
	for i in range(len(slices)):
		(ss,se)=slices[i]
		diff=float(se)-float(ss)
		total_duration=total_duration+diff

	audio_bitrate=64 #libvorbis -q 0 = 64kps
	bits_per_pixel=0.1
	fps=targetfps
	targetsize=int(targetsize)
	
	#### now we now the overall size, duration, audio bitrate (64kbps)
	#### and we know that bit_per_pixel=0.1 
	#### therefore we calculate how many pixels_per_second
	#### we need at every resolution test. given that
	#### bits_per_pixel*pixels_per_second is equal to
	#### the needed bitrate, we calcuate the bitrate each time
	#### accordingly. this way, even at tiny resolutions,
	#### we'll always have a (proportionally) decent quality
	
	starting_width=int(sourcewidth)
	starting_height=int(sourceheight)
	#### approx_factor are used to determine the fork value between
	#### the minimum and maximum acceptable target sizes when
	#### a quality compromise is found. this is necessary because,
	#### even using the godawful constant bitrate quality that 
	#### **should** enforce bitrate, the frigging encoder overshoots
	#### anyway. So, if target_size is 4M, the estimated 
	#### size that's considered to be ok has to be between
	#### for e.g. 84% and 90% of 4M. that's to avoid the encoder overshooting
	#### to the point that the file exceeds 4M.
	#approx_factor_min=86
	#approx_factor_max=94
	approx_factor_min=90
	approx_factor_max=96

	### cfr_factor is used to adapt quantizers and cfr (constant bitrate) quality
	cfr_factor=40

	while True:
		pixels_per_second = starting_width*starting_height*fps
		bitrate=round(bits_per_pixel*pixels_per_second)
		bitrate=bitrate-(audio_bitrate*1000)
		print("trying with res:"+str(starting_width)+"x"+str(starting_height)+", bitrate: "+str(bitrate/1000)+"kbps",end='\r')

		MBrate=(bitrate/(1000*1000))*0.125
		estimated_size=MBrate*total_duration
		if estimated_size <= ((target_size*approx_factor_max)/100) and estimated_size > ((target_size*approx_factor_min)/100):
			print("Optimal parameters found: resolution is "+str(starting_width)+"x"+str(starting_height)+", bitrate is "+str(bitrate/1000)+"kbps, estimated size is "+str(estimated_size)+"MB")

			ffmpeg_write_vo(sourcefile,slices,destfile,fps,starting_width,starting_height,bitrate/1000,threads,1,cfr_factor)
			break
		elif estimated_size > ((target_size*approx_factor_max)/100):
			print("estimated size too big ("+str(estimated_size)+"), lets lower the resolution",end='\r')
			#starting_width=round(starting_width/0.5)
			#starting_height=round(starting_height/0.5)
			starting_width=math.floor(starting_width/1.4)
			starting_height=math.floor(starting_height/1.4)
		elif estimated_size < ((target_size*approx_factor_min)/100):
			print("estimated size too small ("+str(estimated_size)+"), lets up the resolution",end='\r')
			#starting_width=round(starting_width*1.2)
			#starting_height=round(starting_height*1.2)
			starting_width=math.floor(starting_width*1.2)
			starting_height=math.floor(starting_height*1.2)

	#### we check if the encoded file is actually within target_size
	#### if not, we remove it and we decrease/increase the quality by changing
	#### cfr_factor. If cfr_factor ends higher then the max codec allowed value (63)
	#### we simply surrender.
	real_size=(os.path.getsize(destfile)/(1024*1024))
	while (real_size > target_size) or (real_size < (target_size*approx_factor_min)/100):
		print("Looks like the output file size differs too much ("+str(real_size)+"MB), let's tweak the quality accordingly (cfr:"+str(cfr_factor)+")")
		#### DEBUG:
		#print("target_size: "+str(target_size))
		#print("real_size: "+str(real_size))
		#print("crf_factor calculation: round(("+str(cfr_factor)+"/"+str(target_size)+")*"+str(real_size)+")")
		cfr_factor=round((cfr_factor/target_size)*real_size)

		#### DEBUG:
		#print("calculated crf_factor: "+str(cfr_factor))

		if cfr_factor > 63:
			print("Surpassed lowest quality cfr value (63), I quit!")
			break
		else:
			os.system("rm " +  destfile)
			ffmpeg_write_vo(sourcefile,slices,destfile,fps,starting_width,starting_height,bitrate/1000,threads,1,cfr_factor)
			real_size=(os.path.getsize(destfile)/(1024*1024))

def write_all_slices(sourcefile,slices,destfile,sourcefps,sourcewidth,sourceheight,sourcebitrate):
	try:
		#### encoder = either libx264 or libvpx
		encoder="libvpx"
		vo_slices = []
		for i in range(len(slices)):
			outfile="\'" + destfile + "_" + str(i) + ".webm\'"
			print("encoding slice #" + str(i) + " with filename: " + outfile)
			(ss,se)=slices[i]

			#### with libvpx options
			ffmpeg_command="ffmpeg -stats -v quiet -i " + "\'" + sourcefile + "\'" + " -y -r " + str(sourcefps) + " -codec:v " + encoder + "  -quality good -cpu-used 0  -b:v " + str(sourcebitrate) + "k -qmin 10 -qmax 42 -s " + str(sourcewidth) + "x" + str(sourceheight) + "-c:a libvorbis -q 0 -threads " + str(threads) + " -filter_complex \""
	
	
			ffmpeg_command=ffmpeg_command + "[0:v]trim="+ str(ss) + ":" + str(se) + ",setpts=PTS-STARTPTS[v" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[0:a]atrim="+ str(ss) + ":" + str(se) + ",asetpts=PTS-STARTPTS[a" + str(i) + "]; "
			ffmpeg_command=ffmpeg_command + "[v" + str(i) + "][a" + str(i) + "]"
		
			ffmpeg_command=ffmpeg_command + "concat=n=1:v=1:a=1[out]\" "
			ffmpeg_command=ffmpeg_command + "-map \"[out]\" " + outfile
			#print("#### ffmpeg_command: " + "\"" + ffmpeg_command + "\"")
	
			try:
				os.system(ffmpeg_command)
			except OSError as err:
				input("Error: {0}".format(err) + " (Press ENTER to continue)")

	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def write_preview(sourcefile,slices,destfile,fps,height,width,bitrate,threads):

	#### using mp4 format for faster preview rendering
	ext="mp4"
	#encoder="libx264" ### either x264/mp4 or libvpx/webm
	encoder="libvpx" ### either x264/mp4 or libvpx/webm
	font="DejaVuSans-Bold.ttf"
	fontsize=100
	opts=" -cpu-used 8 -threads " + str(threads)
	#try:
	vo_slices = []

	print("Encoding preview file: \"" + destfile + "\"")
	ffmpeg_command="ffmpeg -stats -v quiet -i \'" + sourcefile + "\' -y -codec:v " + encoder + " -b:v " + str(bitrate) + " -s " + str(width) + "x" + str(height) + opts + " -c:a libvorbis -q 0 -filter_complex \""
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

	### DEBUG 
	#print(ffmpeg_command)

	print("(p) to watch the preview file, (r) to remove the preview file, (q) to resume editing ")
	while True:
		confirm=input("")
		if confirm == "p" or confirm == "P": # or confirm == "":
			xdg_open(destfile)
			#input("press enter to resume editing")
		elif confirm == "r" or confirm == "R":
			os.system("rm " +  destfile)
		elif confirm == "q" or confirm == "Q":
			break

#	except (ValueError, OSError) as err:
#                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def change_settings(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices):
	try:
		settings_loop=False
		while not settings_loop:
			## Settings Menu
			print_title()
			print("")
			print("1) (o)utput Filename (" + destfile + ")")
			print("2) (f)ps (" + str(fps) + ")")
			print("3) (w)idth (" + str(width) + ")")
			print("4) (b)itrate (" + bitrate + ")")
			print("5) encoder (t)hreads (" + str(threads) + ")")
			#print("6) (C)ompressed video target size (0 means no further compression) (" + str(target_size) + ")")
			#print("6) (C)ompress output video to ./variable (0 means no, >1 means yes) (" + str(target_size) + ")")
			print("6) f(u)ll quality video output (" + str(write_full_quality) + ")")
			print("7) (v)ariable bitrate video output (" + str(write_custom_quality) + ")")
			print("8) (s)lices output (" + str(write_slices) + ")")
			print("9) (c)onstant bitrate output target size (0 means do not encode, any int >0 is the target size in MB) (" + str(target_size) + ")")
			print("10) (q)uit to main menu")
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
			elif any(q in settings_choice for q in ["6","U","u"]):
				write_full_quality = input("full quality output: ")
			elif any(q in settings_choice for q in ["7","V","v"]):
				write_custom_quality = input("variable bitrate output: ")
			elif any(q in settings_choice for q in ["8","S","s"]):
				write_slices = input("write each slice as its own video: ")
			elif any(q in settings_choice for q in ["9","C","c"]):
				new_target_size = input("target size: ")
				target_size=new_target_size
			elif any(q in settings_choice for q in ["10","Q","q"]):
				settings_loop=True
		return (destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices)
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")
		

#### Load State ####
def load_state(state_file_name):
	line_number = 0
	slices = []

	try:
		with open(state_file_name, encoding='utf-8') as state_file:
			#### skip first two lines
			state_file.readline().strip()
			state_file.readline().strip()
			#### the third line is to ignore the legacy "video" variable
			#### it may be reused in the future
			state_file.readline().strip()
			#video = VideoFileClip(state_file.readline().rstrip())
				
			destfile = state_file.readline().rstrip()
			fps = int(state_file.readline().rstrip())
			bitrate = (state_file.readline().rstrip())
			width = int(state_file.readline().rstrip())
			threads = int(state_file.readline().rstrip())
			target_size = int(state_file.readline().rstrip())
			write_full_quality = int(state_file.readline().rstrip())
			write_custom_quality = int(state_file.readline().rstrip())
			write_slices = int(state_file.readline().rstrip())
			
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

		return (destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices)

	except (ValueError, OSError) as err:
		print("Can't parse state file!")
		input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### Save State ####
def save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices):
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
			state_file.write(str(write_full_quality)+"\n")
			state_file.write(str(write_custom_quality)+"\n")
			state_file.write(str(write_slices)+"\n")
			
			state_file.write(""+"\n")
			state_file.write("slices"+"\n")
			state_file.write("-"*12+"\n")
	
			for a_line in range(len(slices)):
				(ss,se)=slices[a_line]
				ss=convert_to_minutes(ss)
				se=convert_to_minutes(se)
				state_file.write(str(ss)+"-"+str(se)+"\n")
				line_number += 1

		input("State saved correctly (Press ENTER to continue)")

	except (ValueError, OSError) as err:
		print("Can't write state file!")
		input("Error: {0}".format(err) + " (Press ENTER to continue)")

#### Edit slices with an external editor ####
def external_edit(slices,editor):
	tmpfile='/tmp/' + destfile+str(random.randint(0,1024))+".edit.v2t"
	try:
		with open(tmpfile,mode='w', encoding='utf-8') as state_file:
                        for i in range(len(slices)):
                                (ss,se)=slices[i]
                                ss=convert_to_minutes(ss)
                                se=convert_to_minutes(se)
                                state_file.write(str(i) + ")" +  str(ss)+"-"+str(se)+"\n")
                                i += 1

		subprocess.call(editor + " " + tmpfile,shell=True)	

		slices=[]
		with open(tmpfile, encoding='utf-8') as state_file:
			for a_line in state_file:
			        slice_line=a_line.rstrip()
			        slice_line=slice_line.split(")")[1]
			        ss=convert_to_seconds(slice_line.split('-')[0])
			        se=convert_to_seconds(slice_line.split('-')[1])
			        slices.append([ss,se])
			        #a_line += 1

                #input("State saved correctly (Press ENTER to continue)")
		os.remove(tmpfile)
		
		return(slices)

	except (ValueError, OSError) as err:
                print("Can't write state file!")
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

def parse_ffprobe_info(sourcefile):
	#### Ask ffmpeg to provide a json with info about the video that we're going to parse
	command='ffprobe -v quiet -print_format json -show_format -show_streams \"' + sourcefile + "\""
	stream_info = subprocess.getoutput(command)
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

def slices_menu(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps,show_info):
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
			print("2) (i)nsert slice")
			print("3) (c)hange slice")
			print("4) (r)emove slice")
			print("5) (d)elete all slices")
			print("6) (e)dit all slices")
			print("7) (s)lice preview")
			print("8) (p)review clip")
			print("9) (w)rite destination file/s")
			print("10) (q)uit to main menu")
			print("")
			print_separator()
			
			if slices:
				print_duration(slices)
				print_slices(slices,show_info)
	
	
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
			elif any(q in slices_choice for q in ["6","E","e"]):
				if slices:
					slices = external_edit(slices,editor)
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["7","S","s"]):
				if slices:
					try:
						print("which slice would you like to preview? (slice index)")
						which_slice=int(input("#"))
						subslice=[]
						subslice.append(slices[which_slice])
						tempfile=destfile+str(random.randint(0,1024))+".webm"

						write_preview(sourcefile,subslice,tempfile,20,180,320,"0.2M",threads)
					except (ValueError, OSError) as err:
				                input("Error: {0}".format(err) + " (Press ENTER to continue)")
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["8","P","p"]):
				if slices:
					try:
						ext=".webm" #either .mp4 or .webm
						path="./preview/"
						check_path(path)
						tempfile=path+destfile+str(random.randint(0,1024))+ext
						write_preview(sourcefile,slices,tempfile,20,180,320,"0.2M",threads)
					except (ValueError, OSError) as err:
				                input("Error: {0}".format(err) + " (Press ENTER to continue)")
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["9","W","w"]):
				if slices:
					ext=".webm" 
					#### write the full quality webm
					#### targetfile is destfile less the file extension (first thing after "." starting from 
					#### the right plus resolution and extension: "_WIDTHxHEIGHT.webm"
					if int(write_full_quality) > 0:

						path="./full/"
						check_path(path)
						targetfile=path+destfile.rsplit( "." ,1 )[0]+"_"+str(sourcewidth)+"x"+str(sourceheight)+ext
						print("encoding with full quality output: " +targetfile)
						ffmpeg_write_vo(sourcefile,slices,targetfile,sourcefps,sourcewidth,sourceheight,sourcebitrate,threads)

					#### write the custom quality version
					#if int(target_size) > 0:
					if int(write_custom_quality) > 0:
						path="./variable/"
						check_path(path)
						#### find correct height value given the priginl aspect ratio
						#height=calculate_height(int(width),int(sourcewidth),int(sourceheight))
						height=calculate_height(width,sourcewidth,sourceheight)
						#file_to_compress=targetfile
						targetfile=path+destfile.rsplit( "." ,1 )[0]+"_"+str(width)+"x"+str(height)+".vbr"+str(bitrate)+"."+str(fps)+"fps"+ext
						#print("encoding with choosen quality output: " +targetfile)
						ffmpeg_write_vo(sourcefile,slices,targetfile,fps,width,height,bitrate,threads)
						#compress(file_to_compress,targetfile,bitrate,fps,width,threads)

					#### write each slice as it's own webm
					if int(write_slices) > 0:
						path="./slices/"
						check_path(path)
						targetfile=path+destfile.rsplit( "." ,1 )[0]
						write_all_slices(sourcefile,slices,targetfile,sourcefps,sourcewidth,sourceheight,sourcebitrate)

					#### chan renderer call
					if int(target_size) > 0:
						path="./constant/"
						check_path(path)
						targetfile=path+destfile.rsplit( "." ,1 )[0]+"_cfr.webm"
						chan_renderer(sourcefile,slices,targetfile,target_size,25,sourcewidth,sourceheight,threads)

					input("Encoding completed (Press ENTER to continue)")
				else:
					input("No defined slice! (Press ENTER to continue)")
			elif any(q in slices_choice for q in ["10","Q","q"]):
				slices_loop=True
		return slices
	except (ValueError, OSError) as err:
                input("Error: {0}".format(err) + " (Press ENTER to continue)")

#################### BEGIN #########################

#### Parse arguments and load state eventually
title = "|| video2trailer ||"
#player="xdg-open"
#player="vlc"
player="mplayer -loop 0 -osd-fractions 1"
editor="vim"

write_full_quality=1
write_custom_quality=1
write_slices=1

sourcefile = args.sourcefile

if sourcefile.lower().endswith(('.v2t')):
	state_file_name=sourcefile
	(destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices) = load_state(state_file_name)
	sourcefile=os.path.splitext(sourcefile)[0]
	
	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)

else:
	state_file_name=sourcefile + ".v2t"

	(sourcewidth,sourceheight,sourcefps,sourcebitrate,sourceduration)=parse_ffprobe_info(sourcefile)

	try:
		with open(state_file_name,encoding='utf-8'):
			#(destfile,fps,width,bitrate,threads,target_size,slices) = load_state(state_file_name)
			(destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices) = load_state(state_file_name)
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
			#size_coefficient=4
			#bitrate=size_coefficient*8192
			#bitrate=str(bitrate/sourceduration)+"M"
			#bitrate="0.2M"
			bitrate="300"
		else:
		        #bitrate=sourcebitrate+"M"
		        bitrate=sourcebitrate
		
		if not args.threads:
			threads=4
		else:
			threads=args.threads

		if not args.targetsize:
			target_size=4
		else:
			target_size=args.targetsize


## MAIN LOOP BEGINS HERE
quit_loop=False
show_info=False

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
		print("6) show sourcefile (i)nfo")
		print("7) (q)uit")
		print("")
		print_separator()
		

		choice=input("# ")
		
		if any(q in choice for q in ["1","O","o"]):
			xdg_open(sourcefile)
		elif any(q in choice for q in ["2","F","f"]):
			print_separator()
			video2filmstrip(sourcefile)
		elif any(q in choice for q in ["3","E","e"]):
			slices = slices_menu(sourcefile,slices,sourceduration,sourcebitrate,sourcewidth,sourceheight,sourcefps,show_info)
		elif any(q in choice for q in ["4","c","c"]):
			(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices) = change_settings(destfile,fps,width,bitrate,threads,target_size,write_full_quality,write_custom_quality,write_slices)
		elif any(q in choice for q in ["5","i","i"]):
			show_info=not show_info
		elif any(q in choice for q in ["6","S","s"]):
			save_state(sourcefile,destfile,fps,width,bitrate,threads,target_size,slices,write_full_quality,write_custom_quality,write_slices)
		elif any(q in choice for q in ["6","Q","q"]):
			os.system('cls||clear')
			quit_loop=True
except KeyboardInterrupt:
			os.system('cls||clear')
			sys.exit()
except (ValueError, OSError) as err:
	input("Error: {0}".format(err) + " (Press ENTER to continue)")
