import bpy
import typing, enum
from . import UTIL_functions, UTIL_virtools_types

# Annotation

g_Annotation_VXMESH_LITMODE: dict[int, UTIL_virtools_types.EnumAnnotation] = {
    UTIL_virtools_types.VXMESH_LITMODE.VX_PRELITMESH.value: UTIL_virtools_types.EnumAnnotation("Prelit", "Lighting use color information store with vertices "),
    UTIL_virtools_types.VXMESH_LITMODE.VX_LITMESH.value: UTIL_virtools_types.EnumAnnotation("Lit", "Lighting is done by renderer using normals and face material information. "),
}

# Raw Data

class RawVirtoolsMesh():
    # Instance Member Declarations
    mLitMode: UTIL_virtools_types.VXMESH_LITMODE
    # Default Value Declarations
    cDefaultLitMode: typing.ClassVar[UTIL_virtools_types.VXMESH_LITMODE] = UTIL_virtools_types.VXMESH_LITMODE.VX_LITMESH

    def __init__(self, **kwargs):
        # assign default value for each component
        self.mLitMode = kwargs.get('mLitMode', RawVirtoolsMesh.cDefaultLitMode)

# Blender Property Group

class BBP_PG_virtools_mesh(bpy.types.PropertyGroup):
    lit_mode: bpy.props.EnumProperty(
        name = "Lit Mode",
        description = "Lighting mode of the mesh.",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXMESH_LITMODE,
            g_Annotation_VXMESH_LITMODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMesh.cDefaultLitMode)
    )
    
# Getter Setter

def get_virtools_mesh(mesh: bpy.types.Mesh) -> BBP_PG_virtools_mesh:
    return mesh.virtools_mesh

def get_raw_virtools_mesh(mesh: bpy.types.Mesh) -> RawVirtoolsMesh:
    props: BBP_PG_virtools_mesh = get_virtools_mesh(mesh)
    rawdata: RawVirtoolsMesh = RawVirtoolsMesh()

    rawdata.mLitMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXMESH_LITMODE, props.lit_mode)

    return rawdata

def set_raw_virtools_mesh(mesh: bpy.types.Mesh, rawdata: RawVirtoolsMesh) -> None:
    props: BBP_PG_virtools_mesh = get_virtools_mesh(mesh)

    props.lit_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mLitMode)

# Display Panel

class BBP_PT_virtools_mesh(bpy.types.Panel):
    """Show Virtools Mesh Properties."""
    bl_label = "Virtools Mesh"
    bl_idname = "BBP_PT_virtools_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data" # idk why blender use `data` as the mesh tab.
    
    @classmethod
    def poll(cls, context):
        return context.mesh is not None
    
    def draw(self, context):
        # get layout and target
        layout = self.layout
        props: BBP_PG_virtools_mesh = get_virtools_mesh(context.mesh)

        # draw data
        layout.prop(props, 'lit_mode')

# Register

def register():
    bpy.utils.register_class(BBP_PG_virtools_mesh)
    bpy.utils.register_class(BBP_PT_virtools_mesh)

    # add into mesh metadata
    bpy.types.Mesh.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)

def unregister():
    # remove from metadata
    del bpy.types.Mesh.virtools_mesh

    bpy.utils.unregister_class(BBP_PT_virtools_mesh)
    bpy.utils.unregister_class(BBP_PG_virtools_mesh)

