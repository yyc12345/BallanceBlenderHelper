import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

class BALLANCE_OT_add_virtools_group(bpy.types.Operator):
    """Add a Virtools Group for Active Object."""
    bl_idname = "ballance.add_virtools_group"
    bl_label = "Add Virtools Group"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        UTILS_virtools_prop.set_virtools_group_data(obj, ("aaa", "bbb", "ccc"))
        return {'FINISHED'}

class BALLANCE_OT_rm_virtools_group(bpy.types.Operator):
    """Remove a Virtools Group for Active Object."""
    bl_idname = "ballance.rm_virtools_group"
    bl_label = "Remove Virtools Group"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        print(UTILS_virtools_prop.get_virtools_group_data(obj))
        return {'FINISHED'}

class BALLANCE_UL_virtools_group(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, 'group_name', icon='GROUP', text="")

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
