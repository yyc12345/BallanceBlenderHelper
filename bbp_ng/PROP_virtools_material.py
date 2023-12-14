import bpy
import typing, enum
from . import UTIL_virtools_types, UTIL_functions, UTIL_ballance_texture, UTIL_file_browser
from . import PROP_virtools_texture, PROP_preferences

class RawVirtoolsMaterial():
    
    # Instance Member Declarations
    
    mDiffuse: UTIL_virtools_types.VxColor
    mAmbient: UTIL_virtools_types.VxColor
    mSpecular: UTIL_virtools_types.VxColor
    mEmissive: UTIL_virtools_types.VxColor
    mSpecularPower: float
    
    mTexture: bpy.types.Image | None
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
    
    cDefaultTexture: typing.ClassVar[bpy.types.Image | None] = None
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
    
    def __init__(self, **kwargs):
        # assign default value for each component
        self.mDiffuse = kwargs.get('mDiffuse', RawVirtoolsMaterial.cDefaultDiffuse).clone()
        self.mAmbient = kwargs.get('mAmbient', RawVirtoolsMaterial.cDefaultAmbient).clone()
        self.mSpecular = kwargs.get('mSpecular', RawVirtoolsMaterial.cDefaultSpecular).clone()
        self.mSpecularPower = kwargs.get('mSpecularPower', RawVirtoolsMaterial.cDefaultSpecularPower)
        self.mEmissive = kwargs.get('mEmissive', RawVirtoolsMaterial.cDefaultEmissive).clone()
        self.mEnableTwoSided = kwargs.get('mEnableTwoSided', RawVirtoolsMaterial.cDefaultEnableTwoSided)
        self.mTexture = kwargs.get('mTexture', RawVirtoolsMaterial.cDefaultTexture)
        self.mTextureMinMode = kwargs.get('mTextureMinMode', RawVirtoolsMaterial.cDefaultTextureMinMode)
        self.mTextureMagMode = kwargs.get('mTextureMagMode', RawVirtoolsMaterial.cDefaultTextureMagMode)
        self.mSourceBlend = kwargs.get('mSourceBlend', RawVirtoolsMaterial.cDefaultSourceBlend)
        self.mDestBlend = kwargs.get('mDestBlend', RawVirtoolsMaterial.cDefaultDestBlend)
        self.mEnableAlphaBlend = kwargs.get('mEnableAlphaBlend', RawVirtoolsMaterial.cDefaultEnableAlphaBlend)
        self.mShadeMode = kwargs.get('mShadeMode', RawVirtoolsMaterial.cDefaultShadeMode)
        self.mFillMode = kwargs.get('mFillMode', RawVirtoolsMaterial.cDefaultFillMode)
        self.mEnableAlphaTest = kwargs.get('mEnableAlphaTest', RawVirtoolsMaterial.cDefaultEnableAlphaTest)
        self.mEnableZWrite = kwargs.get('mEnableZWrite', RawVirtoolsMaterial.cDefaultEnableZWrite)
        
        self.mEnablePerspectiveCorrection = kwargs.get('mEnablePerspectiveCorrection', RawVirtoolsMaterial.cDefaultEnablePerspectiveCorrection)
        self.mTextureBlendMode = kwargs.get('mTextureBlendMode', RawVirtoolsMaterial.cDefaultTextureBlendMode)
        self.mTextureAddressMode = kwargs.get('mTextureAddressMode', RawVirtoolsMaterial.cDefaultTextureAddressMode)
        self.mZFunc = kwargs.get('mZFunc', RawVirtoolsMaterial.cDefaultZFunc)
        self.mAlphaFunc = kwargs.get('mAlphaFunc', RawVirtoolsMaterial.cDefaultAlphaFunc)
        self.mTextureBorderColor = kwargs.get('mTextureBorderColor', RawVirtoolsMaterial.cDefaultTextureBorderColor).clone()
        self.mAlphaRef = kwargs.get('mAlphaRef', RawVirtoolsMaterial.cDefaultAlphaRef)
    
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
        default = RawVirtoolsMaterial.cDefaultAmbient.to_const_rgb()
    )
    
    diffuse: bpy.props.FloatVectorProperty(
        name = "Diffuse",
        description = "Diffuse color of the material",
        subtype = 'COLOR_GAMMA',
        min = 0.0,
        max = 1.0,
        size = 4,
        default = RawVirtoolsMaterial.cDefaultDiffuse.to_const_rgba()
    )
    
    specular: bpy.props.FloatVectorProperty(
        name = "Specular",
        description = "Specular color of the material",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsMaterial.cDefaultSpecular.to_const_rgb()
    )
    
    emissive: bpy.props.FloatVectorProperty(
        name = "Emissive",
        description = "Emissive color of the material",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsMaterial.cDefaultEmissive.to_const_rgb()
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
        default = RawVirtoolsMaterial.cDefaultTextureBorderColor.to_const_rgba()
    )
    
    texture_blend_mode: bpy.props.EnumProperty(
        name = "Texture Blend",
        description = "Texture blend mode",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXTEXTURE_BLENDMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_BLENDMODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultTextureBlendMode)
    )
    
    texture_min_mode: bpy.props.EnumProperty(
        name = "Filter Min",
        description = "Texture filter mode when the texture is minified",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultTextureMinMode)
    )
    
    texture_mag_mode: bpy.props.EnumProperty(
        name = "Filter Mag",
        description = "Texture filter mode when the texture is magnified",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXTEXTURE_FILTERMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_FILTERMODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultTextureMagMode)
    )
    
    texture_address_mode: bpy.props.EnumProperty(
        name = "Address Mode",
        description = "The address mode controls how the texture coordinates outside the range 0..1",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXTEXTURE_ADDRESSMODE,
            UTIL_virtools_types.g_Annotation_VXTEXTURE_ADDRESSMODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultTextureAddressMode)
    )
    
    source_blend: bpy.props.EnumProperty(
        name = "Source Blend",
        description = "Source blend factor",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultSourceBlend)
    )
    
    dest_blend: bpy.props.EnumProperty(
        name = "Destination Blend",
        description = "Destination blend factor",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXBLEND_MODE,
            UTIL_virtools_types.g_Annotation_VXBLEND_MODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultDestBlend)
    )
    
    fill_mode: bpy.props.EnumProperty(
        name = "Fill Mode",
        description = "Fill mode",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXFILL_MODE,
            UTIL_virtools_types.g_Annotation_VXFILL_MODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultFillMode)
    )
    
    shade_mode: bpy.props.EnumProperty(
        name = "Shade Mode",
        description = "Shade mode",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXSHADE_MODE,
            UTIL_virtools_types.g_Annotation_VXSHADE_MODE
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultShadeMode)
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
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultAlphaFunc)
    )
    
    z_func: bpy.props.EnumProperty(
        name = "Z Compare Function",
        description = "Z Comparison function",
        items = UTIL_virtools_types.EnumPropHelper.generate_items(
            UTIL_virtools_types.VXCMPFUNC,
            UTIL_virtools_types.g_Annotation_VXCMPFUNC
        ),
        default = UTIL_virtools_types.EnumPropHelper.to_selection(RawVirtoolsMaterial.cDefaultZFunc)
    )

