import os
import sublime
import sublime_plugin
import sys
import threading
import requests

# Ensure it works for python 2 and 3
try:
  from urllib.parse import urlencode
  from urllib.request import urlopen
except ImportError:
  from urllib import urlencode, urlopen

API_URL = "http://uploads.im/api"

class SendToUploadsImPromptCommand(sublime_plugin.WindowCommand):
  """Show a window to allow the user to setup the Paste options"""

  def run(self):
    self.window.show_input_panel("Paste Name:", "", self.on_done, None, None)

  def on_done(self, paste_name):
    if self.window.active_view():
      self.window.active_view().run_command("send_to_paste_bin", {"paste_name": paste_name} )

class SendToUploadsImCommand(sublime_plugin.TextCommand):

  def run(self, view, paste_name = None):
    self.settings = sublime.load_settings("SendToUploadsIm.sublime-settings")  

    # Use the filename as a default paste name
    if paste_name is None:
      paste_name = self.view.file_name()

      # Check if file exists on disk
      if paste_name is not None:
        # Only use the basename (we don't care about the path)
        paste_name =  os.path.basename(paste_name)
      else:
        paste_name = "Untitled"

    # Manage the user selected text
    for region in self.view.sel():
      syntax = syntaxes.get(self.view.settings().get('syntax').split('/')[-1], 'text')

      text = self.view.substr(region)

      if not text:
        sublime.status_message('Error sending to UploadsIm: Nothing selected')
      else:
        args = {
          'format': 'txt'
        }

        # Use a background thread to avoid freezing the main thread
        thread = UploadsImApiCall(args)
        thread.start()

class UploadsImApiCall(threading.Thread):
  """Manages the call to UploadsIm's API.
  Used to be able to do the call in another thread."""

  def __init__(self, call_args):
    self.call_args = call_args
    threading.Thread.__init__(self)

  def run(self):
    sublime.status_message('Sending to UploadsIm...')

    response = urlopen(url=API_URL, data=urlencode(self.call_args).encode('utf8')).read().decode('utf8')

    sublime.set_clipboard(response)
    sublime.status_message('Image URL copied to clipboard: ' + response)
