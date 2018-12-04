import logging
import os
import os.path
from shutil import copyfile
import copy
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from CreateToolTip import *

import dustmaker

from Settings import *
import Actions
from Config import Config

class MainApplication(tk.Frame):
	def __init__(self, root, *args, **kwargs):
		tk.Frame.__init__(self, root, *args, **kwargs)
		self.root = root

		logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='w')
		self.logger = logging.getLogger(__name__)
		
		self.config = Config()
		
		self.current_map_path = ''
		self.map = None
		self.backup = None
		self.map_name = ''

		PADDING = 4
		HPADDING = PADDING / 2

		root.title('Map Utils')
		root.iconbitmap(default=FILES_ROOT + 'dustman.ico')
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		root.resizable(0,0)
		root.protocol('WM_DELETE_WINDOW', self.onWindowClose)
		
		mainframe = ttk.Frame(root, padding=PADDING)
		mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
		mainframe.columnconfigure(0, weight=1)
		mainframe.rowconfigure(2, weight=1)

		self.map_name_var = tk.StringVar()
		self.map_name_var.set('No map selected')
		self.map_filename_var = tk.StringVar()
		self.map_path_var = tk.StringVar()

		file_label_frame = ttk.Frame(mainframe, borderwidth=2, relief='groove')
		file_label_frame.grid(column=0, row=0, rowspan=2, sticky=(tk.N,tk.S,tk.W,tk.E))

		# self.MapNameLabel = ttk.Label(fileLabelFrame, textvariable=self.MapNameVar, width=30, justify='left')
		self.map_name_label = ttk.Entry(file_label_frame, textvariable=self.map_name_var, justify='left')
		self.map_name_label.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E), padx=PADDING, pady=PADDING)
		self.map_name_label.config(font='Helvetica 12 bold')

		self.map_filename_label = ttk.Label(file_label_frame, textvariable=self.map_filename_var, justify='left')
		self.map_filename_label.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E))
		self.map_filename_tooltip = CreateToolTip(self.map_filename_label, '')

		self.map_path_label = ttk.Label(file_label_frame, textvariable=self.map_path_var, width=60, justify='left')
		self.map_path_label.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E))
		self.map_path_tooltip = CreateToolTip(self.map_path_label, '')

		button_frame = ttk.Frame(mainframe)
		button_frame.grid(column=1, row=0, rowspan=2, sticky=(tk.N,tk.S,tk.W,tk.E))
		
		ttk.Button(button_frame, text='Open', command=self.open_map).grid(column=0, row=0, sticky=(tk.N), padx=(PADDING, 0))
		ttk.Button(button_frame, text='Save', command=self.save_map).grid(column=0, row=1, sticky=(tk.N), padx=(PADDING, 0))
		save_copy_btn = ttk.Button(button_frame, text='Save Copy', command=lambda: self.save_map(True))
		save_copy_btn.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E), padx=(PADDING,0))
		CreateToolTip(save_copy_btn, 'Saves a copy with "_modified" appended to the map and file name')

		# Disabled until I can figure out how to change a map's name directly without having to read/write the entire map
		# save_and_backup_btn = ttk.Button(mainframe, text='Save+Backup', command=lambda: self.save_map(True, True))
		# save_and_backup_btn.grid(column=2, row=0, sticky=(tk.N, tk.W, tk.E), padx=(PADDING, 0))
		# CreateToolTip(save_and_backup_btn, 'Makes a backup of the map file before saving')

		self.actionFrame = ttk.Frame(mainframe, borderwidth=2, relief='groove', padding = PADDING)
		self.actionFrame.grid(column=0, row=2, columnspan=3, sticky=(tk.N,tk.S,tk.W,tk.E), pady=(PADDING,0))

		actions = [
			('Merge', Actions.MergeAction(self)),
			('Flip X', Actions.FlipXAction(self), True),
			('Flip Y', Actions.FlipYAction(self), True),
			('Extract Thumb', Actions.ExtractThumbAction(self)),
			('-', None),
			('Translate', Actions.TranslateAction(self)),
			('Rotate', Actions.RotateAction(self)),
			('Upscale', Actions.UpscaleAction(self)),
			('-', None),
			('Swap Layers', Actions.SwapLayerAction(self)),
			('Clear Layer', Actions.ClearLayerAction(self)),
			('Replace Dust', Actions.ReplaceDustAction(self)),
			('Tile Borders', Actions.TileBorders(self)),
			('-', None),
			('Set Tile Sprites', Actions.SetTileSpritesAction(self)),
			('Move Props', Actions.MoveSublayerAction(self)),
			('Text Triggers', Actions.TextTriggerAction(self)),
			# ('Render', Actions.RenderAction(self))
		]

		column = 0
		row = 0
		for name, action, *confirm in actions:
			if name == '-':
				row += 1
				column = 0
				continue

			padx = PADDING if column > 0 else 0
			pady = PADDING if row > 0 else 0
			button = ttk.Button(self.actionFrame, text=name)
			button.grid(column=column, row=row, sticky=(tk.W, tk.E, tk.N), padx=(padx, 0), pady=(pady, 0))
			button.bind('<ButtonRelease-1>', self.runAction)
			button._actionVar = action
			button._confirm_action = confirm[0] if confirm else False
			column += 1

		self.LOAD_TEST_MAPS = False
		self.set_map(os.getenv('APPDATA') + '/Dustforce/user/level_src/Test1' if self.LOAD_TEST_MAPS else None)
		self.centre()
	# END __init__
	
	def centre(self):
		self.root.update_idletasks()
		w = self.root.winfo_reqwidth()
		h = self.root.winfo_reqheight()
		ws = self.root.winfo_screenwidth()
		hs = self.root.winfo_screenheight()
		x = (ws/2) - (w/2)
		y = (hs/2) - (h/2)
		self.root.geometry('+%d+%d' % (x, y))
	# END centre
	
	def set_map(self, path=None):
		if path is not None:
			self.map_name_var.set('Loading...')
			self.map_path_var.set('')
			self.root.update_idletasks()

			try:
				with open(path, 'rb') as f:
					try:
						self.map = dustmaker.read_map(f.read())
						self.map_name = self.map.name()
						# self.backup = copy.deepcopy(self.map)
					except Exception:
						self.set_map()
						self.map_name_var.set('Error loading map file')
						return
					#
			except FileNotFoundError:
				self.set_map()
				self.map_name_var.set('Error loading map file')
				return
		
			filename = os.path.basename(path)
			location = os.path.dirname(path)
			self.map_name_var.set(self.map_name)
			self.map_name_label.state(['!readonly'])
			self.map_filename_var.set('File: %s' % filename)
			self.map_path_var.set('Location: %s' % location)
			self.map_filename_tooltip.text = filename
			self.map_path_tooltip.text = location
		else:
			self.map = None
			self.map_name = ''
			self.map_name_var.set('No map selected')
			self.map_name_label.state(['readonly'])
			self.map_filename_var.set('')
			self.map_path_var.set('')
		# END ifelse
		
		self.current_map_path = path

		Actions.Action.enable_frame(self.actionFrame, path is not None)
		state = 'disable' if path is None else 'enable'
		for child in self.actionFrame.winfo_children():
			child.configure(state=state)
	# END setMap
	
	def open_map(self):
		filename = filedialog.askopenfilename()
		
		if filename != '':
			self.set_map(filename)
		# END if
	# END openMap
	
	def save_map(self, save_copy=False, save_backup=False):
		if self.current_map_path == '':
			messagebox.showinfo(message='No map selected', icon='warning')
			return

		self.map_name = self.map_name_var.get()
		currentMapPath = self.current_map_path

		# if save_backup:
		# 	save_copy = False
		#
		# 	folder = os.path.dirname(currentMapPath)
		# 	name, ext = os.path.splitext(os.path.basename(self.currentMapPath))
		# 	backup_index = 0
		# 	backup_path = ''
		#
		# 	while True:
		# 		backup_path = os.path.join(folder, name + '_bak_' + str(backup_index) + ext)
		# 		if not os.path.isfile(backup_path):
		# 			break
		# 		backup_index += 1
		#
		# 	if not os.path.isfile(currentMapPath):
		# 		messagebox.showinfo(message='File does not exist. Cannot backup', icon='error')
		# 		return
		#
		# 	# copyfile(currentMapPath, backup_path)
		# 	self.backup.name(self.map_name + '_bak_' + str(backup_index))
		# 	with open(backup_path, 'wb') as f:
		# 		f.write(dustmaker.write_map(self.backup))

		if not save_copy and not save_backup:
			if not messagebox.askyesno(
				message='This will overwrite the file.\nDo you want to continue?',
				icon='question',
				title='Save'):
				return

		try:
			if save_copy:
				self.map.name(self.map_name + '_modified')
				currentMapPath = os.path.join(os.path.dirname(currentMapPath), os.path.basename(self.current_map_path) + '_modified')
			else:
				self.map.name(self.map_name)

			with open(currentMapPath, 'wb') as f:
				f.write(dustmaker.write_map(self.map))
			messagebox.showinfo(message='Map saved')
			self.map.name(self.map_name)
			# self.backup = copy.deepcopy(self.map)
		except Exception as err:
			self.logger.exception(err)
			messagebox.showinfo(message='There was an error saving the map', icon='error')
	# END saveMap

	def runAction(self, event=None):
		try:
			button = event.widget
			if str(button['state']) == 'disable':
				return

			if button._confirm_action:
				if not messagebox.askyesno(
					message='Run this action?',
					icon='question',
					title=button.config('text')[-1]):
					return

			button._actionVar.run(self.map)
		except AttributeError:
			pass
	# END runAction
	
	def onWindowClose(self):
		self.config.write()
		self.root.destroy()
	# END onWindowClose
	
# END MainApplication

if __name__ == '__main__':
	root = tk.Tk()
	MainApplication(root)
	root.mainloop()