#region Getter Setter

def get_virtools_material(mtl: bpy.types.Material) -> BBP_PG_virtools_material:
    return mtl.virtools_material

def get_raw_virtools_material(mtl: bpy.types.Material) -> RawVirtoolsMaterial:
    props: BBP_PG_virtools_material = get_virtools_material(mtl)
    rawdata: RawVirtoolsMaterial = RawVirtoolsMaterial()
    
    rawdata.mDiffuse.from_const_rgba(props.diffuse)
    rawdata.mAmbient.from_const_rgb(props.ambient)
    rawdata.mSpecular.from_const_rgb(props.specular)
    rawdata.mEmissive.from_const_rgb(props.emissive)
    rawdata.mSpecularPower = props.specular_power
    
    rawdata.mTexture = props.texture
    rawdata.mTextureBorderColor.from_const_rgba(props.texture_border_color)
    
    rawdata.mTextureBlendMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXTEXTURE_BLENDMODE, props.texture_blend_mode)
    rawdata.mTextureMinMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXTEXTURE_FILTERMODE, props.texture_min_mode)
    rawdata.mTextureMagMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXTEXTURE_FILTERMODE, props.texture_mag_mode)
    rawdata.mTextureAddressMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXTEXTURE_ADDRESSMODE, props.texture_address_mode)
    
    rawdata.mSourceBlend = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXBLEND_MODE, props.source_blend)
    rawdata.mDestBlend = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXBLEND_MODE, props.dest_blend)
    rawdata.mFillMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXFILL_MODE, props.fill_mode)
    rawdata.mShadeMode = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXSHADE_MODE, props.shade_mode)
    
    rawdata.mEnableAlphaTest = props.enable_alpha_test
    rawdata.mEnableAlphaBlend = props.enable_alpha_blend
    rawdata.mEnablePerspectiveCorrection = props.enable_perspective_correction
    rawdata.mEnableZWrite = props.enable_z_write
    rawdata.mEnableTwoSided = props.enable_two_sided
    
    rawdata.mAlphaRef = props.alpha_ref
    rawdata.mAlphaFunc = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXCMPFUNC, props.alpha_func)
    rawdata.mZFunc = UTIL_virtools_types.EnumPropHelper.get_selection(UTIL_virtools_types.VXCMPFUNC, props.z_func)
    
    rawdata.regulate()
    return rawdata

