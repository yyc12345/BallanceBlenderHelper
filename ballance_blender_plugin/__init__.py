bl_info={
	"name":"Ballance Blender Plugin",
	"description":"Ballance mapping tools for Blender",
	"author":"yyc12345",
	"version":(3,0),
	"blender":(2,83,0),
	"category":"Object",
	"support":"TESTING",
    "warning": "Please read document before using this plugin.",
    "wiki_url": "https://github.com/yyc12345/BallanceBlenderHelper",
    "tracker_url": "https://github.com/yyc12345/BallanceBlenderHelper/issues"
}

# ============================================= 
# import system
import bpy, bpy_extras
import bpy.utils.previews
import os
# import my code (with reload)
if "bpy" in locals():
    import importlib
    if "UTILS_constants" in locals():
        importlib.reload(UTILS_constants)
    if "UTILS_functions" in locals():
        importlib.reload(UTILS_functions)
    if "UTILS_preferences" in locals():
        importlib.reload(UTILS_preferences)
    if "UTILS_file_io" in locals():
        importlib.reload(UTILS_file_io)
    if "UTILS_zip_helper" in locals():
        importlib.reload(UTILS_zip_helper)

    if "BMFILE_export" in locals():
        importlib.reload(BMFILE_export)
    if "BMFILE_import" in locals():
        importlib.reload(BMFILE_import)

    if "MODS_rail_uv" in locals():
        importlib.reload(MODS_rail_uv)
    if "MODS_3dsmax_align" in locals():
        importlib.reload(MODS_3dsmax_align)
    if "MODS_flatten_uv" in locals():
        importlib.reload(MODS_flatten_uv)

    if "OBJS_add_components" in locals():
        importlib.reload(OBJS_add_components)
    if "OBJS_add_floors" in locals():
        importlib.reload(OBJS_add_floors)
    if "OBJS_add_rails" in locals():
        importlib.reload(OBJS_add_rails)

    if "NAMES_rename_system" in locals():
        importlib.reload(NAMES_rename_system)

from . import UTILS_constants, UTILS_functions, UTILS_preferences
from . import BMFILE_export, BMFILE_import
from . import MODS_3dsmax_align, MODS_flatten_uv, MODS_rail_uv
from . import OBJS_add_components, OBJS_add_floors, OBJS_add_rails
from . import NAMES_rename_system

# ============================================= 
# menu system

class BALLANCE_MT_ThreeDViewerMenu(bpy.types.Menu):
    """Ballance related 3D operators"""
    bl_idname = "BALLANCE_MT_ThreeDViewerMenu"
    bl_label = "Ballance"

    def draw(self, context):
        layout = self.layout

        layout.operator(MODS_3dsmax_align.BALLANCE_OT_super_align.bl_idname)
        layout.operator(MODS_rail_uv.BALLANCE_OT_rail_uv.bl_idname)
        layout.operator(MODS_flatten_uv.BALLANCE_OT_flatten_uv.bl_idname)

class BALLANCE_MT_OutlinerMenu(bpy.types.Menu):
    """Ballance rename operators"""
    bl_idname = "BALLANCE_MT_OutlinerMenu"
    bl_label = "Ballance"

    def draw(self, context):
        layout = self.layout

        layout.label(text="For Collection")
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_rename_via_group.bl_idname)
        oprt.oper_source = 'COLLECTION'
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_convert_name.bl_idname)
        oprt.oper_source = 'COLLECTION'
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_auto_grouping.bl_idname)
        oprt.oper_source = 'COLLECTION'

        layout.separator()

        layout.label(text="For Objects")
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_rename_via_group.bl_idname)
        oprt.oper_source = 'OBJECTS'
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_convert_name.bl_idname)
        oprt.oper_source = 'OBJECTS'
        oprt = layout.operator(NAMES_rename_system.BALLANCE_OT_auto_grouping.bl_idname)
        oprt.oper_source = 'OBJECTS'

