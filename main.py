#!/usr/bin/python

import sys
import vidme
import json
import os.path
import shlex

session = None
operations = {
	'upload': 'upload_video',
	'comments': 'get_comments',
	'upload_folder': 'upload_folder',
}

def main():
	settings = get_settings('settings')

	global session
	session = vidme.Session(settings, no_output=True)

	args = sys.argv

	if len(args) <= 1:
		start_commandline()
	else:
		run_command(args[1].lower(), args[2:])

"""
 
	Test Case Functions

"""

def get_likes_for_video(url):
	return get_video_by_url(url).get_likes()

def add_video_to_album(album, url):
	return album.add_video(session, vidme.Video(url=url).get_video_id())

def create_album(title):
	return vidme.Album().create(session, title)

def get_user_albums(username):
	return [album for album in get_user_by_username(username).get_albums()]

def get_album(album_id):
	# 90822
	return vidme.Album(album_id)

def get_videos(username):
	return [video for video in get_user_by_username(username).get_videos()]

def is_blocked(username, other_username):
	return get_user_by_username(username).is_blocked(get_user_by_username(other_username))

def is_following(username, other_username):
	return get_user_by_username(username).is_following(get_user_by_username(other_username))

def get_following(username):
	return [following for following in get_user_by_username(username).get_following()]

def get_followers(username):
	return [follower for follower in get_user_by_username(username).get_followers()]

def get_video_views(username):
	return get_user_by_username(username).get_video_views()

def get_user_by_user_id(user_id):
	return vidme.User(user_id=user_id)

def get_user_by_username(username):
	return vidme.User(username=username)

def get_search_by_likes(term):
	return vidme.get_search(term, order='likes_count')

def get_search(term):
	# nsfw (1 for true, 0 for false)
	# order (string :: 'likes_count', 'hot_score', 'date_completed')
	# user (string)
	return vidme.get_serach(term)

def get_new():
	# nsfw (1 for true, 0 for false)
	return vidme.get_new()

def get_trending():
	# offset (int)
	# limit (int)
	return vidme.get_trending()

def get_hot():
	# subindex (int)
	# offset (int)
	# limit (int)
	return vidme.get_hot()

def list_featured_videos(count = 5):
	# offset (int)
	# limit (int)
	# marker (string)
	# order (string)
	for video in vidme.get_featured(limit=count):
		print video.get_title()

def get_featured():
	return vidme.get_featured()

def set_title(url, title):
	return get_video_by_url(url).set_title(title)

def upvote_video(url):
	return get_video_by_url(url).vote(session)

def remove_vote(url):
	return get_video_by_url(url).vote(session, False)

def get_comments(url):
	return [comment for comment in get_video_by_url(url).get_comments()]

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

def upload_video(video_filename, title = "My Super Epic 1337 Video", thumbnail=None, category_id=None):
	if not session: 
		print "User is not set!"
		return

	print "[+] Uploading file:", video_filename

	# Create a new instance with the path to our file
	video = vidme.Video(uri = video_filename)

	# Upload our file and get if_successful
	video_upload = video.upload(session, title, no_output=False)

	if thumbnail:
		video.set_thumbnail(session, thumbnail)

	if category_id:
		video.set_channel(session, category_id)

	if video_upload:
		print "Video title:", video.get_title()
	else:
		print "[-] Failed to upload video."

def upload_folder(directory, regex="*.mp4"):
	import glob

	directory = directory.replace('\\', '\\\\')

	videos = [
		vidme.Video(uri=video_uri)
		for video_uri in glob.glob(directory + "/"+ regex)
	]

	print videos

	for video in videos:
		video.upload(session)

		# Prepare for thumbnail
		video_dir = os.path.dirname(video.get_uri())
		video_name = os.path.splitext(os.path.basename(video.get_uri()))[0]

		# Try to get jpg thumbnail.
		# If no jpg, try png.
		video_thumb1 = video_dir + "/" + video_name + ".jpg"
		video_thumb2 = video_dir + "/" + video_name + ".png"

		if os.path.isfile(video_thumb1):
			video.set_thumbnail(video_thumb1)
		elif os.path.isfile(video_thumb2):
			video.set_thumbnail(video_thumb2)

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
		line = shlex.split(raw_input("Command: "))
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
