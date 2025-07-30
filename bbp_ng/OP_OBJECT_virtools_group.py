import bpy
import enum
from . import PROP_virtools_group
from . import UTIL_functions

#region Select by Group

class SelectMode(enum.IntEnum):
    Set = enum.auto()
    Extend = enum.auto()
    Subtract = enum.auto()
    Difference = enum.auto()
    Intersect = enum.auto()
_g_SelectModeDesc: dict[SelectMode, tuple[str, str, str]] = {
    SelectMode.Set: ('Set', 'Sets a new selection.', 'SELECT_SET'),
    SelectMode.Extend: ('Extend', 'Adds newly selected items to the existing selection.', 'SELECT_EXTEND'),
    SelectMode.Subtract: ('Subtract', 'Removes newly selected items from the existing selection.', 'SELECT_SUBTRACT'),
    SelectMode.Difference: ('Invert', 'Inverts the selection.', 'SELECT_DIFFERENCE'),
    SelectMode.Intersect: ('Intersect', 'Selects items that intersect with the existing selection.', 'SELECT_INTERSECT')
}
_g_EnumHelper_SelectMode = UTIL_functions.EnumPropHelper(
    SelectMode,
    lambda x: str(x.value),
    lambda x: SelectMode(int(x)),
    lambda x: _g_SelectModeDesc[x][0],
    lambda x: _g_SelectModeDesc[x][1],
    lambda x: _g_SelectModeDesc[x][2]
)

class BBP_OT_select_object_by_virtools_group(bpy.types.Operator, PROP_virtools_group.SharedGroupNameInputProperties):
    """Select Objects by Virtools Group"""
    bl_idname = "bbp.select_object_by_virtools_group"
    bl_label = "Select by Virtools Group"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_select_object_by_virtools_group'

    selection_mode: bpy.props.EnumProperty(
        name = "Mode",
        description = "Selection mode",
        items = _g_EnumHelper_SelectMode.generate_items(),
        default = _g_EnumHelper_SelectMode.to_selection(SelectMode.Intersect),
        translation_context = 'BBP_OT_select_object_by_virtools_group/property'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        return UTIL_functions.is_in_object_mode()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        _select_object_by_virtools_group(
            context,
            self.general_get_group_name(),
            _g_EnumHelper_SelectMode.get_selection(self.selection_mode)
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Selection Mode', text_ctxt='BBP_OT_select_object_by_virtools_group/draw')
        sublayout = layout.column()    # make selection expand vertically, not horizontal.
        sublayout.prop(self, 'selection_mode', expand = True)

        layout.separator()
        layout.label(text='Group Parameters', text_ctxt='BBP_OT_select_object_by_virtools_group/draw')
        self.draw_group_name_input(layout)

def _select_object_by_virtools_group(context: bpy.types.Context, group_name: str, mode: SelectMode) -> None:
    match(mode):
        case SelectMode.Set:
            # iterate all objects and directly set
            for obj in context.scene.objects:
                # check group and decide whether select this obj
                with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                    obj.select_set(gp.contain_group(group_name))
        case SelectMode.Extend:
            # also iterate all objects
            for obj in context.scene.objects:
                # but only increase selection, for selected object, skip check
                if obj.select_get(): continue
                # if not selected, check whether add it.
                with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                    if gp.contain_group(group_name):
                        obj.select_set(True)
        case SelectMode.Subtract:
            # subtract only involving selected item. so we get selected objest first
            # and copy it (because we need modify it)
            # and iterate it to reduce useless operations
            selected = context.selected_objects[:]
            for obj in selected:
                # remove matched only
                with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                    if gp.contain_group(group_name):
                        obj.select_set(False)
        case SelectMode.Difference:
            # construct a selected obj set for convenient operations
            selected_set = set(context.selected_objects)
            # iterate all objects
            for obj in context.scene.objects:
                with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                    # use xor to select
                    # in_selected XOR in_group
                    obj.select_set((obj in selected_set) ^ gp.contain_group(group_name))
        case SelectMode.Intersect:
            # like subtract, only iterate selected obj
            selected = context.selected_objects[:]
            for obj in selected:
                # but remove not matched
                with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                    if not gp.contain_group(group_name):
                        obj.select_set(False)
        case _:
            raise UTIL_functions.BBPException('invalid selection mode')
        
#endregion

#region Objects Group Opers

class BBP_OT_add_objects_virtools_group(bpy.types.Operator, PROP_virtools_group.SharedGroupNameInputProperties):
    """Grouping Selected Objects"""
    bl_idname = "bbp.add_objects_virtools_group"
    bl_label = "Grouping Objects"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_add_objects_virtools_group'

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        group_name: str = self.general_get_group_name()
        for obj in context.selected_objects:
            with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                gp.add_group(group_name)
        self.report({'INFO'}, "Grouping objects successfully.")
        return {'FINISHED'}

    def draw(self, context):
        self.draw_group_name_input(self.layout)

class BBP_OT_rm_objects_virtools_group(bpy.types.Operator, PROP_virtools_group.SharedGroupNameInputProperties):
    """Ungrouping Selected Objects"""
    bl_idname = "bbp.rm_objects_virtools_group"
    bl_label = "Ungrouping Objects"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_rm_objects_virtools_group'

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        group_name: str = self.general_get_group_name()
        for obj in context.selected_objects:
            with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                gp.remove_group(group_name)
        self.report({'INFO'}, "Ungrouping objects successfully.")
        return {'FINISHED'}

    def draw(self, context):
        self.draw_group_name_input(self.layout)

class BBP_OT_clear_objects_virtools_group(bpy.types.Operator):
    """Clear Virtools Groups on Selected Objects"""
    bl_idname = "bbp.clear_objects_virtools_group"
    bl_label = "Clear All Groups"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_clear_objects_virtools_group'

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        # iterate object
        for obj in context.selected_objects:
            with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
                gp.clear_groups()
        self.report({'INFO'}, "Clear objects groups successfully.")
        return {'FINISHED'}

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_select_object_by_virtools_group)

    bpy.utils.register_class(BBP_OT_add_objects_virtools_group)
    bpy.utils.register_class(BBP_OT_rm_objects_virtools_group)
    bpy.utils.register_class(BBP_OT_clear_objects_virtools_group)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_clear_objects_virtools_group)
    bpy.utils.unregister_class(BBP_OT_rm_objects_virtools_group)
    bpy.utils.unregister_class(BBP_OT_add_objects_virtools_group)

    bpy.utils.unregister_class(BBP_OT_select_object_by_virtools_group)

