from tkinter import ttk

import dustmaker
from dustmaker.Entity import Emitter, Trigger, CheckPoint, FogTrigger, LevelDoor
from CreateToolTip import *

from .Action import Action


class ClearLayerAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['layer'] = (tk.IntVar(), 12)
		self.vars['sublayer'] = (tk.IntVar(), -1)
		self.vars['clearProps'] = (tk.BooleanVar(), True)
		self.vars['clearTiles'] = (tk.BooleanVar(), True)
		self.vars['clearEmitters'] = (tk.BooleanVar(), True)
		self.vars['withinPlayerBounds'] = (tk.BooleanVar(), False)
		self.vars['invertBounds'] = (tk.BooleanVar(), False)

		self.message_var = tk.StringVar()

	# END __init__

	def init(self):
		Action.init(self)

	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Clear Layer')

		options_frame = ttk.Frame(dlg, padding=PADDING)
		options_frame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))
		button_frame = ttk.Frame(dlg, padding=PADDING)
		button_frame.grid(column=0, row=3, sticky=(tk.N, tk.S, tk.W, tk.E))
		other_frame = ttk.Labelframe(dlg, text='Other', padding=PADDING)
		other_frame.grid(column=0, row=4, sticky=(tk.N, tk.S, tk.W, tk.E), padx=PADDING, pady=PADDING)

		ttk.Label(options_frame, text='Layer').grid(column=0, row=0, sticky=tk.W)
		layer1 = tk.Spinbox(options_frame, from_=-1, to=22, textvariable=self.vars['layer'][0])
		layer1.grid(column=1, row=0)
		ttk.Label(options_frame, text='Sub Layer').grid(column=0, row=1, sticky=tk.W)
		sublayer1 = tk.Spinbox(options_frame, from_=-1, to=24, textvariable=self.vars['sublayer'][0])
		sublayer1.grid(column=1, row=1)

		ttk.Checkbutton(options_frame, text='Props', variable=self.vars['clearProps'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=2, sticky=tk.W)
		ttk.Checkbutton(options_frame, text='Tiles', variable=self.vars['clearTiles'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=3, sticky=tk.W)
		ttk.Checkbutton(options_frame, text='Emitters', variable=self.vars['clearEmitters'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=4, sticky=tk.W)
		ttk.Checkbutton(options_frame, text='Within player 3 and 4 bounds',
		                variable=self.vars['withinPlayerBounds'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=5, sticky=tk.W)
		ttk.Checkbutton(options_frame, text='Invert Bounds',
		                variable=self.vars['invertBounds'][0], onvalue=True,
		                offvalue=False).grid(column=0, row=6, sticky=tk.W)

		button = ttk.Button(button_frame, text='Clear')
		button.grid(column=0, row=0, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		button = ttk.Button(button_frame, text='Clear All')
		button.grid(column=1, row=0, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		ttk.Label(button_frame, textvariable=self.message_var).grid(column=2, row=0, sticky=(tk.W))

		button = ttk.Button(other_frame, text='Clear Enemies')
		button.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=(PADDING, 0))
		button.bind('<ButtonRelease-1>', self.apply)
		button = ttk.Button(other_frame, text='Clear Camera')
		button.grid(column=1, row=1, sticky=(tk.W, tk.E), pady=(PADDING, 0))
		button.bind('<ButtonRelease-1>', self.apply)

		button = ttk.Button(other_frame, text='Clear Checkpoints')
		button.grid(column=0, row=2, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)
		button = ttk.Button(other_frame, text='Clear Deathzones')
		button.grid(column=1, row=2, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		button = ttk.Button(other_frame, text='Clear Doors')
		button.grid(column=0, row=3, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		button = ttk.Button(other_frame, text='Clear Fog')
		button.grid(column=0, row=4, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)
		button = ttk.Button(other_frame, text='Clear Ambience')
		button.grid(column=1, row=4, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		button = ttk.Button(other_frame, text='Clear Music')
		button.grid(column=0, row=5, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)
		button = ttk.Button(other_frame, text='Clear Emitters')
		button.grid(column=1, row=5, sticky=(tk.W, tk.E))
		button.bind('<ButtonRelease-1>', self.apply)

		self.centre_window(dlg)

	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()

	# END run

	def apply(self, event=None):
		type = event.widget.config('text')[-1]
		entities = self.map.entities

		# for (id, (x, y, entity)) in list(entities.items()):
		# 	print(entity.type)
		# return

		within_player_bounds = self.var('withinPlayerBounds')
		invert_bounds = self.var('invertBounds')
		bounds1 = self.map.start_position(None, 3)
		bounds2 = self.map.start_position(None, 4)
		min_x = min(bounds1[0], bounds2[0])
		min_y = min(bounds1[1], bounds2[1])
		max_x = max(bounds1[0], bounds2[0])
		max_y = max(bounds1[1], bounds2[1])

		clear_all = (type == 'Clear All')

		if type == 'Clear' or clear_all:
			layer = self.var('layer')
			sublayer = self.var('sublayer')
			clear_props = self.var('clearProps')
			clear_tiles = self.var('clearTiles')
			clear_emitters = self.var('clearEmitters')

			if clear_all:
				layer = -1
				sublayer = -1

			if clear_emitters or clear_all:
				for (id, (x, y, entity)) in list(self.map.entities.items()):
					if within_player_bounds:
						if x < min_x or x > max_x or y < min_y or y > max_y:
							if not invert_bounds: continue
						elif invert_bounds: continue
					if (layer == -1 or entity.layer == layer) and isinstance(entity, Emitter):
						del self.map.entities[id]

			if clear_props or clear_all:
				props_del = []
				for map in [self.map, self.map.backdrop]:
					for id, value in map.props.items():
						prop_layer, x, y, prop = value
						if within_player_bounds:
							if x < min_x or x > max_x or y < min_y or y > max_y:
								if not invert_bounds: continue
							elif invert_bounds:
								continue
						if (layer == -1 or prop_layer == layer) and (sublayer == -1 or prop.layer_sub == sublayer):
							props_del.append((map, id))

				for (map, id) in props_del:
					del map.props[id]

			if clear_tiles or clear_all:
				tiles_del = []
				for id, tile in self.map.tiles.items():
					tile_layer, x, y = id
					if within_player_bounds:
						if x < min_x or x > max_x or y < min_y or y > max_y:
							if not invert_bounds: continue
						elif invert_bounds: continue
					if layer == -1 or tile_layer == layer:
						tiles_del.append(id)

				for id in tiles_del:
					del self.map.tiles[id]

		if type != 'Clear' or clear_all:
			if type == 'Clear Enemies':
				type = 'AI_controller'
			elif type == 'Clear Camera':
				type = 'camera_node'
			elif type == 'Clear Checkpoints':
				type = 'check_point'
			elif type == 'Clear Deathzones':
				type = 'kill_box'
			elif type == 'Clear Doors':
				type = 'level_door'

			elif type == 'Clear Fog':
				type = 'fog_trigger'
			elif type == 'Clear Ambience':
				type = 'ambience_trigger'
			elif type == 'Clear Music':
				type = 'music_trigger'
			elif type == 'Clear Emitters':
				type = 'entity_emitter'
			elif clear_all:
				type = ''
			else:
				type = None

			if not type is None:
				entities_del = []
				for (id, (x, y, entity)) in list(entities.items()):
					if within_player_bounds:
						if x < min_x or x > max_x or y < min_y or y > max_y:
							if not invert_bounds: continue
						elif invert_bounds: continue
					if entity.type == type or clear_all:
						entities_del.append(id)
						if type == 'AI_controller':
							puppet_id = entity.vars['puppet_id'].value
							if puppet_id in entities:
								entities_del.append(puppet_id)

				for id in entities_del:
					del self.map.entities[id]

		self.message_var.set('Success!')
		return

	# END apply

# END SwapLayerAction
