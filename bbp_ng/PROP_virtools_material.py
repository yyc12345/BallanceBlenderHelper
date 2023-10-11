import bpy
import typing
from . import UTIL_virtools_types, UTIL_functions

# todo:
# some properties are not set default value
# sync the display name with virtools
# no regulator for RawVirtoolsMaterial. split from / to blender into indepent function.
# export default from RawVirtoolsMaterial. upgrade the level of RawVirtoolsMaterial. move up
# then BBP_PG_virtools_material use the default value provided by RawVirtoolsMaterial

class RawVirtoolsMaterial():
    
    # Instance Member Declarations
    
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
    
    # Default Value Declarations
    
    cDefaultDiffuse: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(0.7, 0.7, 0.7, 1.0)
    cDefaultAmbient: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(0.3, 0.3, 0.3, 1.0)
    cDefaultSpecular: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(0.5, 0.5, 0.5, 1.0)
    cDefaultEmissive: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0, 1.0)
    cDefaultSpecularPower: typing.ClassVar[float] = 0.0
    
    cDefaultTexture: typing.ClassVar[bpy.types.Texture | None] = None
    cDefaultTextureBorderColor: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0, 0.0)
    
    cDefaultTextureBlendMode: typing.ClassVar[UTIL_virtools_types.VXTEXTURE_BLENDMODE]= UTIL_virtools_types.VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEALPHA
    cDefaultTextureMinMode: typing.ClassVar[UTIL_virtools_types.VXTEXTURE_FILTERMODE] = UTIL_virtools_types.VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR
    cDefaultTextureMagMode: typing.ClassVar[UTIL_virtools_types.VXTEXTURE_FILTERMODE] = UTIL_virtools_types.VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR
    cDefaultTextureAddressMode: typing.ClassVar[UTIL_virtools_types.VXTEXTURE_ADDRESSMODE] = UTIL_virtools_types.VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSWRAP
    
    cDefaultSourceBlend: typing.ClassVar[UTIL_virtools_types.VXBLEND_MODE] = UTIL_virtools_types.VXBLEND_MODE.VXBLEND_ONE
    cDefaultDestBlend: typing.ClassVar[UTIL_virtools_types.VXBLEND_MODE] = UTIL_virtools_types.VXBLEND_MODE.VXBLEND_ZERO
    cDefaultFillMode: typing.ClassVar[UTIL_virtools_types.VXFILL_MODE] = UTIL_virtools_types.VXFILL_MODE.VXFILL_SOLID
    cDefaultShadeMode: typing.ClassVar[UTIL_virtools_types.VXSHADE_MODE] = UTIL_virtools_types.VXSHADE_MODE.VXSHADE_GOURAUD
    
    cDefaultEnableAlphaTest: typing.ClassVar[bool] = False
    cDefaultEnableAlphaBlend: typing.ClassVar[bool] = False
    cDefaultEnablePerspectiveCorrection: typing.ClassVar[bool] = True
    cDefaultEnableZWrite: typing.ClassVar[bool] = True
    cDefaultEnableTwoSided: typing.ClassVar[bool] = False
    
    cDefaultAlphaRef: typing.ClassVar[int] = 0
    cDefaultAlphaFunc: typing.ClassVar[UTIL_virtools_types.VXCMPFUNC] = UTIL_virtools_types.VXCMPFUNC.VXCMP_ALWAYS
    cDefaultZFunc: typing.ClassVar[UTIL_virtools_types.VXCMPFUNC] = UTIL_virtools_types.VXCMPFUNC.VXCMP_LESSEQUAL
    
    def __init__(self):
        # assign default value for each component
        self.mDiffuse = RawVirtoolsMaterial.cDefaultDiffuse.clone()
        self.mAmbient = RawVirtoolsMaterial.cDefaultAmbient.clone()
        self.mSpecular = RawVirtoolsMaterial.cDefaultSpecular.clone()
        self.mSpecularPower = RawVirtoolsMaterial.cDefaultSpecularPower
        self.mEmissive = RawVirtoolsMaterial.cDefaultEmissive.clone()
        self.mEnableTwoSided = RawVirtoolsMaterial.cDefaultEnableTwoSided
        self.mTexture = RawVirtoolsMaterial.cDefaultTexture
        self.mTextureMinMode = RawVirtoolsMaterial.cDefaultTextureMinMode
        self.mTextureMagMode = RawVirtoolsMaterial.cDefaultTextureMagMode
        self.mSourceBlend = RawVirtoolsMaterial.cDefaultSourceBlend
        self.mDestBlend = RawVirtoolsMaterial.cDefaultDestBlend
        self.mEnableAlphaBlend = RawVirtoolsMaterial.cDefaultEnableAlphaBlend
        self.mShadeMode = RawVirtoolsMaterial.cDefaultShadeMode
        self.mFillMode = RawVirtoolsMaterial.cDefaultFillMode
        self.mEnableAlphaTest = RawVirtoolsMaterial.cDefaultEnableAlphaTest
        self.mEnableZWrite = RawVirtoolsMaterial.cDefaultEnableZWrite
        
        self.mEnablePerspectiveCorrection = RawVirtoolsMaterial.cDefaultEnablePerspectiveCorrection
        self.mTextureBlendMode = RawVirtoolsMaterial.cDefaultTextureBlendMode
        self.mTextureAddressMode = RawVirtoolsMaterial.cDefaultTextureAddressMode
        self.mZFunc = RawVirtoolsMaterial.cDefaultZFunc
        self.mAlphaFunc = RawVirtoolsMaterial.cDefaultAlphaFunc
        self.mTextureBorderColor = RawVirtoolsMaterial.cDefaultTextureBorderColor.clone()
        self.mAlphaRef = RawVirtoolsMaterial.cDefaultAlphaRef
    
    def regulate(self):
        # regulate colors
        self.mDiffuse.regulate()
        self.mAmbient.regulate()
        self.mSpecular.regulate()
        self.mEmissive.regulate()
        self.mTextureBorderColor.regulate()
        # only diffuse and texture border color can have alpha component
        self.mAmbient.a = 1.0
        self.mSpecular.a = 1.0
        self.mEmissive.a = 1.0
        
        # alpha ref limit
        self.mAlphaRef = UTIL_functions.clamp_int(self.mAlphaRef, 0, 255)
        
        # specular power
        self.mSpecularPower = UTIL_functions.clamp_float(self.mSpecularPower, 0.0, 100.0)

