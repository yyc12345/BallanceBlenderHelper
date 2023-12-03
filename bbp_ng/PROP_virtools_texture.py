import bpy
import typing
from . import UTIL_virtools_types, UTIL_functions

class RawVirtoolsTexture():
    
    # Instance Member Declarations
    
    mSaveOptions: UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS
    mVideoFormat: UTIL_virtools_types.VX_PIXELFORMAT

    # Default Value Declarations
    
    cDefaultSaveOptions: typing.ClassVar[UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS] = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA
    cDefaultVideoFormat: typing.ClassVar[UTIL_virtools_types.VX_PIXELFORMAT] = UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB1555

    def __init__(self, **kwargs):
        # assign default value for each component
        self.mSaveOptions = kwargs.get('mSaveOptions', RawVirtoolsTexture.cDefaultSaveOptions)
        self.mVideoFormat = kwargs.get('mVideoFormat', RawVirtoolsTexture.cDefaultVideoFormat)
    
class BBP_PG_virtools_texture(bpy.types.PropertyGroup):

    save_options: bpy.props.EnumProperty(
        name = "Save Options",
        description = "When saving a composition textures or sprites can be kept as reference to external files or converted to a given format and saved inside the composition file.",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS,
            UTIL_virtools_types.g_Annotation_CK_TEXTURE_SAVEOPTIONS
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsTexture.cDefaultSaveOptions)
    )
    
    video_format: bpy.props.EnumProperty(
        name = "Video Format",
        description = "The desired surface pixel format in video memory.",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VX_PIXELFORMAT,
            UTIL_virtools_types.g_Annotation_VX_PIXELFORMAT
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsTexture.cDefaultVideoFormat)
    )
    
#region Virtools Texture Getter Setter

def get_virtools_texture(img: bpy.types.Image) -> BBP_PG_virtools_texture:
    return img.virtools_texture

def get_raw_virtools_texture(img: bpy.types.Image) -> RawVirtoolsTexture:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    rawdata: RawVirtoolsTexture = RawVirtoolsTexture()
    
    rawdata.mSaveOptions = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS, props.save_options)
    rawdata.mVideoFormat = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VX_PIXELFORMAT, props.video_format)
    return rawdata

def set_raw_virtools_texture(img: bpy.types.Image, rawdata: RawVirtoolsTexture) -> None:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    
    props.save_options = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mSaveOptions)
    props.video_format = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mVideoFormat)

#endregion

#region Virtools Texture Drawer

"""!
@remark
Because Image do not have its unique properties window
so we only can draw virtools texture properties in other window
we provide various function to help draw property.
"""

def draw_virtools_texture(img: bpy.types.Image, layout: bpy.types.UILayout):
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    
    layout.prop(props, 'save_options')
    layout.prop(props, 'video_format')

#endregion

def register():
    bpy.utils.register_class(BBP_PG_virtools_texture)
    
    # add into image metadata
    bpy.types.Image.virtools_texture = bpy.props.PointerProperty(type = BBP_PG_virtools_texture)

def unregister():
    # del from image metadata
    del bpy.types.Image.virtools_texture

    bpy.utils.unregister_class(BBP_PG_virtools_texture)
