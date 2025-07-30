import bpy, mathutils
from bpy.types import Context
import typing, math
from . import UTIL_functions, UTIL_virtools_types

# Raw Data

class RawVirtoolsLight():
    # Class member

    mType: UTIL_virtools_types.VXLIGHT_TYPE
    mColor: UTIL_virtools_types.VxColor

    mConstantAttenuation: float
    mLinearAttenuation: float
    mQuadraticAttenuation: float

    mRange: float

    mHotSpot: float
    mFalloff: float
    mFalloffShape: float

    # Class member default value

    cDefaultType: typing.ClassVar[UTIL_virtools_types.VXLIGHT_TYPE] = UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTPOINT
    cDefaultColor: typing.ClassVar[UTIL_virtools_types.VxColor] = UTIL_virtools_types.VxColor(1.0, 1.0, 1.0, 1.0)

    cDefaultConstantAttenuation: typing.ClassVar[float] = 1.0
    cDefaultLinearAttenuation: typing.ClassVar[float] = 0.0
    cDefaultQuadraticAttenuation: typing.ClassVar[float] = 0.0

    cDefaultRange: typing.ClassVar[float] = 100.0

    cDefaultHotSpot: typing.ClassVar[float] = math.radians(40)
    cDefaultFalloff: typing.ClassVar[float] = math.radians(45)
    cDefaultFalloffShape: typing.ClassVar[float] = 1.0

    def __init__(self, **kwargs):
        # assign default value for each component
        self.mType = kwargs.get('mType', RawVirtoolsLight.cDefaultType)
        self.mColor = kwargs.get('mColor', RawVirtoolsLight.cDefaultColor).clone()

        self.mConstantAttenuation = kwargs.get('mConstantAttenuation', RawVirtoolsLight.cDefaultConstantAttenuation)
        self.mLinearAttenuation = kwargs.get('mLinearAttenuation', RawVirtoolsLight.cDefaultLinearAttenuation)
        self.mQuadraticAttenuation = kwargs.get('mQuadraticAttenuation', RawVirtoolsLight.cDefaultQuadraticAttenuation)
        
        self.mRange = kwargs.get('mRange', RawVirtoolsLight.cDefaultRange)

        self.mHotSpot = kwargs.get('mHotSpot', RawVirtoolsLight.cDefaultHotSpot)
        self.mFalloff = kwargs.get('mFalloff', RawVirtoolsLight.cDefaultFalloff)
        self.mFalloffShape = kwargs.get('mFalloffShape', RawVirtoolsLight.cDefaultFalloffShape)

    def regulate(self) -> None:
        # regulate color and reset its alpha value
        self.mColor.regulate()
        self.mColor.a = 1.0
        # regulate range
        self.mRange = UTIL_functions.clamp_float(self.mRange, 0.0, 200.0)

        # regulate attenuation
        self.mConstantAttenuation = UTIL_functions.clamp_float(self.mConstantAttenuation, 0.0, 10.0)
        self.mLinearAttenuation = UTIL_functions.clamp_float(self.mLinearAttenuation, 0.0, 10.0)
        self.mQuadraticAttenuation = UTIL_functions.clamp_float(self.mQuadraticAttenuation, 0.0, 10.0)

        # regulate spot cone
        self.mHotSpot = UTIL_functions.clamp_float(self.mHotSpot, 0.0, math.radians(180))
        self.mFalloff = UTIL_functions.clamp_float(self.mFalloff, 0.0, math.radians(180))
        self.mFalloffShape = UTIL_functions.clamp_float(self.mFalloffShape, 0.0, 10.0)
        # regulate spot cone size order
        if self.mFalloff < self.mHotSpot:
            self.mFalloff = self.mHotSpot

# Blender Property Group

_g_Helper_VXLIGHT_TYPE = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.VXLIGHT_TYPE)