class BBP_PG_virtools_material(bpy.types.PropertyGroup):
    ambient: bpy.props.FloatVectorProperty(
        name = "Ambient",
        description = "Ambient color of the material",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsMaterial.cDefaultAmbient.to_tuple_rgb()
    )
    
    diffuse: bpy.props.FloatVectorProperty(
        name = "Diffuse",
        description = "Diffuse color of the material",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        size = 4,
        default = RawVirtoolsMaterial.cDefaultDiffuse.to_tuple_rgba()
    )
    
    specular: bpy.props.FloatVectorProperty(
        name = "Specular",
        description = "Specular color of the material",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsMaterial.cDefaultSpecular.to_tuple_rgb()
    )
    
    emissive: bpy.props.FloatVectorProperty(
        name = "Emissive",
        description = "Emissive color of the material",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsMaterial.cDefaultEmissive.to_tuple_rgb()
    )
    
    specular_power: bpy.props.FloatProperty(
        name = "Power",
        description = "Specular highlight power",
        min = 0.0,
        max = 100.0,
        default = RawVirtoolsMaterial.cDefaultSpecularPower
    )
    
    texture: bpy.props.PointerProperty(
        type = bpy.types.Image,
        name = "Texture",
        description = "Texture of the material"
    )
    
    texture_border_color: bpy.props.FloatVectorProperty(
        name = "Border Color",
        description = "The border color is used when the texture address mode is VXTEXTURE_ADDRESSBORDER.",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        size = 4,
        default = RawVirtoolsMaterial.cDefaultTextureBorderColor.to_tuple_rgba()
    )
    
    texture_blend_mode: bpy.props.EnumProperty(
        name = "Texture Blend",
        description = "Texture blend mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_BLENDMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_BLENDMODE
        ),
        default = RawVirtoolsMaterial.cDefaultTextureBlendMode.value
    )
    
    texture_min_mode: bpy.props.EnumProperty(
        name = "Filter Min",
        description = "Texture filter mode when the texture is minified",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        ),
        default = RawVirtoolsMaterial.cDefaultTextureMinMode.value
    )
    
    texture_mag_mode: bpy.props.EnumProperty(
        name = "Filter Mag",
        description = "Texture filter mode when the texture is magnified",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        ),
        default = RawVirtoolsMaterial.cDefaultTextureMagMode.value
    )
    
    texture_address_mode: bpy.props.EnumProperty(
        name = "Address Mode",
        description = "The address mode controls how the texture coordinates outside the range 0..1",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXTEXTURE_ADDRESSMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_ADDRESSMODE
        ),
        default = RawVirtoolsMaterial.cDefaultTextureAddressMode.value
    )
    
    source_blend: bpy.props.EnumProperty(
        name = "Source Blend",
        description = "Source blend factor",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        ),
        default = RawVirtoolsMaterial.cDefaultSourceBlend.value
    )
    
    dest_blend: bpy.props.EnumProperty(
        name = "Destination Blend",
        description = "Destination blend factor",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        ),
        default = RawVirtoolsMaterial.cDefaultDestBlend.value
    )
    
    fill_mode: bpy.props.EnumProperty(
        name = "Fill Mode",
        description = "Fill mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXFILL_MODE,
            UTIL_virtools_types.g_Annotation_VXFILL_MODE
        ),
        default = RawVirtoolsMaterial.cDefaultFillMode.value
    )
    
    shade_mode: bpy.props.EnumProperty(
        name = "Shade Mode",
        description = "Shade mode",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXSHADE_MODE,
            UTIL_virtools_types.g_Annotation_VXSHADE_MODE
        ),
        default = RawVirtoolsMaterial.cDefaultShadeMode.value
    )
    
    enable_alpha_test: bpy.props.BoolProperty(
        name = "Alpha Test",
        description = "Whether the alpha test is enabled",
        default = RawVirtoolsMaterial.cDefaultEnableAlphaTest
    )
    enable_alpha_blend: bpy.props.BoolProperty(
        name = "Blend",
        description = "Whether alpha blending is enabled or not.",
        default = RawVirtoolsMaterial.cDefaultEnableAlphaBlend
    )
    enable_perspective_correction: bpy.props.BoolProperty(
        name = "Perspective Correction",
        description = "Whether texture perspective correction is enabled",
        default = RawVirtoolsMaterial.cDefaultEnablePerspectiveCorrection
    )
    enable_z_write: bpy.props.BoolProperty(
        name = "Z-Buffer Write",
        description = "Whether writing in ZBuffer is enabled.",
        default = RawVirtoolsMaterial.cDefaultEnableZWrite
    )
    enable_two_sided: bpy.props.BoolProperty(
        name = "Both Sided",
        description = "Whether the material is both sided or not",
        default = RawVirtoolsMaterial.cDefaultEnableTwoSided
    )
    
    alpha_ref: bpy.props.IntProperty(
        name = "Alpha Ref Value",
        description = "Alpha referential value",
        min = 0,
        max = 255,
        default = RawVirtoolsMaterial.cDefaultAlphaRef
    )
    
    alpha_func: bpy.props.EnumProperty(
        name = "Alpha Test Function",
        description = "Alpha comparision function",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        ),
        default = RawVirtoolsMaterial.cDefaultAlphaFunc.value
    )
    
    z_func: bpy.props.EnumProperty(
        name = "Z Compare Function",
        description = "Z Comparison function",
        items = UTIL_virtools_types.generate_blender_enum_prop_entries(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        ),
        default = RawVirtoolsMaterial.cDefaultZFunc.value
    )