class BALLANCE_MT_AddFloorMenu(bpy.types.Menu):
    """Add Ballance floor"""
    bl_idname = "BALLANCE_MT_AddFloorMenu"
    bl_label = "Floors"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Basic floor")
        for item in UTILS_constants.floor_basicBlockList:
            cop = layout.operator(
                OBJS_add_floors.BALLANCE_OT_add_floors.bl_idname, 
                text=item, icon_value = UTILS_constants.icons_floorDict[item])
            cop.floor_type = item

        layout.separator()
        layout.label(text="Derived floor")
        for item in UTILS_constants.floor_derivedBlockList:
            cop = layout.operator(
                OBJS_add_floors.BALLANCE_OT_add_floors.bl_idname, 
                text=item, icon_value = UTILS_constants.icons_floorDict[item])
            cop.floor_type = item


# ============================================= 
# blender call system

classes = (
    UTILS_preferences.BallanceBlenderPluginPreferences,
    UTILS_preferences.MyPropertyGroup,
    
    BMFILE_import.BALLANCE_OT_import_bm,
    BMFILE_export.BALLANCE_OT_export_bm,

    MODS_rail_uv.BALLANCE_OT_rail_uv,
    MODS_3dsmax_align.BALLANCE_OT_super_align,
    MODS_flatten_uv.BALLANCE_OT_flatten_uv,
    BALLANCE_MT_ThreeDViewerMenu,

    OBJS_add_components.BALLANCE_OT_add_components,
    OBJS_add_rails.BALLANCE_OT_add_rails,
    OBJS_add_floors.BALLANCE_OT_add_floors,
    BALLANCE_MT_AddFloorMenu,

    NAMES_rename_system.BALLANCE_OT_rename_via_group,
    NAMES_rename_system.BALLANCE_OT_convert_name,
    NAMES_rename_system.BALLANCE_OT_auto_grouping,
    BALLANCE_MT_OutlinerMenu
)

def menu_func_bm_import(self, context):
    self.layout.operator(BMFILE_import.BALLANCE_OT_import_bm.bl_idname, text="Ballance Map (.bmx)")
def menu_func_bm_export(self, context):
    self.layout.operator(BMFILE_export.BALLANCE_OT_export_bm.bl_idname, text="Ballance Map (.bmx)")
def menu_func_ballance_3d(self, context):
    layout = self.layout
    layout.menu(BALLANCE_MT_ThreeDViewerMenu.bl_idname)
def menu_func_ballance_add(self, context):
    layout = self.layout
    layout.separator()
    layout.label(text="Ballance")
    layout.operator_menu_enum(
        OBJS_add_components.BALLANCE_OT_add_components.bl_idname, 
        "elements_type", icon='MESH_ICOSPHERE', text="Elements")
    layout.operator(OBJS_add_rails.BALLANCE_OT_add_rails.bl_idname, icon='MESH_CIRCLE', text="Rail section")
    layout.menu(BALLANCE_MT_AddFloorMenu.bl_idname, icon='MESH_CUBE')
def menu_func_ballance_rename(self, context):
    layout = self.layout
    layout.menu(BALLANCE_MT_OutlinerMenu.bl_idname)


def register():
    # we need init all icon first
    icon_path = os.path.join(os.path.dirname(__file__), "icons")
    UTILS_constants.icons_floor = bpy.utils.previews.new()
    for key, value in UTILS_constants.floor_blockDict.items():
        blockIconName = "Ballance_FloorIcon_" + key
        UTILS_constants.icons_floor.load(blockIconName, os.path.join(icon_path, "floor", value["BindingDisplayTexture"]), 'IMAGE')
        UTILS_constants.icons_floorDict[key] = UTILS_constants.icons_floor[blockIconName].icon_id

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.BallanceBlenderPluginProperty = bpy.props.PointerProperty(type=UTILS_preferences.MyPropertyGroup)
        
    bpy.types.TOPBAR_MT_file_import.append(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_bm_export)

    bpy.types.VIEW3D_MT_editor_menus.prepend(menu_func_ballance_3d)
    bpy.types.VIEW3D_MT_add.append(menu_func_ballance_add)
    bpy.types.OUTLINER_HT_header.append(menu_func_ballance_rename)
def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_bm_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_bm_export)
    
    bpy.types.VIEW3D_MT_editor_menus.remove(menu_func_ballance_3d)
    bpy.types.VIEW3D_MT_add.remove(menu_func_ballance_add)
    bpy.types.OUTLINER_HT_header.remove(menu_func_ballance_rename)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # we need uninstall all icon after all classes unregister
    bpy.utils.previews.remove(UTILS_constants.icons_floor)
    
if __name__=="__main__":
	register()