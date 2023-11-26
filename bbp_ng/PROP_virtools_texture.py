import bpy
import typing
from . import UTIL_virtools_types, UTIL_functions

#region Virtools Texture Annotation Data

g_Annotation_CK_TEXTURE_SAVEOPTIONS: dict[int, UTIL_virtools_types.EnumAnnotation] = {
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA.value: UTIL_virtools_types.EnumAnnotation("Raw Data", "Save raw data inside file. The bitmap is saved in a raw 32 bit per pixel format. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL.value: UTIL_virtools_types.EnumAnnotation("External", "Store only the file name for the texture. The bitmap file must be present in the bitmap paths when loading the composition. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_IMAGEFORMAT.value: UTIL_virtools_types.EnumAnnotation("Image Format", "Save using format specified. The bitmap data will be converted to the specified format by the correspondant bitmap plugin and saved inside file. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_USEGLOBAL.value: UTIL_virtools_types.EnumAnnotation("Use Global", "Use Global settings, that is the settings given with CKContext::SetGlobalImagesSaveOptions. (Not valid when using CKContext::SetImagesSaveOptions). "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_INCLUDEORIGINALFILE.value: UTIL_virtools_types.EnumAnnotation("Include Original File", "Insert original image file inside CMO file. The bitmap file that was used originally for the texture or sprite will be append to the composition file and extracted when the file is loaded. "),
}

g_Annotation_VX_PIXELFORMAT: dict[int, UTIL_virtools_types.EnumAnnotation] = {
    UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888.value: UTIL_virtools_types.EnumAnnotation("32 Bits ARGB8888", "32-bit ARGB pixel format with alpha "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_RGB888.value: UTIL_virtools_types.EnumAnnotation("32 Bits RGB888", "32-bit RGB pixel format without alpha "),
    UTIL_virtools_types.VX_PIXELFORMAT._24_RGB888.value: UTIL_virtools_types.EnumAnnotation("24 Bits RGB888", "24-bit RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_RGB565.value: UTIL_virtools_types.EnumAnnotation("16 Bits RGB565", "16-bit RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_RGB555.value: UTIL_virtools_types.EnumAnnotation("16 Bits RGB555", "16-bit RGB pixel format (5 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB1555.value: UTIL_virtools_types.EnumAnnotation("16 Bits ARGB1555", "16-bit ARGB pixel format (5 bits per color + 1 bit for alpha) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB4444.value: UTIL_virtools_types.EnumAnnotation("16 Bits ARGB4444", "16-bit ARGB pixel format (4 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_RGB332.value: UTIL_virtools_types.EnumAnnotation("8 Bits RGB332", "8-bit  RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ARGB2222.value: UTIL_virtools_types.EnumAnnotation("8 Bits ARGB2222", "8-bit  ARGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_ABGR8888.value: UTIL_virtools_types.EnumAnnotation("32 Bits ABGR8888", "32-bit ABGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_RGBA8888.value: UTIL_virtools_types.EnumAnnotation("32 Bits RGBA8888", "32-bit RGBA pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_BGRA8888.value: UTIL_virtools_types.EnumAnnotation("32 Bits BGRA8888", "32-bit BGRA pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_BGR888.value: UTIL_virtools_types.EnumAnnotation("32 Bits BGR888", "32-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._24_BGR888.value: UTIL_virtools_types.EnumAnnotation("24 Bits BGR888", "24-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_BGR565.value: UTIL_virtools_types.EnumAnnotation("16 Bits BGR565", "16-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_BGR555.value: UTIL_virtools_types.EnumAnnotation("16 Bits BGR555", "16-bit BGR pixel format (5 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ABGR1555.value: UTIL_virtools_types.EnumAnnotation("16 Bits ABGR1555", "16-bit ABGR pixel format (5 bits per color + 1 bit for alpha) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ABGR4444.value: UTIL_virtools_types.EnumAnnotation("16 Bits ABGR4444", "16-bit ABGR pixel format (4 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT1.value: UTIL_virtools_types.EnumAnnotation("DXT1", "S3/DirectX Texture Compression 1 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT2.value: UTIL_virtools_types.EnumAnnotation("DXT2", "S3/DirectX Texture Compression 2 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT3.value: UTIL_virtools_types.EnumAnnotation("DXT3", "S3/DirectX Texture Compression 3 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT4.value: UTIL_virtools_types.EnumAnnotation("DXT4", "S3/DirectX Texture Compression 4 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT5.value: UTIL_virtools_types.EnumAnnotation("DXT5", "S3/DirectX Texture Compression 5 "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_V8U8.value: UTIL_virtools_types.EnumAnnotation("16 Bits V8U8", "16-bit Bump Map format format (8 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_V16U16.value: UTIL_virtools_types.EnumAnnotation("32 Bits V16U16", "32-bit Bump Map format format (16 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_L6V5U5.value: UTIL_virtools_types.EnumAnnotation("16 Bits L6V5U5", "16-bit Bump Map format format with luminance "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_X8L8V8U8.value: UTIL_virtools_types.EnumAnnotation("32 Bits X8L8V8U8", "32-bit Bump Map format format with luminance "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ABGR8888_CLUT.value: UTIL_virtools_types.EnumAnnotation("8 Bits ABGR8888 CLUT", "8 bits indexed CLUT (ABGR) "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ARGB8888_CLUT.value: UTIL_virtools_types.EnumAnnotation("8 Bits ARGB8888 CLUT", "8 bits indexed CLUT (ARGB) "),
    UTIL_virtools_types.VX_PIXELFORMAT._4_ABGR8888_CLUT.value: UTIL_virtools_types.EnumAnnotation("4 Bits ABGR8888 CLUT", "4 bits indexed CLUT (ABGR) "),
    UTIL_virtools_types.VX_PIXELFORMAT._4_ARGB8888_CLUT.value: UTIL_virtools_types.EnumAnnotation("4 Bits ARGB8888 CLUT", "4 bits indexed CLUT (ARGB) "),
}

#endregion

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
            g_Annotation_CK_TEXTURE_SAVEOPTIONS
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsTexture.cDefaultSaveOptions)
    )
    
    video_format: bpy.props.EnumProperty(
        name = "Video Format",
        description = "The desired surface pixel format in video memory.",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VX_PIXELFORMAT,
            g_Annotation_VX_PIXELFORMAT
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
