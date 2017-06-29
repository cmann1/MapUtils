import os.path
import sys
import math
import re
from tkinter import ttk
from tkinter import filedialog

import Render.png as png
from Render.font import RenderFont

from dustmaker import *
from dustmaker.Entity import Trigger, FogTrigger, Apple
from .Action import Action
from CreateToolTip import *


class RenderAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.vars['plxOffsetX'] = (tk.IntVar(), 0)
		self.vars['plxOffsetY'] = (tk.IntVar(), 0)
		self.vars['plx6OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx6OffsetY'] = (tk.IntVar(), 0)
		self.vars['plx7OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx7OffsetY'] = (tk.IntVar(), 0)
		self.vars['plx8OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx8OffsetY'] = (tk.IntVar(), 0)
		self.vars['plx9OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx9OffsetY'] = (tk.IntVar(), 0)
		self.vars['plx10OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx10OffsetY'] = (tk.IntVar(), 0)
		self.vars['plx11OffsetX'] = (tk.IntVar(), 0)
		self.vars['plx11OffsetY'] = (tk.IntVar(), 0)
		self.vars['useFogTrigger'] = (tk.IntVar(), 1)
		self.vars['renderEntities'] = (tk.BooleanVar(), True)
		self.vars['padding'] = (tk.IntVar(), 4)

		self.layerList = []
		self.parallaxOffset = None
		self.parallaxLayersOffset = None
		self.padding = 0

		self.messageVar = tk.StringVar()
	# END __init__
	
	def init(self):
		Action.init(self)
	# END init

	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		offset_min = -1000
		offset_max = 1000

		dlg = self.create_modal_window("Swap Layers")
		dlg.resizable(0, 0)

		optionsFrame = ttk.Frame(dlg, padding=PADDING)
		optionsFrame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.W, tk.E))

		useFogTrigger = ttk.Label(optionsFrame, text='Fog trigger index')
		useFogTrigger.grid(column=0, row=0, sticky=tk.W, pady=(2,0))
		CreateToolTip(useFogTrigger, "-1 indicates no fog trigger")
		tk.Spinbox(optionsFrame, from_=-1, to=100, textvariable=self.vars['useFogTrigger'][0]).grid(column=1, row=0, padx=(PADDING, 0), pady=(2,0))

		ttk.Label(optionsFrame, text='Image padding').grid(column=0, row=1, sticky=tk.W, pady=(2,0))
		tk.Spinbox(optionsFrame, from_=0, to=100, textvariable=self.vars['padding'][0]).grid(column=1, row=1, padx=(PADDING, 0), pady=(2,0))

		ttk.Checkbutton(optionsFrame, text='Render entities', variable=self.vars['renderEntities'][0], onvalue=True, offvalue=False).grid(column=0, row=2, columnspan=2, sticky=tk.W, pady=(2,0))

		parallaxFrame = ttk.LabelFrame(dlg, padding=PADDING, text="Parallax Offsets")
		parallaxFrame.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx = PADDING, pady=(PADDING, 0))

		row = 0
		for layer in ['', 6, 7, 8, 9, 10, 11]:
			name = 'Global' if layer == '' else 'Layer ' + str(layer)
			var_name = 'plx' + str(layer) + 'Offset'
			ttk.Label(parallaxFrame, text=name).grid(column=0, row=row, sticky=tk.W, pady=(2,0))
			tk.Spinbox(parallaxFrame, from_=offset_min, to=offset_max, textvariable=self.vars[var_name + 'X'][0]).grid(column=1, row=row, padx=(PADDING,0), pady=(2,0))
			tk.Spinbox(parallaxFrame, from_=offset_min, to=offset_max, textvariable=self.vars[var_name + 'Y'][0]).grid(column=2, row=row, padx=(PADDING,0), pady=(2,0))
			row += 1

		buttonFrame = ttk.Frame(dlg, padding=PADDING)
		buttonFrame.grid(column=0, row=3, sticky=(tk.N, tk.S, tk.W, tk.E))

		ttk.Button(buttonFrame, text="Render", command=self.apply).grid(column=0, row=0, sticky=(tk.W))
		ttk.Label(buttonFrame, textvariable=self.messageVar).grid(column=1, row=0, sticky=(tk.W))

		self.centre_window(dlg)
	# END 	createGui

	def run(self, map):
		Action.run(self, map)

		self.messageVar.set('')
		self.create_gui()
	# END run

	def apply(self):
		filename = filedialog.asksaveasfilename(initialfile=self.map.name() + '.png')
		if filename == '':
			return

		self.messageVar.set('Rendering...')
		self.root.update_idletasks()

		map = self.map
		parallaxOffset = self.parallaxOffset = (self.vars['plxOffsetX'][0].get(), self.vars['plxOffsetY'][0].get())
		parallaxLayersOffset = self.parallaxLayersOffset = {  # Offsets for individual layers
			6: (self.vars['plx6OffsetX'][0].get(), self.vars['plx6OffsetY'][0].get()),
			7: (self.vars['plx7OffsetX'][0].get(), self.vars['plx7OffsetY'][0].get()),
			8: (self.vars['plx8OffsetX'][0].get(), self.vars['plx8OffsetY'][0].get()),
			9: (self.vars['plx9OffsetX'][0].get(), self.vars['plx9OffsetY'][0].get()),
			10: (self.vars['plx10OffsetX'][0].get(), self.vars['plx10OffsetY'][0].get()),
			11: (self.vars['plx11OffsetX'][0].get(), self.vars['plx11OffsetY'][0].get())
		}
		useFogTrigger = self.vars['useFogTrigger'][0].get()
		renderEntities = self.vars['renderEntities'][0].get()
		padding = self.padding = self.vars['padding'][0].get()

		bgColour = [0, 0, 0, 255]
		layerList = self.layerList = [LayersImage(self, x) for x in range(23)]
		entitySprites = {}
		tiles = {}

		entityLayer = layerList[18]
		collisionLayer = layerList[19]
		fogTriggerCount = -1

		# Get fog colours
		for (id, (x, y, entity)) in list(map.entities.items()):
			if isinstance(entity, FogTrigger):
				fogTriggerCount += 1

				if useFogTrigger == -1 or fogTriggerCount != useFogTrigger:
					continue
				#

				vars = entity.vars
				gradient_middle = vars['gradient_middle'].value
				gradient = vars['gradient'].value[1]
				fog_per = vars['fog_per'].value[1]
				fog_colour = vars['fog_colour'].value[1]

				g1 = self.int2rgb(gradient[0].value)
				g2 = self.int2rgb(gradient[1].value)
				g3 = self.int2rgb(gradient[2].value)

				bgColour[0] = round((g1[0] + g2[0] + g3[0]) / 3)
				bgColour[1] = round((g1[1] + g2[1] + g3[1]) / 3)
				bgColour[2] = round((g1[2] + g2[2] + g3[2]) / 3)

				for i in range(len(fog_per)):
					layerList[i].colour = self.int2rgb(fog_colour[i].value)
					layerList[i].blend = fog_per[i].value
				#

			#
			elif renderEntities and (isinstance(entity, Enemy) or isinstance(entity, Apple)):
				spritePath = 'Render/sprites/'
				sprite = entity.type
				if isinstance(entity, Apple):
					spritePath += 'entity/'
				#
				else:
					spritePath += 'enemy/'
					sprite = re.sub(r"^enemy_", r"", sprite)
				#
				spritePath += sprite + '.png'

				if not os.path.isfile(spritePath):
					continue
				#

				if spritePath not in entitySprites:
					reader = png.Reader(spritePath)
					w, h, pixels, metadata = reader.read()
					pixels = list(pixels)
					# width, height, offsetX, offsetY, pixels
					entitySprites[spritePath] = (w, h, math.floor(w / 2), h, pixels)
				#

				entityLayer.entities.append([x, y, spritePath])

		# Calculate sizes
		for id, tile in map.tiles.items():
			layer, x, y = id

			layerData = layerList[layer]

			layerData.tiles.append((layer, x, y, self.getTileName(tile)))
			layerData.minX = min(layerData.minX, x)
			layerData.minY = min(layerData.minY, y)
			layerData.maxX = max(layerData.maxX, x)
			layerData.maxY = max(layerData.maxY, y)
		#

		maxSizeX = 0
		maxSizeY = 0
		for layerData in layerList:
			layerData.update()
			maxSizeX = max(maxSizeX, layerData.sizeX)
			maxSizeY = max(maxSizeY, layerData.sizeY)
		#
		layerList[19].updateOffsets(maxSizeX, maxSizeY)
		for layerData in layerList:
			if layerData.index != 19:
				layerData.updateOffsets(maxSizeX, maxSizeY)
			#
		#

		maxSizeX += padding * 2
		maxSizeY += padding * 2
		w, h = maxSizeX * 4, maxSizeY
		pixels = [[bgColour[x % 4] for x in range(w)] for y in range(h)]

		# Write to pixels array
		for layerData in layerList:
			# log.write("----\n")
			minX = layerData.minX
			minY = layerData.minY
			layerColour = layerData.colour
			layerBlend = layerData.blend

			for tileData in layerData.tiles:
				layer, x, y, sprite = tileData

				sprite = 'Render/' + sprite
				if sprite not in tiles:
					alt_sprite = ''
					if not os.path.isfile(sprite):
						base = os.path.basename(sprite)
						alt_sprite = sprite
						sprite = os.path.dirname(sprite) + '/' + re.sub(r"^tile(\d+)_(\d+)_0001\.png$",
						                                                r"tile\1_1_0001.png", base)
					# log.write(base + ' - ' + re.sub(r"^tile(\d+)_(\d+)_0001\.png$", r"tile\1_1_0001.png", base) + "\n")
					# log.write(alt_sprite + ' - ' + sprite + "\n")
					#
					reader = png.Reader(sprite)
					w, h, tilePixels, metadata = reader.read()
					rgb = list(tilePixels)[0]
					tiles[sprite] = [rgb[0], rgb[1], rgb[2], rgb[3]]

					if alt_sprite != '':
						tiles[alt_sprite] = tiles[sprite]
					#
				#

				r, g, b, a = tiles[sprite]
				a /= 255

				px = x - minX
				py = y - minY

				if px < 0 or py < 0 or px >= maxSizeX or py >= maxSizeY:
					continue
				#

				if layerData.blend > 0:
					r = r + (layerColour[0] - r) * layerBlend
					g = g + (layerColour[1] - g) * layerBlend
					b = b + (layerColour[2] - b) * layerBlend
				#

				pi = px * 4
				dstr = pixels[py][pi + 0]
				dstg = pixels[py][pi + 1]
				dstb = pixels[py][pi + 2]
				pixels[py][pi + 0] = round(dstr + (r - dstr) * a)
				pixels[py][pi + 1] = round(dstg + (g - dstg) * a)
				pixels[py][pi + 2] = round(dstb + (b - dstb) * a)
				# pixels[py][pi + 1] = 0
				# pixels[py][pi + 2] = 0
				# pixels[py][pi + 3] = 255

			if renderEntities:
				for ex, ey, spritePath in layerData.entities:
					width, height, offsetX, offsetY, entityPixels = entitySprites[spritePath]

					for y in range(height):
						pixRow = entityPixels[y]
						for x in range(width):
							spritei = x * 4
							r = pixRow[spritei + 0]
							g = pixRow[spritei + 1]
							b = pixRow[spritei + 2]

							# px = round(ex) + x - offsetX
							# py = round(ey) + y - offsetY
							px = round(ex) - collisionLayer.minX + x - offsetX
							py = round(ey) - collisionLayer.minY + y - offsetY

							if px < 0 or py < 0 or px >= maxSizeX or py >= maxSizeY:
								continue
							#

							if layerData.blend > 0:
								r = r + (layerColour[0] - r) * layerBlend
								g = g + (layerColour[1] - g) * layerBlend
								b = b + (layerColour[2] - b) * layerBlend
							#

							pi = px * 4
							pixels[py][pi + 0] = round(r)
							pixels[py][pi + 1] = round(g)
							pixels[py][pi + 2] = round(b)

		png.from_array(pixels, 'RGBA').save(filename)

		font = RenderFont()
		font.render(map.name(), os.path.join(os.path.dirname(filename), os.path.splitext(os.path.basename(filename))[0] + '-name.png'))

		self.messageVar.set('Success!')
	# END apply

	def getTileName(self, tile):
		return "tiles/%s/tile%d_%d_0001.png" % (
			tile.sprite_set().name, tile.sprite_tile(), tile.sprite_palette() + 1)

	def int2rgb(self, int):
		return [
			(int >> 16) & 255,
			(int >> 8) & 255,
			(int >> 0) & 255
		]

