import bpy
import typing, math, enum
from . import UTIL_functions, UTIL_virtools_types

class RawVirtoolsCamera():
    # Class Member

    mProjectionType: UTIL_virtools_types.CK_CAMERA_PROJECTION

    mOrthographicZoom: float

    mFrontPlane: float
    mBackPlane: float
    mFov: float

    mAspectRatio: tuple[int, int]

    # Class member default value

    cDefaultProjectionType: typing.ClassVar[UTIL_virtools_types.CK_CAMERA_PROJECTION] = UTIL_virtools_types.CK_CAMERA_PROJECTION.CK_PERSPECTIVEPROJECTION
    
    cDefaultOrthographicZoom: typing.ClassVar[float] = 1.0

    cDefaultFrontPlane: typing.ClassVar[float] = 1.0
    cDefaultBackPlane: typing.ClassVar[float] = 4000.0
    cDefaultFov: typing.ClassVar[float] = 0.5

    cDefaultAspectRatio: typing.ClassVar[tuple[int, int]] = (4, 3)

    def __init__(self, **kwargs):
        # assign default value for each component
        self.mProjectionType = kwargs.get("mProjectionType", RawVirtoolsCamera.cDefaultProjectionType)
        
        self.mOrthographicZoom = kwargs.get("mOrthographicZoom", RawVirtoolsCamera.cDefaultOrthographicZoom)
        
        self.mFrontPlane = kwargs.get("mFrontPlane", RawVirtoolsCamera.cDefaultFrontPlane)
        self.mBackPlane = kwargs.get("mBackPlane", RawVirtoolsCamera.cDefaultBackPlane)
        self.mFov = kwargs.get("mFov", RawVirtoolsCamera.cDefaultFov)
        
        self.mAspectRatio = kwargs.get("mAspectRatio", RawVirtoolsCamera.cDefaultAspectRatio)
        
    def regulate(self) -> None:
        # everything should be positive
        self.mOrthographicZoom = max(0.0, self.mOrthographicZoom)
        self.mFrontPlane = max(0.0, self.mFrontPlane)
        self.mBackPlane = max(0.0, self.mBackPlane)
        self.mFov = max(0.0, self.mFov)

        # aspect ratio should be positive and at least 1
        (w, h) = self.mAspectRatio
        w = max(1, w)
        h = max(1, h)
        self.mAspectRatio = (w, h)

#region Blender Enum Prop Helper

_g_Helper_CK_CAMERA_PROJECTION = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.CK_CAMERA_PROJECTION)

#endregion

