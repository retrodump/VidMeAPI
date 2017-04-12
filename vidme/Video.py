
import os
import os.path
import api
import math
from Comment import Comment


class Video:

	def __init__(self, url = "", uri = "", video_id = "", code = ""):
		self.url = url
		self.uri = uri
		self.video_id = video_id
		self.code = code

		if url or video_id or code:
			self.set_meta(self.retrieve_meta())

		# Upload in 2.5 MB chunks
		self.chunk_size = 1024 * 2500

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
		if 'status' in meta:
			if not meta['status']:
				return False
		else:
			return False

		self.meta = meta

		if 'video' in meta:
			video = meta['video']

			for key, value in video.items():
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

	def _retrieve_comments(self, order = 'comment_id', direction = 'ASC'):
		video_id = self._get_safe('video_id')

		if video_id:
			print '/video/' + video_id + '/comments'
			comments = api.request('/video/' + video_id + '/comments', data=dict(
				order=order,
				direction=direction
			), method='GET')

			if comments and 'status' in comments and comments['status']:
				self.comments = [
					Comment(comment) for comment in comments['comments']
				]
				return True
			else:
				return False
		else:
			return False

	def get_comments(self):
		comments = self._get_safe('comments')

		# If comments not found, try to retrieve them.
		if not comments: self._retrieve_comments()

		comments = self._get_safe('comments')

		if comments:
			return comments
		else:
			return False

	def upload(self, user, title = "", no_output=False):
		if not self.uri:
			print "[-] No uri given!"
			return False
		elif not user.get_token() and not user.new_token():
			return False

		if os.path.isfile(self.uri):
			filename = os.path.basename(self.uri)
			file_info = os.stat(self.uri)
			file_size = file_info.st_size

			if not title:
				title = filename

			video_request = api.request('/video/request', data=dict(
				filename=filename,
				size=file_size,
				title=title,
				mode='chunked',
				token=user.get_token()
			))

			if not video_request:
				return False

			code = video_request['code']

			if not no_output:
				print "New Video Code:", code

			upload = api.request('/upload/create', data=dict(
				code=code,
				size=file_size,
				token=user.get_token()
			))

			if not no_output:
				print upload

			upload_id = upload['upload']['upload_id']

			finished_video = {}

			with open(self.uri, 'rb') as f:
				chunk_request = True
				chunk_upload = {'state': ""}

				if not no_output:
					print "[+] Upload is uploading..."

				chunk_request = api.request('/upload/chunk', params=dict(
					code=code,
					upload=upload_id,
					token=user.get_token()
				), data=self._read_chunks(f, file_size, self.chunk_size))

				if chunk_request:
					finished_video = chunk_request['video']
					chunk_upload = chunk_request['upload']

					if not no_output:
						print "[+] Upload is at 100%."
				else:
					if not no_output:
						print "[-] File failed to upload."

			if 'video_id' in finished_video:
				self.url = None
				self.video_id = finished_video['video_id']
				self.set_meta(self.retrieve_meta())

			return True
		else:
			print "[-] Could not find file", self.uri

	def _read_chunks(self, file, file_size, size=1024000, chunk_count=-1):
		count = 0.0

		print "[*] Uploading in", size / 1000000.0, "MB sized chunks."

		while chunk_count:
			data = file.read(size)
			count += len(data)
			if not data:
				break
			yield data

			print "[*] Upload at: " + str(math.ceil(count / file_size * 100)) + ("%.")
			chunk_count -= 1

	def delete(self, user):
		video_id = self._get_safe('video_id')

		if video_id:
			video_delete = api.request('/video/' + video_id + '/delete', data=dict(
					token=user.get_token()
				))

			if video_delete and 'status' in video_delete and video_delete['status']
				return True
			else:
				return False
		return False

	def get_uri(self):
		return self.uri
