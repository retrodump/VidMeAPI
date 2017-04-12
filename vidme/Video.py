
import os
import os.path
import Requests


class Video:

	def __init__(self, url = "", uri = ""):
		self.url = url
		self.uri = uri

		# Upload in 10 MB chunks
		self.chunk_size = 1024 * 1000

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

			video_request = Requests.request('/video/request', data=dict(
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

			upload = Requests.request('/upload/create', data=dict(
				code=code,
				size=file_size,
				token=user.get_token()
			))

			upload_id = upload['upload']['upload_id']

			finished_video = {}

			with open(self.uri, 'rb') as f:
				chunk = ""
				chunk_request = True
				chunk_upload = {'state': ""}

				if not no_output:
					print "[+] Upload is uploading..."

				while chunk_request and (len(chunk) < self.chunk_size or chunk_upload['state'] == 'complete'):
					# chunk = f.read(self.chunk_size)
					# It's not liking chunk_size....It wants the file as 1 entire chunk.
					chunk = f.read()
					chunk_request = Requests.request('/upload/chunk', params=dict(
						code=code,
						upload=upload_id,
						token=user.get_token()
					), data=chunk)

					if chunk_request:
						finished_video = chunk_request['video']
						chunk_upload = chunk_request['upload']

						if not no_output:
							print "[+] File is uploading..."
							# print "[+] Upload is at {}%".format((float(chunk_upload['size_completed']) / float(chunk_upload['size_total']) * 100.0))
					else:
						if not no_output:
							print "[+] Upload is at 100%"

			return finished_video

		else:
			print "[-] Could not find file", self.uri

	def get_uri(self):
		return self.uri
