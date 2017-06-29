import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .Action import Action


class TextTriggerAction(Action):
	def __init__(self, root):
		Action.__init__(self, root)

		self.listbox = None
		self.list_var = tk.StringVar()
		self.list_items = None
		self.text_area = None
		self.triggers = []
		self.edit_index = -1
		self.current_trigger = None

		self.font_frame = None
		self.font_box = None
		self.font_size_box = None
		self.font_var = tk.StringVar()
		self.font_size_var = tk.StringVar()

		self.import_separator = '\n-------------------------------------------------------- !! DO NOT EDIT THIS LINE !!\n'

		self.default_text = 'Select an item to edit its contents.'

		self.preview_pattern = re.compile(r'[\s\n\r]+')

		self.fonts = {
			'envy_bold': [20],
			'sans_bold': [20, 26, 36],
			'Caracteres': [26, 36, 40, 52, 64, 72, 92, 140],
			'ProximaNovaReg': [20, 26, 36, 42, 58, 72, 100],
			'ProximaNovaThin': [20, 26, 36, 42]
		}
	# END __init__

	def init(self):
		Action.init(self)
	# END init
	
	def create_gui(self):
		PADDING = 4
		HPADDING = PADDING / 2

		dlg = self.create_modal_window('Text Triggers')

		self.edit_index = -1
		list_items = self.list_items = []
		self.triggers = []
		for (id, (x, y, entity)) in list(self.map.entities.items()):
			if entity.type == 'text_trigger' or entity.type == 'z_text_prop_trigger':
				text = self.text(entity)
				list_items.append(self.text_preview(text))
				self.triggers.append(entity)

		top_frame = ttk.Frame(dlg, padding=PADDING)
		top_frame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		self.list_var.set(list_items)
		lbox = self.listbox =tk.Listbox(top_frame, listvariable=self.list_var, width=30, height=25)
		lbox.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(PADDING, 0), pady=PADDING)
		lbox.config(font='Helvetica 11')
		lbox.bind('<<ListboxSelect>>', self.on_select)

		lbox_scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=lbox.yview)
		lbox_scrollbar.grid(column=1, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, PADDING), pady=PADDING)
		lbox.configure(yscrollcommand=lbox_scrollbar.set)

		text_frame = ttk.Frame(top_frame, padding=PADDING)
		text_frame.grid(column=2, row=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		text_area = self.text_area = tk.Text(text_frame, width=60, height=25, wrap='none')
		text_area.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, PADDING), pady=PADDING)
		text_area.insert('1.0', self.default_text)

		text_area_vscrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
		text_area_vscrollbar.grid(column=1, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, PADDING), pady=PADDING)
		text_area.configure(yscrollcommand=text_area_vscrollbar.set)

		text_area_hscrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_area.xview)
		text_area_hscrollbar.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, PADDING), pady=PADDING)
		text_area.configure(xscrollcommand=text_area_hscrollbar.set)
		text_area.bind('<KeyRelease>', self.on_text_changed)

		font_frame = self.font_frame = ttk.Frame(text_frame, padding=PADDING)
		font_frame.grid(column=0, row=2, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		font_box = self.font_box = ttk.Combobox(font_frame, textvariable=self.font_var, state='readonly')
		font_box['values'] = ['envy_bold', 'sans_bold', 'Caracteres', 'ProximaNovaReg', 'ProximaNovaThin']
		font_box.grid(column=0, row=0,  sticky=tk.W)
		font_box.bind('<<ComboboxSelected>>', self.on_font_select)

		font_size_box = self.font_size_box = ttk.Combobox(font_frame, textvariable=self.font_size_var, state='readonly')
		font_size_box['values'] = []
		font_size_box.grid(column=1, row=0, sticky=tk.W, padx=(PADDING, 0))
		font_size_box.bind('<<ComboboxSelected>>', self.on_font_size_select)

		buttons_frame = ttk.Frame(top_frame, padding=PADDING)
		buttons_frame.grid(column=0, row=2, columnspan=3, sticky=(tk.N, tk.S, tk.W, tk.E), padx=0, pady=0)

		ttk.Button(buttons_frame, text='Import', command=self.import_text).grid(column=0, row=0, sticky=(tk.N), padx=(0, PADDING))
		ttk.Button(buttons_frame, text='Export', command=self.export_text).grid(column=1, row=0, sticky=(tk.N), padx=(0, PADDING))

		Action.enable_frame(self.font_frame, False)

		self.centre_window(dlg)
	# END createGui

	def run(self, map):
		Action.run(self, map)

		self.create_gui()
	# END run

	def import_text(self):
		text = self.app.root.clipboard_get().split(self.import_separator)

		if len(text) != len(self.triggers):
			messagebox.showinfo(message='Number of items in clipboard do not match number of text triggers', icon='warning')
			return

		index = 0
		for trigger in self.triggers:
			new_text = text[index]
			self.text(trigger, new_text)
			self.list_items[index] = self.text_preview(new_text)
			index += 1

		self.list_var.set(self.list_items)

		messagebox.showinfo(message='Text successfully imported', icon='info')

	def export_text(self):
		text = ''
		index = 0
		for trigger in self.triggers:
			if index > 0:
				text += self.import_separator
			text += self.text(trigger)
			index += 1

		self.app.root.clipboard_clear()
		self.app.root.clipboard_append(text)

		messagebox.showinfo(message='All text copied to clipboard', icon='info')

	def set_text(self, value):
		self.text_area.delete(1.0, 'end')
		self.text_area.insert('end', value)

	def get_text(self):
		return self.text_area.get(1.0, 'end-1c')

	def text_preview(self, text, preview_length=30):
		text = re.sub(self.preview_pattern, ' ', text).strip()
		return (text[:preview_length] + '..') if len(text) > preview_length else text

	def trigger_text(self, index, value=None):
		return self.text(self.triggers[index], value)

	@staticmethod
	def text(trigger, value=None):
		var_name = 'text' if trigger.type == 'z_text_prop_trigger' else 'text_string'
		# print(trigger.vars)

		if value is None:
			return trigger.vars[var_name].value
		else:
			trigger.vars[var_name].value = value
			return value

	def on_text_changed(self, event=None):
		if self.current_trigger is not None:
			new_text = self.get_text()
			self.text(self.current_trigger, new_text)

	def on_select(self, event = None):
		previous_trigger = self.current_trigger
		previous_index = self.edit_index

		selection = self.listbox.curselection()
		if len(selection) == 1:
			selection_index = self.edit_index = int(selection[0])
			self.listbox.see(selection_index)
			self.current_trigger = self.triggers[self.edit_index]
		else:
			selection_index = self.edit_index = -1
			self.current_trigger = None
			return

		if previous_trigger is not None and previous_trigger != self.current_trigger:
			self.list_items[previous_index] = self.text_preview(self.text(previous_trigger))
			self.list_var.set(self.list_items)

		self.set_text(self.default_text if selection_index == -1 else self.trigger_text(selection_index))

		trigger = self.current_trigger
		z_text = trigger.type == 'z_text_prop_trigger'
		Action.enable_frame(self.font_frame, z_text)

		if z_text:
			font_name = trigger.vars['font'].value
			self.font_box.set(font_name)
			self.font_size_box.set(trigger.vars['font_size'].value)
			self.font_size_box['values'] = self.fonts[font_name]
		else:
			self.font_box.set('')
			self.font_size_box.set('')

	def on_font_select(self, event=None):
		self.font_size_box['values'] = self.fonts[self.font_box.get()]

		if self.current_trigger is not None:
			self.current_trigger.vars['font'].value = self.font_box.get()

	def on_font_size_select(self, event=None):
		if self.current_trigger is not None:
			self.current_trigger.vars['font_size'].value = int(self.font_size_box.get())

# END Action