class BBP_PG_virtools_light(bpy.types.PropertyGroup):
    light_type: bpy.props.EnumProperty(
        name = "Type",
        description = "The type of this light",
        items = _g_Helper_VXLIGHT_TYPE.generate_items(),
        default = _g_Helper_VXLIGHT_TYPE.to_selection(RawVirtoolsLight.cDefaultType),
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    light_color: bpy.props.FloatVectorProperty(
        name = "Color",
        description = "Defines the red, green and blue components of the light.",
        subtype = 'COLOR',
        min = 0.0,
        max = 1.0,
        size = 3,
        default = RawVirtoolsLight.cDefaultColor.to_const_rgb(),
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    constant_attenuation: bpy.props.FloatProperty(
        name = "Constant Attenuation",
        description = "Defines the constant attenuation factor.",
        min = 0.0,
        max = 10.0,
        step = 10,
        default = RawVirtoolsLight.cDefaultConstantAttenuation,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    linear_attenuation: bpy.props.FloatProperty(
        name = "Linear Attenuation",
        description = "Defines the linear attenuation factor.",
        min = 0.0,
        max = 10.0,
        step = 10,
        default = RawVirtoolsLight.cDefaultLinearAttenuation,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    quadratic_attenuation: bpy.props.FloatProperty(
        name = "Quadratic Attenuation",
        description = "Defines the quadratic attenuation factor.",
        min = 0.0,
        max = 10.0,
        step = 10,
        default = RawVirtoolsLight.cDefaultQuadraticAttenuation,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    light_range: bpy.props.FloatProperty(
        name = "Range",
        description = "Defines the radius of the lighting area.",
        min = 0.0,
        max = 200.0,
        step = 100,
        default = RawVirtoolsLight.cDefaultRange,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    hot_spot: bpy.props.FloatProperty(
        name = "Hot Spot",
        description = "Sets the value of the hot spot of the light.",
        min = 0.0,
        max = math.radians(180),
        subtype = 'ANGLE',
        default = RawVirtoolsLight.cDefaultHotSpot,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    falloff: bpy.props.FloatProperty(
        name = "Fall Off",
        description = "Sets the light fall off rate.",
        min = 0.0,
        max = math.radians(180),
        subtype = 'ANGLE',
        default = RawVirtoolsLight.cDefaultFalloff,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

    falloff_shape: bpy.props.FloatProperty(
        name = "Fall Off Shape",
        description = "Sets the value of the light fall off shape.",
        min = 0.0,
        max = 10.0,
        step = 10,
        default = RawVirtoolsLight.cDefaultFalloffShape,
        translation_context = 'BBP_PG_virtools_light/property'
    ) # type: ignore

# Getter Setter and Applyer

def get_virtools_light(lit: bpy.types.Light) -> BBP_PG_virtools_light:
    return lit.virtools_light

def get_raw_virtools_light(lit: bpy.types.Light) -> RawVirtoolsLight:
    props: BBP_PG_virtools_light = get_virtools_light(lit)
    rawdata: RawVirtoolsLight = RawVirtoolsLight()

    rawdata.mType = _g_Helper_VXLIGHT_TYPE.get_selection(props.light_type)
    rawdata.mColor.from_const_rgb(props.light_color)

    rawdata.mConstantAttenuation = props.constant_attenuation
    rawdata.mLinearAttenuation = props.linear_attenuation
    rawdata.mQuadraticAttenuation = props.quadratic_attenuation

    rawdata.mRange = props.light_range

    rawdata.mHotSpot = props.hot_spot
    rawdata.mFalloff = props.falloff
    rawdata.mFalloffShape = props.falloff_shape

    rawdata.regulate()
    return rawdata

def set_raw_virtools_light(lit: bpy.types.Light, rawdata: RawVirtoolsLight) -> None:
    props: BBP_PG_virtools_light = get_virtools_light(lit)

    props.light_type = _g_Helper_VXLIGHT_TYPE.to_selection(rawdata.mType)
    props.light_color = rawdata.mColor.to_const_rgb()

    props.constant_attenuation = rawdata.mConstantAttenuation
    props.linear_attenuation = rawdata.mLinearAttenuation
    props.quadratic_attenuation = rawdata.mQuadraticAttenuation

    props.light_range = rawdata.mRange

    props.hot_spot = rawdata.mHotSpot
    props.falloff = rawdata.mFalloff
    props.falloff_shape = rawdata.mFalloffShape

def apply_to_blender_light(lit: bpy.types.Light) -> None:
    # get raw data first
    rawdata: RawVirtoolsLight = get_raw_virtools_light(lit)

    # set light type and color
    match(rawdata.mType):
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTPOINT:
            lit.type = 'POINT'
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTSPOT:
            lit.type = 'SPOT'
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTDIREC:
            lit.type = 'SUN'
    lit.color = rawdata.mColor.to_const_rgb()

    # MARK:
    # After set light type, we must re-fetch light object,
    # because it seems that the object hold by this variable 
    # is not the object after light type changes.
    # 
    # If I do not do this, function will throw exception 
    # like `'PointLight' object has no attribute 'spot_size'`.
    lit = bpy.data.lights[lit.name]
    match(rawdata.mType):
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTPOINT:
            point_lit: bpy.types.PointLight = typing.cast(bpy.types.PointLight, lit)
            point_lit.shadow_soft_size = rawdata.mRange
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTSPOT:
            spot_lit: bpy.types.SpotLight = typing.cast(bpy.types.SpotLight, lit)
            spot_lit.shadow_soft_size = rawdata.mRange
            spot_lit.spot_size = rawdata.mFalloff
            if rawdata.mFalloff == 0: spot_lit.spot_blend = 0.0
            else: spot_lit.spot_blend = 1.0 - rawdata.mHotSpot / rawdata.mFalloff
        case UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTDIREC:
            pass

# Operators

class BBP_OT_apply_virtools_light(bpy.types.Operator):
    """Apply Virtools Light to Blender Light."""
    bl_idname = "bbp.apply_virtools_light"
    bl_label = "Apply to Blender Light"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_apply_virtools_light'

    @classmethod
    def poll(cls, context):
        return context.light is not None

    def execute(self, context):
        lit: bpy.types.Light = context.light
        apply_to_blender_light(lit)
        return {'FINISHED'}

# Display Panel

class BBP_PT_virtools_light(bpy.types.Panel):
    """Show Virtools Light Properties"""
    bl_label = "Virtools Light"
    bl_idname = "BBP_PT_virtools_light"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data" # idk why blender use `data` as the light tab same as mesh.
    bl_translation_context = 'BBP_PT_virtools_light'

    @classmethod
    def poll(cls, context):
        return context.light is not None

    def draw(self, context):
        # get layout and target
        layout = self.layout
        layout.use_property_split = True
        lit: bpy.types.Light = context.light
        props: BBP_PG_virtools_light = get_virtools_light(lit)
        rawdata: RawVirtoolsLight = get_raw_virtools_light(lit)

        # draw operator
        layout.operator(
            BBP_OT_apply_virtools_light.bl_idname, text='Apply', icon='NODETREE',
            text_ctxt='BBP_PT_virtools_light/draw')

        # draw data
        layout.separator()
        layout.label(text='Basics', text_ctxt='BBP_PT_virtools_light/draw')
        # all lights has type and color property
        sublayout = layout.row()
        sublayout.use_property_split = False
        sublayout.prop(props, 'light_type', expand = True)
        layout.prop(props, 'light_color')
        # all light has range property exception directional light
        if rawdata.mType != UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTDIREC:
            layout.prop(props, 'light_range')

        # all light has attenuation exception directional light
        if rawdata.mType != UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTDIREC:
            layout.separator()
            layout.label(text='Attenuation', text_ctxt='BBP_PT_virtools_light/draw')
            layout.prop(props, 'constant_attenuation', text='Constant', text_ctxt='BBP_PT_virtools_light/draw')
            layout.prop(props, 'linear_attenuation', text='Linear', text_ctxt='BBP_PT_virtools_light/draw')
            layout.prop(props, 'quadratic_attenuation', text='Quadratic', text_ctxt='BBP_PT_virtools_light/draw')

        # only spot light has spot cone properties.
        if rawdata.mType == UTIL_virtools_types.VXLIGHT_TYPE.VX_LIGHTSPOT:
            layout.separator()
            layout.label(text='Spot Cone', text_ctxt='BBP_PT_virtools_light/draw')
            layout.prop(props, 'hot_spot')
            layout.prop(props, 'falloff')
            layout.prop(props, 'falloff_shape')

# Register

def register() -> None:
    bpy.utils.register_class(BBP_PG_virtools_light)
    bpy.utils.register_class(BBP_OT_apply_virtools_light)
    bpy.utils.register_class(BBP_PT_virtools_light)

    # add into light metadata
    bpy.types.Light.virtools_light = bpy.props.PointerProperty(type = BBP_PG_virtools_light)

def unregister() -> None:
    # remove from metadata
    del bpy.types.Light.virtools_light

    bpy.utils.unregister_class(BBP_PT_virtools_light)
    bpy.utils.unregister_class(BBP_OT_apply_virtools_light)
    bpy.utils.unregister_class(BBP_PG_virtools_light)
