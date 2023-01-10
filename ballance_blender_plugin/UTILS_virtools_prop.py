import bpy
from . import UTILS_constants, UTILS_functions

class BALLANCE_PG_virtools_material(bpy.types.PropertyGroup):
    enable_virtools_material: bpy.props.BoolProperty(
        name="Enable Virtools Material",
        default=False,
    )

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

    alpha_test: bpy.props.BoolProperty(
        name="Alpha Test",
        description="Alpha Func: VXCMP_GREATER. Alpha Ref: 1.",
        default=False,
    )

    alpha_blend: bpy.props.BoolProperty(
        name="Alpha Blend",
        description="Source Blend: VXBLEND_SRCALPHA. Dest Blend: VXBLEND_INVSRCALPHA.",
        default=False,
    )

    z_buffer: bpy.props.BoolProperty(
        name="Z Buffer",
        description="ZFunc: VXCMP_LESSEQUAL.",
        default=True,
    )

    two_sided: bpy.props.BoolProperty(
        name="Two Sided",
        default=False,
    )

    texture: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Texture",
        description="The texture used for Virtools material"
    )

class BALLANCE_PG_virtools_group(bpy.types.PropertyGroup):
    group_name: bpy.props.StringProperty(
        name="Group Name",
        default=""
    )

class common_group_name_props(bpy.types.Operator):
    group_name_source: bpy.props.EnumProperty(
        name="Group Name Source",
        items=(('DEFINED', "Predefined", "Pre-defined group name."),
               ('CUSTOM', "Custom", "User specified group name."),
               ),
    )

    group_name: bpy.props.EnumProperty(
        name="Group Name",
        description="Pick vanilla Ballance group name.",
        items=tuple((x, x, "") for x in UTILS_constants.propsVtGroups_availableGroups),
    )

    custom_group_name: bpy.props.StringProperty(
        name="Custom Group Name",
        description="Input your custom group name.",
        default="",
    )

    def parent_draw(self, parent_layout):
        parent_layout.prop(self, 'group_name_source', expand=True)
        if (self.group_name_source == 'CUSTOM'):
            parent_layout.prop(self, 'custom_group_name')
        else:
            parent_layout.prop(self, 'group_name') # do not translate group name. it's weird

    def get_group_name_string(self):
        return str(self.custom_group_name if self.group_name_source == 'CUSTOM' else self.group_name)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def get_virtools_material(mtl):
    return mtl.virtools_material

def get_virtools_material_data(mtl):
    data = get_virtools_material(mtl)
    return (
        data.enable_virtools_material,
        data.ambient, 
        data.diffuse, 
        data.specular, 
        data.emissive, 
        data.specular_power, 
        data.alpha_test,
        data.alpha_blend,
        data.z_buffer,
        data.two_sided,
        data.texture
    )

def set_virtools_material_data(mtl, packed_data):
    data = get_virtools_material(mtl)
    # packed_data have the same order with the return value of `get_virtools_material_data`
    (data.enable_virtools_material,
    data.ambient, data.diffuse, data.specular, data.emissive, data.specular_power,
    data.alpha_test, data.alpha_blend, data.z_buffer, data.two_sided,
    data.texture) = packed_data

def get_active_virtools_group(obj):
    return obj.active_virtools_group
def get_virtools_group(obj):
    return obj.virtools_group

def check_virtools_group_data(obj, probe):
    for item in get_virtools_group(obj):
        if probe == str(item.group_name):
            return True

    return False

def add_virtools_group_data(obj, new_data):
    # check exist
    if check_virtools_group_data(obj, new_data):
        # existed, give up
        return False

    # "add" do not need operate active_virtools_group
    data = get_virtools_group(obj)
    it = data.add()
    it.name = ""
    it.group_name = new_data

    return True

def remove_virtools_group_data(obj, rm_data):
    gp = get_virtools_group(obj)
    active_gp = get_active_virtools_group(obj)

    for idx, item in enumerate(gp):
        if rm_data == str(item.group_name):
            # decrease active group if removed item is ahead of active group
            if idx <= active_gp:
                active_gp -= 1
            # remove
            gp.remove(idx)
            # indicate success
            return True

    return False

def remove_virtools_group_data_by_index(obj, rm_idx):
    gp = get_virtools_group(obj)
    active_gp = get_active_virtools_group(obj)

    # report error
    if rm_idx >= len(gp):
        return False

    # remove
    if rm_idx <= active_gp:
        active_gp -= 1
    gp.remove(rm_idx)
    return True

def clear_virtools_group_data(obj):
    gp = get_virtools_group(obj)
    active_gp = get_active_virtools_group(obj)

    gp.clear()
    active_gp = 0

def fill_virtools_group_data(obj, data_list):
    # clear first
    clear_virtools_group_data(obj)

    # if no data to add, return
    if data_list is None:
        return

    # add one by one after check duplication
    data = get_virtools_group(obj)
    for item in set(data_list):
        it = data.add()
        it.name = ""
        it.group_name = item

def get_virtools_group_data(obj):
    return tuple(str(item.group_name) for item in get_virtools_group(obj))

def register_props():
    bpy.types.Object.virtools_group = bpy.props.CollectionProperty(type=BALLANCE_PG_virtools_group)
    bpy.types.Object.active_virtools_group = bpy.props.IntProperty()
    bpy.types.Material.virtools_material = bpy.props.PointerProperty(type=BALLANCE_PG_virtools_material)

def unregister_props():
    del bpy.types.Material.virtools_material
    del bpy.types.Object.virtools_group
    del bpy.types.Object.active_virtools_group


