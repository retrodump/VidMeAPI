#!/usr/bin/python

import sys
import vidme
import json
import os.path

def main():
	settings = get_settings('settings')

	video_filename = "C:/somedir/another/myvideo.mp4"

	if len(sys.argv) > 0 and sys.argv[1]:
		video_filename = sys.argv[1]

	print "Uploading file:", video_filename

	user = vidme.User(settings, no_output=True)
	video = vidme.Video(uri = video_filename)

	video_upload = video.upload(user, "Test Video", no_output=False)

	if video_upload:
		print video_upload['full_url']
	else:
		print "[-] Failed to upload video."

"""

	Helper functoins

"""


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