class BBP_PG_virtools_camera(bpy.types.PropertyGroup):
    projection_type: bpy.props.EnumProperty(
        name = "Type",
        description = "The type of this camera.",
        items = _g_Helper_CK_CAMERA_PROJECTION.generate_items(),
        default = _g_Helper_CK_CAMERA_PROJECTION.to_selection(RawVirtoolsCamera.cDefaultProjectionType),
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    orthographic_zoom: bpy.props.FloatProperty(
        name = "Orthographic Zoom",
        description = "Defines the orthographic zoom.",
        min = 0.0,
        soft_min = 0.0,
        soft_max = 0.5,
        step = 5,
        default = RawVirtoolsCamera.cDefaultOrthographicZoom,
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    front_plane: bpy.props.FloatProperty(
        name = "Front Plane",
        description = "Defines the front plane.",
        min = 0.0,
        soft_min = 0.0,
        soft_max = 5000.0,
        step = 100,
        default = RawVirtoolsCamera.cDefaultFrontPlane,
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    back_plane: bpy.props.FloatProperty(
        name = "Back Plane",
        description = "Defines the back plane.",
        min = 0.0,
        soft_min = 0.0,
        soft_max = 5000.0,
        step = 100,
        default = RawVirtoolsCamera.cDefaultBackPlane,
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    fov: bpy.props.FloatProperty(
        name = "Field of View",
        description = "Defines the field of view.",
        subtype = 'ANGLE',
        min = 0.0,
        max = math.radians(180.0),
        step = 100,
        precision = 100,
        default = RawVirtoolsCamera.cDefaultFov,
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    aspect_ratio_w: bpy.props.IntProperty(
        name = "Aspect Ratio Width",
        description = "Defines the width of aspect ratio.",
        min = 1,
        soft_min = 1,
        soft_max = 40,
        step = 1,
        default = RawVirtoolsCamera.cDefaultAspectRatio[0],
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

    aspect_ratio_h: bpy.props.IntProperty(
        name = "Aspect Ratio Height",
        description = "Defines the height of aspect ratio.",
        min = 1,
        soft_min = 1,
        soft_max = 40,
        step = 1,
        default = RawVirtoolsCamera.cDefaultAspectRatio[1],
        translation_context = 'BBP_PG_virtools_camera/property'
    ) # type: ignore

#region Getter Setter and Applyer

def get_virtools_camera(cam: bpy.types.Camera) -> BBP_PG_virtools_camera:
    return cam.virtools_camera

def get_raw_virtools_camera(cam: bpy.types.Camera) -> RawVirtoolsCamera:
    props: BBP_PG_virtools_camera = get_virtools_camera(cam)
    rawdata: RawVirtoolsCamera = RawVirtoolsCamera()

    rawdata.mProjectionType = _g_Helper_CK_CAMERA_PROJECTION.get_selection(props.projection_type)

    rawdata.mOrthographicZoom = props.orthographic_zoom

    rawdata.mFrontPlane = props.front_plane
    rawdata.mBackPlane = props.back_plane
    rawdata.mFov = props.fov

    rawdata.mAspectRatio = (props.aspect_ratio_w, props.aspect_ratio_h)

    rawdata.regulate()
    return rawdata

def set_raw_virtools_camera(cam: bpy.types.Camera, rawdata: RawVirtoolsCamera) -> None:
    props: BBP_PG_virtools_camera = get_virtools_camera(cam)

    props.projection_type = _g_Helper_CK_CAMERA_PROJECTION.to_selection(rawdata.mProjectionType)

    props.orthographic_zoom = rawdata.mOrthographicZoom

    props.front_plane = rawdata.mFrontPlane
    props.back_plane = rawdata.mBackPlane
    props.fov = rawdata.mFov

    (props.aspect_ratio_w, props.aspect_ratio_h) = rawdata.mAspectRatio

def apply_to_blender_camera(cam: bpy.types.Camera) -> None:
    # get raw data first
    rawdata: RawVirtoolsCamera = get_raw_virtools_camera(cam)

    # set camera type
    match(rawdata.mProjectionType):
        case UTIL_virtools_types.CK_CAMERA_PROJECTION.CK_PERSPECTIVEPROJECTION:
            cam.type = 'PERSP'
        case UTIL_virtools_types.CK_CAMERA_PROJECTION.CK_ORTHOGRAPHICPROJECTION:
            cam.type = 'ORTHO'

    # set orthographic zoom
    cam.ortho_scale = rawdata.mOrthographicZoom

    # front and back plane
    cam.clip_start = rawdata.mFrontPlane
    cam.clip_end = rawdata.mBackPlane

    # fov
    cam.lens_unit = 'FOV'
    cam.angle = rawdata.mFov

def apply_to_blender_scene_resolution(cam: bpy.types.Camera) -> None:
    # get raw data first
    rawdata: RawVirtoolsCamera = get_raw_virtools_camera(cam)

    # fetch width and height
    (w, h) = rawdata.mAspectRatio

    # compute a proper resolution from this aspect ratio
    # calculate their lcm first
    hw_lcm = math.lcm(w, h)
    # get the first number which is greater than 1000 (1000 is a proper resolution size)
    # and can be integrally divided by this lcm.
    HW_MIN: int = 1000
    min_edge = ((HW_MIN // hw_lcm) + 1) * hw_lcm
    # calculate the final resolution
    if w < h:
        # width is shorter than height, set width as min edge
        width = min_edge
        height = width // w * h
    else:
        # opposite case
        height = min_edge
        width = height // h * w

    # setup resolution
    render_settings = bpy.context.scene.render
    render_settings.resolution_x = width
    render_settings.resolution_y = height

#endregion

#region Aspect Ratio Preset

class AspectRatioPresetType(enum.IntEnum):
    Normal = enum.auto()
    Extended = enum.auto()
    Widescreen = enum.auto()
    Panoramic = enum.auto()

    def to_aspect_ratio(self) -> tuple[int, int]:
        match self:
            case AspectRatioPresetType.Normal: return (4, 3)
            case AspectRatioPresetType.Extended: return (16, 9)
            case AspectRatioPresetType.Widescreen: return (7, 3)
            case AspectRatioPresetType.Panoramic: return (20, 7)

_g_AspectRatioPresetTypeDesc: dict[AspectRatioPresetType, tuple[str, str]] = {
    AspectRatioPresetType.Normal: ("Normal", "Aspect ratio: 4:3."),
    AspectRatioPresetType.Extended: ("Extended", "Aspect ratio: 16:9."),
    AspectRatioPresetType.Widescreen: ("Widescreen", "Aspect ratio: 7:3."),
    AspectRatioPresetType.Panoramic: ("Panoramic", "Aspect ratio: 20:7."),
}

_g_Helper_AspectRatioPresetType = UTIL_functions.EnumPropHelper(
    AspectRatioPresetType,
    lambda x: str(x.value),
    lambda x: AspectRatioPresetType(int(x)),
    lambda x: _g_AspectRatioPresetTypeDesc[x][0],
    lambda x: _g_AspectRatioPresetTypeDesc[x][1],
    lambda _: ""
)

def preset_virtools_camera_aspect_ratio(cam: bpy.types.Camera, preset_type: AspectRatioPresetType) -> None:
    # get raw data from it
    rawdata = get_raw_virtools_camera(cam)
    # modify its aspect ratio
    rawdata.mAspectRatio = preset_type.to_aspect_ratio()
    # rewrite it.
    set_raw_virtools_camera(cam, rawdata)

#endregion

#region Operators

class BBP_OT_apply_virtools_camera(bpy.types.Operator):
    """Apply Virtools Camera to Blender Camera except Resolution."""
    bl_idname = "bbp.apply_virtools_camera"
    bl_label = "Apply to Blender Camera"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_apply_virtools_camera'

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def execute(self, context):
        cam: bpy.types.Camera = context.camera
        apply_to_blender_camera(cam)
        return {'FINISHED'}

class BBP_OT_apply_virtools_camera_resolution(bpy.types.Operator):
    """Apply Virtools Camera Resolution to Blender Scene."""
    bl_idname = "bbp.apply_virtools_camera_resolution"
    bl_label = "Apply to Blender Scene Resolution"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_apply_virtools_camera_resolution'

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def execute(self, context):
        cam: bpy.types.Camera = context.camera
        apply_to_blender_scene_resolution(cam)
        return {'FINISHED'}

class BBP_OT_preset_virtools_camera_aspect_ratio(bpy.types.Operator):
    """Preset Virtools Camera Aspect Ratio with Virtools Presets."""
    bl_idname = "bbp.preset_virtools_camera_aspect_ratio"
    bl_label = "Preset Virtools Camera Aspect Ratio"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_preset_virtools_camera_aspect_ratio'

    preset_type: bpy.props.EnumProperty(
        name = "Preset",
        description = "The preset which you want to apply.",
        items = _g_Helper_AspectRatioPresetType.generate_items(),
        translation_context = 'BBP_OT_preset_virtools_camera_aspect_ratio/property'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, "preset_type")
    
    def execute(self, context):
        # get essential value
        cam: bpy.types.Camera = context.camera
        expected_preset: AspectRatioPresetType = _g_Helper_AspectRatioPresetType.get_selection(self.preset_type)
        
        # apply preset to material
        preset_virtools_camera_aspect_ratio(cam, expected_preset)
        return {'FINISHED'}

#endregion

class BBP_PT_virtools_camera(bpy.types.Panel):
    """Show Virtools Camera Properties"""
    bl_label = "Virtools Camera"
    bl_idname = "BBP_PT_virtools_camera"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data" # idk why blender use `data` as the camera tab same as mesh.
    bl_translation_context = 'BBP_PT_virtools_camera'

    @classmethod
    def poll(cls, context):
        return context.camera is not None

    def draw(self, context):
        # get layout and target
        layout = self.layout
        cam: bpy.types.Camera = context.camera
        props: BBP_PG_virtools_camera = get_virtools_camera(cam)
        rawdata: RawVirtoolsCamera = get_raw_virtools_camera(cam)

        # draw operator
        row = layout.row()
        row.operator(
            BBP_OT_apply_virtools_camera.bl_idname, text='Apply', icon='NODETREE',
            text_ctxt='BBP_PT_virtools_camera/draw')
        row.operator(
            BBP_OT_apply_virtools_camera_resolution.bl_idname, text='Apply Resolution', icon='SCENE',
            text_ctxt='BBP_PT_virtools_camera/draw')

        # draw data
        layout.separator()
        # show camera type first
        layout.prop(props, 'projection_type')
        # all camera has front and back plane
        layout.label(text='Clipping', text_ctxt='BBP_PT_virtools_camera/draw')
        sublayout = layout.column()
        sublayout.use_property_split = True
        sublayout.prop(props, 'front_plane')
        sublayout.prop(props, 'back_plane')
        
        # only perspective camera has fov setting
        if rawdata.mProjectionType == UTIL_virtools_types.CK_CAMERA_PROJECTION.CK_PERSPECTIVEPROJECTION:
            layout.separator()
            layout.label(text='Perspective Parameters', text_ctxt='BBP_PT_virtools_camera/draw')
            sublayout = layout.column()
            sublayout.use_property_split = True
            sublayout.prop(props, 'fov')

        # only orthographic camera has orthographic zoom setting
        if rawdata.mProjectionType == UTIL_virtools_types.CK_CAMERA_PROJECTION.CK_ORTHOGRAPHICPROJECTION:
            layout.separator()
            layout.label(text='Orthographic Parameters', text_ctxt='BBP_PT_virtools_camera/draw')
            sublayout = layout.column()
            sublayout.use_property_split = True
            sublayout.prop(props, 'orthographic_zoom')

        # aspect ratio
        layout.separator()
        row = layout.row()
        row.label(text='Aspect Ratio', text_ctxt='BBP_PT_virtools_camera/draw')
        row.operator(BBP_OT_preset_virtools_camera_aspect_ratio.bl_idname, text='', icon = "PRESET")
        sublayout = layout.row()
        sublayout.use_property_split = False
        sublayout.prop(props, 'aspect_ratio_w', text = '', expand = True)
        sublayout.prop(props, 'aspect_ratio_h', text = '', expand = True)

# Register

def register() -> None:
    bpy.utils.register_class(BBP_PG_virtools_camera)
    bpy.utils.register_class(BBP_OT_apply_virtools_camera)
    bpy.utils.register_class(BBP_OT_apply_virtools_camera_resolution)
    bpy.utils.register_class(BBP_OT_preset_virtools_camera_aspect_ratio)
    bpy.utils.register_class(BBP_PT_virtools_camera)

    # add into camera metadata
    bpy.types.Camera.virtools_camera = bpy.props.PointerProperty(type = BBP_PG_virtools_camera)

def unregister() -> None:
    # remove from metadata
    del bpy.types.Camera.virtools_camera

    bpy.utils.unregister_class(BBP_PT_virtools_camera)
    bpy.utils.unregister_class(BBP_OT_preset_virtools_camera_aspect_ratio)
    bpy.utils.unregister_class(BBP_OT_apply_virtools_camera_resolution)
    bpy.utils.unregister_class(BBP_OT_apply_virtools_camera)
    bpy.utils.unregister_class(BBP_PG_virtools_camera)


