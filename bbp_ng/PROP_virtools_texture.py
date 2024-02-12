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
    
# blender enum prop helper defines
_g_Helper_CK_TEXTURE_SAVEOPTIONS: UTIL_virtools_types.EnumPropHelper = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS)
_g_Helper_VX_PIXELFORMAT: UTIL_virtools_types.EnumPropHelper = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.VX_PIXELFORMAT)

class BBP_PG_virtools_texture(bpy.types.PropertyGroup):

    save_options: bpy.props.EnumProperty(
        name = "Save Options",
        description = "When saving a composition textures or sprites can be kept as reference to external files or converted to a given format and saved inside the composition file.",
        items = _g_Helper_CK_TEXTURE_SAVEOPTIONS.generate_items(),
        default = _g_Helper_CK_TEXTURE_SAVEOPTIONS.to_selection(RawVirtoolsTexture.cDefaultSaveOptions)
    )
    
    video_format: bpy.props.EnumProperty(
        name = "Video Format",
        description = "The desired surface pixel format in video memory.",
        items = _g_Helper_VX_PIXELFORMAT.generate_items(),
        default = _g_Helper_VX_PIXELFORMAT.to_selection(RawVirtoolsTexture.cDefaultVideoFormat)
    )
    
#region Virtools Texture Getter Setter

def get_virtools_texture(img: bpy.types.Image) -> BBP_PG_virtools_texture:
    return img.virtools_texture

def get_raw_virtools_texture(img: bpy.types.Image) -> RawVirtoolsTexture:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    rawdata: RawVirtoolsTexture = RawVirtoolsTexture()
    
    rawdata.mSaveOptions = _g_Helper_CK_TEXTURE_SAVEOPTIONS.get_selection(props.save_options)
    rawdata.mVideoFormat = _g_Helper_VX_PIXELFORMAT.get_selection(props.video_format)
    return rawdata

def set_raw_virtools_texture(img: bpy.types.Image, rawdata: RawVirtoolsTexture) -> None:
    props: BBP_PG_virtools_texture = get_virtools_texture(img)
    
    props.save_options = _g_Helper_CK_TEXTURE_SAVEOPTIONS.to_selection(rawdata.mSaveOptions)
    props.video_format = _g_Helper_VX_PIXELFORMAT.to_selection(rawdata.mVideoFormat)

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

#region Ballance Texture Preset

_g_OpaqueBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._16_ARGB1555,
)
_g_TransparentBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888,
)
_g_NonBallanceTexturePreset: RawVirtoolsTexture = RawVirtoolsTexture(
    mSaveOptions = UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA,
    mVideoFormat = UTIL_virtools_types.VX_PIXELFORMAT._32_ARGB8888,
)

