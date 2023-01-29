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

element_icons = None
element_icons_map: dict = {}

def register_icons():
    global floor_icons, floor_icons_map
    global element_icons, element_icons_map

    icon_path = os.path.join(os.path.dirname(__file__), "icons")

    floor_icons = bpy.utils.previews.new()
    for key, value in UTILS_constants.floor_blockDict.items():
        blockIconName = "BlcBldPlg_FloorIcon_" + key
        floor_icons.load(blockIconName, os.path.join(icon_path, "floor", value["BindingDisplayTexture"]), 'IMAGE')
        floor_icons_map[key] = floor_icons[blockIconName].icon_id

    element_icons = bpy.utils.previews.new()
    for elename in UTILS_constants.bmfile_componentList:
        blockIconName = "BlcBldPlg_ElementIcon_" + elename
        element_icons.load(blockIconName, os.path.join(icon_path, "element", elename + '.png'), 'IMAGE')
        element_icons_map[elename] = element_icons[blockIconName].icon_id

def unregister_icons():
    global floor_icons, floor_icons_map
    global element_icons, element_icons_map

    bpy.utils.previews.remove(floor_icons)
    floor_icons_map.clear()
    bpy.utils.previews.remove(element_icons)
    element_icons_map.clear()

def get_floor_icon(floor_blk_name: str):
    global floor_icons_map
    # default return 0
    return floor_icons_map.get(floor_blk_name, 0)

def get_element_icon(element_name: str):
    global element_icons_map
    # default return 0
    return element_icons_map.get(element_name, 0)
