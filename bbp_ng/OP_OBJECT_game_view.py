import bpy, mathutils
import typing, enum, math
from . import UTIL_functions

# TODO:
# This file should have fully refactor after we finish Virtools Camera import and export,
# because this module is highly rely on it. Current implementation is a compromise.
# There is a list of things to be done:
# - Remove BBP_OT_game_resolution operator, because Virtools Camera will have similar function in panel.
# - Update BBP_OT_game_cameraoperator with Virtools Camera.

#region Game Resolution

class ResolutionKind(enum.IntEnum):
    Normal = enum.auto()
    Extended = enum.auto()
    Widescreen = enum.auto()
    Panoramic = enum.auto()

    def to_resolution(self) -> tuple[int, int]:
        match self:
            case ResolutionKind.Normal: return (1024, 768)
            case ResolutionKind.Extended: return (1280, 720)
            case ResolutionKind.Widescreen: return (1400, 600)
            case ResolutionKind.Panoramic: return (2000, 700)

_g_ResolutionKindDesc: dict[ResolutionKind, tuple[str, str]] = {
    ResolutionKind.Normal: ("Normal", "Aspect ratio: 4:3."),
    ResolutionKind.Extended: ("Extended", "Aspect ratio: 16:9."),
    ResolutionKind.Widescreen: ("Widescreen", "Aspect ratio: 7:3."),
    ResolutionKind.Panoramic: ("Panoramic", "Aspect ratio: 20:7."),
}
_g_EnumHelper_ResolutionKind = UTIL_functions.EnumPropHelper(
    ResolutionKind,
    lambda x: str(x.value),
    lambda x: ResolutionKind(int(x)),
    lambda x: _g_ResolutionKindDesc[x][0],
    lambda x: _g_ResolutionKindDesc[x][1],
    lambda _: ""
)

class BBP_OT_game_resolution(bpy.types.Operator):
    """Set Blender render resolution to Ballance game"""
    bl_idname = "bbp.game_resolution"
    bl_label = "Game Resolution"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_game_resolution'

    resolution_kind: bpy.props.EnumProperty(
        name = "Resolution Kind",
        description = "The type of preset resolution.",
        items = _g_EnumHelper_ResolutionKind.generate_items(),
        default = _g_EnumHelper_ResolutionKind.to_selection(ResolutionKind.Normal),
        translation_context = 'BBP_OT_game_resolution/property'
    ) # type: ignore

    def invoke(self, context, event):
        return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'resolution_kind')

    def execute(self, context):
        # fetch resolution
        resolution_kind = _g_EnumHelper_ResolutionKind.get_selection(self.resolution_kind)
        resolution = resolution_kind.to_resolution()
        # setup resolution
        render_settings = bpy.context.scene.render
        render_settings.resolution_x = resolution[0]
        render_settings.resolution_y = resolution[1]
        return {'FINISHED'}

#endregion

#region Game Camera

#region Enum Defines

class TargetKind(enum.IntEnum):
    Cursor = enum.auto()
    ActiveObject = enum.auto()
_g_TargetKindDesc: dict[TargetKind, tuple[str, str, str]] = {
    TargetKind.Cursor: ("3D Cursor", "3D cursor is player ball.", "CURSOR"),
    TargetKind.ActiveObject: ("Active Object", "The origin point of active object is player ball.", "OBJECT_DATA"),
}
_g_EnumHelper_TargetKind = UTIL_functions.EnumPropHelper(
    TargetKind,
    lambda x: str(x.value),
    lambda x: TargetKind(int(x)),
    lambda x: _g_TargetKindDesc[x][0],
    lambda x: _g_TargetKindDesc[x][1],
    lambda x: _g_TargetKindDesc[x][2],
)

class RotationKind(enum.IntEnum):
    Preset = enum.auto()
    Custom = enum.auto()
