from tkinter import ttk, messagebox
import dustmaker

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

		SpriteSet = dustmaker.TileSpriteSet
		self.sprites = dict(
			Leaves=(SpriteSet.forest, False), Thorns=(SpriteSet.forest, True),
			Trash=(SpriteSet.city, False), Cones=(SpriteSet.city, True),
			Dust=(SpriteSet.mansion, False), Spikes=(SpriteSet.mansion, True),
			Slime=(SpriteSet.laboratory, False), Wires=(SpriteSet.laboratory, True),
			Polygons=(SpriteSet.tutorial, False), PolygonSpikes=(SpriteSet.tutorial, True)
		)
		self.sprites_list = [
			'Leaves', 'Trash', 'Dust', 'Slime', 'Polygons',
			'Thorns', 'Cones', 'Spikes', 'Wires', 'PolygonSpikes'
		]

		self.messageVar = tk.StringVar()
	# END __init__

	def init(self):
		Action.init(self)
	# END init

	def createGui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.createModalWindow('Replace Dust')

		top_frame = ttk.Frame(dlg)
		top_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		list_var = tk.StringVar(value=self.sprites_list)

		ttk.Label(top_frame, text="From").grid(column=0, row=0, sticky=tk.W)
		self.from_box = tk.Listbox(top_frame, listvariable=list_var, width=26, height=10, selectmode='extended', exportselection=False)
		self.from_box.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(PADDING, 0), pady=PADDING)
		self.from_box.config(font='Helvetica 11')

		ttk.Label(top_frame, text="To").grid(column=1, row=0, sticky=tk.W)
		self.to_box = tk.Listbox(top_frame, listvariable=list_var, width=26, height=10, exportselection=False)
		self.to_box.grid(column=1, row=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(PADDING, 0), pady=PADDING)
		self.to_box.config(font='Helvetica 11')

		ttk.Button(top_frame, text='Replace', command=self.apply).grid(column=0, row=2, sticky=(tk.W), padx=PADDING, pady=PADDING)
		ttk.Label(top_frame, textvariable=self.messageVar).grid(column=1, row=2, sticky=(tk.W))

		self.centreWindow(dlg)

		pass # END func

	def run(self, map):
		Action.run(self, map)

		self.messageVar.set('')
		self.createGui()

	# END run

	def apply(self):
		from_selection = self.from_box.curselection()
		if len(from_selection) == 0:
			messagebox.showinfo(message='Please select one or more types of dust/spikes to replace', icon='warning')
			return

		to_selection = self.to_box.curselection()
		if len(to_selection) == 0:
			messagebox.showinfo(message='Please select a new dust/spike', icon='warning')
			return

		self.messageVar.set('Working...')
		self.root.update_idletasks()

		from_list = {}
		for index in from_selection:
			name = self.from_box.get(index)
			from_list[self.sprites[name]] = True

		to_name = self.to_box.get(to_selection[0])
		to_sprite, to_spikes = self.sprites[to_name]

		sides = [dustmaker.TileSide.LEFT, dustmaker.TileSide.RIGHT, dustmaker.TileSide.TOP, dustmaker.TileSide.BOTTOM]
		for id, tile in self.map.tiles.items():
			for side in sides:
				if tile.edge_filth_sprite(side) in from_list:
					tile.edge_filth_sprite(side, to_sprite, to_spikes)
			pass

		self.messageVar.set('Success!')

		pass # END func
