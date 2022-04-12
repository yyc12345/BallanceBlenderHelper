import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

class BALLANCE_OT_add_virtools_group(bpy.types.Operator):
    """Add a Virtools Group for Active Object."""
    bl_idname = "ballance.add_virtools_group"
    bl_label = "Add Virtools Group"
    bl_options = {'UNDO'}

    group_name: bpy.props.EnumProperty(
        name="Group Name",
        description="Group name. For custom group name, please pick `CustomCKGroup` and change it later.",
        items=tuple((x, x, "") for x in UTILS_constants.propsVtGroups_availableGroups),
    )

    @classmethod
    def poll(self, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        gp = UTILS_virtools_prop.get_virtools_group(obj)
        item = gp.add()
        item.name = ""
        item.group_name = str(self.group_name)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
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

        try:
            obj = context.object
            gp = UTILS_virtools_prop.get_virtools_group(obj)
            active_gp = UTILS_virtools_prop.get_active_virtools_group(obj)
            data = gp[active_gp]
        except:
            return False
        else:
            return True
        
    def execute(self, context):
        obj = context.object
        gp = UTILS_virtools_prop.get_virtools_group(obj)
        active_gp = UTILS_virtools_prop.get_active_virtools_group(obj)
        idx = int(active_gp)
        
        active_gp -= 1
        gp.remove(idx)
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
