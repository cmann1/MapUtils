from tkinter import ttk
import copy as copy_func

from dustmaker.Entity import Trigger, FogTrigger, Apple
from CreateToolTip import *

from .Action import Action


class SwapLayerAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['layer1'] = (tk.IntVar(), 12)
		self.vars['layer2'] = (tk.IntVar(), 13)
		self.vars['swapProps'] = (tk.BooleanVar(), True)
		self.vars['swapTiles'] = (tk.BooleanVar(), True)
		self.vars['swapAllFogTriggers'] = (tk.BooleanVar(), True)
		self.vars['copy'] = (tk.BooleanVar(), False)
		self.vars['clear'] = (tk.BooleanVar(), False)
		self.vars['ignoreDustBlocks'] = (tk.BooleanVar(), False)
		self.vars['offsetX'] = (tk.DoubleVar(), 0)
		self.vars['offsetY'] = (tk.DoubleVar(), 0)

		self.message_var = tk.StringVar()
	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Swap Layers')

		# root.columnconfigure(0, weight=1)
		# root.rowconfigure(0, weight=1)
		layerFrame = ttk.Frame(dlg, padding=PADDING)
		layerFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		optionsFrame = ttk.Frame(dlg, padding=PADDING)
		optionsFrame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))
		copyOptionsFrame = ttk.Frame(dlg, padding=PADDING)
		copyOptionsFrame.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.W, tk.E))
		offsetFrame = ttk.Labelframe(dlg, text='Offset', padding=PADDING)
		offsetFrame.grid(column=0, row=3, sticky=(tk.N, tk.S, tk.W, tk.E))
		buttonFrame = ttk.Frame(dlg, padding=PADDING)
		buttonFrame.grid(column=0, row=4, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(layerFrame, text='Layer 1').grid(column=0, row=0)
		ttk.Label(layerFrame, text='Layer 2').grid(column=0, row=1)

		layer1 = tk.Spinbox(layerFrame, from_=0, to=20, textvariable=self.vars['layer1'][0])
		layer1.grid(column=1, row=0)
		layer2 = tk.Spinbox(layerFrame, from_=0, to=20, textvariable=self.vars['layer2'][0])
		layer2.grid(column=1, row=1)

		ttk.Checkbutton(optionsFrame, text='Props', variable=self.vars['swapProps'][0], onvalue=True,
						offvalue=False).grid(column=0, row=0, sticky=tk.W)
		ttk.Checkbutton(optionsFrame, text='Tiles', variable=self.vars['swapTiles'][0], onvalue=True,
						offvalue=False).grid(column=0, row=1, sticky=tk.W)
		ttk.Checkbutton(optionsFrame, text='All fog triggers', variable=self.vars['swapAllFogTriggers'][0],
						onvalue=True, offvalue=False).grid(column=0, row=2, sticky=tk.W)

		copy = ttk.Checkbutton(copyOptionsFrame, text='Copy', variable=self.vars['copy'][0], onvalue=True,
						offvalue=False)
		copy.grid(column=0, row=0, sticky=tk.W)
		clear = ttk.Checkbutton(copyOptionsFrame, text='Clear', variable=self.vars['clear'][0], onvalue=True,
						offvalue=False)
		clear.grid(column=1, row=0, sticky=tk.W)
		ignore_dust_blocks = ttk.Checkbutton(copyOptionsFrame, text='Ignore dust blocks', variable=self.vars['ignoreDustBlocks'][0], onvalue=True,
						offvalue=False)
		ignore_dust_blocks.grid(column=0, row=1, columnspan=2, sticky=tk.W)
		CreateToolTip(copy, 'Instead of being swapped, the contents of layer 1 will be copied to layer 2')
		CreateToolTip(clear, 'Clears layer 2 before copying over the contents from layer 1.\nOnly applies of Copy is checked')
		CreateToolTip(ignore_dust_blocks, 'Won\'t copy dust blocks')

		offset_min = -1000000000
		offset_max =  1000000000
		tk.Spinbox(offsetFrame, from_=offset_min, to=offset_max, increment=1, textvariable=self.vars['offsetX'][0]).grid(column=1, row=1)
		tk.Spinbox(offsetFrame, from_=offset_min, to=offset_max, increment=1, textvariable=self.vars['offsetY'][0]).grid(column=2, row=1, padx=(PADDING, 0))

		ttk.Button(buttonFrame, text='Apply', command=self.apply).grid(column=0, row=0, sticky=(tk.W))
		ttk.Label(buttonFrame, textvariable=self.message_var).grid(column=1, row=0, sticky=(tk.W))

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
		swap_props = self.var('swapProps')
		swap_tiles = self.var('swapTiles')
		swap_all_fog_triggers = self.var('swapAllFogTriggers')
		copy = self.var('copy')
		clear = self.var('clear')
		ignore_dust_blocks = self.var('ignoreDustBlocks')
		offset_x = self.var('offsetX')
		offset_y = self.var('offsetY')

		if swap_props:
			props_add = []
			props_del = []
			for map in [self.map, self.map.backdrop]:
				for id, value in map.props.items():
					layer, x, y, prop = value
					new_prop = copy_func.copy(prop)
					if copy:
						if layer == layer1:
							props_add.append((map, id, x, y, new_prop, layer2))
						if clear and layer == layer2:
							props_del.append((map, id))
					elif layer == layer1 or layer == layer2:
						props_add.append((map, id, x, y, new_prop, layer1 if layer == layer2 else layer2))
						props_del.append((map, id))

			for (map, id) in props_del:
				del map.props[id]

			for (map, id, x, y, prop, layer) in props_add:
				map.add_prop(layer, x + offset_x, y + offset_y, prop)

		map = self.map

		if swap_tiles:
			tiles_add = []
			tiles_del = []
			for id, tile in map.tiles.items():
				layer, x, y = id
				new_tile = copy_func.copy(tile)
				if copy:
					if layer == layer1:
						if not ignore_dust_blocks or not tile.is_dustblock():
							tiles_add.append((id, x, y, new_tile, layer2))
					if clear and layer == layer2:
						tiles_del.append(id)
				elif layer == layer1 or layer == layer2:
					tiles_add.append((id, x, y, new_tile, layer1 if layer == layer2 else layer2))
					tiles_del.append(id)

			for id in tiles_del:
				del map.tiles[id]

			for (id, x, y, tile, layer) in tiles_add:
				x += int(offset_x)
				y += int(offset_y)
				if (layer, x, y) in map.tiles:
					del map.tiles[(layer, x, y)]
				map.add_tile(layer, x, y, tile)

		if swap_all_fog_triggers:
			for (id, (x, y, entity)) in list(map.entities.items()):
				if isinstance(entity, FogTrigger):
					vars = entity.vars
					fog_per = vars['fog_per'].value[1]
					fog_colour = vars['fog_colour'].value[1]

					sub_layers = range(
						-1,
						25 if 'has_sub_layers' in vars and vars['has_sub_layers'].value else 0
					)

					if copy:
						for layer_sub in sub_layers:
							sub_layer_index_1 = layer1 + 21 + layer_sub * 21
							sub_layer_index_2 = layer2 + 21 + layer_sub * 21

							fog_per[sub_layer_index_2].value = fog_per[sub_layer_index_1].value
							fog_colour[sub_layer_index_2].value = fog_colour[sub_layer_index_1].value
					else:
						for layer_sub in sub_layers:
							sub_layer_index_1 = layer1 + 21 + layer_sub * 21
							sub_layer_index_2 = layer2 + 21 + layer_sub * 21

							tmp_per = fog_per[sub_layer_index_1].value
							tmp_colour = fog_colour[sub_layer_index_1].value
							fog_per[sub_layer_index_1].value = fog_per[sub_layer_index_2].value
							fog_colour[sub_layer_index_1].value = fog_colour[sub_layer_index_2].value
							fog_per[sub_layer_index_2].value = tmp_per
							fog_colour[sub_layer_index_2].value = tmp_colour

		self.message_var.set('Success!')

	# END apply

# END SwapLayerAction