def set_raw_virtools_material(mtl: bpy.types.Material, rawdata: RawVirtoolsMaterial) -> None:
    props: BBP_PG_virtools_material = get_virtools_material(mtl)
    
    props.diffuse = rawdata.mDiffuse.to_const_rgba()
    props.ambient = rawdata.mAmbient.to_const_rgb()
    props.specular = rawdata.mSpecular.to_const_rgb()
    props.emissive = rawdata.mEmissive.to_const_rgb()
    props.specular_power = rawdata.mSpecularPower
    
    props.texture = rawdata.mTexture
    props.texture_border_color = rawdata.mTextureBorderColor.to_const_rgba()
    
    props.texture_blend_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mTextureBlendMode)
    props.texture_min_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mTextureMinMode)
    props.texture_mag_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mTextureMagMode)
    props.texture_address_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mTextureAddressMode)
    
    props.source_blend = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mSourceBlend)
    props.dest_blend = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mDestBlend)
    props.fill_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mFillMode)
    props.shade_mode = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mShadeMode)
    
    props.enable_alpha_test = rawdata.mEnableAlphaTest
    props.enable_alpha_blend = rawdata.mEnableAlphaBlend
    props.enable_perspective_correction = rawdata.mEnablePerspectiveCorrection
    props.enable_z_write = rawdata.mEnableZWrite
    props.enable_two_sided = rawdata.mEnableTwoSided
    
    props.alpha_ref = rawdata.mAlphaRef
    props.alpha_func = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mAlphaFunc)
    props.z_func = UTIL_virtools_types.EnumPropHelper.to_selection(rawdata.mZFunc)

