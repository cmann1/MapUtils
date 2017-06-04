from tkinter import messagebox

from .Action import Action


class FlipXAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)
	# END __init__
	
	def init(self):
		Action.init(self)
	# END init
	
	def run(self, map):
		Action.run(self, map)

		self.map.flip_horizontal()
		messagebox.showinfo(message='Flip X Success!')
	# END run

# END Action
