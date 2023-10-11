import bpy
from . import UTIL_virtools_types

# todo:
# some properties are not set default value
# sync the display name with virtools
# no regulator for RawVirtoolsMaterial. split from / to blender into indepent function.
# export default from RawVirtoolsMaterial. upgrade the level of RawVirtoolsMaterial. move up
# then BBP_PG_virtools_material use the default value provided by RawVirtoolsMaterial

class BBP_PG_virtools_material(bpy.types.PropertyGroup):
    ambient: bpy.props.FloatVectorProperty(
        name = "Ambient",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = (0.3, 0.3, 0.3)
    )
    
    diffuse: bpy.props.FloatVectorProperty(
        name = "Diffuse",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        size = 4,
        default = (0.7, 0.7, 0.7, 1.0)
    )
    
    specular: bpy.props.FloatVectorProperty(
        name = "Specular",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = (0.5, 0.5, 0.5)
    )
    
    emissive: bpy.props.FloatVectorProperty(
        name = "Emissive",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = (0.0, 0.0, 0.0)
    )
    
    specular_power: bpy.props.FloatProperty(
        name = "Specular Power",
        min = 0.0,
        max = 100.0,
        default = 0.0,
    )
    
    texture: bpy.props.PointerProperty(
        type = bpy.types.Image,
        name = "Texture"
    )
    
    texture_border_color: bpy.props.FloatVectorProperty(
        name = "Texture Border Color",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = (0.0, 0.0, 0.0)
    )
    
    texture_blend_mode: bpy.props.EnumProperty(
        name = "Texture Blend Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_BLENDMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_BLENDMODE
        )
    )
    
    texture_min_mode: bpy.props.EnumProperty(
        name = "Texture Min Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        )
    )
    
    texture_mag_mode: bpy.props.EnumProperty(
        name = "Texture Mag Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        )
    )
    
    texture_address_mode: bpy.props.EnumProperty(
        name = "Texture Address Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_ADDRESSMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_ADDRESSMODE
        )
    )
    
    source_blend: bpy.props.EnumProperty(
        name = "Source Blend",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        )
    )
    
    dest_blend: bpy.props.EnumProperty(
        name = "Dest Blend",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        )
    )
    
    fill_mode: bpy.props.EnumProperty(
        name = "Fill Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXFILL_MODE,
            UTIL_virtools_types.g_Annotation_VXFILL_MODE
        )
    )
    
    shade_mode: bpy.props.EnumProperty(
        name = "Shade Mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXSHADE_MODE,
            UTIL_virtools_types.g_Annotation_VXSHADE_MODE
        )
    )
    
    enable_alpha_test: bpy.props.BoolProperty(
        name = "Enable Alpha Test",
        default = False,
    )
    enable_alpha_blend: bpy.props.BoolProperty(
        name = "Enable Alpha Blend",
        default = False,
    )
    enable_perspective_correction: bpy.props.BoolProperty(
        name = "Enable Perspective Correction",
        default = False,
    )
    enable_zwrite: bpy.props.BoolProperty(
        name = "Enable ZWrite",
        default = True,
    )
    enable_two_sided: bpy.props.BoolProperty(
        name = "Enable Two Sided",
        default = False,
    )
    
    alpha_ref: bpy.props.IntProperty(
        name = "Alpha Ref",
        min = 0,
        max = 255,
        default = 0,
    )

    alpha_func: bpy.props.EnumProperty(
        name = "Alpha Func",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        )
    )

    z_func: bpy.props.EnumProperty(
        name = "Z Func",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        )
    )


    

class RawVirtoolsMaterial():
    mDiffuse: UTIL_virtools_types.VxColor
    mAmbient: UTIL_virtools_types.VxColor
    mSpecular: UTIL_virtools_types.VxColor
    mEmissive: UTIL_virtools_types.VxColor
    mSpecularPower: float
    
    mTexture: bpy.types.Texture | None
    mTextureBorderColor: UTIL_virtools_types.VxColor
    
    mTextureBlendMode: UTIL_virtools_types.VXTEXTURE_BLENDMODE
    mTextureMinMode: UTIL_virtools_types.VXTEXTURE_FILTERMODE
    mTextureMagMode: UTIL_virtools_types.VXTEXTURE_FILTERMODE
    mTextureAddressMode: UTIL_virtools_types.VXTEXTURE_ADDRESSMODE
    
    mSourceBlend: UTIL_virtools_types.VXBLEND_MODE
    mDestBlend: UTIL_virtools_types.VXBLEND_MODE
    mFillMode: UTIL_virtools_types.VXFILL_MODE
    mShadeMode: UTIL_virtools_types.VXSHADE_MODE
    
    mEnableAlphaTest: bool
    mEnableAlphaBlend: bool
    mEnablePerspectiveCorrection: bool
    mEnableZWrite: bool
    mEnableTwoSided: bool
    
    mAlphaRef: int
    mAlphaFunc: UTIL_virtools_types.VXCMPFUNC
    mZFunc: UTIL_virtools_types.VXCMPFUNC
    
    def __init__(self):
        # assign default value for each component
        self.mDiffuse = (0.7, 0.7, 0.7, 1.0)
        self.mAmbient = (0.3, 0.3, 0.3, 1.0)
        self.mSpecular = (0.5, 0.5, 0.5, 1.0)
        self.mSpecularPower = 0.0
        self.mEmissive = (0.0, 0.0, 0.0, 1.0)
        self.mEnableTwoSided = False
        self.mTexture = None
        self.mTextureMinMode = UTIL_virtools_types.VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR
        self.mTextureMagMode = UTIL_virtools_types.VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR
        self.mSourceBlend = UTIL_virtools_types.VXBLEND_MODE.VXBLEND_ONE
        self.mDestBlend = UTIL_virtools_types.VXBLEND_MODE.VXBLEND_ZERO
        self.mEnableAlphaBlend = False
        self.mShadeMode = UTIL_virtools_types.VXSHADE_MODE.VXSHADE_GOURAUD
        self.mFillMode = UTIL_virtools_types.VXFILL_MODE.VXFILL_SOLID
        self.mEnableAlphaTest = False
        self.mEnableZWrite = True
        
        self.mEnablePerspectiveCorrection = True
        self.mTextureBlendMode = UTIL_virtools_types.VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEALPHA
        self.mTextureAddressMode = UTIL_virtools_types.VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSWRAP
        self.mZFunc = UTIL_virtools_types.VXCMPFUNC.VXCMP_LESSEQUAL
        self.mAlphaFunc = UTIL_virtools_types.VXCMPFUNC.VXCMP_ALWAYS
        self.mTextureBorderColor = (0.0, 0.0, 0.0, 0.0)
        self.mAlphaRef = 0
    
    def from_blender_prop(self):
        pass
    
    
    def to_blender_prop(self):
        pass
