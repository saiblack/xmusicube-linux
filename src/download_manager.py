import threading
import subprocess
import os
import re
from gi.repository import GLib

class DownloadManager:
    def __init__(self):
        self.download_path = os.path.expanduser("~/Downloads")
        self._ensure_directories()

    def set_download_path(self, path):
        self.download_path = path
        self._ensure_directories()

    def _ensure_directories(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    def start_download(self, url, quality, format_ext, callback_progress, callback_finished, auto_best=True):
        thread = threading.Thread(target=self._download_worker, 
                                  args=(url, quality, format_ext, callback_progress, callback_finished, auto_best))
        thread.daemon = True
        thread.start()

    def _download_worker(self, url, quality, format_ext, callback_progress, callback_finished, auto_best):
        try:
            if "spotify.com" in url:
                self._download_spotify(url, format_ext, callback_progress, callback_finished, auto_best)
            else:
                self._download_youtube(url, quality, format_ext, callback_progress, callback_finished, auto_best)
        except Exception as e:
            print(f"Download error: {e}")
            GLib.idle_add(callback_finished, "Error", str(e), None)

    def _download_youtube(self, url, quality, format_ext, callback_progress, callback_finished, auto_best):
        # Using yt-dlp subprocess to easily capture stdout for progress
        quality_val = "0" # Best
        if not auto_best:
            # Map quality string to kbps (e.g., "320 kbps (High)" -> "320")
            kbps_match = re.search(r'(\d+)', quality)
            if kbps_match:
                quality_val = kbps_match.group(1)

        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", format_ext.lower(),
            "--audio-quality", quality_val,
            "-o", f"{self.download_path}/%(title)s.%(ext)s",
            "--no-playlist",
            url
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        info = {"artist": "YouTube", "title": "Downloading...", "cover": None}
        
        # Regex to parse progress
        # [download]  23.5% of 10.00MiB at 120.00KiB/s ETA 00:30
        progress_re = re.compile(r'\[download\]\s+(\d+\.\d+)%')
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
                
            line = line.strip()
            # print(f"YT: {line}") # Debug
            
            # Try to catch title
            if "[ExtractAudio]" in line:
                 GLib.idle_add(callback_progress, 0.95)
                 
            match = progress_re.search(line)
            if match:
                percent = float(match.group(1))
                GLib.idle_add(callback_progress, percent / 100.0)

        process.wait()
        
        # After download, try to get the filename or title
        # For now, we return specific Done state
        GLib.idle_add(callback_finished, "YouTube Download", "Completed", None)

    def _download_spotify(self, url, format_ext, callback_progress, callback_finished, auto_best):
        # Using spotdl
        cmd = [
            "spotdl",
            url,
            "--output", self.download_path,
            "--format", format_ext.lower()
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            # print(f"SPOT: {line}") # Debug
            
            # spotdl output is not as easy to parse for %.
            # "Downloading: Artist - Title"
            if "Downloading" in line:
                 GLib.idle_add(callback_progress, 0.1)
            if "Converting" in line:
                 GLib.idle_add(callback_progress, 0.8)

        process.wait()
        GLib.idle_add(callback_finished, "Spotify Download", "Completed", None)