def get_virtools_material(mtl: bpy.types.Material) -> BBP_PG_virtools_material:
    return mtl.virtools_material

def get_raw_virtools_material(mtl: bpy.types.Material) -> RawVirtoolsMaterial:
    props: BBP_PG_virtools_material = get_virtools_material(mtl)
    rawdata: RawVirtoolsMaterial = RawVirtoolsMaterial()
    
    rawdata.mDiffuse.from_tuple_rgba(props.diffuse)
    rawdata.mAmbient.from_tuple_rgb(props.ambient)
    rawdata.mSpecular.from_tuple_rgb(props.specular)
    rawdata.mEmissive.from_tuple_rgb(props.emissive)
    rawdata.mSpecularPower = props.specular_power
    
    rawdata.mTexture = props.texture
    rawdata.mTextureBorderColor.from_tuple_rgba(props.texture_border_color)
    
    rawdata.mTextureBlendMode = int(props.texture_blend_mode)
    rawdata.mTextureMinMode = int(props.texture_min_mode)
    rawdata.mTextureMagMode = int(props.texture_mag_mode)
    rawdata.mTextureAddressMode = int(props.texture_address_mode)
    
    rawdata.mSourceBlend = int(props.source_blend)
    rawdata.mDestBlend = int(props.dest_blend)
    rawdata.mFillMode = int(props.fill_mode)
    rawdata.mShadeMode = int(props.shade_mode)
    
    rawdata.mEnableAlphaTest = props.enable_alpha_test
    rawdata.mEnableAlphaBlend = props.enable_alpha_blend
    rawdata.mEnablePerspectiveCorrection = props.enable_perspective_correction
    rawdata.mEnableZWrite = props.enable_z_write
    rawdata.mEnableTwoSided = props.enable_two_sided
    
    rawdata.mAlphaRef = props.alpha_ref
    rawdata.mAlphaFunc = int(props.alpha_func)
    rawdata.mZFunc = int(props.z_func)
    
    rawdata.regulate()
    return rawdata