def apply_to_blender_material(mtl: bpy.types.Material):
    # get raw material data
    rawdata: RawVirtoolsMaterial = get_raw_virtools_material(mtl)
    
    # enable nodes mode
    mtl.use_nodes = True
    # delete all existed nodes
    for node in mtl.node_tree.nodes:
        mtl.node_tree.nodes.remove(node)
    
    # create ballance-style blender material
    # for sockets name, see `bpy_extras.node_shader_utils` for more infos
    bnode: bpy.types.ShaderNodeBsdfPrincipled = mtl.node_tree.nodes.new(type = "ShaderNodeBsdfPrincipled")
    mnode: bpy.types.ShaderNodeOutputMaterial = mtl.node_tree.nodes.new(type = "ShaderNodeOutputMaterial")
    mtl.node_tree.links.new(bnode.outputs["BSDF"], mnode.inputs["Surface"])
    
    # set basic colors
    metallic_value = sum(rawdata.mAmbient.to_const_rgb()) / 3
    mtl.metallic = metallic_value
    bnode.inputs["Metallic"].default_value = metallic_value

    diffuse_value = rawdata.mDiffuse.to_const_rgba()
    mtl.diffuse_color = diffuse_value
    bnode.inputs["Base Color"].default_value = diffuse_value

    mtl.specular_color = rawdata.mSpecular.to_const_rgb()

    # too shiny, disabled.
    # bnode.inputs["Emission"].default_value = rawdata.mEmissive.to_const_rgba()

    mtl.specular_intensity = rawdata.mSpecularPower
    bnode.inputs["Specular"].default_value = UTIL_functions.clamp_float(
        rawdata.mSpecularPower, 0.0, 1.0
    )
    
    # set some alpha data
    mtl.use_backface_culling = not rawdata.mEnableTwoSided
    mtl.blend_method = 'BLEND' if rawdata.mEnableAlphaBlend else 'OPAQUE'

    # set texture
    if rawdata.mTexture is not None:
        # basic texture setter
        inode: bpy.types.ShaderNodeTexImage = mtl.node_tree.nodes.new(type = "ShaderNodeTexImage")
        inode.image = rawdata.mTexture
        mtl.node_tree.links.new(inode.outputs["Color"], bnode.inputs["Base Color"])

        # todo: sync texture mapping config here
        
        # link alpha if necessary
        if rawdata.mEnableAlphaBlend:
            mtl.node_tree.links.new(inode.outputs["Alpha"], bnode.inputs["Alpha"])
            
#endregion

#region Preset Paramters

class MaterialPresetType(enum.IntEnum):
    FloorSide = enum.auto()
    FloorTop = enum.auto()
    TrafoPaper = enum.auto()
    TraforWoodStone = enum.auto()
    Rail = enum.auto()
    WoodPath = enum.auto()
    WoodChip = enum.auto()

class MaterialPresetData():
    mDisplayName: str
    mData: RawVirtoolsMaterial
    def __init__(self, display_name: str, data: RawVirtoolsMaterial):
        self.mDisplayName = display_name
        self.mData = data

