import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop, UTILS_icons_manager

class BALLANCE_OT_select_virtools_group(UTILS_virtools_prop.common_group_name_props):
    """Select objects by Virtools Group."""
    bl_idname = "ballance.select_virtools_group"
    bl_label = "Select by Virtools Group"
    bl_options = {'UNDO'}

    selection_type: bpy.props.EnumProperty(
        name="Mode",
        description="Selection mode",
        items=(
            ('SET', "Set", "Sets a new selection.", "SELECT_SET", 0),
            ('EXTEND', "Extend", "Adds newly selected items to the existing selection.", "SELECT_EXTEND", 1),
            ('SUBTRACT', "Subtract", "Removes newly selected items from the existing selection.", "SELECT_SUBTRACT", 2),
            ('DIFFERENCE', "Invert", "Inverts the selection.", "SELECT_DIFFERENCE", 3),
            ('INTERSECT', "Intersect", "Selects items that intersect with the existing selection.", "SELECT_INTERSECT", 4),
        ),
        default='SET'
    )

    def execute(self, context):
        if self.selection_type == 'SET':
            # iterate object
            for obj in bpy.context.scene.objects:
                # check group and decide whether select this obj
                obj.select_set(UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()))
        
        elif self.selection_type == 'EXTEND':
            # also iterate all objects
            for obj in bpy.context.scene.objects:
                # directly add if group matched. do not deselect anything
                if UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()):
                    obj.select_set(True)
        elif self.selection_type == 'SUBTRACT':
            # subtract only involving selected item. so we get selected objest first
            # and iterate it to reduce useless operations
            selected = bpy.context.selected_objects[:]
            for obj in selected:
                # remove matched only
                if UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()):
                    obj.select_set(False)

        elif self.selection_type == 'DIFFERENCE':
            # construct a selected obj set for convenient operations
            selected_set = set(bpy.context.selected_objects)
            # iterate all objects
            for obj in bpy.context.scene.objects:
                # use xor to select
                # in_selected XOR in_group
                obj.select_set((obj in selected_set) ^ UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()))
        elif self.selection_type == 'INTERSECT':
            # like subtract, only iterate selected obj
            selected = bpy.context.selected_objects[:]
            for obj in selected:
                # remove not matched
                if not UTILS_virtools_prop.check_virtools_group_data(obj, self.get_group_name_string()):
                    obj.select_set(False)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        layout.label(text='Selection Parameters')
        layout.prop(self, 'selection_type', expand=True, icon_only=True)

        layout.separator()
        layout.label(text='Group Parameters')
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
            UTILS_functions.show_message_box(
                ("Some objects have duplicated group name.", "These objects have been omitted.", ), 
                "Duplicated Group", UTILS_icons_manager.blender_error_icon
            )

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
            UTILS_functions.show_message_box(
                ("Some objects lack specified group name.", "These objects have been omitted.", ), 
                "Lack Group", UTILS_icons_manager.blender_error_icon
            )

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

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        # iterate object
        for obj in bpy.context.selected_objects:
            UTILS_virtools_prop.clear_virtools_group_data(obj)
        
        return {'FINISHED'}

