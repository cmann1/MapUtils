from tkinter import ttk

from CreateToolTip import *
from dustmaker.Tile import TileSide

from .Action import Action


class TileBorders(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['layer'] = (tk.IntVar(), 20)
		self.vars['withinPlayerBounds'] = (tk.BooleanVar(), False)

		self.message_var = tk.StringVar()
	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Tile Borders')

		layerFrame = ttk.Frame(dlg, padding=PADDING)
		layerFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		buttonFrame = ttk.Frame(dlg, padding=PADDING)
		buttonFrame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(layerFrame, text='Layer').grid(column=0, row=0)
		layer = tk.Spinbox(layerFrame, from_=0, to=20, textvariable=self.vars['layer'][0])
		layer.grid(column=1, row=0)
		ttk.Checkbutton(layerFrame, text='Within player 3 and 4 bounds',
		                variable=self.vars['withinPlayerBounds'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=2, columnspan=3, sticky=tk.W)

		ttk.Button(buttonFrame, text='Remove', command=self.apply).grid(column=0, row=0, sticky=(tk.W))
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

		layer = self.var('layer')
		within_player_bounds = self.var('withinPlayerBounds')

		bounds1 = self.map.start_position(None, 3)
		bounds2 = self.map.start_position(None, 4)
		min_x = min(bounds1[0], bounds2[0])
		min_y = min(bounds1[1], bounds2[1])
		max_x = max(bounds1[0], bounds2[0])
		max_y = max(bounds1[1], bounds2[1])

		map = self.map

		for id, tile in map.tiles.items():
			tile_layer, x, y = id

			if tile_layer == layer:
				if within_player_bounds:
					if x < min_x or x > max_x or y < min_y or y > max_y:
						continue

				for side in TileSide:
					tile.edge_bits(side, 0)
				pass

		self.message_var.set('Success!')

	# END apply

# END SwapLayerAction
