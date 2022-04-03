import bpy,bmesh
import mathutils
import bpy.types
from . import UTILS_functions

class BALLANCE_OT_rename_via_group(bpy.types.Operator):
    """Rename object via Virtools groups"""
    bl_idname = "ballance.rename_via_group"
    bl_label = "Rename via Group"
    bl_options = {'UNDO'}

    name_standard: bpy.props.EnumProperty(
        name="Name Standard",
        description="Choose your prefered name standard",
        items=(
            ("YYC", "YYC Tools Chains", "YYC Tools Chains name standard."),
            ("IMENGYU", "Imengyu Ballance", "Auto grouping name standard for Imengyu/Ballance")
            ),
    )

    @classmethod
    def poll(self, context):
        return True
        #return _check_rail_target()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name_standard")