## The preset collection of all Ballance texture.
#  Key is texture name and can be used as file name checking.
#  Value is its preset which can be assigned.
_g_BallanceTexturePresets: dict[str, RawVirtoolsTexture] = {
    # "atari.avi": _g_TransparentBallanceTexturePreset,
    "atari.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere1.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere2.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_LightningSphere3.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_Paper.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_Stone.bmp": _g_OpaqueBallanceTexturePreset,
    "Ball_Wood.bmp": _g_OpaqueBallanceTexturePreset,
    "Brick.bmp": _g_OpaqueBallanceTexturePreset,
    "Button01_deselect.tga": _g_TransparentBallanceTexturePreset,
    "Button01_select.tga": _g_TransparentBallanceTexturePreset,
    "Button01_special.tga": _g_TransparentBallanceTexturePreset,
    "Column_beige.bmp": _g_OpaqueBallanceTexturePreset,
    "Column_beige_fade.tga": _g_TransparentBallanceTexturePreset,
    "Column_blue.bmp": _g_OpaqueBallanceTexturePreset,
    "Cursor.tga": _g_TransparentBallanceTexturePreset,
    "Dome.bmp": _g_OpaqueBallanceTexturePreset,
    "DomeEnvironment.bmp": _g_OpaqueBallanceTexturePreset,
    "DomeShadow.tga": _g_TransparentBallanceTexturePreset,
    "ExtraBall.bmp": _g_OpaqueBallanceTexturePreset,
    "ExtraParticle.bmp": _g_OpaqueBallanceTexturePreset,
    "E_Holzbeschlag.bmp": _g_OpaqueBallanceTexturePreset,
    "FloorGlow.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Side.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_Border.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_Borderless.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_Checkpoint.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_Flat.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_Profil.bmp": _g_OpaqueBallanceTexturePreset,
    "Floor_Top_ProfilFlat.bmp": _g_OpaqueBallanceTexturePreset,
    "Font_1.tga": _g_TransparentBallanceTexturePreset,
    "Gravitylogo_intro.bmp": _g_OpaqueBallanceTexturePreset,
    "HardShadow.bmp": _g_OpaqueBallanceTexturePreset,
    "Laterne_Glas.bmp": _g_OpaqueBallanceTexturePreset,
    "Laterne_Schatten.tga": _g_TransparentBallanceTexturePreset,
    "Laterne_Verlauf.tga": _g_TransparentBallanceTexturePreset,
    "Logo.bmp": _g_OpaqueBallanceTexturePreset,
    "Metal_stained.bmp": _g_OpaqueBallanceTexturePreset,
    "Misc_Ufo.bmp": _g_OpaqueBallanceTexturePreset,
    "Misc_UFO_Flash.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul03_Floor.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul03_Wall.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul11_13_Wood.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul11_Wood.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul15.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul16.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul18.bmp": _g_OpaqueBallanceTexturePreset,
    "Modul18_Gitter.tga": _g_TransparentBallanceTexturePreset,
    "Modul30_d_Seiten.bmp": _g_OpaqueBallanceTexturePreset,
    "Particle_Flames.bmp": _g_OpaqueBallanceTexturePreset,
    "Particle_Smoke.bmp": _g_OpaqueBallanceTexturePreset,
    "PE_Bal_balloons.bmp": _g_OpaqueBallanceTexturePreset,
    "PE_Bal_platform.bmp": _g_OpaqueBallanceTexturePreset,
    "PE_Ufo_env.bmp": _g_OpaqueBallanceTexturePreset,
    "Pfeil.tga": _g_TransparentBallanceTexturePreset,
    "P_Extra_Life_Oil.bmp": _g_OpaqueBallanceTexturePreset,
    "P_Extra_Life_Particle.bmp": _g_OpaqueBallanceTexturePreset,
    "P_Extra_Life_Shadow.bmp": _g_OpaqueBallanceTexturePreset,
    "Rail_Environment.bmp": _g_OpaqueBallanceTexturePreset,
    "sandsack.bmp": _g_OpaqueBallanceTexturePreset,
    "SkyLayer.bmp": _g_OpaqueBallanceTexturePreset,
    "Sky_Vortex.bmp": _g_OpaqueBallanceTexturePreset,
    "Stick_Bottom.tga": _g_TransparentBallanceTexturePreset,
    "Stick_Stripes.bmp": _g_OpaqueBallanceTexturePreset,
    "Target.bmp": _g_OpaqueBallanceTexturePreset,
    "Tower_Roof.bmp": _g_OpaqueBallanceTexturePreset,
    "Trafo_Environment.bmp": _g_OpaqueBallanceTexturePreset,
    "Trafo_FlashField.bmp": _g_OpaqueBallanceTexturePreset,
    "Trafo_Shadow_Big.tga": _g_TransparentBallanceTexturePreset,
    "Tut_Pfeil01.tga": _g_TransparentBallanceTexturePreset,
    "Tut_Pfeil_Hoch.tga": _g_TransparentBallanceTexturePreset,
    "Wolken_intro.tga": _g_TransparentBallanceTexturePreset,
    "Wood_Metal.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_MetalStripes.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Misc.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Nailed.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Old.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Panel.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Plain.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Plain2.bmp": _g_OpaqueBallanceTexturePreset,
    "Wood_Raft.bmp": _g_OpaqueBallanceTexturePreset,
}

def get_ballance_texture_preset(texname: str) -> RawVirtoolsTexture:
    try_preset: RawVirtoolsTexture | None = _g_BallanceTexturePresets.get(texname, None)
    if try_preset is None:
        # fallback to non-ballance one
        try_preset = _g_NonBallanceTexturePreset

    return try_preset

def get_nonballance_texture_preset() -> RawVirtoolsTexture:
    return _g_NonBallanceTexturePreset

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_PG_virtools_texture)
    
    # add into image metadata
    bpy.types.Image.virtools_texture = bpy.props.PointerProperty(type = BBP_PG_virtools_texture)

def unregister() -> None:
    # del from image metadata
    del bpy.types.Image.virtools_texture

    bpy.utils.unregister_class(BBP_PG_virtools_texture)
