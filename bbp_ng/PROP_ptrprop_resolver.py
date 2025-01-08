import bpy
from bpy.types import Context, Event
from . import UTIL_functions

## Intent
#  Operator is not allowed to register Pointer Properties.
#  The solution is register pointer properties in Scene and reference it when drawing operator window.
#  This module contains all pointer properties used by other operators.

#region Blender Type Defines

class BBP_PG_bmap_encoding(bpy.types.PropertyGroup):
    encoding: bpy.props.StringProperty(
        name = "Encoding",
        default = ""
    ) # type: ignore

class BBP_UL_bmap_encoding(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item: BBP_PG_bmap_encoding, icon, active_data, active_propname):
        layout.prop(item, 'encoding', emboss = False, text = '', icon = 'FONT_DATA')

class BBP_PG_ptrprop_resolver(bpy.types.PropertyGroup):
    rail_uv_material: bpy.props.PointerProperty(
        name = "Material",
        description = "The material used for rail",
        type = bpy.types.Material,
    ) # type: ignore
    
    export_collection: bpy.props.PointerProperty(
        type = bpy.types.Collection,
        name = "Collection",
        description = "The collection exported. Nested collections allowed."
    ) # type: ignore
    
    export_object: bpy.props.PointerProperty(
        type = bpy.types.Object,
        name = "Object",
        description = "The object exported"
    ) # type: ignore

    ioport_encodings: bpy.props.CollectionProperty(
        type = BBP_PG_bmap_encoding
    ) # type: ignore
    active_ioport_encodings: bpy.props.IntProperty() # type: ignore

#endregion

def get_ptrprop_resolver() -> BBP_PG_ptrprop_resolver:
    return bpy.context.scene.bbp_ptrprop_resolver

def get_ioport_encodings() -> UTIL_functions.CollectionVisitor[BBP_PG_bmap_encoding]:
    return UTIL_functions.CollectionVisitor(get_ptrprop_resolver().ioport_encodings)
def get_active_ioport_encoding() -> int:
    return get_ptrprop_resolver().active_ioport_encodings
def set_active_ioport_encoding(val: int) -> None:
    get_ptrprop_resolver().active_ioport_encodings = val

#region Blender Operator Defines for Encodings

class BBP_OT_add_ioport_encodings(bpy.types.Operator):
    """Add item at the tail of encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.add_ioport_encodings"
    bl_label = "Add in Encodings List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def execute(self, context):
        encodings = get_ioport_encodings()
        encodings.add()
        return {'FINISHED'}

class BBP_OT_rm_ioport_encodings(bpy.types.Operator):
    """Remove selected item in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.rm_ioport_encodings"
    bl_label = "Remove from Encodings List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings()
        index = get_active_ioport_encoding()
        return index >= 0 and index < len(encodings)

    def execute(self, context):
        encodings = get_ioport_encodings()
        encodings.remove(get_active_ioport_encoding())
        return {'FINISHED'}

class BBP_OT_up_ioport_encodings(bpy.types.Operator):
    """Move selected item up in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.up_ioport_encodings"
    bl_label = "Move Up in Encodings List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings()
        index = get_active_ioport_encoding()
        return index >= 1 and index < len(encodings)

    def execute(self, context):
        encodings = get_ioport_encodings()
        index = get_active_ioport_encoding()
        encodings.move(index, index - 1)
        set_active_ioport_encoding(index - 1)
        return {'FINISHED'}

class BBP_OT_down_ioport_encodings(bpy.types.Operator):
    """Move selected item down in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.down_ioport_encodings"
    bl_label = "Move Down in Encodings List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings()
        index = get_active_ioport_encoding()
        return index >= 0 and index < len(encodings) - 1

    def execute(self, context):
        encodings = get_ioport_encodings()
        index = get_active_ioport_encoding()
        encodings.move(index, index + 1)
        set_active_ioport_encoding(index + 1)
        return {'FINISHED'}

