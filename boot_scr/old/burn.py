#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import sys, os, signal, re
import pygtk
pygtk.require('2.0')
import gtk, gobject
import ConfigParser, tempfile
from subprocess import *

#
# TODO:
#   - needs error checking everywhere
#

# CONFIG
TEMP_DIR   = "/var/tmp"
CDRW_DEV   = "/dev/cdrw"
DUMMY_MODE = False

# IF you want to manually set the speed of your burner, use this
#os.environ["CDR_SPEED"]="6"

class Burn:
	# burn modes
	MODE_DATA  = 1
	MODE_AUDIO = 2
	MODE_ISO   = 3
	MODE_ERASE = 4
	# our working directory
	tempdir = None
	# sub processes
	p1, p2 = None, None
	int_watch, ext_watch = None, None
	# function to use to report errors
	errfunc = None

	def __init__(self, mode, files, callback, errfunc):
		self.mode     = mode
		self.files    = files
		self.callback = callback
		self.errfunc  = errfunc

	def start(self):
		self.tempdir = tempfile.mkdtemp(dir=TEMP_DIR, prefix="pyburn-")
		if self.mode == Burn.MODE_DATA:
			self.prepare_data()
		if self.mode == Burn.MODE_AUDIO:
			self.filenum = 1
			self.prepare_audio()
		if self.mode == Burn.MODE_ISO:
			self.burn_iso()
		if self.mode == Burn.MODE_ERASE:
			self.erase_disc()

	def cancel(self):
		if self.ext_watch:
			gobject.source_remove(self.ext_watch)
			self.ext_watch = None
		if self.int_watch:
			gobject.source_remove(self.int_watch)
			self.int_watch = None
		if self.p1 and self.p1.returncode == None:
			os.kill(self.p1.pid, signal.SIGTERM)
			self.p1.wait()
		if self.p2 and self.p2.returncode == None:
			os.kill(self.p2.pid, signal.SIGTERM)
			self.p2.wait()
		self.cleanup()

	def cleanup(self):
		if self.tempdir:
			# remove all our temp files
			for root, dirs, files in os.walk(self.tempdir, topdown=False):
				for name in files:
					os.remove(os.path.join(root, name))
				for name in dirs:
					# might be a symlink -- if so, treat it like a file, not a dir
					if os.path.islink(os.path.join(root, name)):
						os.remove(os.path.join(root, name))
					else:
						os.rmdir(os.path.join(root, name))
			os.rmdir(self.tempdir)

	def get_output(self):
		if self.p2:
			return self.p2.stdout.read(1)
		elif self.p1:
			return self.p1.stdout.read(1)
		return None

	def prepare_data(self):
		for src in self.files:
			dst = self.tempdir + "/" + src.split("/")[-1]
			os.symlink(src, dst)
		self.burn_data()

	def burn_data(self):
		# Pipe mkisofs into cdrecord
		cmd1 = ["mkisofs", "-J", "-r", "-follow-links", self.tempdir]
		dev = "dev=%s" % (CDRW_DEV)
		if DUMMY_MODE:
			cmd2 = ["cdrecord", "-v", "-eject", "-dummy", "driveropts=burnfree", dev, "-data", "-"]
		else:
			cmd2 = ["cdrecord", "-v", "-eject", "driveropts=burnfree", dev, "-data", "-"]
		print "cmd1: %s" % (cmd1)
		print "cmd2: %s" % (cmd2)
		self.p1 = Popen(cmd1, stdout=PIPE)
		self.p2 = Popen(cmd2, stdin=self.p1.stdout, stdout=PIPE, stderr=STDOUT)
		self.ext_watch = gobject.io_add_watch(self.p2.stdout, gobject.IO_IN | gobject.IO_HUP, self.callback)

	def burn_iso(self):
		# we should only have one file in the list
		isofn = self.files[0]
		dev = "dev=%s" % (CDRW_DEV)
		if DUMMY_MODE:
			cmd = ["cdrecord", "-v", "-eject", "-dummy", "driveropts=burnfree", dev, "-data", isofn]
		else:
			cmd = ["cdrecord", "-v", "-eject", "driveropts=burnfree", dev, "-data", isofn]
		print "cmd: %s" % (cmd)
		self.p1 = Popen(cmd, stdout=PIPE, stderr=STDOUT)
		self.ext_watch = gobject.io_add_watch(self.p1.stdout, gobject.IO_IN | gobject.IO_HUP, self.callback)

	def erase_disc(self):
		dev = "dev=%s" % (CDRW_DEV)
		if DUMMY_MODE:
			cmd = ["cdrecord", "-v", "-eject", "-dummy", "driveropts=burnfree", dev, "blank=fast"]
		else:
			cmd = ["cdrecord", "-v", "-eject", "driveropts=burnfree", dev, "blank=fast"]
		print "cmd: %s" % (cmd)
		self.p1 = Popen(cmd, stdout=PIPE, stderr=STDOUT)
		self.ext_watch = gobject.io_add_watch(self.p1.stdout, gobject.IO_IN | gobject.IO_HUP, self.callback)

	def prepare_audio(self):
		fn = self.files[self.filenum-1]
		wavfn = "%s/%d.wav" % (self.tempdir, self.filenum)
		if fn.endswith(".wav") or fn.endswith(".WAV"):
			# a symlink should suffice
			cmd = ["ln", "-s", fn, wavfn]
		elif fn.endswith(".mp3") or fn.endswith(".MP3"):
			cmd = ["mpg123", "-w", wavfn, fn]
		elif fn.endswith(".ogg") or fn.endswith(".OGG"):
			cmd = ["oggdec", "-o", wavfn, fn]
		else:
			self.errfunc("Unrecognized file extension: %s" % (fn))
			return
		print "cmd: %s" % (cmd)
		self.p1 = Popen(cmd, stdout=PIPE, stderr=STDOUT)
		self.ext_watch = gobject.io_add_watch(self.p1.stdout, gobject.IO_IN, self.callback)
		# additional callback, so we know when the decode process is finished
		self.int_watch = gobject.io_add_watch(self.p1.stdout, gobject.IO_HUP, self.pcallback)

	def burn_audio(self):
		dev = "dev=%s" % (CDRW_DEV)
		if DUMMY_MODE:
			cmd = ["cdrecord", "-v", "-eject", "-dummy", "driveropts=burnfree", dev, "-pad", "-audio"]
		else:
			cmd = ["cdrecord", "-v", "-eject", "driveropts=burnfree", dev, "-pad", "-audio"]
		for i in range(1,len(self.files)+1):
			fn = "%s/%d.wav" % (self.tempdir, i)
			cmd.append(fn)
		print "cmd: %s" % (cmd)
		self.p1 = Popen(cmd, stdout=PIPE, stderr=STDOUT)
		gobject.io_add_watch(self.p1.stdout, gobject.IO_IN | gobject.IO_HUP, self.callback)

	def pcallback(self, source, condition):
		# remove the other io watch callback
		gobject.source_remove(self.ext_watch)
		self.ext_watch = None
		# if there's a zombie kicking around, wait 'em out
		if self.p1:
			self.p1.wait()
		if self.filenum == len(self.files):
			# finished decoding, start the cdrecord process
			self.burn_audio()
		else:
			# decode the next file
			self.filenum = self.filenum + 1
			self.prepare_audio()
		return False


