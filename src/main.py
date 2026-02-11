#!/usr/bin/env python3
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
from .window import MainWindow

class XMusicubeApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.xmusicube',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()



def main():
    app = XMusicubeApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