class BBP_OT_clear_ioport_encodings(bpy.types.Operator):
    """Clear the encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.clear_ioport_encodings"
    bl_label = "Clear Encodings List"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        encodings = get_ioport_encodings()
        encodings.clear()
        set_active_ioport_encoding(0)
        return {'FINISHED'}

#endregion

class PtrPropResolver():
    """
    All outside code should use this class static methods to fetch property data or draw property.
    All function inside in this module should not be called directly.
    """

    @staticmethod
    def get_rail_uv_material() -> bpy.types.Material:
        return get_ptrprop_resolver().rail_uv_material
    @staticmethod
    def draw_rail_uv_material(layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(), 'rail_uv_material')

    @staticmethod
    def get_export_collection() -> bpy.types.Collection:
        return get_ptrprop_resolver().export_collection
    @staticmethod
    def draw_export_collection(layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(), 'export_collection')

    @staticmethod
    def get_export_object() -> bpy.types.Object:
        return get_ptrprop_resolver().export_object
    @staticmethod
    def draw_export_object(layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(), 'export_object')

    @staticmethod
    def get_ioport_encodings() -> tuple[str, ...]:
        encodings = get_ioport_encodings()
        return tuple(i.encoding for i in encodings)
    @staticmethod
    def set_ioport_encodings(user_encodings: tuple[str, ...]) -> None:
        encodings = get_ioport_encodings()
        # clear and apply user encoding one by one
        encodings.clear()
        for user_encoding in user_encodings:
            item = encodings.add()
            item.encoding = user_encoding
    @staticmethod
    def draw_ioport_encodings(layout: bpy.types.UILayout) -> None:
        target = get_ptrprop_resolver()
        row = layout.row()

        # draw main list
        row.template_list(
            "BBP_UL_bmap_encoding", "", 
            target, "ioport_encodings",
            target, "active_ioport_encodings",
            rows = 6, maxrows = 6,
            sort_reverse = False, sort_lock = True # disable sort feature because the order od this encoding list is crucial
        )

        # draw sidebar
        col = row.column(align=True)
        col.operator(BBP_OT_add_ioport_encodings.bl_idname, icon='ADD', text='')
        col.operator(BBP_OT_rm_ioport_encodings.bl_idname, icon='REMOVE', text='')
        col.separator()
        col.operator(BBP_OT_up_ioport_encodings.bl_idname, icon='TRIA_UP', text='')
        col.operator(BBP_OT_down_ioport_encodings.bl_idname, icon='TRIA_DOWN', text='')
        col.separator()
        col.operator(BBP_OT_clear_ioport_encodings.bl_idname, icon='TRASH', text='')

def register() -> None:
    bpy.utils.register_class(BBP_PG_bmap_encoding)
    bpy.utils.register_class(BBP_UL_bmap_encoding)
    bpy.utils.register_class(BBP_PG_ptrprop_resolver)

    bpy.utils.register_class(BBP_OT_add_ioport_encodings)
    bpy.utils.register_class(BBP_OT_rm_ioport_encodings)
    bpy.utils.register_class(BBP_OT_up_ioport_encodings)
    bpy.utils.register_class(BBP_OT_down_ioport_encodings)
    bpy.utils.register_class(BBP_OT_clear_ioport_encodings)

    bpy.types.Scene.bbp_ptrprop_resolver = bpy.props.PointerProperty(type = BBP_PG_ptrprop_resolver)

def unregister() -> None:
    del bpy.types.Scene.bbp_ptrprop_resolver

    bpy.utils.unregister_class(BBP_OT_clear_ioport_encodings)
    bpy.utils.unregister_class(BBP_OT_down_ioport_encodings)
    bpy.utils.unregister_class(BBP_OT_up_ioport_encodings)
    bpy.utils.unregister_class(BBP_OT_rm_ioport_encodings)
    bpy.utils.unregister_class(BBP_OT_add_ioport_encodings)

    bpy.utils.unregister_class(BBP_PG_ptrprop_resolver)
    bpy.utils.unregister_class(BBP_UL_bmap_encoding)
    bpy.utils.unregister_class(BBP_PG_bmap_encoding)
