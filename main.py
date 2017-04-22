#!/usr/bin/python

import sys
import vidme
import json
import os.path
import shlex
import urllib2
import json
import time

session = None
operations = {
	'upload': 'upload_video',
	'comments': 'get_comments',
	'upload_folder': 'upload_folder',
	'download': 'download_video_by_command',
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

def download_video_by_command(dtype, form, video, uri, *args):
	if dtype.lower() == 'video':
		try:
			# Get code
			if video.endswith('/'):
				video = video[:-1]
			video = video.split('/')[-1]
			download_video(form, vidme.Video(code=video), uri, *args)
		except Exception as e:
			print '[-] ERROR:', e
	elif dtype.lower() == 'album':
		# album_id - 90822
		album = vidme.Album(video)

		for video_chunk in album.get_videos():
			for video_to_download in video_chunk:
				try:
					download_video(form, video_to_download, uri, *args)
				except Exception as e:
					print '[-] ERROR:', e
	elif dtype.lower() == 'user':
		# Get username
		if video.endswith('/'):
			video = video[:-1]
		video = video.split('/')[-1]

		user = vidme.User(video)

		for video_chunk in user.get_videos():
			for video_to_download in video_chunk:
				# Has formats but only hls. >.>
				video_to_download = vidme.Video(video_to_download.get_full_url())
				try:
					download_video(form, video_to_download, uri, *args)
				except Exception as e:
					print '[-] ERROR:', e

# download 480p 0ex2 .
def download_video(form, video, uri, *args):
	"""

		Helper functions START

	"""
	def _to_ascii(title):
		return ''.join([i if ord(i) < 128 and i.isalnum() else '-' for i in title])

	def _download_file(url, size=1024 * 5000, chunk_count=-1, no_output=False):
		count = 0.0
		start_time = time.time()

		try:
			file_size = float(url.info().getheaders('Content-Length')[0])
		except:
			file_size = 1.0

		if not no_output:
			print "[*] Dowloading in", size / 1000000.0, "MB sized chunks."

		while chunk_count < 0:
			data = url.read(size)
			count += len(data)
			if not data:
				break

			yield data

			if not no_output:
				per_left = count / file_size * 100.0

				out = "[*] Download at: {0:6.2f}%.".format(per_left)

				# Output and go up one line. This is so it auto updates.
				sys.stdout.write(out + "\r")

			chunk_count -= 1

		if not no_output:
			print "[*] Download at: {0:6.2f}%. Took: {1:7.2f} seconds.".format(
				100.0, time.time() - start_time
			)

	"""

		Helper functions END

	"""

	# Convert title to ascii.
	video.title = _to_ascii(video.get_title())

	# Get our URI path without extension.
	final_path = uri + '/' + video.get_title()

	if '--no-overwrites' in args or '-w' in args:
		if os.path.isfile(final_path + ".mp4"):
			print "[-] File exists. Not downloading."
			return False

	if uri.endswith('/') or uri.endswith('\\'):
		uri = uri[:-1]

	code = video.get_url()

	if not video._get_safe('formats'):
		video = vidme.Video(video.get_full_url())

	if '--no-download' not in args:
		forms = video.get_formats()

		if form not in forms:
			print "[-] Format not found! ", form
			return False
		else:
			print "[*] Downloading video:", video.get_title()

			url = forms[form]['uri']
			success = False

		try:
			video_url = urllib2.urlopen(url)

			# Open our local file for writing
			with open(final_path + ".mp4", "wb") as f:
				for c in _download_file(video_url):
					f.write(c)

			success = True
		except urllib2.HTTPError, e:
			print "HTTP Error:", e.code, url
		except urllib2.URLError, e:
			print "URL Error:", e.reason, url

		print "[*] Finished downloading."
	else:
		success = True

	if success:
		if '--write-description' in args:
			with open(final_path + ".description", "wb") as f:
				f.write(video.get_description())
		if '--write-comments' in args:
			with open(final_path + ".comments", "wb") as f:
				for cchunk in video.get_comments():
					f.write('\r\n\r\n'.join([
							"CID: {0}\r\nUser: {1}\r\n\r\n{2}".format(c.get_comment_id(), c.get_user().get_username(), c.get_body())
							for c in cchunk
						]))
		if '--write-thumbnail' in args:
			with open(final_path + ".jpg", "wb") as f:
				thumbnail_url = urllib2.urlopen(video.get_thumbnail_url())
				for c in _download_file(thumbnail_url):
					f.write(c)
		if '--write-info-json' in args:
			with open(final_path + '.info.json', "wb") as f:
				json.dump(video.meta, f)

	return success

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

		if line:
			try:
				run_command(line[0], line[1:])
			except KeyboardInterrupt:
				pass
			except Exception as e:
				print '[-] ERROR:', e

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
