import bpy, mathutils
import enum, typing
from . import UTIL_functions

#region Align Mode 

class AlignMode(enum.IntEnum):
    Min = enum.auto()
    BBoxCenter = enum.auto()
    AxisCenter = enum.auto()
    Max = enum.auto()
_g_AlignModeDesc: dict[AlignMode, tuple[str, str]] = {
    AlignMode.Min: ("Min", "The min value in specified axis."),
    AlignMode.BBoxCenter: ("Center (Bounding Box)", "The bounding box center in specified axis."),
    AlignMode.AxisCenter: ("Center (Axis)", "The object's source point in specified axis."),
    AlignMode.Max: ("Max", "The max value in specified axis."),
}
_g_EnumHelper_AlignMode: UTIL_functions.EnumPropHelper = UTIL_functions.EnumPropHelper(
    AlignMode,
    lambda x: str(x.value),
    lambda x: AlignMode(int(x)),
    lambda x: _g_AlignModeDesc[x][0],
    lambda x: _g_AlignModeDesc[x][1],
    lambda _: ''
)

#endregion

#region Align Cache Implement

## As we known, 3ds Max's align window have a Apply button which can apply current align to scene, 
#  and user call set next align settings after clicking Apply. It will not affect previous set align settings.
#  But Blender have no vanilla Apply function for operator. The only possible way is re-run this operator.
#  However the experience is pretty shit. Because the window still locate at the left-bottom corner.
#  User can't keep up to change it.
#  
#  We use a dirty way to implement Apply function. The solution is pretty like BME struct adder.
#  We use a CollectionProperty to store all align steps.
#  And use a BoolProperty with update function to implement Apply button. Once its value changed,
#  reset its value (order a recursive hinder), and add a new settings.

class BBP_PG_legacy_align_history(bpy.types.PropertyGroup):
    align_x: bpy.props.BoolProperty(
        name = "X Position",
        default = False,
    )
    align_y: bpy.props.BoolProperty(
        name = "Y Position",
        default = False,
    )
    align_z: bpy.props.BoolProperty(
        name = "Z Position",
        default = False,
    )
    current_align_mode: bpy.props.EnumProperty(
        name = "Current Object (Active Object)",
        items = _g_EnumHelper_AlignMode.generate_items(),
        default = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter),
    )
    target_align_mode: bpy.props.EnumProperty(
        name = "Target Objects (Other Objects)",
        items = _g_EnumHelper_AlignMode.generate_items(),
        default = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter),
    )

#endregion

class BBP_OT_legacy_align(bpy.types.Operator):
    """Align Objects with 3ds Max Style"""
    bl_idname = "bbp.legacy_align"
    bl_label = "3ds Max Align"
    bl_options = {'REGISTER', 'UNDO'}

    # the updator for apply flag value
    def apply_flag_updated(self, context):
        # check hinder and set hinder first
        if self.recursive_hinder: return
        self.recursive_hinder = True

        # reset apply button value (default is True)
        # due to the hinder, no recursive calling will happend
        if self.apply_flag == True: return
        self.apply_flag = True

        # add a new entry in history
        self.align_history.add()

        # reset hinder
        self.recursive_hinder = False
        # blender required
        return None
    
    apply_flag: bpy.props.BoolProperty(
        name = "Apply Flag",
        description = "Internal flag.",
        options = {'HIDDEN', 'SKIP_SAVE'},
        default = True, # default True value to make it as a "light" button, not a grey one.
        update = apply_flag_updated,
    )
    recursive_hinder: bpy.props.BoolProperty(
        name = "Recursive Hinder",
        description = "An internal flag to prevent the loop calling to apply_flags's updator.",
        options = {'HIDDEN', 'SKIP_SAVE'},
        default = False,
    )
    align_history : bpy.props.CollectionProperty(
        name = "Historys",
        description = "Align history.",
        type = BBP_PG_legacy_align_history,
    )
    
    @classmethod
    def poll(self, context):
        return _check_align_requirement()

    def invoke(self, context, event):
        # clear history and add 1 entry for following functions
        self.align_history.clear()
        self.align_history.add()
        # run execute() function
        return self.execute(context)
    
    def execute(self, context):
        # get processed objects
        (current_obj, target_objs) = _prepare_objects()
        # iterate history to align objects
        entry: BBP_PG_legacy_align_history
        for entry in self.align_history:
            _align_objects(
                current_obj, target_objs,
                entry.align_x, entry.align_y, entry.align_z,
                _g_EnumHelper_AlignMode.get_selection(entry.current_align_mode), 
                _g_EnumHelper_AlignMode.get_selection(entry.target_align_mode)
            )
        return {'FINISHED'}

    def draw(self, context):
        # get last entry in history to show
        entry: BBP_PG_legacy_align_history = self.align_history[-1]

        layout = self.layout
        col = layout.column()

        # show axis
        col.label(text="Align Axis")
        row = col.row()
        row.prop(entry, "align_x", toggle = 1)
        row.prop(entry, "align_y", toggle = 1)
        row.prop(entry, "align_z", toggle = 1)

        # show mode
        col.separator()
        col.label(text = 'Current Object (Active Object)')
        col.prop(entry, "current_align_mode", expand = True)
        col.label(text = 'Target Objects (Other Objects)')
        col.prop(entry, "target_align_mode", expand = True)

        # show apply button
        col.separator()
        col.prop(self, 'apply_flag', text = 'Apply', icon = 'CHECKMARK', toggle = 1)

