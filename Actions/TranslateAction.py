from tkinter import ttk

from CreateToolTip import *

from .Action import Action


class TranslateAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['translateX'] = (tk.IntVar(), 0)
		self.vars['translateY'] = (tk.IntVar(), 0)

		self.message_var = tk.StringVar()

	# END __init__
	
	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		offset_min = -1000000000
		offset_max =  1000000000

		dlg = self.create_modal_window('Translate')

		frame = ttk.Frame(dlg, padding=PADDING)
		frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(frame, text='Tiles').grid(column=0, row=0, sticky=tk.W, pady=(2, 0))
		tk.Spinbox(frame, from_=offset_min, to=offset_max, textvariable=self.vars['translateX'][0]).grid(
			column=1, row=0, padx=(PADDING, 0), pady=(2, 0))
		tk.Spinbox(frame, from_=offset_min, to=offset_max, textvariable=self.vars['translateY'][0]).grid(
			column=2, row=0, padx=(PADDING, 0), pady=(2, 0))

		ttk.Button(frame, text='Translate', command=self.apply).grid(column=0, row=3, sticky=(tk.W))
		ttk.Label(frame, textvariable=self.message_var).grid(column=1, row=3, sticky=(tk.W))

		self.centre_window(dlg)
	# END createGui
	
	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()

	# END run

	def apply(self):
		translate_x = self.var('translateX')
		translate_y = self.var('translateY')
		self.map.translate(round(translate_x), round(translate_y))
		self.message_var.set('Success!')
	# END apply

# END Action