_g_MaterialPresets: dict[int, MaterialPresetData] = {
    MaterialPresetType.FloorSide: MaterialPresetData(
        "Floor Side",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mDiffuse = UTIL_virtools_types.VxColor(122 / 255.0, 122 / 255.0, 122 / 255.0),
            mSpecular = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mEmissive = UTIL_virtools_types.VxColor(104 / 255.0, 104 / 255.0, 104 / 255.0),
            mSpecularPower = 0.0
        )
    ),
    MaterialPresetType.FloorTop: MaterialPresetData(
        "Floor Top",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mDiffuse = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0),
            mSpecular = UTIL_virtools_types.VxColor(80 / 255.0, 80 / 255.0, 80 / 255.0),
            mEmissive = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mSpecularPower = 100.0
        )
    ),
    MaterialPresetType.TrafoPaper: MaterialPresetData(
        "Transform Paper",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(25 / 255.0, 25 / 255.0, 25 / 255.0),
            mDiffuse = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0),
            mSpecular = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mEmissive = UTIL_virtools_types.VxColor(100 / 255.0, 100 / 255.0, 100 / 255.0),
            mSpecularPower = 0.0
        )
    ),
    MaterialPresetType.TraforWoodStone: MaterialPresetData(
        "Transform Stone & Wood",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(25 / 255.0, 25 / 255.0, 25 / 255.0),
            mDiffuse = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0),
            mSpecular = UTIL_virtools_types.VxColor(229 / 255.0, 229 / 255.0, 229 / 255.0),
            mEmissive = UTIL_virtools_types.VxColor(60 / 255.0, 60 / 255.0, 60 / 255.0),
            mSpecularPower = 0.0
        )
    ),
    MaterialPresetType.Rail: MaterialPresetData(
        "Rail",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(0.0, 0.0, 0.0),
            mDiffuse = UTIL_virtools_types.VxColor(100 / 255.0, 118 / 255.0, 133 / 255.0),
            mSpecular = UTIL_virtools_types.VxColor(210 / 255.0, 210 / 255.0, 210 / 255.0),
            mEmissive = UTIL_virtools_types.VxColor(124 / 255.0, 134 / 255.0, 150 / 255.0),
            mSpecularPower = 10.0
        )
    ),
    MaterialPresetType.WoodPath: MaterialPresetData(
        "Wood Path",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(2 / 255.0, 2 / 255.0, 2 / 255.0),
            mDiffuse = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0),
            mSpecular = UTIL_virtools_types.VxColor(59 / 255.0, 59 / 255.0, 59 / 255.0),
            mEmissive = UTIL_virtools_types.VxColor(30 / 255.0, 30 / 255.0, 30 / 255.0),
            mSpecularPower = 25.0
        )
    ),
    MaterialPresetType.WoodChip: MaterialPresetData(
        "Wood Chip",
        RawVirtoolsMaterial(
            mAmbient = UTIL_virtools_types.VxColor(25 / 255.0, 25 / 255.0, 25 / 255.0),
            mDiffuse = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0),
            mSpecular = UTIL_virtools_types.VxColor(100 / 255.0, 100 / 255.0, 100 / 255.0),
            mEmissive = UTIL_virtools_types.VxColor(50 / 255.0, 50 / 255.0, 50 / 255.0),
            mSpecularPower = 50.0
        )
    ),
}

def get_virtools_material_preset(preset_type: MaterialPresetType) -> MaterialPresetData:
    return _g_MaterialPresets[preset_type]

def preset_virtools_material(mtl: bpy.types.Material, preset_type: MaterialPresetType) -> None:
    preset_data: MaterialPresetData = _g_MaterialPresets[preset_type]
    set_raw_virtools_material(mtl, preset_data.mData)

class _MtlPresetEnumPropHelper():
    """
    Operate like UTIL_virtools_types.EnumPropHelper
    """

    @staticmethod
    def __get_name(v: MaterialPresetType) -> str:
        entry: MaterialPresetData | None = _g_MaterialPresets.get(v, None)
        if entry: return entry.mDisplayName
        else: return ""

    @staticmethod
    def generate_items() -> tuple[tuple, ...]:
        # token, display name, descriptions, icon, index
        return tuple(
            (
                str(member.value), 
                _MtlPresetEnumPropHelper.__get_name(member), 
                "", 
                "", 
                member.value
            ) for member in MaterialPresetType
        )
    
    @staticmethod
    def get_selection(prop: str) -> MaterialPresetType:
        return MaterialPresetType(int(prop))
    
    @staticmethod
    def to_selection(val: MaterialPresetType) -> str:
        return str(val.value)

#endregion

#region Operators

class BBP_OT_apply_virtools_material(bpy.types.Operator):
    """Apply Virtools Material to Blender Material."""
    bl_idname = "bbp.apply_virtools_material"
    bl_label = "Apply to Blender Material"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def execute(self, context):
        mtl: bpy.types.Material = context.material
        apply_to_blender_material(mtl)
        return {'FINISHED'}

class BBP_OT_preset_virtools_material(bpy.types.Operator):
    """Preset Virtools Material with Original Ballance Data."""
    bl_idname = "bbp.preset_virtools_material"
    bl_label = "Preset Virtools Material"
    bl_options = {'UNDO'}
    
    preset_type: bpy.props.EnumProperty(
        name = "Preset",
        description = "The preset which you want to apply.",
        items = _MtlPresetEnumPropHelper.generate_items(),
    )
    
    @classmethod
    def poll(cls, context):
        return context.material is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, "preset_type")
    
    def execute(self, context):
        # get essential value
        mtl: bpy.types.Material = context.material
        expected_preset: MaterialPresetType = _MtlPresetEnumPropHelper.get_selection(self.preset_type)
        
        # apply preset to material
        preset_virtools_material(mtl, expected_preset)
        return {'FINISHED'}

