from tkinter import ttk

from CreateToolTip import *
from .Action import Action


class UpscaleAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['factor'] = (tk.IntVar(), 0)

		self.message_var = tk.StringVar()

	# END __init__
	
	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Upscale')

		frame = ttk.Frame(dlg, padding=PADDING)
		frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(frame, text='Factor').grid(column=0, row=0, sticky=tk.W, pady=(2, 0))
		tk.Spinbox(frame, from_=1, to=1000000000, textvariable=self.vars['factor'][0]).grid(
			column=1, row=0, padx=(PADDING, 0), pady=(2, 0))

		ttk.Button(frame, text='Upscale', command=self.apply).grid(column=0, row=3, sticky=(tk.W))
		ttk.Label(frame, textvariable=self.message_var).grid(column=1, row=3, sticky=(tk.W))

		self.centre_window(dlg)
	# END createGui
	
	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()

	# END run

	def apply(self):
		factor = self.var('factor')
		self.map.upscale(factor)
		self.message_var.set('Success!')
	# END apply

# END Action
