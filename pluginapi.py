# import main
import os
import sys
import yaml
# import threading
PLUGIN_FOLDER_PATH = "plugins"

# API

class PluginLoader(object):
    def __init__(self, server):
        self.server = server
        
    def core_get_version(self):
        return f"{self.server.CLIENT_VERSION} {self.server.SERVER_VERSION}.{self.server.PROTOCOL_VERSION}"

    def execute_file(self, file_path, plugin_directory):
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                exec(file_content, {'__file__': file_path, 'os': os})
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(e)

    def process_list_file(self, yaml_file_path, plugin_directory):
        try:
            with open(yaml_file_path, "r") as yaml_file:
                plugin_data = yaml.load(yaml_file, Loader=yaml.FullLoader)

                name = plugin_data.get("Name")
                description = plugin_data.get("Description")
                main_file = plugin_data.get("main_file")
                self.server.log(f"Starting loading : {name}",0)

            self.execute_file(os.path.join(plugin_directory, main_file), plugin_directory)

        except FileNotFoundError:
            print("")
        except Exception as e:
            print("")
        self.server.log('Loaded !',0)

    def load_plugins(self, plugins_directory):
        try:
            # threads = []
            plugins = os.listdir(plugins_directory)
            for plugin in plugins:
                plugin_path = os.path.join(plugins_directory, plugin)
                yaml_file_path = os.path.join(plugin_path, "plugin.yaml")  
                if os.path.isfile(yaml_file_path):
                    # thread_plugin = threading.Thread(target=process_list_file, args=(yaml_file_path, plugin_path))
                    # thread_plugin.start()
                    # threads.append(thread_plugin)

            # Wait for all threads to finish
            # for thread in threads:
                # thread.join()
                    ...
        except Exception as e:
            print(e)

    def init_api(self):
        main.log("Plugin API loading...", 0)
        main.log("Checking some things...", 0)
        try:
            if os.path.isdir(PLUGIN_FOLDER_PATH):
                self.server.log("Folder plugin exists!", 0)
            else:
                os.mkdir(PLUGIN_FOLDER_PATH)
        except Exception as e:
            print(e)
        self.load_plugins(plugins_directory=PLUGIN_FOLDER_PATH)