_g_RotationKindDesc: dict[RotationKind, tuple[str, str]] = {
    RotationKind.Preset: ("Preset", "8 preset rotation angles usually used in game."),
    RotationKind.Custom: ("Custom", "User manually input rotation angle.")
}
_g_EnumHelper_RotationKind = UTIL_functions.EnumPropHelper(
    RotationKind,
    lambda x: str(x.value),
    lambda x: RotationKind(int(x)),
    lambda x: _g_RotationKindDesc[x][0],
    lambda x: _g_RotationKindDesc[x][1],
    lambda _: ""
)

class RotationAngle(enum.IntEnum):
    Deg0 = enum.auto()
    Deg45 = enum.auto()
    Deg90 = enum.auto()
    Deg135 = enum.auto()
    Deg180 = enum.auto()
    Deg225 = enum.auto()
    Deg270 = enum.auto()
    Deg315 = enum.auto()

    def to_degree(self) -> float:
        match self:
            case RotationAngle.Deg0: return 0
            case RotationAngle.Deg45: return 45
            case RotationAngle.Deg90: return 90
            case RotationAngle.Deg135: return 135
            case RotationAngle.Deg180: return 180
            case RotationAngle.Deg225: return 225
            case RotationAngle.Deg270: return 270
            case RotationAngle.Deg315: return 315
    
    def to_radians(self) -> float:
        return math.radians(self.to_degree())

_g_RotationAngleDesc: dict[RotationAngle, tuple[str, str]] = {
    # TODO: Add axis direction in description after we add Camera support when importing
    # (because we only can confirm game camera behavior after that).
    RotationAngle.Deg0: ("0 Degree", "0 degree"),
    RotationAngle.Deg45: ("45 Degree", "45 degree"),
    RotationAngle.Deg90: ("90 Degree", "90 degree"),
    RotationAngle.Deg135: ("135 Degree", "135 degree"),
    RotationAngle.Deg180: ("180 Degree", "180 degree"),
    RotationAngle.Deg225: ("225 Degree", "225 degree"),
    RotationAngle.Deg270: ("270 Degree", "270 degree"),
    RotationAngle.Deg315: ("315 Degree", "315 degree"),
}
_g_EnumHelper_RotationAngle = UTIL_functions.EnumPropHelper(
    RotationAngle,
    lambda x: str(x.value),
    lambda x: RotationAngle(int(x)),
    lambda x: _g_RotationAngleDesc[x][0],
    lambda x: _g_RotationAngleDesc[x][1],
    lambda _: ""
)

class PerspectiveKind(enum.IntEnum):
    Ordinary = enum.auto()
    Lift = enum.auto()
    EasterEgg = enum.auto()
_g_PerspectiveKindDesc: dict[PerspectiveKind, tuple[str, str]] = {
    PerspectiveKind.Ordinary: ("Ordinary", "The default perspective for game camera."),
    PerspectiveKind.Lift: ("Lift", "Lifted camera in game for downcast level."),
    PerspectiveKind.EasterEgg: ("Easter Egg", "A very close view to player ball in game."),
}
_g_EnumHelper_PerspectiveKind = UTIL_functions.EnumPropHelper(
    PerspectiveKind,
    lambda x: str(x.value),
    lambda x: PerspectiveKind(int(x)),
    lambda x: _g_PerspectiveKindDesc[x][0],
    lambda x: _g_PerspectiveKindDesc[x][1],
    lambda _: ""
)

#endregion

