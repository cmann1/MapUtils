from tkinter import ttk
import tkinter as tk
import dustmaker

from .Action import Action


class SetTileSpritesAction(Action):

	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['layer'] = (tk.IntVar(), 19)
		self.vars['filter_set'] = (tk.IntVar(), 0)
		self.vars['filter_tile'] = (tk.IntVar(), -1)
		self.vars['filter_palette'] = (tk.IntVar(), -1)

		self.vars['target_set'] = (tk.IntVar(), int(dustmaker.TileSpriteSet.mansion))
		self.vars['target_tile'] = (tk.IntVar(), 1)
		self.vars['target_palette'] = (tk.IntVar(), 1)

		self.vars['withinPlayerBounds'] = (tk.BooleanVar(), False)

		self.message_var = tk.StringVar()

	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Set Tile Sprites')

		layer_frame = ttk.Frame(dlg, padding=PADDING)
		layer_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
		options_frame = ttk.Frame(dlg, padding=PADDING)
		options_frame.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.W, tk.E))
		button_frame = ttk.Frame(dlg, padding=PADDING)
		button_frame.grid(column=0, row=4, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(layer_frame, text='Layer').grid(column=0, row=0)
		layer = tk.Spinbox(layer_frame, from_=0, to=20, textvariable=self.vars['layer'][0])
		layer.grid(column=1, row=0)

		ttk.Label(options_frame, text='Filter Set').grid(column=0, row=0)
		filter_set = tk.Spinbox(options_frame, from_=0, to=20, textvariable=self.vars['filter_set'][0])
		filter_set.grid(column=1, row=0)
		ttk.Label(options_frame, text='Filter Tile').grid(column=0, row=1)
		filter_tile = tk.Spinbox(options_frame, from_=-1, to=20, textvariable=self.vars['filter_tile'][0])
		filter_tile.grid(column=1, row=1)
		ttk.Label(options_frame, text='Filter Palette').grid(column=0, row=2)
		filter_palette = tk.Spinbox(options_frame, from_=-1, to=20, textvariable=self.vars['filter_palette'][0])
		filter_palette.grid(column=1, row=2)

		ttk.Label(options_frame, text='Target Set').grid(column=2, row=0)
		target_set = tk.Spinbox(options_frame, from_=0, to=20, textvariable=self.vars['target_set'][0])
		target_set.grid(column=3, row=0)
		ttk.Label(options_frame, text='Target Tile').grid(column=2, row=1)
		target_tile = tk.Spinbox(options_frame, from_=1, to=20, textvariable=self.vars['target_tile'][0])
		target_tile.grid(column=3, row=1)
		ttk.Label(options_frame, text='Target Palette').grid(column=2, row=2)
		target_palette = tk.Spinbox(options_frame, from_=1, to=20, textvariable=self.vars['target_palette'][0])
		target_palette.grid(column=3, row=2)

		ttk.Checkbutton(options_frame, text='Within player 3 and 4 bounds',
		                variable=self.vars['withinPlayerBounds'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=3, columnspan=4, sticky=tk.W)

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

		filter_layer = self.var('layer')

		filter_set = dustmaker.TileSpriteSet(self.var('filter_set'))
		filter_tile = self.var('filter_tile')
		filter_palette = self.var('filter_palette')

		target_set = dustmaker.TileSpriteSet(self.var('target_set'))
		target_tile = self.var('target_tile')
		target_palette = self.var('target_palette')

		within_player_bounds = self.var('withinPlayerBounds')

		bounds1 = self.map.start_position(None, 3)
		bounds2 = self.map.start_position(None, 4)
		min_x = min(bounds1[0], bounds2[0])
		min_y = min(bounds1[1], bounds2[1])
		max_x = max(bounds1[0], bounds2[0])
		max_y = max(bounds1[1], bounds2[1])

		map = self.map

		for id, tile in map.tiles.items():
			layer, x, y = id

			if within_player_bounds:
				if x < min_x or x > max_x or y < min_y or y > max_y:
					continue

			if layer != filter_layer:
				continue

			if(
				(tile.sprite_set() == filter_set or filter_set == dustmaker.TileSpriteSet.none_0) and
				(filter_tile == -1 or tile.sprite_tile() == filter_tile) and
				(filter_palette == -1 or tile.sprite_palette() == filter_palette)
			):
				tile.sprite_set(target_set)
				tile.sprite_tile(target_tile)
				tile.sprite_palette(target_palette)



		self.message_var.set('Success!')
	# END apply
