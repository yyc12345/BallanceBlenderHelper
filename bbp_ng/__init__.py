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

# we must load icons manager first
# and register it
from . import UTIL_icons_manager
UTIL_icons_manager.register()

# then load other modules
from . import PROP_preferences, PROP_ptrprop_resolver, PROP_virtools_material, PROP_virtools_texture, PROP_virtools_mesh, PROP_virtools_group, PROP_ballance_element, PROP_bme_material
from . import OP_IMPORT_bmfile, OP_EXPORT_bmfile, OP_IMPORT_virtools, OP_EXPORT_virtools
from . import OP_UV_flatten_uv, OP_UV_rail_uv
from . import OP_ADDS_component, OP_ADDS_bme, OP_ADDS_rail
from . import OP_OBJECT_legacy_align, OP_OBJECT_virtools_group, OP_OBJECT_naming_convention

#region Menu

# ===== Menu Defines =====

class BBP_MT_View3DMenu(bpy.types.Menu):
    """Ballance 3D Operators"""
    bl_idname = "BBP_MT_View3DMenu"
    bl_label = "Ballance"

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'UV', icon = 'UV')
        layout.operator(OP_UV_flatten_uv.BBP_OT_flatten_uv.bl_idname)
        layout.operator(OP_UV_rail_uv.BBP_OT_rail_uv.bl_idname)
        layout.separator()
        layout.label(text = 'Align', icon = 'SNAP_ON')
        layout.operator(OP_OBJECT_legacy_align.BBP_OT_legacy_align.bl_idname)
        layout.separator()
        layout.label(text = 'Select', icon = 'SELECT_SET')
        layout.operator(OP_OBJECT_virtools_group.BBP_OT_select_object_by_virtools_group.bl_idname)

class BBP_MT_AddBmeMenu(bpy.types.Menu):
    """Add Ballance Floor"""
    bl_idname = "BBP_MT_AddBmeMenu"
    bl_label = "Floors"

    def draw(self, context):
        layout = self.layout
        OP_ADDS_bme.BBP_OT_add_bme_struct.draw_blc_menu(layout)
        
class BBP_MT_AddRailMenu(bpy.types.Menu):
    """Add Ballance Rail"""
    bl_idname = "BBP_MT_AddRailMenu"
    bl_label = "Rails"

    def draw(self, context):
        layout = self.layout

        layout.label(text = "Sections", icon = 'MESH_CIRCLE')
        layout.operator(OP_ADDS_rail.BBP_OT_add_rail_section.bl_idname)
        layout.operator(OP_ADDS_rail.BBP_OT_add_transition_section.bl_idname)

        layout.separator()
        layout.label(text = "Straight Rails", icon = 'IPO_CONSTANT')
        layout.operator(OP_ADDS_rail.BBP_OT_add_straight_rail.bl_idname)
        layout.operator(OP_ADDS_rail.BBP_OT_add_transition_rail.bl_idname)
        layout.operator(OP_ADDS_rail.BBP_OT_add_side_rail.bl_idname)

        layout.separator()
        layout.label(text = "Curve Rails", icon = 'MOD_SCREW')
        layout.operator(OP_ADDS_rail.BBP_OT_add_arc_rail.bl_idname)
        layout.operator(OP_ADDS_rail.BBP_OT_add_spiral_rail.bl_idname)
        layout.operator(OP_ADDS_rail.BBP_OT_add_side_spiral_rail.bl_idname)
        
class BBP_MT_AddComponentsMenu(bpy.types.Menu):
    """Add Ballance Components"""
    bl_idname = "BBP_MT_AddComponentsMenu"
    bl_label = "Components"
    def draw(self, context):
        layout = self.layout

        layout.label(text = "Basic Components")
        OP_ADDS_component.BBP_OT_add_component.draw_blc_menu(layout)
        
        layout.separator()
        layout.label(text = "Nong Components")
        OP_ADDS_component.BBP_OT_add_nong_extra_point.draw_blc_menu(layout)
        OP_ADDS_component.BBP_OT_add_nong_ventilator.draw_blc_menu(layout)

        layout.separator()
        layout.label(text = "Series Components")
        OP_ADDS_component.BBP_OT_add_tilting_block_series.draw_blc_menu(layout)
        OP_ADDS_component.BBP_OT_add_ventilator_series.draw_blc_menu(layout)

        layout.separator()
        layout.label(text = "Components Pair")
        OP_ADDS_component.BBP_OT_add_sector_component_pair.draw_blc_menu(layout)

# ===== Menu Drawer =====

MenuDrawer_t = typing.Callable[[typing.Any, typing.Any], None]

