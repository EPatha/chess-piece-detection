import json
import os

class ConfigManager:
    DEFAULT_CONFIG = {
        "features": {
            "clock_mode": True,
            "sync_edit": True,
            "game_mode": True,  # Enables Engine/Analysis
            "yolo_enabled": False
        },
        "camera": {
            "default_index": 0
        }
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        print(f"ConfigManager: Loading config from {os.path.abspath(self.config_file)}")
        if not os.path.exists(self.config_file):
            print("ConfigManager: Config file not found, creating default.")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                print(f"ConfigManager: Loaded config: {config}")
                return config
        except Exception as e:
            print(f"ConfigManager: Error loading config: {e}")
            return self.DEFAULT_CONFIG

    def save_config(self, config=None):
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        # Support nested keys like "features.clock_mode"
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    def set(self, key, value):
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = value
        self.save_config()
