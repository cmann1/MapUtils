from tkinter import ttk, messagebox
import dustmaker

from Settings import *
from CreateToolTip import *
from .Action import Action


class ReplaceDustAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		# self.list_var = tk.StringVar()

		# self.vars['layer1'] = (tk.IntVar(), 12)
		# self.vars['sublayer1'] = (tk.IntVar(), 19)
		# self.vars['layer2'] = (tk.IntVar(), 13)
		# self.vars['sublayer2'] = (tk.IntVar(), 19)
		# self.vars['offsetX'] = (tk.DoubleVar(), 0)
		# self.vars['offsetY'] = (tk.DoubleVar(), 0)
		# self.vars['rotation'] = (tk.DoubleVar(), 0)
		# self.vars['repeat'] = (tk.IntVar(), 1)
		# self.vars['copy'] = (tk.BooleanVar(), False)

		self.from_box = None
		self.to_box = None

		self.from_tree = None
		self.to_tree = None
		self.drag_select_state = True

		SpriteSet = dustmaker.TileSpriteSet
		self.sprites = dict(
			Dust=dict(
				Leaves=(SpriteSet.forest, False),
				Trash=(SpriteSet.city, False),
				Dust=(SpriteSet.mansion, False),
				Slime=(SpriteSet.laboratory, False),
				Polygons=(SpriteSet.tutorial, False),
			),
			Spikes=dict(
				Thorns=(SpriteSet.forest, True),
				Cones=(SpriteSet.city, True),
				Spikes=(SpriteSet.mansion, True),
				Wires=(SpriteSet.laboratory, True),
				Polygons=(SpriteSet.tutorial, True)
			)
		)
		self.sprites['None'] = (SpriteSet.none_0, False)
		self.sprites_list = [
			'Leaves', 'Trash', 'Dust', 'Slime', 'Polygons',
			'Thorns', 'Cones', 'Spikes', 'Wires', 'PolygonSpikes'
		]

		self.icons = {}

		self.message_var = tk.StringVar()
	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Replace Dust')

		top_frame = ttk.Frame(dlg)
		top_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)
		button_frame = ttk.Frame(dlg)
		button_frame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		list_var = tk.StringVar(value=self.sprites_list)

		ttk.Label(top_frame, text='From').grid(column=0, row=0, sticky=tk.W)
		ttk.Label(top_frame, text='To').grid(column=1, row=0, sticky=tk.W)

		ttk.Button(button_frame, text='Replace', command=self.apply).grid(column=0, row=3, sticky=(tk.W), padx=PADDING, pady=PADDING)
		ttk.Label(button_frame, textvariable=self.message_var).grid(column=1, row=3, sticky=(tk.W))

		style = ttk.Style(dlg)
		style.configure('Treeview', rowheight=30)
		self.from_tree = self.create_tree(top_frame, column=0, row=1, padding=PADDING, selectmode='extended')
		self.to_tree = self.create_tree(top_frame, column=1, row=1, padding=PADDING, selectmode='browse', include_none=True)
		self.to_tree.configure(selectmode='browse')

		self.centre_window(dlg)

		pass  # END func

	def add_node(self, tree, parent_node, type_name, dust_type):
		dust_name = dust_type.lower()
		icon_name = '%s_%s.png' % (type_name, dust_name)
		if icon_name in self.icons:
			image = self.icons[icon_name]
		else:
			image = self.icons[icon_name] = tk.PhotoImage(file=FILES_ROOT + icon_name)

		tree.insert(parent_node, 'end', text=dust_type, open=True, image=image)

		pass

	def create_tree(self, top_frame, column, row, padding, selectmode, include_none=False):
		nodes = (
			('Dust', ('Leaves', 'Trash', 'Dust', 'Slime', 'Polygons')),
			('Spikes', ('Thorns', 'Cones', 'Spikes', 'Wires', 'Polygons'))
		)

		tree = ttk.Treeview(top_frame, show='tree', height=13, selectmode=selectmode)
		tree.grid(column=column, row=row, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(padding, 0), pady=padding)
		tree.bind('<<TreeviewSelect>>', self.on_tree_select)
		tree.bind('<ButtonPress-1>', self.on_tree_down)
		tree.bind('<B1-Motion>', self.on_tree_move)

		for (type, dust_list) in nodes:
			type_name = type.lower()
			parent_node = tree.insert('', 'end', text=type, open=True, tags='is_parent')
			for dust_type in dust_list:
				self.add_node(tree, parent_node, type_name, dust_type)
				pass
			pass

		if include_none:
			self.add_node(tree, '', 'dust', 'None')
			pass

		return tree

		pass  # END func

	def on_tree_down(self, event):
		s = event.state
		ctrl = (s & 0x4) != 0

		if not ctrl:
			self.drag_select_state = True
			return

		tree = event.widget
		item = tree.identify_row(event.y)
		self.drag_select_state = item not in tree.selection()
		pass

	def on_tree_move(self, event):
		tree = event.widget
		item = tree.identify_row(event.y)

		multiple = (str(tree.cget('selectmode')) == 'extended')

		if multiple:
			if self.drag_select_state:
				if item not in tree.selection():
					tree.selection_add(item)
			else:
				if item in tree.selection():
					tree.selection_remove(item)
		else:
			tree.selection('set', item)

		pass

	def on_tree_select(self, event):
		tree = event.widget
		selection = tree.selection()
		for item in selection:
			if 'is_parent' in tree.item(item, 'tags'):
				tree.selection_remove(item)

	def get_sprite(self, tree, item):
		parent_text = tree.item(tree.parent(item), 'text')
		item_text = tree.item(item, 'text')

		if parent_text == '':
			return self.sprites[item_text]
		else:
			return self.sprites[parent_text][item_text]

	def run(self, map):
		Action.run(self, map)

		self.message_var.set('')
		self.create_gui()

	# END run

	def apply(self):
		from_selection = self.from_tree.selection()
		if len(from_selection) == 0:
			messagebox.showinfo(message='Please select one or more types of dust/spikes to replace', icon='warning')
			return

		to_selection = self.to_tree.selection()
		if len(to_selection) == 0:
			messagebox.showinfo(message='Please select a new dust/spike', icon='warning')
			return
		
		self.message_var.set('Working...')
		self.root.update_idletasks()

		from_list = {}
		for item in from_selection:
			parent = self.from_tree.item(self.from_tree.parent(item), 'text')
			# print(parent+'.'+self.from_tree.item(item, 'text'), self.get_sprite(self.from_tree, item))
			from_list[self.get_sprite(self.from_tree, item)] = True

		# from_list = {}
		# for index in from_selection:
		# 	name = self.from_box.get(index)
		# 	from_list[self.sprites[name]] = True
		#
		# to_name = self.to_box.get(to_selection[0])
		# to_sprite, to_spikes = self.sprites[to_name]
		#
		to_sprite, to_spikes = self.get_sprite(self.to_tree, to_selection[0])

		sides = (dustmaker.TileSide.LEFT, dustmaker.TileSide.RIGHT, dustmaker.TileSide.TOP, dustmaker.TileSide.BOTTOM)
		for id, tile in self.map.tiles.items():
			for side in sides:
				if tile.edge_filth_sprite(side) in from_list:
					tile.edge_filth_sprite(side, to_sprite, to_spikes)
		# 	pass

		self.message_var.set('Success!')

		pass # END func
