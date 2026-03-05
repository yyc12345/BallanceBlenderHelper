import bpy
import typing, enum
from . import UTIL_functions, UTIL_blender_mesh, UTIL_virtools_types

# Raw Data

class RawVirtoolsMesh():
    # Instance Member Declarations
    mLitMode: UTIL_virtools_types.VXMESH_LITMODE
    # Default Value Declarations
    cDefaultLitMode: typing.ClassVar[UTIL_virtools_types.VXMESH_LITMODE] = UTIL_virtools_types.VXMESH_LITMODE.VX_LITMESH

    def __init__(self, **kwargs):
        # assign default value for each component
        self.mLitMode = kwargs.get('mLitMode', RawVirtoolsMesh.cDefaultLitMode)

# blender enum prop helper defines
_g_Helper_VXMESH_LITMODE = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.VXMESH_LITMODE)

# Blender Property Group

class BBP_PG_virtools_mesh(bpy.types.PropertyGroup):
    lit_mode: bpy.props.EnumProperty(
        name = "Lit Mode",
        description = "Lighting mode of the mesh.",
        items = _g_Helper_VXMESH_LITMODE.generate_items(),
        default = _g_Helper_VXMESH_LITMODE.to_selection(RawVirtoolsMesh.cDefaultLitMode),
        translation_context = 'BBP_PG_virtools_mesh/property'
    ) # type: ignore
    
# Getter Setter

CanToMesh = bpy.types.Mesh | bpy.types.Curve | bpy.types.SurfaceCurve | bpy.types.TextCurve | bpy.types.MetaBall

def get_virtools_mesh(meshlike: CanToMesh) -> BBP_PG_virtools_mesh:
    return meshlike.virtools_mesh

def get_raw_virtools_mesh(meshlike: CanToMesh) -> RawVirtoolsMesh:
    props: BBP_PG_virtools_mesh = get_virtools_mesh(meshlike)
    rawdata: RawVirtoolsMesh = RawVirtoolsMesh()

    rawdata.mLitMode = _g_Helper_VXMESH_LITMODE.get_selection(props.lit_mode)

    return rawdata

def set_raw_virtools_mesh(meshlike: CanToMesh, rawdata: RawVirtoolsMesh) -> None:
    props: BBP_PG_virtools_mesh = get_virtools_mesh(meshlike)

    props.lit_mode = _g_Helper_VXMESH_LITMODE.to_selection(rawdata.mLitMode)

# Display Panel

class BBP_PT_virtools_mesh(bpy.types.Panel):
    """Show Virtools Mesh Properties."""
    bl_label = "Virtools Mesh"
    bl_idname = "BBP_PT_virtools_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data" # idk why blender use `data` as the mesh tab.
    bl_translation_context = 'BBP_PT_virtools_mesh'
    
    @classmethod
    def poll(cls, context):
        if context.mesh is not None: return True
        if context.curve is not None: return True
        if context.meta_ball is not None: return True
        return False
    
    def draw(self, context):
        # get layout
        layout = self.layout
        # get target
        datablock: typing.Any
        if context.mesh is not None: datablock = context.mesh
        elif context.curve is not None: datablock = context.curve
        elif context.meta_ball is not None: datablock = context.meta_ball
        else: datablock = None
        # get mesh properties
        props: BBP_PG_virtools_mesh = get_virtools_mesh(datablock)

        # draw data
        layout.prop(props, 'lit_mode')

# Register

def register() -> None:
    bpy.utils.register_class(BBP_PG_virtools_mesh)
    bpy.utils.register_class(BBP_PT_virtools_mesh)

    # Add metadata into mesh-like data block.
    # according to TemporaryMesh, we need add it into:
    # mesh, curve, surface, font, and metaball.
    bpy.types.Mesh.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)
    bpy.types.Curve.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)
    bpy.types.SurfaceCurve.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)
    bpy.types.TextCurve.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)
    bpy.types.MetaBall.virtools_mesh = bpy.props.PointerProperty(type = BBP_PG_virtools_mesh)

def unregister() -> None:
    # remove from metadata
    del bpy.types.MetaBall.virtools_mesh
    del bpy.types.TextCurve.virtools_mesh
    del bpy.types.SurfaceCurve.virtools_mesh
    del bpy.types.Curve.virtools_mesh
    del bpy.types.Mesh.virtools_mesh

    bpy.utils.unregister_class(BBP_PT_virtools_mesh)
    bpy.utils.unregister_class(BBP_PG_virtools_mesh)

