"""BEACONMC - modulable_pluginsystem file"""

#If this option is true, the plugins will be loaded normally. Else, they will not be loaded.
ENABLE_PLUGINS = True

#Put here the plugins import
#
# EXAMPLE
#
# import exampleplugin.main as exampleplugin
# ep = exampleplugin.Plugin
#
# import example2plugin.main as example2
# e2 = example2.Plugin

import plugins.example.main as ex
pl = ex.Plugin()

#Put here the plugin instances
#
# EXAMPLE
#
# PLUGIN_LIST = [ep, e2]

PLUGIN_LIST = [pl]