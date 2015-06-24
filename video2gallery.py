#!/usr/bin/env python
# incremental version 0.9.1_dev

# example usage: 
# video2gallery -v -u "https://myexample.com/videgalleries/" -fl "https://myexample.com/js/flowplayer/flowplayer-3.1.5.swf" -fs "https://myexample.com/js/flowplayer/flowplayer-3.1.4.min.js"
# "filetypes" defines the extensions this script will recursively search for, if you wish to generate galleries for different extensions just modify its value

import glob2
import time
import os
import math
import argparse
import mimetypes
import urllib.request
import random

parser = argparse.ArgumentParser()
parser.add_argument("-d","--directory", help="Directory to search for HTML5 compliant videos", type=str)
parser.add_argument("-u", "--baseurl", help="Prefix file with the specifice base URL, useful to generate web compatible galleries", type=str)
parser.add_argument("-fl", "--flowplayerpath", help="Flowplayer path. If empty assume \"directory/js/flowplayer/flowplayer-3.1.5.swf\". If empty and baseURL is specified assume \"baseURL/js/flowplayer/flowplayer-3.1.5.swf\"", type=str)
parser.add_argument("-fs", "--flowplayerscript", help="Flowplayer js script path. If empty assume \"directory/js/flowplayer/flowplayer-3.1.4.min.js\". If empty and baseURL is specified assume \"baseURL/js/flowplayer/flowplayer-3.1.4.min.js\"", type=str)
parser.add_argument("-f","--filepaging", help="Number of files per each page, if unspecified assumes 10", type=int)
parser.add_argument("-t","--datetime", help="Append date and time to the filename of the generated pages, if unspecified assume no", action="store_true")
parser.add_argument("-v", "--verbose", help="Print additional info", action="store_true" )

mimetypes.init()
args = parser.parse_args()
filetypes=["webm","mp4","ogg","ogv","flv","gif","jpg","jpeg","jpe","png","bmp"]

############ creates page navigation
def page_navigation(d, txt, pg, pgnum):
	txt=txt+"<div style=\"text-align:center\">\n"

	
	if pg > 0:
		if args.datetime:
			txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_0.html\"> &lt;&lt;First</a> | "
			if pg >= 5:
				txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(pg-5)+".html\"> &lt;Previous 5</a> | "
			txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(pg-1)+".html\"> &lt;Previous</a> | "
		else:
			txt=txt+"<a href=\""+d+"videogallery_0.html\"> &lt;&lt;First</a> | "
			if pg >= 5:
				txt=txt+"<a href=\""+d+"videogallery_"+str(pg-5)+".html\"> &lt;Previous 5</a> | "
			txt=txt+"<a href=\""+d+"videogallery_"+str(pg-1)+".html\"> &lt;Previous</a> | "
	if args.datetime:
		txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(random.randint(0,pgnum-1))+".html\"> Random Page</a> | "
	else:
		txt=txt+"<a href=\""+d+"videogallery_"+str(random.randint(0,pgnum-1))+".html\"> Random Page</a> | "
	if not pg==pgnum-1:
		if args.datetime:
			txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(pg+1)+".html\"> Next><a> |"
			if (pgnum-pg-1) >= 5:
				txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(pg+5)+".html\"> Next 5><a> |"
			txt=txt+"<a href=\""+d+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(pgnum-1)+".html\"> Last>></a>"
		else:
			txt=txt+"<a href=\""+d+"videogallery_"+str(pg+1)+".html\"> Next><a> |"
			if (pgnum-pg-1) >= 5:
				txt=txt+"<a href=\""+d+"videogallery_"+str(pg+5)+".html\"> Next 5><a> |"
			txt=txt+"<a href=\""+d+"videogallery_"+str(pgnum-1)+".html\"> Last>></a>"
	txt=txt+"</div>\n<br>"

	return txt

############ embeds the video/image object with the appropriate tag/player
def embed_object(fileobject, filepath, txt, playerid, flowpath):
	if mimetypes.guess_type(filepath, strict=True)[0].find("flv")>=0:
		txt=txt+"<center><a href=\"" 
		txt=txt+fileobject
		txt=txt+"\" style=\"display:block;width:720px;\" id=\"player"+str(playerid)+"\"></a>"
		txt=txt+"<script language=\"JavaScript\"> flowplayer(\"player"+str(playerid)+"\", \""+flowpath+"\", {clip:  {autoPlay: false, autoBuffering: false }});</script></center>"
	elif mimetypes.guess_type(filepath, strict=True)[0].find("video")>=0:
		txt=txt+"<video id="+fileobject+" width=\"720\" controls>\n"
		txt=txt+"<source src="
		txt=txt+fileobject
		txt=txt+" type=\""+mimetypes.guess_type(fileobject, strict=True)[0]+"\" preload=\"metadata\">\n"
		txt=txt+"</video>\n"
	elif mimetypes.guess_type(filepath, strict=True)[0].find("image")>=0:
		txt=txt+"<img src=\""
		txt=txt+fileobject
		txt=txt+"\" width=\"720\">"
	return txt

