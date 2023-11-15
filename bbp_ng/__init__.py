bl_info = {
    "name": "Ballance Blender Plugin",
    "description": "Ballance mapping tools for Blender",
    "author": "yyc12345",
    "version": (4, 0),
    "blender": (3, 6, 0),
    "category": "Object",
    "support": "COMMUNITY",
    "warning": "Please read document before using this plugin.",
    "doc_url": "https://github.com/yyc12345/BallanceBlenderHelper",
    "tracker_url": "https://github.com/yyc12345/BallanceBlenderHelper/issues"
}

#region Reload and Import

# import core lib
import bpy
import typing, collections

# reload if needed
if "bpy" in locals():
    import importlib

#endregion

from . import PROP_preferences, PROP_virtools_material, PROP_virtools_texture, PROP_virtools_mesh, PROP_ballance_element, PROP_virtools_group
from . import OP_IMPORT_bmfile, OP_EXPORT_bmfile, OP_IMPORT_virtools, OP_EXPORT_virtools
from . import OP_UV_flatten_uv, OP_UV_rail_uv

#region Menu

# ===== Menu Defines =====

class BBP_MT_View3DMenu(bpy.types.Menu):
    """Ballance 3D operators"""
    bl_idname = "BBP_MT_View3DMenu"
    bl_label = "Ballance"

    def draw(self, context):
        layout = self.layout
        layout.operator(OP_UV_flatten_uv.BBP_OT_flatten_uv.bl_idname)
        layout.operator(OP_UV_rail_uv.BBP_OT_rail_uv.bl_idname)

# ===== Menu Drawer =====

MenuDrawer_t = typing.Callable[[typing.Any, typing.Any], None]

def menu_drawer_import(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.operator(OP_IMPORT_bmfile.BBP_OT_import_bmfile.bl_idname, text = "Ballance Map (.bmx)")
    layout.operator(OP_IMPORT_virtools.BBP_OT_import_virtools.bl_idname, text = "Virtools File (.nmo/.cmo/.vmo) (experimental)")

def menu_drawer_export(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.operator(OP_EXPORT_bmfile.BBP_OT_export_bmfile.bl_idname, text = "Ballance Map (.bmx)")
    layout.operator(OP_EXPORT_virtools.BBP_OT_export_virtools.bl_idname, text = "Virtools File (.nmo/.cmo/.vmo) (experimental)")

def menu_drawer_view3d(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.menu(BBP_MT_View3DMenu.bl_idname)

#endregion

#region Register and Unregister.

g_BldClasses: tuple[typing.Any, ...] = (
    BBP_MT_View3DMenu,
)

class MenuEntry():
    mContainerMenu: bpy.types.Menu
    mIsAppend: bool
    mMenuDrawer: MenuDrawer_t
    def __init__(self, cont: bpy.types.Menu, is_append: bool, menu_func: MenuDrawer_t):
        self.mContainerMenu = cont
        self.mIsAppend = is_append
        self.mMenuDrawer = menu_func

g_BldMenus: tuple[MenuEntry, ...] = (
     MenuEntry(bpy.types.VIEW3D_MT_editor_menus, False, menu_drawer_view3d),
     MenuEntry(bpy.types.TOPBAR_MT_file_import, True, menu_drawer_import),
     MenuEntry(bpy.types.TOPBAR_MT_file_export, True, menu_drawer_export),
)

def register() -> None:
    # register module
    PROP_preferences.register()
    PROP_virtools_material.register()
    PROP_virtools_texture.register()
    PROP_virtools_mesh.register()
    PROP_ballance_element.register()
    PROP_virtools_group.register()

    OP_IMPORT_bmfile.register()
    OP_EXPORT_bmfile.register()
    OP_IMPORT_virtools.register()
    OP_EXPORT_virtools.register()

    OP_UV_rail_uv.register()
    OP_UV_flatten_uv.register()

    # register other classes
    for cls in g_BldClasses:
        bpy.utils.register_class(cls)

    # add menu drawer
    for entry in g_BldMenus:
        if entry.mIsAppend:
            entry.mContainerMenu.append(entry.mMenuDrawer)
        else:
            entry.mContainerMenu.prepend(entry.mMenuDrawer)

def unregister() -> None:
    # remove menu drawer
    for entry in g_BldMenus:
        entry.mContainerMenu.remove(entry.mMenuDrawer)

    # unregister other classes
    for cls in g_BldClasses:
        bpy.utils.unregister_class(cls)

    # unregister modules
    OP_UV_flatten_uv.unregister()
    OP_UV_rail_uv.unregister()

    OP_EXPORT_virtools.unregister()
    OP_IMPORT_virtools.unregister()
    OP_EXPORT_bmfile.unregister()
    OP_IMPORT_bmfile.unregister()

    PROP_virtools_group.unregister()
    PROP_ballance_element.unregister()
    PROP_virtools_mesh.unregister()
    PROP_virtools_texture.unregister()
    PROP_virtools_material.unregister()
    PROP_preferences.unregister()

if __name__ == "__main__":
    register()

#endregion
