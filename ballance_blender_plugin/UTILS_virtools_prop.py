import bpy
from . import UTILS_constants, UTILS_functions

class BALLANCE_PG_virtools_material(bpy.types.PropertyGroup):
    ambient: bpy.props.FloatVectorProperty(name="Ambient", 
                                subtype='COLOR',
                                min=0.0,
                                max=1.0,
                                default=[0.0,0.0,0.0])

    diffuse: bpy.props.FloatVectorProperty(name="Diffuse", 
                                subtype='COLOR', 
                                min=0.0,
                                max=1.0,
                                default=[0.0,0.0,0.0])

    specular: bpy.props.FloatVectorProperty(name="Specular", 
                                subtype='COLOR', 
                                min=0.0,
                                max=1.0,
                                default=[0.0,0.0,0.0])

    emissive: bpy.props.FloatVectorProperty(name="Emissive", 
                                subtype='COLOR', 
                                min=0.0,
                                max=1.0,
                                default=[0.0,0.0,0.0])

    specular_power: bpy.props.FloatProperty(
        name="Specular Power",
        min=0.0,
        max=100.0,
        default=0.0,
    )

class BALLANCE_PG_virtools_group(bpy.types.PropertyGroup):
    group_name: bpy.props.StringProperty(
        name="Group Name",
        default=""
    )

def get_virtools_material(mtl):
    return mtl.virtools_material

def get_virtools_material_data(mtl):
    data = get_virtools_material(mtl)
    return (data.ambient, data.diffuse, data.specular, data.emissive, data.specular_power)

def set_virtools_material_data(mtl, ambient, diffuse, specular, emissive, specular_power):
    data = get_virtools_material(mtl)
    data.ambient = ambient
    data.diffuse = diffuse
    data.specular = specular
    data.emissive = emissive
    data.specular_power = specular_power

def get_virtools_group(obj):
    return obj.virtools_group

def get_virtools_group_data(obj):
    return tuple(str(item.group_name) for item in get_virtools_group(obj))

def set_virtools_group_data(obj, new_data):
    data = get_virtools_group(obj)
    data.clear()

    for item in new_data:
        it = data.add()
        it.name = ""
        it.group_name = item

def register_props():
    bpy.types.Object.virtools_group = bpy.props.CollectionProperty(type=BALLANCE_PG_virtools_group)
    bpy.types.Object.active_virtools_group = bpy.props.IntProperty()
    bpy.types.Material.virtools_material = bpy.props.PointerProperty(type=BALLANCE_PG_virtools_material)

def unregister_props():
    del bpy.types.Material.virtools_material
    del bpy.types.Object.virtools_group
    del bpy.types.Object.active_virtools_group


