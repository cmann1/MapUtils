import os
import os.path
from tkinter import ttk
from tkinter import filedialog

import dustmaker
from CreateToolTip import *

from .Action import Action


class MergeAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.optionsFrame = None

		self.current_map_path = None
		self.current_map = None
		self.map_name_var = tk.StringVar()

		self.vars['translateX'] = (tk.IntVar(), 0)
		self.vars['translateY'] = (tk.IntVar(), 0)
		self.vars['alignToPlayerSpawn'] = (tk.BooleanVar(), False)
		self.vars['alignToMap2PlayerSpawn'] = (tk.BooleanVar(), False)
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
		offset_max = 1000000000

		dlg = self.create_modal_window('Merge')

		map_frame = ttk.Frame(dlg, padding=PADDING)
		map_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		name_label = ttk.Label(map_frame, textvariable=self.map_name_var, width=30, justify='left')
		name_label.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))
		name_label.config(font='Helvetica 11 bold')
		ttk.Button(map_frame, text='Open', command=self.open).grid(column=2, row=0, sticky=(tk.W, tk.E))

		options_frame = self.optionsFrame = ttk.Frame(dlg, padding=PADDING)
		options_frame.grid(column=0, row=1, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(options_frame, text='Translate').grid(column=0, row=0, sticky=tk.W, pady=(2, 0))
		tk.Spinbox(options_frame, from_=offset_min, to=offset_max, textvariable=self.vars['translateX'][0]).grid(
			column=1, row=0, padx=(PADDING, 0), pady=(2, 0))
		tk.Spinbox(options_frame, from_=offset_min, to=offset_max, textvariable=self.vars['translateY'][0]).grid(
			column=2, row=0, padx=(PADDING, 0), pady=(2, 0))

		align_map1_spawn = ttk.Checkbutton(options_frame, text='Align to player spawn', variable=self.vars['alignToPlayerSpawn'][0],
		                onvalue=True,
		                offvalue=False)
		align_map1_spawn.grid(column=0, row=1, columnspan=2, sticky=tk.W)
		align_map2_spawn = ttk.Checkbutton(options_frame, text='Align to map 2 player spawn',
		                variable=self.vars['alignToMap2PlayerSpawn'][0], onvalue=True,
		                offvalue=False)
		align_map2_spawn.grid(column=0, row=2, columnspan=2, sticky=tk.W)
		selective_checkbox = ttk.Checkbutton(options_frame, text='Within player 3 and 4 bounds',
		                                     variable=self.vars['withinPlayerBounds'][0], onvalue=True,
		                                     offvalue=False)
		selective_checkbox.grid(column=0, row=3, columnspan=2, sticky=tk.W)
		CreateToolTip(align_map1_spawn, 'Aligns the origin of this map with the position of the player spawn in the main map when merging')
		CreateToolTip(align_map2_spawn, 'Aligns the origin of this map with its player spawn.')
		CreateToolTip(selective_checkbox, 'Anything outside of the rectangle created by the player 3 and 4 starting postions will be deleted before merging')

		ttk.Button(options_frame, text='Merge', command=self.apply).grid(column=0, row=4, sticky=(tk.W))
		ttk.Label(options_frame, textvariable=self.message_var).grid(column=1, row=4, sticky=(tk.W))

		self.centre_window(dlg)

	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()
		self.set_map()

		self.set_map(os.getenv('APPDATA') + '/Dustforce/user/level_src/Test2' if self.app.LOAD_TEST_MAPS else None)
	# END run

	def apply(self):
		self.message_var.set('Working...')
		self.root.update_idletasks()

		translate_x = self.var('translateX')
		translate_y = self.var('translateY')
		align_to_map1_start = self.var('alignToPlayerSpawn')
		align_to_map2_start = self.var('alignToMap2PlayerSpawn')
		within_player_bounds = self.var('withinPlayerBounds')
		map1 = self.map
		map2 = self.current_map

		if within_player_bounds:
			bounds1 = map2.start_position(None, 3)
			bounds2 = map2.start_position(None, 4)
			min_x = min(bounds1[0], bounds2[0])
			min_y = min(bounds1[1], bounds2[1])
			max_x = max(bounds1[0], bounds2[0])
			max_y = max(bounds1[1], bounds2[1])

			# ENTITIES
			entities_del = []
			for (id, (x, y, entity)) in list(map2.entities.items()):
				if x < min_x or x > max_x or y < min_y or y > max_y:
					entities_del.append(id)
			for id in entities_del:
				map2.remove_entity(id)

			# PROPS
			props_del = []
			for id, value in map2.props.items():
				layer, x, y, prop = value
				if x < min_x or x > max_x or y < min_y or y > max_y:
					props_del.append(id)
			for id in props_del:
				del map2.props[id]

			# TILES
			tiles_del = []
			for id, tile in map2.tiles.items():
				layer, x, y = id
				if x < min_x or x > max_x or y < min_y or y > max_y:
					tiles_del.append(id)
			for id in tiles_del:
				del map2.tiles[id]

		if align_to_map1_start or align_to_map2_start or translate_x != 0 or translate_y != 0:
			if align_to_map1_start:
				pos1 = map1.start_position()
			else:
				pos1 = (0, 0)

			if align_to_map2_start:
				pos2 = map2.start_position()
			else:
				pos2 = (0, 0)

			map2.translate(round(translate_x + pos1[0] - pos2[0]), round(translate_y + pos1[1] - pos2[1]))
		#

		map1.merge_map(map2)
		self.message_var.set('Success!')

	# END apply

	def open(self):
		filename = filedialog.askopenfilename()

		if filename != "":
			self.set_map(filename)
		# END if

	# END apply

	def set_map(self, path=None):
		if not path is None:
			self.map_name_var.set("Loading...")
			self.dlg.update_idletasks()

			try:
				with open(path, "rb") as f:
					try:
						self.current_map = dustmaker.read_map(f.read())
					except Exception:
						self.set_map()
						self.map_name_var.set("Error loading map file")
						return
					#
			except FileNotFoundError:
				self.set_map()
				self.map_name_var.set("Error loading map file")
				return

			name = os.path.basename(path)
			self.map_name_var.set(name)
			self.current_map_path = path
		else:
			self.current_map = None
			self.current_map_path = None
			self.map_name_var.set('Select a map')
		# END ifelse

		state = 'disabled' if path is None else 'normal'
		for child in self.optionsFrame.winfo_children():
			child.configure(state=state)

		# END apply

# END Action