#region Core Functions

def _check_align_requirement() -> bool:
    # check current obj
    if bpy.context.active_object is None:
        return False

    # check target obj with filter of current obj
    length = len(bpy.context.selected_objects)
    if bpy.context.active_object in bpy.context.selected_objects:
        length -= 1
    return length != 0

def _prepare_objects() -> tuple[bpy.types.Object, set[bpy.types.Object]]:
    # get current object
    current_obj: bpy.types.Object = bpy.context.active_object

    # get target objects
    target_objs: set[bpy.types.Object] = set(bpy.context.selected_objects)
    # remove active one
    if current_obj in target_objs:
        target_objs.remove(current_obj)

    # return value
    return (current_obj, target_objs)

def _align_objects(
        current_obj: bpy.types.Object, target_objs: set[bpy.types.Object],
        align_x: bool, align_y: bool, align_z: bool, current_mode: AlignMode, target_mode: AlignMode) -> None:
    # if no align, skip
    if not (align_x or align_y or align_z):
        return

    # calc current object data
    current_obj_bbox: tuple[mathutils.Vector] = tuple(current_obj.matrix_world @ mathutils.Vector(corner) for corner in current_obj.bound_box)
    current_obj_ref: mathutils.Vector = _get_object_ref_point(current_obj, current_obj_bbox, current_mode)

    # process each target obj
    for target_obj in target_objs:
        # calc target object data
        target_obj_bbox: tuple[mathutils.Vector] = tuple(target_obj.matrix_world @ mathutils.Vector(corner) for corner in target_obj.bound_box)
        target_obj_ref: mathutils.Vector = _get_object_ref_point(target_obj, target_obj_bbox, target_mode)
        # do align
        if align_x:
            target_obj.location.x += current_obj_ref.x - target_obj_ref.x
        if align_y:
            target_obj.location.y += current_obj_ref.y - target_obj_ref.y
        if align_z:
            target_obj.location.z += current_obj_ref.z - target_obj_ref.z

def _get_object_ref_point(obj: bpy.types.Object, corners: tuple[mathutils.Vector], mode: AlignMode) -> mathutils.Vector:
    ref_pos: mathutils.Vector = mathutils.Vector((0, 0, 0))

    match(mode):
        case AlignMode.Min:
            ref_pos.x = min((vec.x for vec in corners))
            ref_pos.y = min((vec.y for vec in corners))
            ref_pos.z = min((vec.z for vec in corners))
        case AlignMode.Max:
            ref_pos.x = max((vec.x for vec in corners))
            ref_pos.y = max((vec.y for vec in corners))
            ref_pos.z = max((vec.z for vec in corners))
        case AlignMode.BBoxCenter:
            max_vec_cache: mathutils.Vector = mathutils.Vector((0, 0, 0))
            min_vec_cache: mathutils.Vector = mathutils.Vector((0, 0, 0))

            min_vec_cache.x = min((vec.x for vec in corners))
            min_vec_cache.y = min((vec.y for vec in corners))
            min_vec_cache.z = min((vec.z for vec in corners))
            max_vec_cache.x = max((vec.x for vec in corners))
            max_vec_cache.y = max((vec.y for vec in corners))
            max_vec_cache.z = max((vec.z for vec in corners))

            ref_pos.x = (max_vec_cache.x + min_vec_cache.x) / 2
            ref_pos.y = (max_vec_cache.y + min_vec_cache.y) / 2
            ref_pos.z = (max_vec_cache.z + min_vec_cache.z) / 2
        case AlignMode.AxisCenter:
            ref_pos.x = obj.location.x
            ref_pos.y = obj.location.y
            ref_pos.z = obj.location.z
        case _:
            raise UTIL_functions.BBPException('inpossible align mode.')

    return ref_pos

#endregion

def register():
    bpy.utils.register_class(BBP_PG_legacy_align_history)
    bpy.utils.register_class(BBP_OT_legacy_align)

def unregister():
    bpy.utils.unregister_class(BBP_OT_legacy_align)
    bpy.utils.unregister_class(BBP_PG_legacy_align_history)
