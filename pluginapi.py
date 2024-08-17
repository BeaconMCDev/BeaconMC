import os
import importlib.util

class Plugin:
    def __init__(self, name):
        self.name = name

class PluginLoader:
    def __init__(self, plugins_dir='plugins'):
        self.plugins_dir = plugins_dir
        self.plugins = []

    def load_plugins(self):
        for root, dirs, files in os.walk(self.plugins_dir):
            for file in files:
                if file == 'plugin.py':
                    plugin_path = os.path.join(root, file)
                    plugin_name = os.path.basename(root)
                    self._load_plugin(plugin_path, plugin_name)

    def _load_plugin(self, plugin_path, plugin_name):
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'Plugin'):
            plugin_instance = module.Plugin(plugin_name)
            self.plugins.append(plugin_instance)
