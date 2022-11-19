import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

class BALLANCE_OT_add_virtools_group(bpy.types.Operator):
    """Add a Virtools Group for Active Object."""
    bl_idname = "ballance.add_virtools_group"
    bl_label = "Add Virtools Group"
    bl_options = {'UNDO'}

    use_custom_name: bpy.props.BoolProperty(
        name="Use Custom Name",
        description="Whether use user defined group name.",
        default=False,
    )

    group_name: bpy.props.EnumProperty(
        name="Group Name",
        description="Pick vanilla Ballance group name.",
        items=tuple((x, x, "") for x in UTILS_constants.propsVtGroups_availableGroups),
    )

    custom_group_name: bpy.props.StringProperty(
        name="Custom Group Name",
        description="Input your custom group name.",
        default="",
    )

    @classmethod
    def poll(self, context):
        return context.object is not None

    def execute(self, context):
        # get name first
        gotten_group_name = str(self.custom_group_name if self.use_custom_name else self.group_name)

        # try adding
        obj = context.object
        if not UTILS_virtools_prop.add_virtools_group_data(obj, gotten_group_name):
            UTILS_functions.show_message_box(("Group name is duplicated!", ), "Duplicated Name", 'ERROR')

        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def draw(self, context):
        self.layout.prop(self, 'use_custom_name')
        if (self.use_custom_name):
            self.layout.prop(self, 'custom_group_name')
        else:
            self.layout.prop(self, 'group_name')


class BALLANCE_OT_rm_virtools_group(bpy.types.Operator):
    """Remove a Virtools Group for Active Object."""
    bl_idname = "ballance.rm_virtools_group"
    bl_label = "Remove Virtools Group"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        if context.object is None:
            return False

        obj = context.object
        gp = UTILS_virtools_prop.get_virtools_group(obj)
        active_gp = UTILS_virtools_prop.get_active_virtools_group(obj)
        return int(active_gp) >= 0 and int(active_gp) < len(gp)

    def execute(self, context):
        obj = context.object
        UTILS_virtools_prop.remove_virtools_group_data_by_index(obj, int(UTILS_virtools_prop.get_active_virtools_group(obj)))
        return {'FINISHED'}

class BALLANCE_UL_virtools_group(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, 'group_name', icon='GROUP', emboss=False, text="")

class BALLANCE_PT_virtools_group(bpy.types.Panel):
    """Show Virtools Group Properties."""
    bl_label = "Virtools Group"
    bl_idname = "BALLANCE_PT_virtools_group"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        target = bpy.context.active_object

        row = layout.row()
        row.template_list("BALLANCE_UL_virtools_group", "", target, "virtools_group", 
            target, "active_virtools_group")

        col = row.column(align=True)
        col.operator(BALLANCE_OT_add_virtools_group.bl_idname, icon='ADD', text="")
        col.operator(BALLANCE_OT_rm_virtools_group.bl_idname, icon='REMOVE', text="")
