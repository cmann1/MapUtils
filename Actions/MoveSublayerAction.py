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
		self.vars['withinPlayerBounds'] = (tk.BooleanVar(), False)

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

		dlg = self.create_modal_window('Move Props')

		layer_frame = ttk.Frame(dlg, padding=PADDING)
		layer_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		copy_frame = ttk.Labelframe(dlg, text='Copy', padding=PADDING)
		copy_frame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=PADDING)
		options_frame = ttk.Frame(dlg, padding=PADDING)
		options_frame.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.W, tk.E))
		button_frame = ttk.Frame(dlg, padding=PADDING)
		button_frame.grid(column=0, row=3, sticky=(tk.N, tk.S, tk.W, tk.E))

		layer_frame.columnconfigure(0, weight=1)
		layer_frame.columnconfigure(1, weight=1)

		from_frame = ttk.Labelframe(layer_frame, text='From', padding=PADDING)
		from_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, PADDING))
		to_frame = ttk.Labelframe(layer_frame, text='To', padding=PADDING)
		to_frame.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(from_frame, text='Layer').grid(column=0, row=0, sticky=tk.W)
		ttk.Label(to_frame, text='Layer').grid(column=0, row=0, sticky=tk.W)
		ttk.Label(from_frame, text='Sublayer').grid(column=0, row=2, sticky=tk.W)
		ttk.Label(to_frame, text='Sublayer').grid(column=0, row=2, sticky=tk.W)
		tk.Spinbox(from_frame, from_=0, to=20, textvariable=self.vars['layer1'][0]).grid(column=0, row=1)
		tk.Spinbox(to_frame, from_=0, to=20, textvariable=self.vars['layer2'][0]).grid(column=0, row=1)
		tk.Spinbox(from_frame, from_=-1, to=24, textvariable=self.vars['sublayer1'][0]).grid(column=0, row=3)
		tk.Spinbox(to_frame, from_=-1, to=24, textvariable=self.vars['sublayer2'][0]).grid(column=0, row=3)

		ttk.Checkbutton(copy_frame, text='Copy', variable=self.vars['copy'][0], onvalue=True,
						offvalue=False).grid(column=0, row=0, sticky=tk.W)

		ttk.Label(copy_frame, text='Offset').grid(column=0, row=1, sticky=tk.W)
		tk.Spinbox(copy_frame, from_=offset_min, to=offset_max, increment=0.1, textvariable=self.vars['offsetX'][0]).grid(column=1, row=1)
		tk.Spinbox(copy_frame, from_=offset_min, to=offset_max, increment=0.1, textvariable=self.vars['offsetY'][0]).grid(column=2, row=1, padx=(PADDING, 0))

		ttk.Label(copy_frame, text='Rotation').grid(column=0, row=2, sticky=tk.W, pady=PADDING)
		tk.Spinbox(copy_frame, from_=-360, to=360, textvariable=self.vars['rotation'][0]).grid(column=1, row=2)

		ttk.Label(copy_frame, text='Repeat').grid(column=0, row=3, sticky=tk.W, pady=PADDING)
		tk.Spinbox(copy_frame, from_=1, to=500, textvariable=self.vars['repeat'][0]).grid(column=1, row=3)

		selective_checkbox = ttk.Checkbutton(options_frame, text='Within player 3 and 4 bounds',
			variable=self.vars['withinPlayerBounds'][0], onvalue=True,
			offvalue=False)
		selective_checkbox.grid(column=0, row=3, columnspan=2, sticky=tk.W)
		CreateToolTip(selective_checkbox, 'Only props within the rectangle defined by player 3 and 4 start positions will be moved')

		ttk.Button(button_frame, text='Apply', command=self.apply).grid(column=0, row=0, sticky=(tk.W))
		ttk.Label(button_frame, textvariable=self.message_var).grid(column=1, row=0, sticky=(tk.W))

		self.centre_window(dlg)
	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()
	# END run

	def apply(self):
		self.message_var.set('Working...')
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
		within_player_bounds = self.var('withinPlayerBounds')

		bounds1 = self.map.start_position(None, 3)
		bounds2 = self.map.start_position(None, 4)
		min_x = min(bounds1[0], bounds2[0])
		min_y = min(bounds1[1], bounds2[1])
		max_x = max(bounds1[0], bounds2[0])
		max_y = max(bounds1[1], bounds2[1])

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

					if within_player_bounds:
						if x < min_x or x > max_x or y < min_y or y > max_y:
							continue

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

		self.message_var.set('Success!')
	# END apply

# END MoveSublayerAction
