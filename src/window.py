import gi
import os
from gi.repository import Gtk, Adw, Gdk, Gio, GLib
from .row import DownloadRow
from .download_manager import DownloadManager
from .settings import SettingsManager

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings_manager = SettingsManager()
        self.download_manager = DownloadManager()
        
        # Load initial settings
        self.current_download_path = self.settings_manager.get("download_path")
        self.download_manager.set_download_path(self.current_download_path)
        
        self.set_default_size(900, 600)
        self.set_title("xmusicube")
        
        # CSS Provider
        self.css_provider = Gtk.CssProvider()
        css_path = 'src/style.css'
        if not os.path.exists(css_path):
            css_path = '/app/share/xmusicube/style.css'
        
        if os.path.exists(css_path):
            self.css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), 
                                                      self.css_provider, 
                                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self.add_css_class("glass-window")

        # Main Layout Box (Outer)
        self.outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.outer_box)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        self.outer_box.append(self.header_bar)

        # Main Overlay/Background
        self.main_overlay = Gtk.Overlay()
        self.main_overlay.set_vexpand(True)
        self.outer_box.append(self.main_overlay)

        # Main Layout Box (Center Card)
        self.card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.card_box.add_css_class("card")
        self.card_box.set_valign(Gtk.Align.CENTER)
        self.card_box.set_halign(Gtk.Align.CENTER)
        # self.card_box.set_size_request(700, 500) # Optional fixed size

        self.main_overlay.set_child(self.card_box)



        self.theme_btn = Gtk.Button(icon_name="weather-clear-night-symbolic")
        self.theme_btn.add_css_class("flat")
        self.theme_btn.connect("clicked", self.toggle_theme)
        
        self.header_bar.pack_end(self.theme_btn)
        
        # Apply initial theme
        self.apply_theme(self.settings_manager.get("theme"))

        # Input Section
        self.input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("Paste song link here...")
        self.url_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "audio-x-generic-symbolic")
        self.url_entry.add_css_class("url-entry")
        self.url_entry.set_hexpand(True)

        self.download_btn = Gtk.Button(icon_name="folder-download-symbolic")
        self.download_btn.add_css_class("download-btn")
        self.download_btn.connect("clicked", self.on_download_clicked)

        self.input_box.append(self.url_entry)
        self.input_box.append(self.download_btn)
        self.card_box.append(self.input_box)

        # Auto Best Audio
        self.auto_best_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        self.auto_best_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.auto_best_label = Gtk.Label(label="Auto best audio")
        self.auto_best_label.set_halign(Gtk.Align.START)
        
        self.auto_best_switch = Gtk.Switch()
        self.auto_best_switch.set_active(self.settings_manager.get("auto_best_audio"))
        self.auto_best_switch.set_valign(Gtk.Align.CENTER)
        self.auto_best_switch.connect("state-set", self.on_auto_best_toggled)
        
        self.auto_best_row.append(self.auto_best_label)
        self.auto_best_row.append(self.auto_best_switch)
        
        self.auto_best_desc = Gtk.Label(label="The application will automatically adjust to download the best format with the best possible download quality.")
        self.auto_best_desc.add_css_class("small-desc")
        self.auto_best_desc.set_halign(Gtk.Align.START)
        self.auto_best_desc.set_wrap(True)
        self.auto_best_desc.set_max_width_chars(60)
        
        self.auto_best_box.append(self.auto_best_row)
        self.auto_best_box.append(self.auto_best_desc)
        
        self.card_box.append(self.auto_best_box)

        # Options Section
        self.options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.options_box.set_halign(Gtk.Align.START)

        # Quality
        self.options_box.append(Gtk.Label(label="Audio Quality"))
        self.quality_dropdown = Gtk.DropDown.new_from_strings(["320 kbps (High)", "256 kbps (Medium)", "128 kbps (Low)"])
        self.quality_dropdown.set_selected(self.settings_manager.get("quality"))
        self.quality_dropdown.add_css_class("pill-dropdown")
        self.quality_dropdown.connect("notify::selected", self.on_quality_changed)
        self.options_box.append(self.quality_dropdown)

        # Format
        self.options_box.append(Gtk.Label(label="Format"))
        self.format_dropdown = Gtk.DropDown.new_from_strings(["MP3", "M4A", "FLAC", "WAV"])
        self.format_dropdown.set_selected(self.settings_manager.get("format"))
        self.format_dropdown.add_css_class("pill-dropdown")
        self.format_dropdown.connect("notify::selected", self.on_format_changed)
        self.options_box.append(self.format_dropdown)

        self.card_box.append(self.options_box)
        
        # Initial sensitivity set
        self.update_options_sensitivity()

        # Downloads List Section
        self.downloads_scroll = Gtk.ScrolledWindow()
        self.downloads_scroll.set_vexpand(True)
        self.downloads_scroll.set_min_content_height(200)
        self.downloads_list = Gtk.ListBox()
        self.downloads_list.add_css_class("download-list")
        self.downloads_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.downloads_scroll.set_child(self.downloads_list)
        
        self.card_box.append(self.downloads_scroll)

        # Footer Section (Download Location)
        self.footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.footer_box.set_halign(Gtk.Align.END)
        
        self.footer_box.append(Gtk.Label(label="Download Location"))
        
        self.location_btn = Gtk.Button(label=os.path.basename(self.current_download_path) or "Browse...")
        self.location_btn.add_css_class("flat")
        self.location_btn.set_icon_name("folder-open-symbolic")
        self.location_btn.connect("clicked", self.on_location_clicked)
        self.footer_box.append(self.location_btn)

        self.card_box.append(self.footer_box)

    def on_location_clicked(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Download Folder")
        dialog.select_folder(self, None, self.on_folder_selected)

    def on_folder_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                self.current_download_path = path
                self.settings_manager.set("download_path", path)
                self.download_manager.set_download_path(path)
                self.location_btn.set_label(os.path.basename(path))
        except Exception as e:
            print(f"Error selecting folder: {e}")

    def on_auto_best_toggled(self, switch, state):
        self.settings_manager.set("auto_best_audio", state)
        self.update_options_sensitivity()
        return False

    def on_quality_changed(self, dropdown, pspec):
        self.settings_manager.set("quality", dropdown.get_selected())

    def on_format_changed(self, dropdown, pspec):
        self.settings_manager.set("format", dropdown.get_selected())

    def update_options_sensitivity(self):
        is_auto = self.auto_best_switch.get_active()
        self.options_box.set_sensitive(not is_auto)

    def on_download_clicked(self, btn):
        url = self.url_entry.get_text()
        if not url:
            return
        
        auto_best = self.auto_best_switch.get_active()
        quality_str = self.quality_dropdown.get_selected_item().get_string()
        format_ext = self.format_dropdown.get_selected_item().get_string()
            
        # Create a row immediately
        row = DownloadRow(f"Downloading ({format_ext})...", url)
        self.downloads_list.append(row)
        
        self.download_manager.start_download(
            url, 
            quality_str, 
            format_ext, 
            row.set_progress, 
            lambda artist, title, cover: self.on_download_finished(row, artist, title, cover),
            auto_best=auto_best
        )
        
        self.url_entry.set_text("")

    def on_download_finished(self, row, artist, title, cover):
        row.title_label.set_label(title)
        row.artist_label.set_label(artist)
        # Set cover if available
        row.set_progress(1.0)


    def toggle_theme(self, button):
        manager = Adw.StyleManager.get_default()
        if manager.get_dark():
            self.apply_theme("light")
        else:
            self.apply_theme("dark")

    def apply_theme(self, theme):
        manager = Adw.StyleManager.get_default()
        if theme == "dark":
            manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            self.add_css_class("dark")
            self.settings_manager.set("theme", "dark")
        else:
            manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            self.remove_css_class("dark")
            self.settings_manager.set("theme", "light")


    def add_dummy_row(self, title, progress, icon_name):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_box.set_margin_top(5)
        row_box.set_margin_bottom(5)
        
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(40)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        lbl = Gtk.Label(label=title)
        lbl.set_halign(Gtk.Align.START)
        
        prog = Gtk.ProgressBar()
        if progress == "100%":
            prog.set_fraction(1.0)
        else:
            prog.set_fraction(0.5)
            
        vbox.append(lbl)
        vbox.append(prog)
        
        row_box.append(icon)
        row_box.append(vbox)
        
        self.downloads_list.append(row_box)