def set_raw_virtools_material(mtl: bpy.types.Material, rawdata: RawVirtoolsMaterial) -> None:
    props: BBP_PG_virtools_material = get_virtools_material(mtl)
    
    props.diffuse = rawdata.mDiffuse.to_tuple_rgba()
    props.ambient = rawdata.mAmbient.to_tuple_rgb()
    props.specular = rawdata.mSpecular.to_tuple_rgb()
    props.emissive = rawdata.mEmissive.to_tuple_rgb()
    props.specular_power = rawdata.mSpecularPower
    
    props.texture = rawdata.mTexture
    props.texture_border_color = rawdata.mTextureBorderColor.to_tuple_rgba()
    
    props.texture_blend_mode = str(rawdata.mTextureBlendMode)
    props.texture_min_mode = str(rawdata.mTextureMinMode)
    props.texture_mag_mode = str(rawdata.mTextureMagMode)
    props.texture_address_mode = str(rawdata.mTextureAddressMode)
    
    props.source_blend = str(rawdata.mSourceBlend)
    props.dest_blend = str(rawdata.mDestBlend)
    props.fill_mode = str(rawdata.mFillMode)
    props.shade_mode = str(rawdata.mShadeMode)
    
    props.enable_alpha_test = rawdata.mEnableAlphaTest
    props.enable_alpha_blend = rawdata.mEnableAlphaBlend
    props.enable_perspective_correction = rawdata.mEnablePerspectiveCorrection
    props.enable_z_write = rawdata.mEnableZWrite
    props.enable_two_sided = rawdata.mEnableTwoSided
    
    props.alpha_ref = rawdata.mAlphaRef
    props.alpha_func = str(rawdata.mAlphaFunc)
    props.z_func = str(rawdata.mZFunc)

class BBP_PT_virtools_material(bpy.types.Panel):
    """Show Virtools Material Properties."""
    bl_label = "Virtools Material"
    bl_idname = "BBP_PT_virtools_material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def draw(self, context):
        # get layout and target
        layout = self.layout
        props: BBP_PG_virtools_material = get_virtools_material(context.material)
        
        # draw layout
        row = layout.row()
        row.label(text="Color Parameters")
        #row.operator(BALLANCE_OT_preset_virtools_material.bl_idname, text="", icon="PRESET")
        layout.prop(props, 'ambient')
        layout.prop(props, 'diffuse')
        layout.prop(props, 'specular')
        layout.prop(props, 'emissive')
        layout.prop(props, 'specular_power')
        
        layout.separator()
        layout.label(text="Mode Parameters")
        layout.prop(props, 'enable_two_sided')
        layout.prop(props, 'fill_mode')
        layout.prop(props, 'shade_mode')
        
        layout.separator()
        layout.label(text="Texture Parameters")
        layout.prop(props, 'texture', emboss = True)
        layout.prop(props, 'texture_blend_mode')
        layout.prop(props, 'texture_min_mode')
        layout.prop(props, 'texture_mag_mode')
        layout.prop(props, 'texture_address_mode')
        layout.prop(props, 'enable_perspective_correction')
        if (int(props.texture_address_mode) == UTIL_virtools_types.VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSBORDER.value):
            layout.prop(props, 'texture_border_color')
        
        layout.separator()
        layout.label(text="Alpha Test Parameters")
        layout.prop(props, 'enable_alpha_test')
        if props.enable_alpha_test:
            layout.prop(props, 'alpha_func')
            layout.prop(props, 'alpha_ref')
        
        layout.separator()
        layout.label(text="Alpha Blend Parameters")
        layout.prop(props, 'enable_alpha_blend')
        if props.enable_alpha_blend:
            layout.prop(props, 'source_blend')
            layout.prop(props, 'dest_blend')

        layout.separator()
        layout.label(text="Z Write Parameters")
        layout.prop(props, 'enable_z_write')
        if props.enable_z_write:
            layout.prop(props, 'z_func')

        layout.separator()
        layout.label(text="Operations")
        #layout.operator(BALLANCE_OT_apply_virtools_material.bl_idname, icon="NODETREE")
        #layout.operator(BALLANCE_OT_parse_virtools_material.bl_idname, icon="HIDE_OFF")


def register_prop():
    bpy.types.Material.virtools_material = bpy.props.PointerProperty(type = BBP_PG_virtools_material)

def unregister_prop():
    del bpy.types.Material.virtools_material
