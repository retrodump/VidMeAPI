

class Comment:

	def __init__(self, meta):
		self.setup_meta(meta)

	def setup_meta(self, meta):
		if meta:
			self.meta = meta

			for key, value in meta.items():
				if key == 'comments':
					value = [
						Comment(comment) for comment in value
					]
				# Add item to class
				setattr(self, key, value)
				# Add getter for item
				setattr(self, 'get_' + key, lambda v=value: v)

	def get_user(self):
		return False

	def get_viewerVote(self):
		return False

	def get_comments(self):
		return False