class BBP_OT_game_camera(bpy.types.Operator):
    """Order active camera look at target like Ballance does"""
    bl_idname = "bbp.game_camera"
    bl_label = "Game Camera"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_game_camera'

    target_kind: bpy.props.EnumProperty(
        name = "Target Kind",
        description = "",
        items = _g_EnumHelper_TargetKind.generate_items(),
        default = _g_EnumHelper_TargetKind.to_selection(TargetKind.Cursor),
        translation_context = 'BBP_OT_game_camera/property'
    ) # type: ignore

    rotation_kind: bpy.props.EnumProperty(
        name = "Rotation Angle Kind",
        description = "",
        items = _g_EnumHelper_RotationKind.generate_items(),
        default = _g_EnumHelper_RotationKind.to_selection(RotationKind.Preset),
        translation_context = 'BBP_OT_game_camera/property'
    ) # type: ignore
    preset_rotation_angle: bpy.props.EnumProperty(
        name = "Preset Rotation Angle",
        description = "",
        items = _g_EnumHelper_RotationAngle.generate_items(),
        default = _g_EnumHelper_RotationAngle.to_selection(RotationAngle.Deg0),
        translation_context = 'BBP_OT_game_camera/property'
    ) # type: ignore
    custom_rotation_angle: bpy.props.FloatProperty(
        name = "Custom Rotation Angle",
        description = "The rotation angle of camera relative to 3D Cursor or Active Object",
        subtype = 'ANGLE',
        min = 0, max = math.radians(360),
        step = 100,
        # MARK: What the fuck of the precision?
        # I set it to 2 but it doesn't work so I forcely set it to 100.
        precision = 100,
        translation_context = 'BBP_OT_game_camera/property'
    ) # type: ignore

    perspective_kind: bpy.props.EnumProperty(
        name = "Rotation Angle Kind",
        description = "",
        items = _g_EnumHelper_PerspectiveKind.generate_items(),
        default = _g_EnumHelper_PerspectiveKind.to_selection(PerspectiveKind.Ordinary),
        translation_context = 'BBP_OT_game_camera/property'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        # find camera object
        camera_obj = _find_camera_obj()
        if camera_obj is None: return False
        # find active object
        active_obj = bpy.context.active_object
        if active_obj is None: return False
        # camera object should not be active object
        return camera_obj != active_obj

    def invoke(self, context, event):
        # order user enter camera view
        _enter_camera_view()
        # then execute following code
        return self.execute(context)
    
    def draw(self, context):
        layout = self.layout

        # Show target picker
        layout.label(text='Target', text_ctxt='BBP_OT_game_camera/draw')
        layout.row().prop(self, 'target_kind', expand=True)

        # Show rotation angle according to different types.
        layout.separator()
        layout.label(text='Rotation', text_ctxt='BBP_OT_game_camera/draw')
        layout.row().prop(self, 'rotation_kind', expand=True)
        rot_kind = _g_EnumHelper_RotationKind.get_selection(self.rotation_kind)
        match rot_kind:
            case RotationKind.Preset:
                layout.prop(self, 'preset_rotation_angle', text='')
            case RotationKind.Custom:
                layout.prop(self, 'custom_rotation_angle', text='')

        # Show perspective kind
        layout.separator()
        layout.label(text='Perspective', text_ctxt='BBP_OT_game_camera/draw')
        layout.row().prop(self, 'perspective_kind', expand=True)

    def execute(self, context):
        # fetch angle
        angle: float
        rot_kind = _g_EnumHelper_RotationKind.get_selection(self.rotation_kind)
        match rot_kind:
            case RotationKind.Preset:
                rot_angle = _g_EnumHelper_RotationAngle.get_selection(self.preset_rotation_angle)
                angle = rot_angle.to_radians()
            case RotationKind.Custom:
                angle = float(self.custom_rotation_angle)
        # fetch others
        camera_obj = typing.cast(bpy.types.Object, _find_camera_obj())
        target_kind = _g_EnumHelper_TargetKind.get_selection(self.target_kind)
        perspective_kind = _g_EnumHelper_PerspectiveKind.get_selection(self.perspective_kind)

        # setup its transform and properties
        glob_trans = _fetch_glob_translation(camera_obj, target_kind)
        _setup_camera_transform(camera_obj, angle, perspective_kind, glob_trans)
        _setup_camera_properties(camera_obj)

        # return
        return {'FINISHED'}

def _find_3d_view_space() -> bpy.types.SpaceView3D | None:
    # get current area
    area = bpy.context.area
    if area is None: return None

    # check whether it is 3d view
    if area.type != 'VIEW_3D': return None

    # get the active space in area
    space = area.spaces.active
    if space is None: return None

    # okey. cast its type and return
    return typing.cast(bpy.types.SpaceView3D, space)

def _enter_camera_view() -> None:
    space = _find_3d_view_space()
    if space is None: return

    region = space.region_3d
    if region is None: return

    region.view_perspective = 'CAMERA'

def _find_camera_obj() -> bpy.types.Object | None:
    space = _find_3d_view_space()
    if space is None: return None

    return space.camera

def _fetch_glob_translation(camobj: bpy.types.Object, target_kind: TargetKind) -> mathutils.Vector:
    # we have checked any bad cases in "poll",
    # so we can simply return value in there without any check.
    match target_kind:
        case TargetKind.Cursor:
            return bpy.context.scene.cursor.location
        case TargetKind.ActiveObject:
            return bpy.context.active_object.location

def _setup_camera_transform(camobj: bpy.types.Object, angle: float, perspective: PerspectiveKind, glob_trans: mathutils.Vector) -> None:
    # decide the camera offset with ref point
    ingamecam_pos: mathutils.Vector
    match perspective:
        case PerspectiveKind.Ordinary:
            ingamecam_pos = mathutils.Vector((22, 0, 35))
        case PerspectiveKind.Lift:
            ingamecam_pos = mathutils.Vector((22, 0, 35 + 20))
        case PerspectiveKind.EasterEgg:
            ingamecam_pos = mathutils.Vector((22, 0, 3.86))

    # decide the position of ref point
    refpot_pos: mathutils.Vector
    match perspective:
        case PerspectiveKind.EasterEgg:
            refpot_pos = mathutils.Vector((4.4, 0, 0))
        case _:
            refpot_pos = mathutils.Vector((0, 0, 0))

    # perform rotation for both positions
    player_rot_mat = mathutils.Matrix.Rotation(angle, 4, 'Z')
    ingamecam_pos = ingamecam_pos @ player_rot_mat
    refpot_pos = refpot_pos @ player_rot_mat

    # calculate the rotation of camera
    
    # YYC MARK:
    # Following code are linear algebra required.
    # 
    # We can calulate the direction of camera by simply substracting 2 vector.
    # In default, the direction of camera is -Z, up direction is +Y.
    # So this computed direction is -Z in new cooredinate system.
    # Now we can compute +Z axis in this new coordinate system.
    new_z = (ingamecam_pos - refpot_pos)
    new_z.normalize()
    # For ballance camera, all camera is +Z up.
    # So we can use it to compute +X axis in new coordinate system
    assistant_y = mathutils.Vector((0, 0, 1))
    new_x = typing.cast(mathutils.Vector, assistant_y.cross(new_z))
    new_x.normalize()
    # now we calc the final axis
    new_y = typing.cast(mathutils.Vector, new_z.cross(new_x))
    new_y.normalize()
    # okey, we conbine them as a matrix
    rot_mat = mathutils.Matrix((
        (new_x.x, new_y.x, new_z.x, 0),
        (new_x.y, new_y.y, new_z.y, 0),
        (new_x.z, new_y.z, new_z.z, 0),
        (0, 0, 0, 1)
    ))

    # calc the final transform matrix and apply it
    trans_mat = mathutils.Matrix.Translation(ingamecam_pos)
    glob_trans_mat = mathutils.Matrix.Translation(glob_trans)
    camobj.matrix_world = glob_trans_mat @ trans_mat @ rot_mat

def _setup_camera_properties(camobj: bpy.types.Object) -> None:
    # fetch camera
    camera = typing.cast(bpy.types.Camera, camobj.data)

    # set clipping
    camera.clip_start = 4
    camera.clip_end = 1200
    # set FOV
    camera.lens_unit = 'FOV'
    camera.angle = math.radians(58)

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_game_resolution)
    bpy.utils.register_class(BBP_OT_game_camera)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_game_camera)
    bpy.utils.unregister_class(BBP_OT_game_resolution)

