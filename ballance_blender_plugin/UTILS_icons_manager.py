import bpy
import bpy.utils.previews
import os
from . import UTILS_constants

blender_info_icon = 'INFO'
blender_warning_icon = 'ERROR'
blender_error_icon = 'CANCEL'

# ImagePreviewCollection ccreated by Blender
floor_icons = None
# a map. key is block name, value is loaded icon id
floor_icons_map: dict = {}

def register_icons():
    global floor_icons, floor_icons_map

    icon_path = os.path.join(os.path.dirname(__file__), "icons")
    floor_icons = bpy.utils.previews.new()
    for key, value in UTILS_constants.floor_blockDict.items():
        blockIconName = "Ballance_FloorIcon_" + key
        floor_icons.load(blockIconName, os.path.join(icon_path, "floor", value["BindingDisplayTexture"]), 'IMAGE')
        floor_icons_map[key] = floor_icons[blockIconName].icon_id

def unregister_icons():
    global floor_icons, floor_icons_map

    bpy.utils.previews.remove(floor_icons)
    floor_icons_map.clear()

def get_floor_icon(floor_blk_name: str):
    global floor_icons_map

    return floor_icons_map[floor_blk_name]
