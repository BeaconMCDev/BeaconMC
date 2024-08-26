import os
import importlib.util

class Plugin:
    def __init__(self, name):
        self.name = name

class PluginLoader:
    def __init__(self, server, plugins_dir='plugins'):
        self.plugins_dir = plugins_dir
        self.plugins = []
        self.server = server

    def load_plugins(self):
        for root, dirs, files in os.walk(self.plugins_dir):
            for file in files:
                if file == 'plugin.py':
                    plugin_path = os.path.join(root, file)
                    plugin_name = os.path.basename(root)
                    self._load_plugin(plugin_path, plugin_name)

    def _load_plugin(self, plugin_path, plugin_name, temp):
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'Plugin'):
            plugin_instance = module.Plugin(self.server)
            try:
                pi = plugin_instance
                if hasattr(pi, "AUTHOR"):
                    self.server.log(f"Loading {pi.NAME} v{pi.VERSION} from {pi.AUTHOR}", 0)
                else:
                    authors = ""
                    for a in pi.AUTHORS:
                        authors += a + ", "
                    authors = authors[:2]
                    self.server.log(f"Loading {pi.NAME} v{pi.VERSION} from {authors}", 0)
                plugin_instance.onEnable()
                plugin_instance.enabled = True
                self.plugins.append(plugin_instance)
            except Exception as e:
                if hasattr(plugin_instance, 'disabled'):
                    plugin_instance.disabled = True
                else:
                    self.plugins.remove(plugin_instance)
                self.server.log("Plugin disabled due to issue when loading.", 2)
                self.server.log(f"{type(e)}: {e}", 2)
        else:
            self.server.log(f"File {plugin_path} does not contain the Plugin class ! Skipping...", 1)