class PyBurn:
	def __init__(self):
		# Initialization
		self.burndlg = None
		# Main window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("destroy", gtk.main_quit, "WM destroy")
		self.window.set_title("PyBurn 0.1")
		
		#
		# Menu bar
		#
		menubar = gtk.MenuBar()
		# File Menu
		file_menu = gtk.Menu()
		file = gtk.MenuItem("_File")
		file.set_submenu(file_menu)
		menubar.append(file)
		# Help Menu
		help_menu = gtk.Menu()
		help = gtk.MenuItem("_Help")
		help.set_submenu(help_menu)
		menubar.append(help)

		menuit = gtk.MenuItem("_About...")
		menuit.connect_object("activate", self.menu_callback, "about")
		help_menu.append(menuit)
		menuit = gtk.MenuItem("_Load Playlist...")
		menuit.connect_object("activate", self.menu_callback, "loadplaylist")
		file_menu.append(menuit)
		menuit = gtk.MenuItem("_Blank CD-RW...")
		menuit.connect_object("activate", self.menu_callback, "erasedisc")
		file_menu.append(menuit)
		menuit = gtk.MenuItem("Burn _ISO Image...")
		menuit.connect_object("activate", self.menu_callback, "burniso")
		file_menu.append(menuit)
		menuit = gtk.MenuItem("_Quit")
		menuit.connect_object("activate", gtk.main_quit, "WM destroy")
		file_menu.append(menuit)

		#
		# Radio Buttons
		#
		label1 = gtk.Label("Burn Mode:")
		self.mode_audio = gtk.RadioButton(None, "Audio", False)
		self.mode_data  = gtk.RadioButton(self.mode_audio, "Data", False)

		#
		# File list
		#
		self.flist = gtk.ListStore(gobject.TYPE_STRING)
		self.ftree = gtk.TreeView(self.flist)
		self.ftree.set_reorderable(True)
		fcol = gtk.TreeViewColumn('Files to Burn:')
		self.ftree.append_column(fcol)
		cell = gtk.CellRendererText()
		fcol.pack_start(cell, True)
		fcol.add_attribute(cell, 'text', 0)

		# 
		# Buttons
		#
		# Helper function to add buttons
		def new_button(icon, label, callbackstr):
			btn = gtk.Button(label=None)
			hbox = gtk.HBox(False, 0)
			btn.add(hbox)
			s = gtk.Style()
			icon = s.lookup_icon_set(icon).render_icon(
					s, gtk.TEXT_DIR_LTR, gtk.STATE_NORMAL, gtk.ICON_SIZE_BUTTON,
					hbox, None)
			img = gtk.Image()
			img.set_from_pixbuf(icon)
			hbox.add(img)
			label = gtk.Label(label)
			label.set_use_underline(True)
			hbox.add(label)
			btn.connect("clicked", self.button_callback, callbackstr)
			return btn
		# The Add/Add/Remove buttons
		btn_add = new_button(gtk.STOCK_FILE, "Add _Files", "addfiles")
		btn_adddir = new_button(gtk.STOCK_DIRECTORY, "Add _Directory", "adddirs")
		btn_del = new_button(gtk.STOCK_REMOVE, "_Remove", "removefiles")
		# The "Start Burn" button
		btn_burn = new_button(gtk.STOCK_MEDIA_RECORD, "_Start Burn", "burncd")

		# Assemble the main window and all its components
		vbox = gtk.VBox(False, 0)
		vbox.set_border_width(1)
		self.window.add(vbox)
		
		hbox = gtk.HBox(False, 0)
		hbox.set_border_width(1)

		scrollwin = gtk.ScrolledWindow()
		scrollwin.add(self.ftree)

		btnbox = gtk.HBox(False, 0)
		btnbox_l = gtk.HButtonBox()
		btnbox_l.set_spacing(5)
		btnbox_l.pack_start(btn_add, False, True, 0)
		btnbox_l.pack_start(btn_adddir, False, True, 0)
		btnbox_l.pack_start(btn_del, False, True, 0)
		btnbox_r = gtk.HButtonBox()
		btnbox_r.set_spacing(5)
		btnbox_r.pack_start(btn_burn, False, True, 0)
		btnbox_r.set_layout(gtk.BUTTONBOX_END)

		# Main VBox
		vbox.pack_start(menubar, False, True, 0)
		vbox.pack_start(hbox, False, True, 0)
		vbox.pack_start(scrollwin, True, True, 0)
		vbox.pack_start(btnbox, False, True, 0)
		# Radio Button HBox
		hbox.pack_end(self.mode_data, False, True, 0)
		hbox.pack_end(self.mode_audio, False, True, 0)
		hbox.pack_end(label1, False, True, 0)
		# Button HBox
		btnbox.pack_start(btnbox_l, False, True, 0)
		btnbox.pack_start(btnbox_r, True, True, 0)

		# Drag n' Drop
		self.ftree.enable_model_drag_dest([
				('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
				('text/plain', 0, 1), ('TEXT', 0, 2), ('STRING', 0, 3)],
				gtk.gdk.ACTION_DEFAULT)
		self.ftree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
				[('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0)], gtk.gdk.ACTION_MOVE)
		self.ftree.connect("drag_data_get", self.dnd_get_data)
		self.ftree.connect("drag_data_received", self.dnd_received_data)

		# and.... show it!
		self.window.set_default_size(640, 350)
		self.window.show_all()

	def show_burn_dialog(self):
		self.burndlg = gtk.Dialog("Burn Progress", self.window, gtk.DIALOG_MODAL)
		self.burnbtn1 = self.burndlg.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
		self.burnbtn1.connect("clicked", self.button_callback, "cancelburn")
		self.burnbtn2 = self.burndlg.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		self.burnbtn2.connect("clicked", self.button_callback, "closeburn")

		self.buffer = gtk.TextBuffer()
		scrollwin = gtk.ScrolledWindow()
		self.outputw = gtk.TextView(self.buffer)
		self.outputw.set_editable(False)
		self.outputw.set_cursor_visible(False)
		self.outputw.set_wrap_mode(gtk.WRAP_NONE)
			
		# set a mark for auto-scrolling
		self.buffer.create_mark("tail", self.buffer.get_end_iter(), False)

		scrollwin.add(self.outputw)
		self.burndlg.vbox.pack_start(scrollwin, True, True, 0)
		scrollwin.show()
		self.outputw.show()
		self.burndlg.set_default_size(600, 300)
		self.burndlg.vbox.show_all()
		self.burnbtn1.show()
		self.burnbtn2.hide()
		self.burndlg.show()

	def button_callback(self, widget, data):
		if data == "adddirs":
			chooser = gtk.FileChooserDialog(title="Select a Directory",action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
					buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			chooser.set_select_multiple(True)

			response = chooser.run()
			if response == gtk.RESPONSE_OK:
				for fn in chooser.get_filenames():
					self.flist.append((fn,))
			chooser.destroy()

		if data == "addfiles":
			chooser = gtk.FileChooserDialog(title="Select a File",action=gtk.FILE_CHOOSER_ACTION_OPEN,
					buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
			chooser.set_select_multiple(True)

			filter = gtk.FileFilter()
			filter.set_name("All files")
			filter.add_pattern("*")
			chooser.add_filter(filter)

			filter = gtk.FileFilter()
			filter.set_name("Music files (*.mp3,*.ogg,*.wav)")
			filter.add_pattern("*.mp3")
			filter.add_pattern("*.ogg")
			filter.add_pattern("*.wav")
			chooser.add_filter(filter)

			response = chooser.run()
			if response == gtk.RESPONSE_OK:
				for fn in chooser.get_filenames():
					self.flist.append((fn,))
			chooser.destroy()

		if data == "removefiles":
			sel = self.ftree.get_selection()
			model, iter = sel.get_selected()
			if iter:
				model.remove(iter)

		if data == "burncd":
			filelist = [i[0].strip() for i in self.ftree.get_model()]
			if len(filelist) == 0:
				self.error("Add some files first!")
				return
			if self.mode_audio.get_active():
				mode = Burn.MODE_AUDIO
			else:
				mode = Burn.MODE_DATA
			self.burn = Burn(mode, filelist, self.burn_callback, self.error)
			# Start the burn process
			self.show_burn_dialog()
			self.burn.start()

		if data == "cancelburn":
			self.burn.cancel()
			self.burndlg.destroy()

		if data == "closeburn":
			self.burndlg.destroy()

	def burn_callback(self, source, condition):
		if condition == gobject.IO_IN:
			self.buffer.insert_at_cursor(self.burn.get_output())
			# scroll down to the last line in the text window
			self.buffer.move_mark_by_name("tail", self.buffer.get_end_iter())
			self.outputw.scroll_mark_onscreen(self.buffer.get_mark("tail"))
			return True
		if condition == gobject.IO_HUP:
			self.burn.cancel()
			self.burnbtn1.hide()
			self.burnbtn2.show()
			self.burndlg.set_title("Burn Finished")
			self.buffer.insert_at_cursor("\nBURN FINISHED.\n")
			# scroll down to the last line in the text window
			self.buffer.move_mark_by_name("tail", self.buffer.get_end_iter())
			self.outputw.scroll_mark_onscreen(self.buffer.get_mark("tail"))
			return False

	def dnd_received_data(self, treeview, context, x, y, selection,
		                          info, etime):
		model = treeview.get_model()
		data = selection.data.strip(chr(0)).strip("\r\n")
		for fn in data.split("\r\n"):
			if fn.startswith("file:"):
				# trim off the "file:" prefix
				fn = fn[5:]
			# trim out consecutive slashes
			fn = re.sub("//+", "/", fn)
			drop_info = treeview.get_dest_row_at_pos(x, y)
			if drop_info:
				path, position = drop_info
				iter = model.get_iter(path)
				if (position == gtk.TREE_VIEW_DROP_BEFORE
						or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
					model.insert_before(iter, [fn])
				else:
					model.insert_after(iter, [fn])
			else:
				model.append([fn])
				if context.action == gtk.gdk.ACTION_MOVE:
					context.finish(True, True, etime)

	def dnd_get_data(self, treeview, context, selection, target_id, etime):
		treeselection = treeview.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, 0)
		selection.set(selection.target, 8, data)
		model.remove(iter)
	
	def menu_callback(self, data):
		if data == "about":
			dlg = gtk.AboutDialog()
			dlg.set_name("PyBurn")
			dlg.set_comments("A frontend application for burning CDs with the cdrecord utility")
			dlg.set_version("0.1")
			dlg.set_copyright(u"Copyright ©2005 Judd Vinet")
			dlg.set_license("""Copyright (C)2005 Judd Vinet <jvinet@zeroflux.org>

This is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2, or (at your option)
any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with program; see the file COPYING. If not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
MA 02111-1307, USA.""")
			dlg.run()
			dlg.destroy()

		if data == "erasedisc":
			msgdlg = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
					gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, "Are you sure?")
			response = msgdlg.run()
			msgdlg.destroy()
			if response != gtk.RESPONSE_YES:
				return
			
			self.burn = Burn(Burn.MODE_ERASE, [], self.burn_callback, self.error)
			self.show_burn_dialog()
			self.burn.start()

		if data == "burniso":
			chooser = gtk.FileChooserDialog(title="Select an ISO Image",action=gtk.FILE_CHOOSER_ACTION_OPEN,
					buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

			filter = gtk.FileFilter()
			filter.set_name("ISO images (*.iso)")
			filter.add_pattern("*.iso")
			chooser.add_filter(filter)
			filter = gtk.FileFilter()
			filter.set_name("All files")
			filter.add_pattern("*")
			chooser.add_filter(filter)

			response = chooser.run()
			if response != gtk.RESPONSE_OK:
				chooser.destroy()
				return
			isofn = chooser.get_filename()
			chooser.destroy()

			self.burn = Burn(Burn.MODE_ISO, [isofn], self.burn_callback, self.error)
			# Start the burn process
			self.show_burn_dialog()
			self.burn.start()

		if data == "loadplaylist":
			chooser = gtk.FileChooserDialog(title="Select a Playlist File",action=gtk.FILE_CHOOSER_ACTION_OPEN,
					buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

			filter = gtk.FileFilter()
			filter.set_name("pls files (*.pls)")
			filter.add_pattern("*.pls")
			chooser.add_filter(filter)
			filter = gtk.FileFilter()
			filter.set_name("plain-text file list (*.lst)")
			filter.add_pattern("*.lst")
			chooser.add_filter(filter)
			filter = gtk.FileFilter()
			filter.set_name("All files")
			filter.add_pattern("*")
			chooser.add_filter(filter)

			response = chooser.run()
			if response != gtk.RESPONSE_OK:
				chooser.destroy()
				return
			plsfn = chooser.get_filename()
			chooser.destroy()

			# try to figure out what type of list we have...
			# default to a plain-text list of files, but use the INI parser if
			# the file starts with "[playlist]"
			pls = open(plsfn, "r")
			if pls.readline().startswith("[playlist]"):
				# INI format
				pls.close()
				pls = ConfigParser.ConfigParser()
				try:
					pls.read([plsfn])
				except:
					self.error("Error parsing %s" % (plsfn))
					return
				num = pls.get("playlist", "NumberOfEntries")
				for i in range(0,int(num)):
					fn = pls.get("playlist", "File%d" % (i+1))
					self.flist.append((fn,))
			else:
				# TXT format
				pls.seek(0)
				for fn in pls:
					self.flist.append((fn.strip(),))

	def error(self, msg):
		dlg = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
				gtk.BUTTONS_OK, msg)
		dlg.run()
		dlg.destroy()
		if self.burndlg:
			self.burn.cancel()
			self.burndlg.destroy()

	def main(self):
		gtk.main()


if __name__ == "__main__":
	pyb = PyBurn()
	pyb.main()


