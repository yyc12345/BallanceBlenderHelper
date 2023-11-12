import bpy, bpy_extras
import typing, os
from . import PROP_preferences, UTIL_virtools_types, UTIL_functions

#region Virtools Texture Annotation Data

from .UTIL_functions import AnnotationData

g_Annotation_CK_TEXTURE_SAVEOPTIONS: dict[int, AnnotationData] = {
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA.value: AnnotationData("Raw Data", "Save raw data inside file. The bitmap is saved in a raw 32 bit per pixel format. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL.value: AnnotationData("External", "Store only the file name for the texture. The bitmap file must be present in the bitmap paths when loading the composition. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_IMAGEFORMAT.value: AnnotationData("Image Format", "Save using format specified. The bitmap data will be converted to the specified format by the correspondant bitmap plugin and saved inside file. "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_USEGLOBAL.value: AnnotationData("Use Global", "Use Global settings, that is the settings given with CKContext::SetGlobalImagesSaveOptions. (Not valid when using CKContext::SetImagesSaveOptions). "),
    UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_INCLUDEORIGINALFILE.value: AnnotationData("Include Original File", "Insert original image file inside CMO file. The bitmap file that was used originally for the texture or sprite will be append to the composition file and extracted when the file is loaded. "),
}

g_Annotation_VX_PIXELFORMAT: dict[int, AnnotationData] = {
    UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888.value: AnnotationData("32 Bits ARGB8888", "32-bit ARGB pixel format with alpha "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_RGB888.value: AnnotationData("32 Bits RGB888", "32-bit RGB pixel format without alpha "),
    UTIL_virtools_types.VX_PIXELFORMAT._24_RGB888.value: AnnotationData("24 Bits RGB888", "24-bit RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_RGB565.value: AnnotationData("16 Bits RGB565", "16-bit RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_RGB555.value: AnnotationData("16 Bits RGB555", "16-bit RGB pixel format (5 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB1555.value: AnnotationData("16 Bits ARGB1555", "16-bit ARGB pixel format (5 bits per color + 1 bit for alpha) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB4444.value: AnnotationData("16 Bits ARGB4444", "16-bit ARGB pixel format (4 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_RGB332.value: AnnotationData("8 Bits RGB332", "8-bit  RGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ARGB2222.value: AnnotationData("8 Bits ARGB2222", "8-bit  ARGB pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_ABGR8888.value: AnnotationData("32 Bits ABGR8888", "32-bit ABGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_RGBA8888.value: AnnotationData("32 Bits RGBA8888", "32-bit RGBA pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_BGRA8888.value: AnnotationData("32 Bits BGRA8888", "32-bit BGRA pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_BGR888.value: AnnotationData("32 Bits BGR888", "32-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._24_BGR888.value: AnnotationData("24 Bits BGR888", "24-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_BGR565.value: AnnotationData("16 Bits BGR565", "16-bit BGR pixel format "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_BGR555.value: AnnotationData("16 Bits BGR555", "16-bit BGR pixel format (5 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ABGR1555.value: AnnotationData("16 Bits ABGR1555", "16-bit ABGR pixel format (5 bits per color + 1 bit for alpha) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_ABGR4444.value: AnnotationData("16 Bits ABGR4444", "16-bit ABGR pixel format (4 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT1.value: AnnotationData("DXT1", "S3/DirectX Texture Compression 1 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT2.value: AnnotationData("DXT2", "S3/DirectX Texture Compression 2 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT3.value: AnnotationData("DXT3", "S3/DirectX Texture Compression 3 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT4.value: AnnotationData("DXT4", "S3/DirectX Texture Compression 4 "),
    UTIL_virtools_types.VX_PIXELFORMAT._DXT5.value: AnnotationData("DXT5", "S3/DirectX Texture Compression 5 "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_V8U8.value: AnnotationData("16 Bits V8U8", "16-bit Bump Map format format (8 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_V16U16.value: AnnotationData("32 Bits V16U16", "32-bit Bump Map format format (16 bits per color) "),
    UTIL_virtools_types.VX_PIXELFORMAT._16_L6V5U5.value: AnnotationData("16 Bits L6V5U5", "16-bit Bump Map format format with luminance "),
    UTIL_virtools_types.VX_PIXELFORMAT._32_X8L8V8U8.value: AnnotationData("32 Bits X8L8V8U8", "32-bit Bump Map format format with luminance "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ABGR8888_CLUT.value: AnnotationData("8 Bits ABGR8888 CLUT", "8 bits indexed CLUT (ABGR) "),
    UTIL_virtools_types.VX_PIXELFORMAT._8_ARGB8888_CLUT.value: AnnotationData("8 Bits ARGB8888 CLUT", "8 bits indexed CLUT (ARGB) "),
    UTIL_virtools_types.VX_PIXELFORMAT._4_ABGR8888_CLUT.value: AnnotationData("4 Bits ABGR8888 CLUT", "4 bits indexed CLUT (ABGR) "),
    UTIL_virtools_types.VX_PIXELFORMAT._4_ARGB8888_CLUT.value: AnnotationData("4 Bits ARGB8888 CLUT", "4 bits indexed CLUT (ARGB) "),
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
        items = UTIL_functions.generate_vt_enums_for_bl_enumprop(
            UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS,
            g_Annotation_CK_TEXTURE_SAVEOPTIONS
        ),
        default = RawVirtoolsTexture.cDefaultSaveOptions.value
    )
    
    video_format: bpy.props.EnumProperty(
        name = "Video Format",
        description = "The desired surface pixel format in video memory.",
        items = UTIL_functions.generate_vt_enums_for_bl_enumprop(
            UTIL_virtools_types.VX_PIXELFORMAT,
            g_Annotation_VX_PIXELFORMAT
        ),
        default = RawVirtoolsTexture.cDefaultVideoFormat.value
    )
    
#region Virtools Texture Getter Setter

def get_virtools_texture(img: bpy.types.Image) -> BBP_PG_virtools_texture:
    return img.virtools_texture

def get_raw_virtools_texture(img: bpy.types.Image) -> RawVirtoolsTexture:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    rawdata: RawVirtoolsTexture = RawVirtoolsTexture()
    
    rawdata.cDefaultSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS(int(props.save_options))
    rawdata.mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT(int(props.video_format))
    return rawdata

def set_raw_virtools_texture(img: bpy.types.Image, rawdata: RawVirtoolsTexture) -> None:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    
    props.save_options = str(rawdata.mSaveOptions.value)
    props.video_format = str(rawdata.mVideoFormat.value)

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

## Ballance Texture Usage
#  The aim of this module is to make sure every Ballance texture only have 1 instance in Blender as much as we can 
#  (it mean that if user force to add multiple textures, we can not stop them)
#  
#  All image loading and saving operation should be operated via this module, no matter what your are loading is or is not Ballance textures.
#  This module provide a universal way to check whether texture is a part of Ballance textures and use different strategy to load them.
#  
#  The loading and saving of textures frequently happend when importing or exporting, there is 2 example about them.
#  ```
#  # bmx loading example
#  bmx_texture = blabla()
#  if bmx_texture.is_external(): 
#      tex = PROP_virtools_texture.load_ballance_texture(bmx_texture.filename)
#  else: 
#      tex = PROP_virtools_texture.load_other_texture(os.path.join(tempfolder, 'Textures', bmx_texture.filename))
#  texture_process(tex) # process loaded texture
#  
#  # nmo loading example
#  vt_texture = blabla()
#  place_to_load = ""
#  if vt_texture.is_raw_data(): 
#      place_to_load = allocate_place()
#      save_vt_raw_data_texture(vt_texture, place_to_load)
#  if vt_texture.is_original_file() or vt_texture.is_external():
#      place_to_load = vt_texture.filename
#  
#  try_filename = PROP_virtools_texture.get_ballance_texture_filename(place_to_load)
#  if try_filename:
#      # load as ballance texture
#      tex = PROP_virtools_texture.load_ballance_texture(try_filename)
#  else:
#      # load as other texture
#      tex = PROP_virtools_texture.load_other_texture(place_to_load)
#  texture_process(tex) # process loaded texture
#  
#  ```
#  
#  ```
#  # bmx saving example
#  tex: bpy.types.Image = texture_getter()
#  try_filename = PROP_virtools_texture.get_ballance_texture_filename(
#      PROP_virtools_texture.get_texture_filepath(tex))
#  if try_filename:
#      write_external_filename(try_filename)
#  else:
#      realpath = PROP_virtools_texture.generate_other_texture_save_path(tex, tempfolder)
#      PROP_virtools_texture.save_other_texture(tex, realpath)
#      write_filename(realpath)
#  
#  ```

#region Ballance Texture Assist Functions

def _get_ballance_texture_folder() -> str:
    """!
    Get Ballance texture folder from preferences.

    @exception BBPException Ballance texture folder is not set in preferences

    @return The path to Ballance texture folder.
    """

    pref: PROP_preferences.RawPreferences = PROP_preferences.get_raw_preferences()
    if not pref.has_valid_blc_tex_folder():
        raise UTIL_functions.BBPException("No valid Ballance texture folder in preferences.")
    
    return pref.mBallanceTextureFolder

def _is_path_equal(path1: str, path2: str) -> bool:
    """!
    Check whether 2 path are equal.

    The checker will call os.path.normcase and os.path.normpath in series to regulate the give path.

    @param path1[in] The given absolute path 1
    @param path2[in] The given absolute path 2
    @return True if equal.
    """

    return os.path.normpath(os.path.normcase(path1)) == os.path.normpath(os.path.normcase(path2))

#endregion

#region Ballance Texture Detect Functions

g_OpaqueBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB1555,
)
g_TransparentBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888,
)
g_NonBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888,
)

## The preset collection of all Ballance texture.
#  Key is texture name and can be used as file name checking.
#  Value is its preset which can be assigned.
g_BallanceTexturePresets: dict[str, RawVirtoolsTexture] = {
    # "atari.avi": g_TransparentBallanceTexturePreset,
    "atari.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere1.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere2.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere3.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_Paper.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_Stone.bmp": g_OpaqueBallanceTexturePreset,
    "Ball_Wood.bmp": g_OpaqueBallanceTexturePreset,
    "Brick.bmp": g_OpaqueBallanceTexturePreset,
    "Button01_deselect.tga": g_TransparentBallanceTexturePreset,
    "Button01_select.tga": g_TransparentBallanceTexturePreset,
    "Button01_special.tga": g_TransparentBallanceTexturePreset,
    "Column_beige.bmp": g_OpaqueBallanceTexturePreset,
    "Column_beige_fade.tga": g_TransparentBallanceTexturePreset,
    "Column_blue.bmp": g_OpaqueBallanceTexturePreset,
    "Cursor.tga": g_TransparentBallanceTexturePreset,
    "Dome.bmp": g_OpaqueBallanceTexturePreset,
    "DomeEnvironment.bmp": g_OpaqueBallanceTexturePreset,
    "DomeShadow.tga": g_TransparentBallanceTexturePreset,
    "ExtraBall.bmp": g_OpaqueBallanceTexturePreset,
    "ExtraParticle.bmp": g_OpaqueBallanceTexturePreset,
    "E_Holzbeschlag.bmp": g_OpaqueBallanceTexturePreset,
    "FloorGlow.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Side.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_Border.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_Borderless.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_Checkpoint.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_Flat.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_Profil.bmp": g_OpaqueBallanceTexturePreset,
    "Floor_Top_ProfilFlat.bmp": g_OpaqueBallanceTexturePreset,
    "Font_1.tga": g_TransparentBallanceTexturePreset,
    "Gravitylogo_intro.bmp": g_OpaqueBallanceTexturePreset,
    "HardShadow.bmp": g_OpaqueBallanceTexturePreset,
    "Laterne_Glas.bmp": g_OpaqueBallanceTexturePreset,
    "Laterne_Schatten.tga": g_TransparentBallanceTexturePreset,
    "Laterne_Verlauf.tga": g_TransparentBallanceTexturePreset,
    "Logo.bmp": g_OpaqueBallanceTexturePreset,
    "Metal_stained.bmp": g_OpaqueBallanceTexturePreset,
    "Misc_Ufo.bmp": g_OpaqueBallanceTexturePreset,
    "Misc_UFO_Flash.bmp": g_OpaqueBallanceTexturePreset,
    "Modul03_Floor.bmp": g_OpaqueBallanceTexturePreset,
    "Modul03_Wall.bmp": g_OpaqueBallanceTexturePreset,
    "Modul11_13_Wood.bmp": g_OpaqueBallanceTexturePreset,
    "Modul11_Wood.bmp": g_OpaqueBallanceTexturePreset,
    "Modul15.bmp": g_OpaqueBallanceTexturePreset,
    "Modul16.bmp": g_OpaqueBallanceTexturePreset,
    "Modul18.bmp": g_OpaqueBallanceTexturePreset,
    "Modul18_Gitter.tga": g_TransparentBallanceTexturePreset,
    "Modul30_d_Seiten.bmp": g_OpaqueBallanceTexturePreset,
    "Particle_Flames.bmp": g_OpaqueBallanceTexturePreset,
    "Particle_Smoke.bmp": g_OpaqueBallanceTexturePreset,
    "PE_Bal_balloons.bmp": g_OpaqueBallanceTexturePreset,
    "PE_Bal_platform.bmp": g_OpaqueBallanceTexturePreset,
    "PE_Ufo_env.bmp": g_OpaqueBallanceTexturePreset,
    "Pfeil.tga": g_TransparentBallanceTexturePreset,
    "P_Extra_Life_Oil.bmp": g_OpaqueBallanceTexturePreset,
    "P_Extra_Life_Particle.bmp": g_OpaqueBallanceTexturePreset,
    "P_Extra_Life_Shadow.bmp": g_OpaqueBallanceTexturePreset,
    "Rail_Environment.bmp": g_OpaqueBallanceTexturePreset,
    "sandsack.bmp": g_OpaqueBallanceTexturePreset,
    "SkyLayer.bmp": g_OpaqueBallanceTexturePreset,
    "Sky_Vortex.bmp": g_OpaqueBallanceTexturePreset,
    "Stick_Bottom.tga": g_TransparentBallanceTexturePreset,
    "Stick_Stripes.bmp": g_OpaqueBallanceTexturePreset,
    "Target.bmp": g_OpaqueBallanceTexturePreset,
    "Tower_Roof.bmp": g_OpaqueBallanceTexturePreset,
    "Trafo_Environment.bmp": g_OpaqueBallanceTexturePreset,
    "Trafo_FlashField.bmp": g_OpaqueBallanceTexturePreset,
    "Trafo_Shadow_Big.tga": g_TransparentBallanceTexturePreset,
    "Tut_Pfeil01.tga": g_TransparentBallanceTexturePreset,
    "Tut_Pfeil_Hoch.tga": g_TransparentBallanceTexturePreset,
    "Wolken_intro.tga": g_TransparentBallanceTexturePreset,
    "Wood_Metal.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_MetalStripes.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Misc.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Nailed.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Old.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Panel.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Plain.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Plain2.bmp": g_OpaqueBallanceTexturePreset,
    "Wood_Raft.bmp": g_OpaqueBallanceTexturePreset,
}

def get_ballance_texture_filename(texpath: str) -> str | None:
    """!
    Return the filename part for valid Ballance texture path.

    If the file name part of given path is not a entry of Ballance texture file name list, function will return None immediately.
    Otherwise, function will check whether the given file path is really point to the Ballance texture folder.

    @exception BBPException Ballance texture folder is not set in preferences

    @param imgpath[in] Absolute path to texture.
    @return File name part of given texture path if given path is a valid Ballance texture path, or None if the path not point to a valid Ballance texture.
    """
    
    # check file name first
    filename: str = os.path.basename(texpath)
    if filename not in g_BallanceTexturePresets: return None

    # if file name matched, check whether it located in ballance texture folder
    probe: str = os.path.join(_get_ballance_texture_folder(), filename)
    if not _is_path_equal(probe, texpath): return None

    return filename

def is_ballance_texture_filepath(texpath: str) -> bool:
    """!
    Check whether the given path is a valid Ballance texture.

    Simply call get_ballance_texture_filename() and check whether it return string or None.

    @exception BBPException Ballance texture folder is not set in preferences

    @param imgpath[in] Absolute path to texture.
    @return True if it is Ballance texture.
    @see get_ballance_texture_filename
    """
    
    return get_ballance_texture_filename(texpath) is not None

def get_texture_filepath(tex: bpy.types.Image) -> str:
    """!
    Get the file path referenced by the given texture.

    This function will try getting the referenced file path of given texture, including packed or not packed texture.

    This function will try resolving the file path when given texture is packed according to the path of 
    current opend blender file and Ballance texture folder speficied in preferences.

    If resolving failed, it may return blender packed data url, for example `\\./xxx.bmp`

    @exception BBPException Ballance texture folder is not set in preferences

    @param tex[in] The image where the file name need to be got.
    @return The resolved absolute file path.
    """

    # resolve image path
    absfilepath: str = bpy_extras.io_utils.path_reference(
        tex.filepath, bpy.data.filepath, _get_ballance_texture_folder(),
        'ABSOLUTE', "", None, None
    )

    # return resolved path
    return absfilepath
    
def is_ballance_texture(tex: bpy.types.Image) -> bool:
    """!
    Check whether the provided image is Ballance texture according to its referenced file path.

    A simply calling combination of get_texture_filepath and is_ballance_texture_filepath

    @exception BBPException Ballance texture folder is not set in preferences

    @param tex[in] The texture to check.
    @return True if it is Ballance texture.
    @see get_texture_filepath, is_ballance_texture_filepath
    """
    
    return is_ballance_texture_filepath(get_texture_filepath(tex))

#endregion

#region Ballance Texture Load & Save

def load_ballance_texture(texname: str) -> bpy.types.Image:
    """!
    Load Ballance texture.

    + The returned image may be redirected to a existing image according to its file path, because all Ballance textures are shared.
    + The loaded image is saved as external. No pack will be operated because plugin assume all user have Ballance texture folder.

    @exception BBPException Ballance texture folder is not set in preferences, or provided file name is invalid.

    @param texname[in] the file name (not the path) of loading Ballance texture. Invalid file name will raise exception.
    @return The loaded image.
    """
    
    # try getting preset (also check texture name)
    tex_preset: RawVirtoolsTexture = g_BallanceTexturePresets.get(texname, None)
    if tex_preset is None:
        raise UTIL_functions.BBPException("Invalid Ballance texture file name.")
    
    # load image
    # check existing image in any case. because we need make sure ballance texture is unique.
    filepath: str = os.path.join(_get_ballance_texture_folder(), texname)
    ret: bpy.types.Image = bpy.data.images.load(filepath, check_existing = True)

    # apply preset and return
    set_raw_virtools_texture(ret, tex_preset)
    return ret

def load_other_texture(texname: str) -> bpy.types.Image:
    """!
    Load the Texture which is not a part of Ballance texture.

    This function is different with load_ballance_texture(). It can be seen as the opposition of load_ballance_texture().
    This function is used when loading the temp images created by BMX file resolving or Virtools engine. 
    Because these temp file will be deleted after importing, this function need pack the loaded file into blender file immediately after loading.

    @remark
    + The loaded texture will be immediately packed into blender file.
    + Loading will NOT check any loaded image according to file path.

    @param texname[in] the absolute path to the loading image.
    @return The loaded image.
    """
    
    # load image first
    # always do not check the same image.
    ret: bpy.types.Image = bpy.data.images.load(texname, check_existing = False)
    
    # then immediately pack it into file.
    ret.pack()
    
    # apply general non-ballance texture preset and return image
    set_raw_virtools_texture(ret, g_NonBallanceTexturePreset)
    return ret

def generate_other_texture_save_path(tex: bpy.types.Image, file_folder: str) -> str:
    """!
    Generate the path to saved file.

    This function first get file name from texture, then combine it with given dest file folder, 
    and return it.
    Frequently used with save_other_texture to create its parameter.

    @param tex[in] The saving texture
    @param filepath[in] The absolute path to the folder where the texture will be saved.
    @return The path to saved file.
    """
    return os.path.join(file_folder, os.path.basename(get_texture_filepath(tex)))

def save_other_texture(tex: bpy.types.Image, filepath: str) -> None:
    """!
    Save the texture which is not a part of Ballance texture.

    This function is frequently used when exporting something.
    Usually used to save the texture loaded by load_other_texture, because the texture loaded by load_ballance_texture do not need save.
    This function accept textures which is packed or not packed in blender file.

    @param tex[in] The saving texture
    @param filepath[in] The absolute path to saving file.
    """
    tex.save(filepath)

#endregion