def menu_drawer_import(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    #layout.operator(OP_IMPORT_bmfile.BBP_OT_import_bmfile.bl_idname, text = "Ballance Map (.bmx)")
    layout.operator(OP_IMPORT_virtools.BBP_OT_import_virtools.bl_idname, text = "Virtools File (.nmo/.cmo/.vmo) (experimental)")

def menu_drawer_export(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    #layout.operator(OP_EXPORT_bmfile.BBP_OT_export_bmfile.bl_idname, text = "Ballance Map (.bmx)")
    layout.operator(OP_EXPORT_virtools.BBP_OT_export_virtools.bl_idname, text = "Virtools File (.nmo/.cmo/.vmo) (experimental)")

def menu_drawer_view3d(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    layout.menu(BBP_MT_View3DMenu.bl_idname)

def menu_drawer_add(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    layout.separator()
    layout.label(text = "Ballance")
    layout.menu(BBP_MT_AddBmeMenu.bl_idname, icon='MESH_CUBE')
    layout.menu(BBP_MT_AddRailMenu.bl_idname, icon='MESH_CIRCLE')
    layout.menu(BBP_MT_AddComponentsMenu.bl_idname, icon='MESH_ICOSPHERE')

def menu_drawer_grouping(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    layout.separator()

    # NOTE: because outline context may change operator context
    # so it will cause no popup window when click operator in outline.
    # thus we create a sub layout and set its operator context as 'INVOKE_DEFAULT'
    # thus, all operators can pop up normally.
    col = layout.column()
    col.operator_context = 'INVOKE_DEFAULT'

    col.label(text = "Virtools Group")
    col.operator(OP_OBJECT_virtools_group.BBP_OT_add_objects_virtools_group.bl_idname, icon = 'ADD', text = "Group into...")
    col.operator(OP_OBJECT_virtools_group.BBP_OT_rm_objects_virtools_group.bl_idname, icon = 'REMOVE', text = "Ungroup from...")
    col.operator(OP_OBJECT_virtools_group.BBP_OT_clear_objects_virtools_group.bl_idname, icon = 'TRASH', text = "Clear All Groups")

def menu_drawer_naming_convention(self, context) -> None:
    layout: bpy.types.UILayout = self.layout
    layout.separator()

    # same reason in `menu_drawer_grouping()``
    col = layout.column()
    col.operator_context = 'INVOKE_DEFAULT'

    col.label(text = "Ballance")
    col.operator(OP_OBJECT_naming_convention.BBP_OT_regulate_objects_name.bl_idname, icon = 'GREASEPENCIL')
    col.operator(OP_OBJECT_naming_convention.BBP_OT_auto_grouping.bl_idname, icon = 'GROUP')
    col.operator(OP_OBJECT_naming_convention.BBP_OT_convert_to_imengyu.bl_idname, icon = 'ARROW_LEFTRIGHT')

#endregion

#region Register and Unregister.

g_BldClasses: tuple[typing.Any, ...] = (
    BBP_MT_View3DMenu,
    BBP_MT_AddBmeMenu,
    BBP_MT_AddRailMenu,
    BBP_MT_AddComponentsMenu
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
     MenuEntry(bpy.types.VIEW3D_MT_add, True, menu_drawer_add),

    # register double (for 2 menus)
     MenuEntry(bpy.types.VIEW3D_MT_object_context_menu, True, menu_drawer_grouping),
     MenuEntry(bpy.types.OUTLINER_MT_object, True, menu_drawer_grouping),

     MenuEntry(bpy.types.OUTLINER_MT_collection, True, menu_drawer_naming_convention),
)

def register() -> None:
    # register module
    PROP_preferences.register()
    PROP_ptrprop_resolver.register()

    PROP_virtools_material.register()
    PROP_virtools_texture.register()
    PROP_virtools_mesh.register()
    PROP_virtools_group.register()
    PROP_ballance_element.register()
    PROP_bme_material.register()

    OP_IMPORT_bmfile.register()
    OP_EXPORT_bmfile.register()
    OP_IMPORT_virtools.register()
    OP_EXPORT_virtools.register()

    OP_UV_rail_uv.register()
    OP_UV_flatten_uv.register()
    OP_ADDS_component.register()
    OP_ADDS_bme.register()
    OP_ADDS_rail.register()

    OP_OBJECT_legacy_align.register()
    OP_OBJECT_virtools_group.register()
    OP_OBJECT_naming_convention.register()

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
    OP_OBJECT_naming_convention.unregister()
    OP_OBJECT_virtools_group.unregister()
    OP_OBJECT_legacy_align.unregister()

    OP_ADDS_rail.unregister()
    OP_ADDS_bme.unregister()
    OP_ADDS_component.unregister()
    OP_UV_flatten_uv.unregister()
    OP_UV_rail_uv.unregister()

    OP_EXPORT_virtools.unregister()
    OP_IMPORT_virtools.unregister()
    OP_EXPORT_bmfile.unregister()
    OP_IMPORT_bmfile.unregister()

    PROP_bme_material.unregister()
    PROP_ballance_element.unregister()
    PROP_virtools_group.unregister()
    PROP_virtools_mesh.unregister()
    PROP_virtools_texture.unregister()
    PROP_virtools_material.unregister()
    
    PROP_ptrprop_resolver.unregister()
    PROP_preferences.unregister()

if __name__ == "__main__":
    register()

#endregion
