import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

class BALLANCE_OT_select_virtools_group(UTILS_virtools_prop.common_group_name_props):
    """Select objects by Virtools Group."""
    bl_idname = "ballance.select_virtools_group"
    bl_label = "Select by Virtools Group"
    bl_options = {'UNDO'}

    merge_selection: bpy.props.BoolProperty(
        name="Merge Selection",
        description="Merge selection, rather than re-select them.",
        default=False,
    )

    ignore_hide: bpy.props.BoolProperty(
        name="Ignore Hide Property",
        description="Select objects without considering visibility.",
        default=False,
    )

    def execute(self, context):
        # iterate object
        for obj in bpy.context.scene.objects:
            # ignore hidden objects
            if (not self.ignore_hide) and obj.hide_get() == True:
                continue

            # check group
            if UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()):
                # select object
                obj.select_set(True)
            else:
                # if not in merge mode, deselect them
                if not self.merge_selection:
                    obj.select_set(False)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, 'ignore_hide')
        row.prop(self, 'merge_selection')

        layout.separator()
        self.parent_draw(layout)

class BALLANCE_OT_filter_virtools_group(UTILS_virtools_prop.common_group_name_props):
    """Filter objects by Virtools Group."""
    bl_idname = "ballance.filter_virtools_group"
    bl_label = "Filter by Virtools Group"
    bl_options = {'UNDO'}

    reverse_selection: bpy.props.BoolProperty(
        name="Reverse",
        description="Reverse operation. Remove matched objects.",
        default=False,
    )

    ignore_hide: bpy.props.BoolProperty(
        name="Ignore Hide Property",
        description="Select objects without considering visibility.",
        default=False,
    )

    def execute(self, context):
        # make a copy for all objects, to ensure it is not viotile
        # becuase we need deselect some objects in for statement
        selected = bpy.context.selected_objects[:]
        # iterate object
        for obj in selected:
            # ignore hidden objects
            if (not self.ignore_hide) and obj.hide_get() == True:
                continue

            # check group and decide select
            is_selected = UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string())
            if self.reverse_selection:
                is_selected = not is_selected

            # select object
            obj.select_set(is_selected)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, 'ignore_hide')
        row.prop(self, 'reverse_selection')

        layout.separator()
        self.parent_draw(layout)



class BALLANCE_OT_ctx_set_group(UTILS_virtools_prop.common_group_name_props):
    """Grouping selected objects"""
    bl_idname = "ballance.ctx_set_group"
    bl_label = "Grouping Objects"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return len(bpy.context.selected_objects) != 0

    def execute(self, context):
        has_duplicated = False

        # iterate object
        for obj in bpy.context.selected_objects:
            # try setting
            if not UTILS_virtools_prop.add_virtools_group_data(obj, self.get_group_name_string()):
                has_duplicated = True

        # throw a warning if some objects have duplicated group
        if has_duplicated:
            UTILS_functions.show_message_box(("Some objects have duplicated group name.", "These objects have been omitted.", ), "Duplicated Group", 'ERROR')

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        self.parent_draw(layout)

class BALLANCE_OT_ctx_unset_group(UTILS_virtools_prop.common_group_name_props):
    """Ungrouping selected objects"""
    bl_idname = "ballance.ctx_unset_group"
    bl_label = "Ungrouping Objects"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return len(bpy.context.selected_objects) != 0

    def execute(self, context):
        lack_group = False

        # iterate object
        for obj in bpy.context.selected_objects:
            # try unsetting
            if not UTILS_virtools_prop.remove_virtools_group_data(obj, self.get_group_name_string()):
                lack_group = True

        # throw a warning if some objects have duplicated group
        if lack_group:
            UTILS_functions.show_message_box(("Some objects lack specified group name.", "These objects have been omitted.", ), "Lack Group", 'ERROR')

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.parent_draw(layout)

class BALLANCE_OT_ctx_clear_group(bpy.types.Operator):
    """Clear Virtools Groups for selected objects"""
    bl_idname = "ballance.ctx_clear_group"
    bl_label = "Clear Grouping"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return len(bpy.context.selected_objects) != 0

    def execute(self, context):
        # iterate object
        for obj in bpy.context.selected_objects:
            UTILS_virtools_prop.clear_virtools_group_data(obj)


        return {'FINISHED'}

