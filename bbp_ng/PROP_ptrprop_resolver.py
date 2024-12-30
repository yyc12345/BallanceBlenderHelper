import bpy

## Intent
#  Operator is not allowed to register Pointer Properties.
#  The solution is register pointer properties in Scene and reference it when drawing operator window.
#  This module contains all pointer properties used by other operators.

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

def get_ptrprop_resolver() -> BBP_PG_ptrprop_resolver:
    return bpy.context.scene.bbp_ptrprop_resolver

def get_rail_uv_material() -> bpy.types.Material:
    return get_ptrprop_resolver().rail_uv_material
def draw_rail_uv_material(layout: bpy.types.UILayout) -> None:
    layout.prop(get_ptrprop_resolver(), 'rail_uv_material')

def get_export_collection() -> bpy.types.Collection:
    return get_ptrprop_resolver().export_collection
def draw_export_collection(layout: bpy.types.UILayout) -> None:
    layout.prop(get_ptrprop_resolver(), 'export_collection')

def get_export_object() -> bpy.types.Object:
    return get_ptrprop_resolver().export_object
def draw_export_object(layout: bpy.types.UILayout) -> None:
    layout.prop(get_ptrprop_resolver(), 'export_object')

def register() -> None:
    bpy.utils.register_class(BBP_PG_ptrprop_resolver)
    bpy.types.Scene.bbp_ptrprop_resolver = bpy.props.PointerProperty(type = BBP_PG_ptrprop_resolver)

def unregister() -> None:
    del bpy.types.Scene.bbp_ptrprop_resolver
    bpy.utils.unregister_class(BBP_PG_ptrprop_resolver)
