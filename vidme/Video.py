
import os
import os.path
import api
import math
from Comment import Comment
from User import User
from Like import Like

class Video:

	def __init__(self, url = "", uri = "", video_id = "", code = "", meta = ""):
		self.url = url
		self.uri = uri
		self.video_id = video_id
		self.code = code

		if meta:
			self.set_meta(meta)
		elif url or video_id or code:
			self.set_meta(self.retrieve_meta())

		# Upload in 5.5 MB chunks
		self.chunk_size = 1024 * 5500
		self.has_started_upload = False

	def retrieve_meta(self):
		video = False

		if self.url:
			video = api.request('/videoByUrl', method="GET", params=dict(
				url=self.url
			))
		elif self.video_id:
			video = api.request('/video/' + str(self.video_id), method="GET")
		elif self.code:
			video = api.request('/videoByUrl', method="GET", params=dict(
				url='https://vid.me/' + self.code
			))

		return video

	def set_meta(self, meta):
		# Confirm meta is good
		self.meta = meta

		if 'video' in meta:
			video = meta['video']

			for key, value in video.items():
				if key == 'user':
					value = User(meta={'user': value})
					# Add item to class
					setattr(self, 'user', value)
					# Add getter for item
					setattr(self, 'get_' + 'user', lambda v=value: v)
				else:
					# Add item to class
					setattr(self, key, value)
					# Add getter for item
					setattr(self, 'get_' + key, lambda v=value: v)

		if 'watchers' in meta:
			watchers = meta['watchers']

			if 'total' in watchers:
				self.total_watchers = watchers['total']
			if 'countries' in watchers:
				self.watcher_countries = watchers['countries']

	def get_meta(self):
		return self.meta

	def _get_safe(self, name):
		if hasattr(self, name):
			return getattr(self, name)
		else:
			return False

	def _retrieve_comments(self, limit = 20, offset = 0, order = 'comment_id', direction = 'ASC'):
		video_id = self._get_safe('video_id')

		if video_id:
			comments = api.request('/video/' + video_id + '/comments', params=dict(
				order=order,
				direction=direction,
				limit=limit,
				offset=offset,
			), method='GET')

			if comments:
				self.comments = [
					Comment(comment) for comment in comments['comments']
				]
				return True
			else:
				return False
		else:
			return False

	def get_comments(self, refresh=False, limit=20, offset=0):
		comments = self._get_safe('comments')

		# If comments not found, try to retrieve them.
		if refresh or not comments: self._retrieve_comments(limit, offset)

		comments = self._get_safe('comments')

		if comments:
			return comments
		else:
			return False

	def _retrieve_likes(self, limit=20, offset = 0, order = 'like_id', direction = 'ASC'):
		video_id = self._get_safe('video_id')

		if video_id:
			likes = api.request('/video/' + video_id + '/likes', params=dict(
				order=order,
				direction=direction,
				limit=limit,
				offset=offset,
			), method='GET')

			if likes:
				self.likes = [
					Like(like) for like in likes['votes']
				]
				return True
			else:
				return False
		else:
			return False

	def get_likes(self, refresh=False, limit=20, offset=0):
		likes = self._get_safe('likes')

		# If likes not found, try to retrieve them.
		if refresh or not likes: self._retrieve_likes(limit, offset)

		likes = self._get_safe('likes')

		if likes:
			return likes
		else:
			return False

	def upload(self, session, title = "", no_output=False, start_at=0, stop_at=None):
		# Stop at not implemented yet.

		if not self.uri:
			print "[-] No uri given!"
			return False
		elif not session.get_token() and not session.new_token():
			return False

		if start_at:
			self._index = start_at

		if not self.has_started_upload:
			self.has_started_upload = True
			self._index = start_at

			if os.path.isfile(self.uri):
				filename = os.path.basename(self.uri)
				file_info = os.stat(self.uri)
				self._file_size = file_info.st_size

				if not title:
					title = filename

				video_request = api.request('/video/request', data=dict(
					filename=filename,
					size=self._file_size,
					title=title,
					token=session.get_token()
				))

				if not video_request:
					return False

				self._code = video_request['code']

				if not no_output:
					print "[+] New Video Code:", self._code

				upload = api.request('/upload/create', data=dict(
					code=self._code,
					size=self._file_size,
					token=session.get_token()
				))

				self._upload_id = upload['upload']['upload_id']

				return self._upload(session, no_output)
			else:
				print "[-] Could not find file", self.uri
		else:
			return self._upload(session, no_output)

	def _upload(self, session, no_output=False):
		finished_video = {}

		with open(self.uri, 'rb') as f:
			if self._index > 0:
				# I guess this works? It need to be (self._index - 1)
				# Maybe one day I'll test this.
				f.seek(self._index)

			if not no_output:
				print "[+] Video is uploading..."

			for chunk in self._read_chunks(f, self.chunk_size, no_output=no_output):
				finished_video = api.request('/upload/chunk', params=dict(
					code=self._code,
					upload=self._upload_id,
					token=session.get_token()
				), extraheaders={
					'Content-Length': str(len(chunk)),
					'Content-Range': 'bytes %s-%s/%s' % (self._index, self._index + len(chunk) - 1, self._file_size),
				},
				data=chunk)

				self._index += len(chunk)

		if finished_video['upload']['state'] == 'completed':
			self.url = None
			self.set_meta(finished_video)

			self.has_started_upload = False
			return True
		else:
			if not no_output:
				print "[-] Failed to finish upload."
				
			return False

	def _read_chunks(self, file, size=1024000, chunk_count=-1, no_output=False):
		count = 0.0

		if not no_output:
			print "[*] Uploading in", size / 1000000.0, "MB sized chunks."

		while chunk_count < 0:
			data = file.read(size)
			count += len(data)
			if not data:
				break
			yield data

			if not no_output:
				print "[*] Upload at: " + str (round(count / self._file_size * 100.0, 2)) + "%."

			chunk_count -= 1

	def _api_call(self, session, action, args = {}):
		video_id = self._get_safe('video_id')

		args['token'] = session.get_token()

		if video_id:
			video_action = api.request('/video/' + video_id + '/' + action, data=args)

			if video_action:
				self.set_meta(video_action)
				return True
			else:
				return False
		return False

	def delete(self, session):
		return self._api_call(session, 'delete')

	def set_title(self, session, title):
		return self._api_call(session, 'edit', dict(title=title))

	def set_description(self, session, description):
		return self._api_call(session, 'edit', dict(description=description))

	def set_source(self, session, source):
		return self._api_call(session, 'edit', dict(source=source))

	def set_private(self, session, private = True):
		return self._api_call(session, 'edit', dict(private=private))

	def set_public(self, session, private = False):
		return set_private(session, private)

	def set_latitude(self, session, latitude):
		return self._api_call(session, 'edit', dict(latitude=latitude))

	def set_longitude(self, session, longitude):
		return self._api_call(session, 'edit', dict(longitude=longitude))

	def set_place_id(self, session, place_id):
		return self._api_call(session, 'edit', dict(place_id=place_id))

	def set_place_name(self, session, place_name):
		return self._api_call(session, 'edit', dict(place_name=place_name))

	def set_nsfw(self, session):
		return self._api_call(session, 'edit', dict(nsfw=True))

	def flag(self, session, flag = 1):
		return self._api_call(session, 'flag', dict(value=flag))

	def vote(self, session, vote = True, time = 0.0):
		if vote:
			vote = 1
		else:
			vote = 0

		return self._api_call(session, 'vote', dict(value=vote, time=time))

	def set_thumbnail(self, session, thumb, no_output=False):
		return False
		#######
		# Doesn't work lol
		# Also tried using /video/:/thumbnail with no luck.
		#######

		# video_id = self._get_safe('video_id')

		# if video_id:
		# 	if os.path.isfile(thumb):
		# 		with open(thumb, 'rb') as f:
		# 			chunk_request = True

		# 			if not no_output:
		# 				print "[+] Thumbnail is uploading..."

		# 			file_info = os.stat(thumb)
		# 			file_size = file_info.st_size

		# 			chunk_request = api.request('/video/' + video_id + '/edit',
		# 				params=dict(
		# 					token=session.get_token()
		# 				),
		# 				data=dict(
		# 					thumbnail=self._read_chunks(f, file_size, self.chunk_size)
		# 				)
		# 			)

		# 			print chunk_request

		# 			if not no_output:
		# 				print "[+] Thumbnail is done uploading."

		# 			if chunk_request:
		# 				return True
		# 			else:
		# 				return False
		# 	else:
		# 		return False
		# else:
		# 	return False

	def get_uri(self):
		return self.uri
