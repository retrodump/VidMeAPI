#!/usr/bin/python

import sys
import vidme
import json
import os.path

user = None
operations = {
	'upload': 'upload_video',
	'comments': 'get_comments'
}

def main():
	settings = get_settings('settings')

	global user
	user = vidme.User(settings, no_output=True)

	args = sys.argv

	if len(args) <= 1:
		start_commandline()
	else:
		run_command(args[1].lower(), args[2:])

"""

	Test Case Functions

"""

def get_comments(url):
	comments = get_video_by_url(url).get_comments()
	return comments

def get_video_by_url(url):
	# url = "https://vid.me/Z47b"
	return vidme.Video(url = url)

def get_video_by_video_id(video_id):
	# video_id = 14854593
	return vidme.Video(video_id = video_id)

def get_video_by_code(code):
	# code = "Z47b"
	return vidme.Video(code = code)

def upload_video_by_command():
	video_filename = "C:/somedir/another/myvideo.mp4"

	if len(sys.argv) > 0 and sys.argv[1]:
		video_filename = sys.argv[1]

	upload_video(video_filename)

def upload_video(video_filename, title = "My Super Epic 1337 Video"):
	if not user: 
		print "User is not set!"
		return

	print "Uploading file:", video_filename

	# Create a new instance with the path to our file
	video = vidme.Video(uri = video_filename)

	# Upload our file and get if_successful
	video_upload = video.upload(user, title, no_output=False)

	if video_upload:
		print video.get_title()
	else:
		print "[-] Failed to upload video."

"""

	Helper functoins

"""

def run_command(cmd, args):
	if cmd in operations:
		try:
			globals()[operations[cmd]](*args)
		except Exception as e:
			print e
	else:
		print "[-] Command not found!"

def start_commandline():
	while True:
		line = raw_input("Command: ").split()
		run_command(line[0], line[1:])

def default_settings(filename):
	settings = ""

	if os.path.isfile('settings.json.example'):
		with open('settings.json.example', 'r') as f:
			settings = json.load(f)
		with open(filename, 'w+') as f:
			json.dump(settings, f)

	return settings

def get_settings(filename):
	if os.path.isfile(filename + '.json'):
		with open(filename + '.json', 'r') as f:
			s = None

			try:
				s = json.load(f)
			except:
				s = default_settings(filename + '.json')

			return s
	else:
		return default_settings(filename + '.json')

if __name__ == "__main__":
    # execute only if run as a script
    main()
