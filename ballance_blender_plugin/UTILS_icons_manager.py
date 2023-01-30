import bpy
import bpy.utils.previews
import os
from . import UTILS_constants

blender_info_icon = 'INFO'
blender_warning_icon = 'ERROR'
blender_error_icon = 'CANCEL'

# universal icon loader, all icon are stored in this preview collection
universal_icons = None

# empty icon for placeholder
empty_icon_id = 0

# a map. key is block name, value is loaded icon id
floor_icons_map: dict = {}
element_icons_map: dict = {}
groupext_icons_map: dict = {}

group_name_conv_map: dict = {
    "PS_Levelstart": "PS_FourFlames",
    "PE_Levelende": "PE_Balloon",
    "PC_Checkpoints": "PC_TwoFlames",
    "PR_Resetpoints": "PR_Resetpoint",

    "Sound_HitID_01": "SoundID_01",
    "Sound_RollID_01": "SoundID_01",
    "Sound_HitID_02": "SoundID_02",
    "Sound_RollID_02": "SoundID_02",
    "Sound_HitID_03": "SoundID_03",
    "Sound_RollID_03": "SoundID_03"
}

def register_icons():
    global universal_icons
    global empty_icon_id
    global floor_icons_map, element_icons_map, groupext_icons_map

    # create preview collection and get icon folder
    icon_path = os.path.join(os.path.dirname(__file__), "icons")
    universal_icons = bpy.utils.previews.new()

    # load empty
    universal_icons.load("BlcBldPlg_EmptyIcon", os.path.join(icon_path, "Empty.png"), 'IMAGE')
    empty_icon_id = universal_icons["BlcBldPlg_EmptyIcon"].icon_id

    # add floor icon
    for key, value in UTILS_constants.floor_blockDict.items():
        blockIconName = "BlcBldPlg_FloorIcon_" + key
        universal_icons.load(blockIconName, os.path.join(icon_path, "floor", value["BindingDisplayTexture"]), 'IMAGE')
        floor_icons_map[key] = universal_icons[blockIconName].icon_id

    # add elements icon
    for elename in UTILS_constants.bmfile_componentList:
        blockIconName = "BlcBldPlg_ElementIcon_" + elename
        universal_icons.load(blockIconName, os.path.join(icon_path, "element", elename + '.png'), 'IMAGE')
        element_icons_map[elename] = universal_icons[blockIconName].icon_id

    # add extra group icon
    for grp in ("SoundID_01", "SoundID_02", "SoundID_03"):
        blockIconName = "BlcBldPlg_GroupIcon_" + grp
        universal_icons.load(blockIconName, os.path.join(icon_path, "group", grp + '.png'), 'IMAGE')
        groupext_icons_map[grp] = universal_icons[blockIconName].icon_id

def unregister_icons():
    global universal_icons
    global floor_icons_map, element_icons_map, groupext_icons_map

    bpy.utils.previews.remove(universal_icons)
    floor_icons_map.clear()
    element_icons_map.clear()
    groupext_icons_map.clear()

def get_floor_icon(floor_blk_name: str):
    # default return empty icon
    return floor_icons_map.get(floor_blk_name, empty_icon_id)

def get_element_icon(element_name: str):
    # default return empty icon
    return element_icons_map.get(element_name, empty_icon_id)

def get_group_icon(group_name: str):
    # try parse string
    # if not found, return self
    conv_name = group_name_conv_map.get(group_name, group_name)

    # get from extra group icon first
    idx = groupext_icons_map.get(conv_name, empty_icon_id)
    if idx != empty_icon_id:
        return idx

    # if failed, get from element. if still failed, return empty icon
    return get_element_icon(conv_name)

# no matter how, register icon always
# and no unregister call
register_icons()
