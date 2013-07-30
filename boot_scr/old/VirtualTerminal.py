#!/usr/bin/env python
#
#      VirtualTerminal.py
#
#      Copyright 2007 Edward Andrew Robinson <earobinson@gmail>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

# Imports
import os
import vte
import gtk
import time

class VirtualTerminal(vte.Terminal):
    def __init__(self, log_file = None, history_length = 5, prompt_watch = {}, prompt_auto_reply = True, icon = None):
        # Set up terminal
        vte.Terminal.__init__(self)

        self.history = []
        self.history_length = history_length
        self.icon = icon
        self.last_row_logged = 0
        self.log_file = log_file
        self.prompt_auto_reply = prompt_auto_reply
        self.prompt_watch = prompt_watch

        self.connect('eof', self.run_command_done_callback)
        self.connect('child-exited', self.run_command_done_callback)
        self.connect('cursor-moved', self.contents_changed_callback)

        if False:
            self.connect('char-size-changed', self.activate_action, 'char-size-changed')
            #self.connect('child-exited', self.activate_action, 'child-exited')
            self.connect('commit', self.activate_action, 'commit')
            self.connect('contents-changed', self.activate_action, 'contents-changed')
            #self.connect('cursor-moved', self.activate_action, 'cursor-moved')
            self.connect('decrease-font-size', self.activate_action, 'decrease-font-size')
            self.connect('deiconify-window', self.activate_action, 'deiconify-window')
            self.connect('emulation-changed', self.activate_action, 'emulation-changed')
            self.connect('encoding-changed', self.activate_action, 'encoding-changed')
            #self.connect('eof', self.activate_action, 'eof')
            self.connect('icon-title-changed', self.activate_action, 'icon-title-changed')
            self.connect('iconify-window', self.activate_action, 'iconify-window')
            self.connect('increase-font-size', self.activate_action, 'increase-font-size')
            self.connect('lower-window', self.activate_action, 'lower-window')
            self.connect('maximize-window', self.activate_action, 'maximize-window')
            self.connect('move-window', self.activate_action, 'move-window')
            self.connect('raise-window', self.activate_action, 'raise-window')
            self.connect('refresh-window', self.activate_action, 'refresh-window')
            self.connect('resize-window', self.activate_action, 'resize-window')
            self.connect('restore-window', self.activate_action, 'restore-window')
            self.connect('selection-changed', self.activate_action, 'selection-changed')
            self.connect('status-line-changed', self.activate_action, 'status-line-changed')
            self.connect('text-deleted', self.activate_action, 'text-deleted')
            self.connect('text-inserted', self.activate_action, 'text-inserted')
            self.connect('text-modified', self.activate_action, 'text-modified')
            self.connect('text-scrolled', self.activate_action, 'text-scrolled')
            self.connect('window-title-changed', self.activate_action, 'window-title-changed')

    def activate_action(self, action, string):
        print 'Action ' + action.get_name() + ' activated ' + str(string)

    def capture_text(self,text,text2,text3,text4):
        return True

    def contents_changed_callback(self, terminal):
        '''Gets the last line printed to the terminal, it will log
        this line using self.log() (if the logger is on, and it will
        also prompt this line using self.prompt() if the line needs
        prompting'''
        column,row = self.get_cursor_position()
        if self.last_row_logged != row:
            off = row-self.last_row_logged
            text = self.get_text_range(row-off,0,row-1,-1,self.capture_text)
            self.last_row_logged=row
            text = text.strip()

            # Log
            self.log(text)

            # Prompter
            self.prompter()

    def get_last_line(self):
        terminal_text = self.get_text(self.capture_text)
        terminal_text = terminal_text.split('\\\\n')
        ii = len(terminal_text) - 1
        while terminal_text[ii] == '':
            ii = ii - 1
        terminal_text = terminal_text[ii]

        return terminal_text

    def log(self, text):
        '''if self.log_file is not None the the line will be logged to
        self.log_file. This function also stors the info in self.histoy
        if self.history_lenght > 0'''
        if self.log_file != None:
            date_string = time.strftime('[%d %b %Y %H:%M:%S] ', time.localtime())
            file = open(self.log_file, 'a')
            file.write(date_string + text + '\\\\n')
            file.close

        # Append to internal history
        if self.history_length != 0:
            if len(self.history) >= self.history_length:
                self.history.pop(0)
            self.history.append(text)

    def prompter(self):
        last_line = self.get_last_line()
        if last_line in self.prompt_watch:
            if self.prompt_auto_reply == False:
                message = ''
                for ii in self.prompt_watch[last_line]:
                    message = message + self.history[self.history_length - 1 - ii]
                if self.yes_no_question(message):
                    self.feed_child('Yes\\\\n')
                    # TODO not sure why this is needed twice
                    self.feed_child('Yes\\\\n')
                else:
                    self.feed_child('No\\\\n')
            else:
                self.feed_child('Yes\\\\n')

    def run_command(self, command_string):
        '''run_command runs the command_string in the terminal. This
        function will only return when self.thred_running is set to
        True, this is done by run_command_done_callback'''
        self.thread_running = True
        spaces = ''
        for ii in range(80 - len(command_string) - 2):
            spaces = spaces + ' '
        self.feed('$ ' + str(command_string) + spaces)
        self.log('$ ' + str(command_string) + spaces)

        command = command_string.split(' ')
        pid =  self.fork_command(command=command[0], argv=command, directory=os.getcwd())

        while self.thread_running:
            #time.sleep(.01)
            gtk.main_iteration()

    def run_command_done_callback(self, terminal):
        '''When called this function sets the thread as done allowing
        the run_command function to exit'''
        #print 'child done'
        self.thread_running = False

    def yes_no_question(self, message):
        message = message.replace('\\\\n\\\\n', '[NEWLINE][NEWLINE]').replace('\\\\n', '').replace('[NEWLINE]', '\\\\n')

        if message.find('?') == -1:
            message = message + '\\\\n\\\\nDo you want to continue?'

        type=gtk.MESSAGE_QUESTION
        if message.lower().find('warning') != -1:
            type=gtk.MESSAGE_WARNING

        dialog = gtk.MessageDialog(parent=None, flags=0, type=type, buttons=gtk.BUTTONS_YES_NO, message_format=message)
        dialog.set_icon(self.icon)
        dialog.show_all()
        responce = dialog.run()
        dialog.destroy()

        # Responce == yes
        return responce == -8

