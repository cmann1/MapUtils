import json

class Config(object):
	def __init__(self, file = "config.json"):
		self.file = file
		
		try:
			with open(file, 'r') as configFile:
				self.data = json.load(configFile)
		except IOError:
			self.data = {}
		except json.decoder.JSONDecodeError:
			self.data = {}
	# END __init__
	
	def get(self, name, defaults):
		if name in self.data:
			data = self.data[name]
		else:
			data = self.data[name] = {}
		# END else
		
		for key, value in defaults.items():
			if key not in data:
				data[key] = value[1]
				value[0].set(value[1])
			else:
				value[0].set(data[key])
		# END for
		
		return data
	# END write
	
	def write(self):
		with open(self.file, "w") as f:
			json.dump(self.data, f)
	# END write
# End Config