class BBP_OT_direct_set_virtools_texture(bpy.types.Operator, UTIL_file_browser.ImportBallanceImage):
    """Import and Assign Texture Directly"""
    bl_idname = "bbp.direct_set_virtools_texture"
    bl_label = "Import and Assign Texture"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # ballance texture order this
        if not PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder(): return False
        # we only accept panel executing
        if context.material is None: return False
        # ok
        return True
    
    def draw(self, context):
        pass

    def invoke(self, context, event):
        # preset tex folder
        self.general_set_filename(PROP_preferences.get_raw_preferences().mBallanceTextureFolder)
        return UTIL_file_browser.ImportBallanceImage.invoke(self, context, event)
    
    def execute(self, context):
        # get assoc mtl
        mtl: bpy.types.Material = context.material
        rawmtl: RawVirtoolsMaterial = get_raw_virtools_material(mtl)

        # import texture according to whether it is ballance texture
        texture_filepath: str = self.general_get_filename()
        try_filepath: str | None = UTIL_ballance_texture.get_ballance_texture_filename(texture_filepath)
        tex: bpy.types.Image
        if try_filepath is None:
            # load as other texture
            tex = UTIL_ballance_texture.load_other_texture(texture_filepath)
            # set texture props
            PROP_virtools_texture.set_raw_virtools_texture(tex, PROP_virtools_texture.get_nonballance_texture_preset())
        else:
            # load as ballance texture
            tex = UTIL_ballance_texture.load_ballance_texture(try_filepath)
            # set texture props
            PROP_virtools_texture.set_raw_virtools_texture(tex, PROP_virtools_texture.get_ballance_texture_preset(try_filepath))
        
        # assign texture
        rawmtl.mTexture = tex
        set_raw_virtools_material(mtl, rawmtl)
        return {'FINISHED'}

#endregion

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
        
        # draw operator
        layout.operator(BBP_OT_preset_virtools_material.bl_idname, icon="PRESET")
        layout.operator(BBP_OT_apply_virtools_material.bl_idname, icon="NODETREE")

        # draw data
        layout.label(text="Color Parameters")
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
        # texture prop with direct importing
        sublay = layout.row()
        sublay.prop(props, 'texture', emboss = True)
        sublay.operator(BBP_OT_direct_set_virtools_texture.bl_idname, text = '', icon = 'FILEBROWSER')
        # texture detail
        if props.texture is not None:
            # have texture, show texture settings and enclosed by a border.
            boxlayout = layout.box()
            boxlayout.label(text="Virtools Texture Settings")
            PROP_virtools_texture.draw_virtools_texture(props.texture, boxlayout)

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
        
def register():
    bpy.utils.register_class(BBP_PG_virtools_material)
    bpy.utils.register_class(BBP_OT_apply_virtools_material)
    bpy.utils.register_class(BBP_OT_preset_virtools_material)
    bpy.utils.register_class(BBP_OT_direct_set_virtools_texture)
    bpy.utils.register_class(BBP_PT_virtools_material)
    
    # add into material metadata
    bpy.types.Material.virtools_material = bpy.props.PointerProperty(type = BBP_PG_virtools_material)

def unregister():
    # del from material metadata
    del bpy.types.Material.virtools_material

    bpy.utils.unregister_class(BBP_PT_virtools_material)
    bpy.utils.unregister_class(BBP_OT_direct_set_virtools_texture)
    bpy.utils.unregister_class(BBP_OT_preset_virtools_material)
    bpy.utils.unregister_class(BBP_OT_apply_virtools_material)
    bpy.utils.unregister_class(BBP_PG_virtools_material)