# END Action

class LayersImage(object):
	def __init__(self, action, index):
		self.action = action
		self.index = index
		self.realMinX = 0
		self.realMinY = 0
		self.minX = sys.maxsize
		self.minY = sys.maxsize
		self.maxX = - sys.maxsize
		self.maxY = - sys.maxsize
		self.sizeX = 0
		self.sizeY = 0
		self.tiles = []
		self.entities = []
		self.colour = [0, 0, 0]
		self.blend = 0

	def update(self):
		self.sizeX = self.maxX - self.minX + 1
		self.sizeY = self.maxY - self.minY + 1

	def updateOffsets(self, maxSizeX, maxSizeY):
		self.realMinX = self.minX
		self.realMinY = self.minY

		self.minX -= self.action.padding
		self.minY -= self.action.padding

		if self.index > 11 and self.index != 19:
			self.minX = self.action.layerList[19].minX
			self.minY = self.action.layerList[19].minY
		#
		else:
			if self.index >= 6 and self.index < 12:
				layerOffsets = self.action.parallaxLayersOffset[self.index]
				self.minX -= self.action.parallaxOffset[0] + layerOffsets[0]
				self.minY -= self.action.parallaxOffset[1] + layerOffsets[1]
			#
			if maxSizeX > self.sizeX:
				self.minX -= math.floor((maxSizeX - self.sizeX) / 2)
			#
			if maxSizeY > self.sizeY:
				self.minY -= math.floor((maxSizeY - self.sizeY) / 2)
			#
			#
