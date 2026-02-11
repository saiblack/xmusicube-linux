import json
import os

class SettingsManager:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/xmusicube")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.defaults = {
            "theme": "system",
            "download_path": os.path.expanduser("~/Downloads"),
            "quality": 0, # High
            "format": 0,  # MP3
            "auto_best_audio": True
        }
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            return self.defaults.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return self.defaults.copy()

    def save_config(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key):
        return self.config.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
