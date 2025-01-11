import bpy
from bpy.types import Context, Event
from . import UTIL_functions, UTIL_virtools_types

## Intent
#  Operator is not allowed to register Pointer Properties.
#  The solution is register pointer properties in Scene and reference it when drawing operator window.
#  This module contains all pointer properties used by other operators.

#region Blender Type Defines

class BBP_PG_bmap_encoding(bpy.types.PropertyGroup):
    encoding: bpy.props.StringProperty(
        name = "Encoding",
        default = "",
        translation_context = 'BBP_PG_bmap_encoding/property'
    ) # type: ignore

class BBP_UL_bmap_encoding(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item: BBP_PG_bmap_encoding, icon, active_data, active_propname):
        layout.prop(item, 'encoding', emboss = False, text = '', icon = 'FONT_DATA')

class BBP_PG_ptrprop_resolver(bpy.types.PropertyGroup):
    rail_uv_material: bpy.props.PointerProperty(
        name = "Material",
        description = "The material used for rail",
        type = bpy.types.Material,
        translation_context = 'BBP_PG_ptrprop_resolver/property'
    ) # type: ignore
    
    export_collection: bpy.props.PointerProperty(
        name = "Collection",
        description = "The collection exported. Nested collections allowed.",
        type = bpy.types.Collection,
        translation_context = 'BBP_PG_ptrprop_resolver/property'
    ) # type: ignore
    
    export_object: bpy.props.PointerProperty(
        name = "Object",
        description = "The object exported",
        type = bpy.types.Object,
        translation_context = 'BBP_PG_ptrprop_resolver/property'
    ) # type: ignore

    # TR: These encoding related items should not have explicit name and description
    ioport_encodings: bpy.props.CollectionProperty(type = BBP_PG_bmap_encoding) # type: ignore
    active_ioport_encodings: bpy.props.IntProperty() # type: ignore

#endregion

def get_ptrprop_resolver(scene: bpy.types.Scene) -> BBP_PG_ptrprop_resolver:
    return scene.bbp_ptrprop_resolver

def get_ioport_encodings(scene: bpy.types.Scene) -> UTIL_functions.CollectionVisitor[BBP_PG_bmap_encoding]:
    return UTIL_functions.CollectionVisitor(get_ptrprop_resolver(scene).ioport_encodings)
def get_active_ioport_encoding(scene: bpy.types.Scene) -> int:
    return get_ptrprop_resolver(scene).active_ioport_encodings
def set_active_ioport_encoding(scene: bpy.types.Scene, val: int) -> None:
    get_ptrprop_resolver(scene).active_ioport_encodings = val

#region Blender Operator Defines for Encodings

class BBP_OT_add_ioport_encodings(bpy.types.Operator):
    """Add item at the tail of encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.add_ioport_encodings"
    bl_label = "Add in Encodings List"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_add_ioport_encodings'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def execute(self, context):
        encodings = get_ioport_encodings(context.scene)
        encodings.add()
        return {'FINISHED'}

class BBP_OT_rm_ioport_encodings(bpy.types.Operator):
    """Remove selected item in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.rm_ioport_encodings"
    bl_label = "Remove from Encodings List"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_rm_ioport_encodings'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        return index >= 0 and index < len(encodings)

    def execute(self, context):
        # delete selected item
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        encodings.remove(index)
        # try to correct selected item
        if index >= len(encodings): index = len(encodings) - 1
        if index < 0: index = 0
        set_active_ioport_encoding(context.scene, index)
        return {'FINISHED'}

class BBP_OT_up_ioport_encodings(bpy.types.Operator):
    """Move selected item up in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.up_ioport_encodings"
    bl_label = "Move Up in Encodings List"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_up_ioport_encodings'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        return index >= 1 and index < len(encodings)

    def execute(self, context):
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        encodings.move(index, index - 1)
        set_active_ioport_encoding(context.scene, index - 1)
        return {'FINISHED'}

class BBP_OT_down_ioport_encodings(bpy.types.Operator):
    """Move selected item down in encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.down_ioport_encodings"
    bl_label = "Move Down in Encodings List"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_down_ioport_encodings'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        return index >= 0 and index < len(encodings) - 1

    def execute(self, context):
        encodings = get_ioport_encodings(context.scene)
        index = get_active_ioport_encoding(context.scene)
        encodings.move(index, index + 1)
        set_active_ioport_encoding(context.scene, index + 1)
        return {'FINISHED'}

class BBP_OT_clear_ioport_encodings(bpy.types.Operator):
    """Clear the encodings list used by BMap for Virtools file read and write."""
    bl_idname = "bbp.clear_ioport_encodings"
    bl_label = "Clear Encodings List"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_clear_ioport_encodings'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        encodings = get_ioport_encodings(context.scene)
        encodings.clear()
        set_active_ioport_encoding(context.scene, 0)
        return {'FINISHED'}

#endregion

class PropsVisitor():
    """
    When outside code want to fetch or draw properties defined in ptrprop_resolver,
    they should create the instance of this class with given associated scene instance first.
    Then use this class provided member function to draw or fetch these properties.
    The function located in this module should not be called directly!
    """

    __mAssocScene: bpy.types.Scene

    def __init__(self, assoc_scene: bpy.types.Scene):
        self.__mAssocScene = assoc_scene

    def get_rail_uv_material(self) -> bpy.types.Material:
        return get_ptrprop_resolver(self.__mAssocScene).rail_uv_material
    def draw_rail_uv_material(self, layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(self.__mAssocScene), 'rail_uv_material')

    def get_export_collection(self) -> bpy.types.Collection:
        return get_ptrprop_resolver(self.__mAssocScene).export_collection
    def draw_export_collection(self, layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(self.__mAssocScene), 'export_collection')

    def get_export_object(self) -> bpy.types.Object:
        return get_ptrprop_resolver(self.__mAssocScene).export_object
    def draw_export_object(self, layout: bpy.types.UILayout) -> None:
        layout.prop(get_ptrprop_resolver(self.__mAssocScene), 'export_object')

    def get_ioport_encodings(self) -> tuple[str, ...]:
        encodings = get_ioport_encodings(self.__mAssocScene)
        return tuple(i.encoding for i in encodings)
    def draw_ioport_encodings(self, layout: bpy.types.UILayout) -> None:
        target = get_ptrprop_resolver(self.__mAssocScene)
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

@bpy.app.handlers.persistent
def _ioport_encodings_initializer(file_path: str):
    # if we can fetch property, and it is empty after loading file
    # we fill it with default value
    encodings = get_ioport_encodings(bpy.context.scene)
    if len(encodings) == 0:
        for default_enc in UTIL_virtools_types.g_PyBMapDefaultEncodings:
            item = encodings.add()
            item.encoding = default_enc

def register() -> None:
    bpy.utils.register_class(BBP_PG_bmap_encoding)
    bpy.utils.register_class(BBP_UL_bmap_encoding)
    bpy.utils.register_class(BBP_PG_ptrprop_resolver)

    # register ioport encodings default value
    bpy.app.handlers.load_post.append(_ioport_encodings_initializer)

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

    # unregister ioport encodings default value
    bpy.app.handlers.load_post.remove(_ioport_encodings_initializer)

    bpy.utils.unregister_class(BBP_PG_ptrprop_resolver)
    bpy.utils.unregister_class(BBP_UL_bmap_encoding)
    bpy.utils.unregister_class(BBP_PG_bmap_encoding)
