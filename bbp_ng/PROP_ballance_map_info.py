import bpy
import typing
from . import UTIL_functions

class RawBallanceMapInfo():
    cSectorCount: typing.ClassVar[int] = 1

    mSectorCount: int

    def __init__(self, **kwargs):
        self.mSectorCount = kwargs.get("mSectorCount", RawBallanceMapInfo.cSectorCount)

    def regulate(self):
        self.mSectorCount = UTIL_functions.clamp_int(self.mSectorCount, 1, 999)

#region Prop Decl & Getter Setter

class BBP_PG_ballance_map_info(bpy.types.PropertyGroup):
    sector_count: bpy.props.IntProperty(
        name = "Sector",
        description = "The sector count of this Ballance map which is used in exporting map and may be changed when importing map.",
        default = 1,
        max = 999, min = 1,
        soft_max = 8, soft_min = 1,
        step = 1
    ) # type: ignore
    
def get_ballance_map_info(scene: bpy.types.Scene) -> BBP_PG_ballance_map_info:
    return scene.ballance_map_info

def get_raw_ballance_map_info(scene: bpy.types.Scene) -> RawBallanceMapInfo:
    props: BBP_PG_ballance_map_info = get_ballance_map_info(scene)
    rawdata: RawBallanceMapInfo = RawBallanceMapInfo()

    rawdata.mSectorCount = props.sector_count

    rawdata.regulate()
    return rawdata

def set_raw_ballance_map_info(scene: bpy.types.Scene, rawdata: RawBallanceMapInfo) -> None:
    props: BBP_PG_ballance_map_info = get_ballance_map_info(scene)

    props.sector_count = rawdata.mSectorCount

#endregion

class BBP_PT_ballance_map_info(bpy.types.Panel):
    """Show Ballance Map Infos."""
    bl_label = "Ballance Map"
    bl_idname = "BBP_PT_ballance_map_info"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        target: bpy.types.Scene = context.scene
        props: BBP_PG_ballance_map_info = get_ballance_map_info(target)

        # show map sector count numberbox
        layout.prop(props, 'sector_count')

def register() -> None:
    # register
    bpy.utils.register_class(BBP_PG_ballance_map_info)
    bpy.utils.register_class(BBP_PT_ballance_map_info)

    # add into scene metadata
    bpy.types.Scene.ballance_map_info = bpy.props.PointerProperty(type = BBP_PG_ballance_map_info)

def unregister() -> None:
    # del from scene metadata
    del bpy.types.Scene.ballance_map_info

    # unregister
    bpy.utils.unregister_class(BBP_PG_ballance_map_info)
    bpy.utils.unregister_class(BBP_PT_ballance_map_info)
