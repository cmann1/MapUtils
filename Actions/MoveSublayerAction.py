from tkinter import ttk
import copy as copy_func
import math

from CreateToolTip import *

from .Action import Action


class MoveSublayerAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['layer1'] = (tk.IntVar(), 12)
		self.vars['sublayer1'] = (tk.IntVar(), 19)
		self.vars['layer2'] = (tk.IntVar(), 13)
		self.vars['sublayer2'] = (tk.IntVar(), 19)
		self.vars['offsetX'] = (tk.DoubleVar(), 0)
		self.vars['offsetY'] = (tk.DoubleVar(), 0)
		self.vars['rotation'] = (tk.DoubleVar(), 0)
		self.vars['repeat'] = (tk.IntVar(), 1)
		self.vars['copy'] = (tk.BooleanVar(), False)

		self.messageVar = tk.StringVar()
	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def createGui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		offset_min = -1000000000
		offset_max =  1000000000

		dlg = self.createModalWindow("Move Props")

		layer_frame = ttk.Frame(dlg, padding=PADDING)
		layer_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		options_frame = ttk.Frame(dlg, padding=PADDING)
		options_frame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))
		button_frame = ttk.Frame(dlg, padding=PADDING)
		button_frame.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.W, tk.E))

		from_frame = ttk.Labelframe(layer_frame, text="From", padding=PADDING)
		to_frame = ttk.Labelframe(layer_frame, text="To", padding=PADDING)
		from_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, PADDING))
		to_frame.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(from_frame, text="Layer").grid(column=0, row=0, sticky=tk.W)
		ttk.Label(to_frame, text="Layer").grid(column=0, row=0, sticky=tk.W)
		ttk.Label(from_frame, text="Sublayer").grid(column=0, row=2, sticky=tk.W)
		ttk.Label(to_frame, text="Sublayer").grid(column=0, row=2, sticky=tk.W)
		tk.Spinbox(from_frame, from_=0, to=20, textvariable=self.vars['layer1'][0]).grid(column=0, row=1)
		tk.Spinbox(to_frame, from_=0, to=20, textvariable=self.vars['layer2'][0]).grid(column=0, row=1)
		tk.Spinbox(from_frame, from_=-1, to=24, textvariable=self.vars['sublayer1'][0]).grid(column=0, row=3)
		tk.Spinbox(to_frame, from_=-1, to=24, textvariable=self.vars['sublayer2'][0]).grid(column=0, row=3)

		ttk.Label(options_frame, text="Offset").grid(column=0, row=0, sticky=tk.W)
		tk.Spinbox(options_frame, from_=offset_min, to=offset_max, increment=0.1, textvariable=self.vars['offsetX'][0]).grid(column=1, row=0)
		tk.Spinbox(options_frame, from_=offset_min, to=offset_max, increment=0.1, textvariable=self.vars['offsetY'][0]).grid(column=2, row=0, padx=(PADDING, 0))

		ttk.Label(options_frame, text="Rotation").grid(column=0, row=1, sticky=tk.W, pady=PADDING)
		tk.Spinbox(options_frame, from_=-360, to=360, textvariable=self.vars['rotation'][0]).grid(column=1, row=1)

		ttk.Label(options_frame, text="Repeat").grid(column=0, row=2, sticky=tk.W, pady=PADDING)
		tk.Spinbox(options_frame, from_=1, to=500, textvariable=self.vars['repeat'][0]).grid(column=1, row=2)
		ttk.Checkbutton(options_frame, text='Copy', variable=self.vars['copy'][0], onvalue=True,
		                       offvalue=False).grid(column=0, row=3, sticky=tk.W)

		ttk.Button(button_frame, text="Apply", command=self.apply).grid(column=0, row=0, sticky=(tk.W))
		ttk.Label(button_frame, textvariable=self.messageVar).grid(column=1, row=0, sticky=(tk.W))

		self.centreWindow(dlg)
	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.messageVar.set('')
		self.createGui()
	# END run

	def apply(self):
		self.messageVar.set('Working...')
		self.root.update_idletasks()

		layer1 = self.var('layer1')
		layer2 = self.var('layer2')
		sublayer1 = self.var('sublayer1')
		sublayer2 = self.var('sublayer2')
		offset_x = self.var('offsetX') / 48
		offset_y = self.var('offsetY') / 48
		rotation = int(0x10000 * self.var('rotation') / 360)
		repeat = self.var('repeat')
		copy = self.var('copy')

		if not copy:
			repeat = 1

		# print(str(layer1 )+ '.' + str(sublayer1))
		# print(str(layer2 )+ '.' + str(sublayer2))

		props_add = []
		props_del = []
		for map in [self.map, self.map.backdrop]:
			for id, value in map.props.items():
				layer, x, y, prop = value
				# print(' - ' + str(layer) + '.' + str(prop.layer_sub))

				if layer == layer1 and (prop.layer_sub == sublayer1 or sublayer1 == -1):
					layer_sub = prop.layer_sub if sublayer2 == -1 else sublayer2
					props_add.append((map, id, x, y, prop, layer2, layer_sub))
					if not copy:
						props_del.append((map, id))

		total_x = 0
		total_y = 0
		total_rotation = 0
		for i in range(repeat):
			total_x += offset_x
			total_y += offset_y
			total_rotation += rotation
			for (map, id, x, y, prop, layer, layer_sub) in props_add:
				new_prop = copy_func.copy(prop)
				new_prop.layer_sub = layer_sub
				new_prop.rotation = (new_prop.rotation + total_rotation) & 0xFFFF
				map.add_prop(layer, x + total_x, y + total_y, new_prop)

		for (map, id) in props_del:
			del map.props[id]

		self.messageVar.set('Success!')
	# END apply

# END MoveSublayerAction
