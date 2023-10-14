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

from . import UTIL_preferences
from . import PROP_virtools_material
from . import OP_UV_flatten_uv

#region Menu

# ===== Menu Defines =====

class BBP_MT_View3DMenu(bpy.types.Menu):
    """Ballance 3D operators"""
    bl_idname = "BBP_MT_View3DMenu"
    bl_label = "Ballance"

    def draw(self, context):
        layout = self.layout

        layout.operator(OP_UV_flatten_uv.BBP_OT_flatten_uv.bl_idname)

# ===== Menu Drawer =====

MenuDrawer_t = typing.Callable[[typing.Any, typing.Any], None]

def menu_drawer_view3d(self, context):
    layout = self.layout
    layout.menu(BBP_MT_View3DMenu.bl_idname)

#endregion

#region Register and Unregister.

g_BldClasses: tuple[typing.Any, ...] = (
    OP_UV_flatten_uv.BBP_OT_flatten_uv,
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
)

def register() -> None:
    # register module
    UTIL_preferences.register()
    PROP_virtools_material.register()

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
    PROP_virtools_material.unregister()
    UTIL_preferences.unregister()

if __name__ == "__main__":
    register()

#endregion
