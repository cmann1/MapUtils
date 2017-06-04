from tkinter import ttk

from CreateToolTip import *

from .Action import Action


class RotateAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['amount'] = (tk.IntVar(), 90)

		self.messageVar = tk.StringVar()

	# END __init__
	
	def init(self):
		Action.init(self)
	# END init

	def createGui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.createModalWindow("Rotate")

		frame = ttk.Frame(dlg, padding=PADDING)
		frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(frame, text='Degrees').grid(column=0, row=0, sticky=tk.W, pady=(2, 0))
		tk.Spinbox(frame, from_=-270, to=270, increment=90, textvariable=self.vars['amount'][0]).grid(
			column=1, row=0, padx=(PADDING, 0), pady=(2, 0))

		ttk.Button(frame, text="Rotate", command=self.apply).grid(column=0, row=3, sticky=(tk.W))
		ttk.Label(frame, textvariable=self.messageVar).grid(column=1, row=3, sticky=(tk.W))

		self.centreWindow(dlg)
	# END createGui
	
	def run(self, map):
		Action.run(self, map)

		self.messageVar.set('')
		self.createGui()

	# END run

	def apply(self):
		amount = self.var('amount') / 90
		self.map.rotate(round(amount))
		self.messageVar.set('Success!')
	# END apply

# END Action
