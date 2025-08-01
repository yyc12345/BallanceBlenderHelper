import bpy, mathutils
import enum, typing
from . import UTIL_functions

#region Align Mode 

class AlignMode(enum.IntEnum):
    Min = enum.auto()
    BBoxCenter = enum.auto()
    AxisCenter = enum.auto()
    Max = enum.auto()
_g_AlignModeDesc: dict[AlignMode, tuple[str, str, str]] = {
    AlignMode.Min: ("Min", "The min value in specified axis.", "REMOVE"),
    AlignMode.BBoxCenter: ("Center (Bounding Box)", "The bounding box center in specified axis.", "SHADING_BBOX"),
    AlignMode.AxisCenter: ("Center (Axis)", "The object's source point in specified axis.", "OBJECT_ORIGIN"),
    AlignMode.Max: ("Max", "The max value in specified axis.", "ADD"),
}
_g_EnumHelper_AlignMode = UTIL_functions.EnumPropHelper(
    AlignMode,
    lambda x: str(x.value),
    lambda x: AlignMode(int(x)),
    lambda x: _g_AlignModeDesc[x][0],
    lambda x: _g_AlignModeDesc[x][1],
    lambda x: _g_AlignModeDesc[x][2]
)

class CurrentInstance(enum.IntEnum):
    ActiveObject = enum.auto()
    Cursor = enum.auto()
