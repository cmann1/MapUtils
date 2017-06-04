from tkinter import filedialog

from .Action import Action

class ExtractThumbAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)
	# END __init__
	
	def init(self):
		Action.init(self)
	# END init
	
	def run(self, map):
		Action.run(self, map)

		filename = filedialog.asksaveasfilename(initialfile=self.map.name() + '.png')

		if filename != '':
			with open(filename, "wb") as f:
				f.write(self.map.sshot)
	# END run

# END Action
