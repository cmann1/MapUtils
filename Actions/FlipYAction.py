from tkinter import messagebox

from .Action import Action


class FlipYAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)
	# END __init__
	
	def init(self):
		Action.init(self)
	# END init
	
	def run(self, map):
		Action.run(self, map)

		self.map.flip_vertical()
		messagebox.showinfo(message='Flip X Success!')
	# END run

# END Action
