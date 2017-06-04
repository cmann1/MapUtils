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

		self.currentMapPath = None
		self.currentMap = None
		self.mapNameVar = tk.StringVar()

		self.vars['translateX'] = (tk.IntVar(), 0)
		self.vars['translateY'] = (tk.IntVar(), 0)
		self.vars['alignToPlayerSpawn'] = (tk.BooleanVar(), False)
		self.vars['alignToMap2PlayerSpawn'] = (tk.BooleanVar(), False)
		self.vars['withinPlayerBounds'] = (tk.BooleanVar(), False)

		self.messageVar = tk.StringVar()

	# END __init__

	def init(self):
		Action.init(self)

	# END init

	def createGui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		offset_min = -1000000000
		offset_max = 1000000000

		dlg = self.createModalWindow("Merge")

		mapFrame = ttk.Frame(dlg, padding=PADDING)
		mapFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))

		nameLabel = ttk.Label(mapFrame, textvariable=self.mapNameVar, width=30, justify="left")
		nameLabel.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E))
		nameLabel.config(font="Helvetica 11 bold")
		ttk.Button(mapFrame, text="Open", command=self.open).grid(column=2, row=0, sticky=(tk.W, tk.E))

		optionsFrame = self.optionsFrame = ttk.Frame(dlg, padding=PADDING)
		optionsFrame.grid(column=0, row=1, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Label(optionsFrame, text='Translate').grid(column=0, row=0, sticky=tk.W, pady=(2, 0))
		tk.Spinbox(optionsFrame, from_=offset_min, to=offset_max, textvariable=self.vars['translateX'][0]).grid(
			column=1, row=0, padx=(PADDING, 0), pady=(2, 0))
		tk.Spinbox(optionsFrame, from_=offset_min, to=offset_max, textvariable=self.vars['translateY'][0]).grid(
			column=2, row=0, padx=(PADDING, 0), pady=(2, 0))

		alignMap1Spawn = ttk.Checkbutton(optionsFrame, text='Align to player spawn', variable=self.vars['alignToPlayerSpawn'][0],
		                onvalue=True,
		                offvalue=False)
		alignMap1Spawn.grid(column=0, row=1, columnspan=2, sticky=tk.W)
		alignMap2Spawn = ttk.Checkbutton(optionsFrame, text='Align to map 2 player spawn',
		                variable=self.vars['alignToMap2PlayerSpawn'][0], onvalue=True,
		                offvalue=False)
		alignMap2Spawn.grid(column=0, row=2, columnspan=2, sticky=tk.W)
		selective_checkbox = ttk.Checkbutton(optionsFrame, text='Within player 3 and 4 bounds',
		                                     variable=self.vars['withinPlayerBounds'][0], onvalue=True,
		                                     offvalue=False)
		selective_checkbox.grid(column=0, row=3, columnspan=2, sticky=tk.W)
		CreateToolTip(alignMap1Spawn, "Aligns the origin of this map with the position of the player spawn in the main map when merging")
		CreateToolTip(alignMap2Spawn, "Aligns the origin of this map with its player spawn.")
		CreateToolTip(selective_checkbox, "Anything outside of the rectangle created by the player 3 and 4 starting postions will be deleted before merging")

		ttk.Button(optionsFrame, text="Merge", command=self.apply).grid(column=0, row=4, sticky=(tk.W))
		ttk.Label(optionsFrame, textvariable=self.messageVar).grid(column=1, row=4, sticky=(tk.W))

		self.centreWindow(dlg)

	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.messageVar.set('')
		self.createGui()
		self.setMap()

		self.setMap(os.getenv('APPDATA') + '/Dustforce/user/level_src/Test2' if self.app.LOAD_TEST_MAPS else None)
	# END run

	def apply(self):
		self.messageVar.set('Working...')
		self.root.update_idletasks()

		translateX = self.var('translateX')
		translateY = self.var('translateY')
		alignToMap1Start = self.var('alignToPlayerSpawn')
		alignToMap2Start = self.var('alignToMap2PlayerSpawn')
		withinPlayerBounds = self.var('withinPlayerBounds')
		map1 = self.map
		map2 = self.currentMap

		if withinPlayerBounds:
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
				del map2.entities[id]

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

		if alignToMap1Start or alignToMap2Start or translateX != 0 or translateY != 0:
			if alignToMap1Start:
				pos1 = map1.start_position()
			else:
				pos1 = (0, 0)

			if alignToMap2Start:
				pos2 = map2.start_position()
			else:
				pos2 = (0, 0)

			map2.translate(round(translateX + pos1[0] - pos2[0]), round(translateY + pos1[1] - pos2[1]))
		#

		map1.merge_map(map2)
		self.messageVar.set('Success!')

	# END apply

	def open(self):
		filename = filedialog.askopenfilename()

		if filename != "":
			self.setMap(filename)
		# END if

	# END apply

	def setMap(self, path=None):
		if not path is None:
			self.mapNameVar.set("Loading...")
			self.dlg.update_idletasks()

			try:
				with open(path, "rb") as f:
					try:
						self.currentMap = dustmaker.read_map(f.read())
					except Exception:
						self.setMap()
						self.mapNameVar.set("Error loading map file")
						return
					#
			except FileNotFoundError:
				self.setMap()
				self.mapNameVar.set("Error loading map file")
				return

			name = os.path.basename(path)
			self.mapNameVar.set(name)
			self.currentMapPath = path
		else:
			self.currentMap = None
			self.currentMapPath = None
			self.mapNameVar.set('Select a map')
		# END ifelse

		state = 'disabled' if path is None else 'normal'
		for child in self.optionsFrame.winfo_children():
			child.configure(state=state)

		# END apply

# END Action
