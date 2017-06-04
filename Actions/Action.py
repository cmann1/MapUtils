import tkinter as tk
import re


class Action(object):
	def __init__(self, app):
		self.app = app
		self.name = re.sub(r"Action$", r"", type(self).__name__)
		self.root = app.root
		self.needsInit = True
		self.config = {}
		self.vars = {}
		self.dlg = None
		self.map = None
	# END __init__
	
	def init(self):
		self.config = self.app.config.get(self.name, self.vars)
		self.needsInit = False
	# END init
	
	def createGui(self):
		pass
	# END createGui
	
	def run(self, map):
		self.map = map
		
		if self.needsInit:
			self.init()
		#
	# END run
	
	def apply(self):
		pass
	# END run

	def createModalWindow(self, title: object) -> object:
		dlg = self.dlg = tk.Toplevel()
		dlg.resizable(0, 0)
		dlg.title(title)
		# ... build the window ...
		# Set the focus on dialog window (needed on Windows)
		dlg.focus_set()
		# Make sure events only go to our dialog
		dlg.grab_set()
		# Make sure dialog stays on top of its parent window (if needed)
		dlg.transient(self.root)

		dlg.protocol("WM_DELETE_WINDOW", self.onWindowClose)

		return dlg

	@staticmethod
	def enable_frame(frame, enabled=True):
		state = 'enable' if enabled else 'disable'
		for child in frame.winfo_children():
			child.configure(state=state)

	# END run

	def updateConfigValues(self):
		for name, value in self.vars.items():
			var, default = value
			self.config[name] = var.get()
	# END updateConfigValues

	def var(self, varname):
		return self.vars[varname][0].get()
	# END 	var
	
	def centreWindow(self, window):
		window.update_idletasks()
		w = window.winfo_reqwidth()
		h = window.winfo_reqheight()
		ws = window.winfo_screenwidth()
		hs = window.winfo_screenheight()
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		window.geometry('+%d+%d' % (x, y))
	# END centre

	def onWindowClose(self):
		try:
			self.updateConfigValues()
			self.app.config.write()
		except Exception as err:
			print("{0}".format(err))

		if self.dlg != None:
			self.dlg.destroy()
		# END onWindowClose

# END Action
