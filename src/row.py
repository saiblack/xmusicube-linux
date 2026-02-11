import gi
from gi.repository import Gtk, Gdk, Pango

class DownloadRow(Gtk.ListBoxRow):
    def __init__(self, title, artist, cover_path=None):
        super().__init__()
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.box.set_margin_top(10)
        self.box.set_margin_bottom(10)
        self.box.set_margin_start(10)
        self.box.set_margin_end(10)
        
        # Cover Art
        self.cover_image = Gtk.Image()
        if cover_path:
            self.cover_image.set_from_file(cover_path)
        else:
            self.cover_image.set_from_icon_name("audio-x-generic-symbolic")
        self.cover_image.set_pixel_size(50)
        self.cover_image.add_css_class("cover-art")
        
        self.box.append(self.cover_image)
        
        # Text Info
        self.info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.info_box.set_valign(Gtk.Align.CENTER)
        
        self.title_label = Gtk.Label(label=title)
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.add_css_class("song-title")
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        self.artist_label = Gtk.Label(label=artist)
        self.artist_label.set_halign(Gtk.Align.START)
        self.artist_label.add_css_class("song-artist")
        self.artist_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        self.info_box.append(self.title_label)
        self.info_box.append(self.artist_label)
        
        self.box.append(self.info_box)
        
        # Spacer
        space = Gtk.Label()
        space.set_hexpand(True)
        self.box.append(space)
        
        # Status/Progress
        self.status_stack = Gtk.Stack()
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_valign(Gtk.Align.CENTER)
        self.progress_bar.set_size_request(100, -1)
        
        self.status_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        self.status_icon.add_css_class("success")
        
        self.status_stack.add_named(self.progress_bar, "progress")
        self.status_stack.add_named(self.status_icon, "done")
        
        self.box.append(self.status_stack)
        
        self.set_child(self.box)

    def set_progress(self, fraction):
        self.progress_bar.set_fraction(fraction)
        if fraction >= 1.0:
            self.status_stack.set_visible_child_name("done")
        else:
            self.status_stack.set_visible_child_name("progress")