if not args.directory:
	directory = os.getcwd()+"/"
else:
	directory = args.directory
if args.verbose:
	print("Directory:", directory)

if not args.filepaging:
	files_per_page=10
else:
	files_per_page=args.filepaging
if args.verbose:
	print("Files displayed per page:", str(files_per_page))


files=[]

if args.baseurl:
	baseurl=args.baseurl

if args.flowplayerpath:
	flowplayerpath=args.flowplayerpath
elif not args.flowplayerpath and args.baseurl:
	flowplayerpath=baseurl+"js/flowplayer/flowplayer-3.1.5.swf"
else:
	flowplayerpath=directory+"js/flowplayer/flowplayer-3.1.5.swf"

if args.flowplayerscript:
	flowplayerscript=args.flowplayerscript
elif not args.flowplayerscript and args.baseurl:
	flowplayerscript=baseurl+"js/flowplayer/flowplayer-3.1.4.min.js"
else:
	flowplayerscript=directory+"js/flowplayer/flowplayer-3.1.4.min.js"

if args.verbose:
	print("Searching for the following file types:", filetypes)

for filetype in filetypes:
	fileext=glob2.glob(directory+'**/'+'*.'+filetype)
	if args.verbose:
		print("Searching for file type:", filetype)
	
	for filename in fileext:
        	files.append(filename)

files.sort(key=os.path.getmtime)
files.reverse()

number_of_pages=math.ceil(len(files)/files_per_page)
if args.verbose:
	print("Number of web pages that will be generated:", str(number_of_pages))

############# Main loop start
videocursor=1
for page in range(0, number_of_pages):
	
	if args.datetime:
		saveFile = open(directory+'videogallery_'+time.strftime("%Y%m%d%H%M")+'_'+str(page)+'.html','w')
	else:
		saveFile = open(directory+'videogallery_'+str(page)+'.html','w')
	saveFile.write("<script src=\""+flowplayerscript+"\"></script><br>")
	text=""

	# insert page navigation here 
	if args.baseurl:
		text=page_navigation(baseurl, text, page, number_of_pages)
	else:
		text=page_navigation(directory, text, page, number_of_pages)
	
	for i in range(0, files_per_page):
		if videocursor < len(files):
			text=text+"<div>\n"
			text=text+"<h6 style=\"text-align:center\">"+files[videocursor]+"</h6>\n"
			text=text+"<div align=\"center\" style=\"text-align:center\">\n"
			fileURL=''
			if args.baseurl:
				fileURL=files[videocursor]
				fileURL=fileURL[len(directory):]
				fileURL=urllib.request.pathname2url(fileURL)
				fileURL=args.baseurl+fileURL
			else:
				fileURL=urllib.request.pathname2url(files[videocursor])
				
			text=embed_object(fileURL,files[videocursor],text,videocursor,flowplayerpath)
			text=text+"</div>\n</div>\n<br>"
			videocursor=videocursor+1

	text=text+"<br>\n"
	
	# insert page navigation here 
	if args.baseurl:
		text=page_navigation(baseurl, text, page, number_of_pages)
	else:
		text=page_navigation(directory, text, page, number_of_pages)

	linebreaker=0
	text=text+"<div style=\"text-align:center\">\n"
	
	if args.baseurl:
		linkpath=baseurl
	else:
		linkpath=directory

	for page in range(0, number_of_pages):
		if args.datetime:
			text=text+"<a href=\""+linkpath+"videogallery_"+time.strftime("%Y%m%d%H%M")+"_"+str(page)+".html\">"+str(page)+"</a>|"
		else:
			text=text+"<a href=\""+linkpath+"videogallery_"+str(page)+".html\">"+str(page)+"</a>|"

		if (linebreaker == 40):
			text=text+"<br>"
			linebreaker=0
		else:
			linebreaker=linebreaker+1
	text=text+"</div>"

	saveFile.write(text)
	saveFile.close()
############# Main loop end

if args.datetime:
	print('First gallery saved at:',directory+'videogallery_'+time.strftime("%Y%m%d%H%M")+'_0.html')
else:
	print('First gallery saved at:',directory+'videogallery_'+'0.html')
