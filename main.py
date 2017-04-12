
import vidme
import json
import os.path

def main():
	settings = get_settings('settings')

	user = vidme.User(settings, no_output=True)
	video = vidme.Video(uri = "C:/videos/my video.mp4")

	video_upload = video.upload(user, "Test Video", no_output=False)

	print video_upload['full_url']

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