_g_CurrentInstanceDesc: dict[CurrentInstance, tuple[str, str, str]] = {
    CurrentInstance.ActiveObject: ("Active Object", "Use Active Object as Current Object", "OBJECT_DATA"),
    CurrentInstance.Cursor: ("3D Cursor", "Use 3D Cursor as Current Object", "CURSOR"),
}
_g_EnumHelper_CurrentInstance = UTIL_functions.EnumPropHelper(
    CurrentInstance,
    lambda x: str(x.value),
    lambda x: CurrentInstance(int(x)),
    lambda x: _g_CurrentInstanceDesc[x][0],
    lambda x: _g_CurrentInstanceDesc[x][1],
    lambda x: _g_CurrentInstanceDesc[x][2]
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
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore
    align_y: bpy.props.BoolProperty(
        name = "Y Position",
        default = False,
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore
    align_z: bpy.props.BoolProperty(
        name = "Z Position",
        default = False,
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore
    current_instance: bpy.props.EnumProperty(
        name = "Current Instance",
        description = "Decide which instance should be used as Current Object",
        items = _g_EnumHelper_CurrentInstance.generate_items(),
        default = _g_EnumHelper_CurrentInstance.to_selection(CurrentInstance.ActiveObject),
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore
    current_align_mode: bpy.props.EnumProperty(
        name = "Current Object",
        description = "The align mode applied to Current Object",
        items = _g_EnumHelper_AlignMode.generate_items(),
        default = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter),
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore
    target_align_mode: bpy.props.EnumProperty(
        name = "Target Objects",
        description = "The align mode applied to Target Objects (selected objects except active object if Current Instance is active object)",
        items = _g_EnumHelper_AlignMode.generate_items(),
        default = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter),
        translation_context = 'BBP_PG_legacy_align_history/property'
    ) # type: ignore

#endregion

class BBP_OT_legacy_align(bpy.types.Operator):
    """Align Objects with 3ds Max Style"""
    bl_idname = "bbp.legacy_align"
    bl_label = "3ds Max Align"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_legacy_align'

    # the updator for apply flag value
    def apply_flag_updated(self, context):
        # check hinder and set hinder first
        if self.recursive_hinder: return
        self.recursive_hinder = True

        # reset apply button value (default is True)
        # due to the hinder, no recursive calling will happend
        if self.apply_flag == True: return
        self.apply_flag = True

        # check whether add new entry
        # if no selected axis, this alignment is invalid
        histories: UTIL_functions.CollectionVisitor[BBP_PG_legacy_align_history]
        histories = UTIL_functions.CollectionVisitor(self.align_history)
        entry: BBP_PG_legacy_align_history = histories[-1]
        if entry.align_x == True or entry.align_y == True or entry.align_z == True:
            # valid one
            # add a new entry in history
            histories.add()
        else:
            # invalid one
            # reset all data to default
            entry.align_x = False
            entry.align_y = False
            entry.align_z = False
            entry.current_align_mode = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter)
            entry.target_align_mode = _g_EnumHelper_AlignMode.to_selection(AlignMode.AxisCenter)

        # reset hinder
        self.recursive_hinder = False
        # blender required
        return None
    
    apply_flag: bpy.props.BoolProperty(
        # TR: Property not showen should not have name and desc.
        # name = "Apply Flag",
        # description = "Internal flag.",
        options = {'HIDDEN', 'SKIP_SAVE'},
        default = True, # default True value to make it as a "light" button, not a grey one.
        update = apply_flag_updated
    ) # type: ignore
    recursive_hinder: bpy.props.BoolProperty(
        # TR: Property not showen should not have name and desc.
        # name = "Recursive Hinder",
        # description = "An internal flag to prevent the loop calling to apply_flags's updator.",
        options = {'HIDDEN', 'SKIP_SAVE'},
        default = False
    ) # type: ignore
    align_history : bpy.props.CollectionProperty(
        # TR: Property not showen should not have name and desc.
        # name = "Historys",
        # description = "Align history.",
        type = BBP_PG_legacy_align_history
    ) # type: ignore
    
    @classmethod
    def poll(cls, context):
        return _check_align_requirement()

    def invoke(self, context, event):
        histories: UTIL_functions.CollectionVisitor[BBP_PG_legacy_align_history]
        histories = UTIL_functions.CollectionVisitor(self.align_history)
        # clear history and add 1 entry for following functions
        histories.clear()
        histories.add()
        # run execute() function
        return self.execute(context)
    
    def execute(self, context):
        # get processed objects
        (current_obj, current_cursor, target_objs) = _prepare_objects()
        # YYC MARK:
        # This statement is VERY IMPORTANT.
        # If this statement is not presented, Blender will return identity matrix
        # when getting world matrix from Object since the second execution of this function.
        # It seems that Blender fail to read restored value from a new execution.
        # Additionally, this statement only can be placed in there.
        # If you place it at the end of this function, it doesn't work.
        context.view_layer.update()
        # iterate history to align objects
        histories: UTIL_functions.CollectionVisitor[BBP_PG_legacy_align_history]
        histories = UTIL_functions.CollectionVisitor(self.align_history)
        for entry in histories:
            _align_objects(
                _g_EnumHelper_CurrentInstance.get_selection(entry.current_instance),
                current_obj, current_cursor, target_objs,
                entry.align_x, entry.align_y, entry.align_z,
                _g_EnumHelper_AlignMode.get_selection(entry.current_align_mode), 
                _g_EnumHelper_AlignMode.get_selection(entry.target_align_mode)
            )
        return {'FINISHED'}

    def draw(self, context):
        # get last entry in history to show
        histories: UTIL_functions.CollectionVisitor[BBP_PG_legacy_align_history]
        histories = UTIL_functions.CollectionVisitor(self.align_history)
        entry: BBP_PG_legacy_align_history = histories[-1]

        layout = self.layout
        col = layout.column()

        # show axis
        col.label(text="Align Axis (Multi-selection)", text_ctxt='BBP_OT_legacy_align/draw')
        row = col.row()
        row.prop(entry, "align_x", toggle = 1)
        row.prop(entry, "align_y", toggle = 1)
        row.prop(entry, "align_z", toggle = 1)

        # show current instance
        col.separator()
        col.label(text='Current Instance', text_ctxt='BBP_OT_legacy_align/draw')
        # it should be shown in horizon so we create a new sublayout
        row = col.row()
        row.prop(entry, 'current_instance', expand=True)

        # show instance and mode
        col.separator()
        # only show current object mode if current instance is active object,
        # because there is no mode for 3d cursor.
        current_instnce = _g_EnumHelper_CurrentInstance.get_selection(entry.current_instance)
        if current_instnce == CurrentInstance.ActiveObject:
            col.label(text='Current Object (Active Object)', text_ctxt='BBP_OT_legacy_align/draw')
            col.prop(entry, "current_align_mode", expand = True)
        col.label(text='Target Objects (Selected Objects)', text_ctxt='BBP_OT_legacy_align/draw')
        col.prop(entry, "target_align_mode", expand = True)

        # show apply button
        col.separator()
        conditional_disable_area = col.column()
        # only allow Apply when there is a selected axis
        conditional_disable_area.enabled = entry.align_x == True or entry.align_y == True or entry.align_z == True
        # show apply and counter
        conditional_disable_area.prop(self, 'apply_flag', toggle = 1, text='Apply', icon='CHECKMARK', text_ctxt='BBP_OT_legacy_align/draw')
        tr_text: str = bpy.app.translations.pgettext_iface(
            'Total {0} applied alignments', 'BBP_OT_legacy_align/draw')
        conditional_disable_area.label(text=tr_text.format(len(histories) - 1), translate=False)

#region Core Functions

def _check_align_requirement() -> bool:
    # If we are not in object mode, do not do legacy align
    if not UTIL_functions.is_in_object_mode():
        return False
    
    # YYC MARK:
    # We still need to check active object (as current object)
    # although we can choose align with active object or 3d cursor.
    # Because we can not make any promise that user will 
    # select Active Object or 3D Cursor as current object before executing this operator.
    if bpy.context.active_object is None:
        return False
    
    # YYC MARK:
    # Roughly check selected objects.
    # We do not need exclude active object from selected objects,
    # because active object may be moved when 3D Cursor is current object.
    if len(bpy.context.selected_objects) == 0:
        return False
    
    return True

def _prepare_objects() -> tuple[bpy.types.Object, mathutils.Vector, list[bpy.types.Object]]:
    # Fetch current object
    current_obj = typing.cast(bpy.types.Object, bpy.context.active_object)

    # Fetch 3d cursor location
    current_cursor: mathutils.Vector = bpy.context.scene.cursor.location

    # YYC MARK:
    # Fetch target objects and do NOT remove active object from it.
    # because active object will be moved when current instance is 3D Cursor.
    target_objs: list[bpy.types.Object] = bpy.context.selected_objects[:]

    # return value
    return (current_obj, current_cursor, target_objs)

def _align_objects(
        current_instance: CurrentInstance,
        current_obj: bpy.types.Object, current_cursor: mathutils.Vector, target_objs: list[bpy.types.Object],
        align_x: bool, align_y: bool, align_z: bool, current_mode: AlignMode, target_mode: AlignMode) -> None:
    # if no align, skip
    if not (align_x or align_y or align_z):
        return
    
    # calc current object data
    current_obj_ref: mathutils.Vector
    match current_instance:
        case CurrentInstance.ActiveObject:
            current_obj_ref = _get_object_ref_point(current_obj, current_mode)
        case CurrentInstance.Cursor:
            current_obj_ref = current_cursor

    # process each target obj
    for target_obj in target_objs:
        # YYC MARK:
        # If we use active object as current instance, we need exclude it from target objects,
        # because there is no pre-exclude considering the scenario that 3D Cursor is current instance.
        if current_instance == CurrentInstance.ActiveObject and current_obj == target_obj:
            continue

        # calc target object data
        target_obj_ref: mathutils.Vector = _get_object_ref_point(target_obj, target_mode)
        # build translation transform
        target_obj_translation: mathutils.Vector = current_obj_ref - target_obj_ref
        if not align_x: target_obj_translation.x = 0
        if not align_y: target_obj_translation.y = 0
        if not align_z: target_obj_translation.z = 0
        # target_obj.location += target_obj_translation
        target_obj_translation_matrix: mathutils.Matrix = mathutils.Matrix.Translation(target_obj_translation)
        # apply translation transform to left side (add into original matrix)
        target_obj.matrix_world = target_obj_translation_matrix @ target_obj.matrix_world

def _get_object_ref_point(obj: bpy.types.Object, mode: AlignMode) -> mathutils.Vector:
    ref_pos = mathutils.Vector((0, 0, 0))
    
    # calc bounding box data
    corners: tuple[mathutils.Vector, ...] = tuple(obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box)
    bbox_min_corner = mathutils.Vector((
        min((vec.x for vec in corners)),
        min((vec.y for vec in corners)),
        min((vec.z for vec in corners)),
    ))
    bbox_max_corner = mathutils.Vector((
        max((vec.x for vec in corners)),
        max((vec.y for vec in corners)),
        max((vec.z for vec in corners)),
    ))

    # return value by given align mode
    match(mode):
        case AlignMode.Min:
            ref_pos = bbox_min_corner
        case AlignMode.Max:
            ref_pos = bbox_max_corner
        case AlignMode.BBoxCenter:
            ref_pos = (bbox_max_corner + bbox_min_corner) / 2
        case AlignMode.AxisCenter:
            ref_pos = obj.matrix_world.translation
        case _:
            raise UTIL_functions.BBPException('impossible align mode.')

    return ref_pos

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_PG_legacy_align_history)
    bpy.utils.register_class(BBP_OT_legacy_align)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_legacy_align)
    bpy.utils.unregister_class(BBP_PG_legacy_align_history)
