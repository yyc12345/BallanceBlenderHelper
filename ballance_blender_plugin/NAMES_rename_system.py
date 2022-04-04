import bpy
from . import UTILS_constants

class rename_system_props(bpy.types.Operator):
    name_standard: bpy.props.EnumProperty(
        name="Name Standard",
        description="Choose your prefered name standard",
        items=(
            ("YYC", "YYC Tools Chains", "YYC Tools Chains name standard."),
            ("IMENGYU", "Imengyu Ballance", "Auto grouping name standard for Imengyu/Ballance")
            ),
    )

    oper_source: bpy.props.EnumProperty(
        name="Operation Target",
        description="Rename target",
        items=(
            ("COLLECTION", "Selected Collections", ""),
            ("OBJECTS", "Selected Objects", "")
            ),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name_standard")

class BALLANCE_OT_rename_via_group(rename_system_props):
    """Rename object via Virtools groups"""
    bl_idname = "ballance.rename_via_group"
    bl_label = "Rename via Group"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

class BALLANCE_OT_convert_name(rename_system_props):
    """Convert name from one name standard to another one."""
    bl_idname = "ballance.convert_name"
    bl_label = "Convert Name"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

class BALLANCE_OT_auto_grouping(rename_system_props):
    """Auto Grouping object according to specific name standard."""
    bl_idname = "ballance.auto_grouping"
    bl_label = "Auto Grouping"
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

class ObjectBasicType():
    COMPONENT = 0

class NameInfoHelper():
    def __init__(_basic_type):
        self.basic_type = _basic_type

    # extra field notes:
    # 

def _get_selected_objects(oper_source):
    if oper_source == 'COLLECTION':
        for selected_item in bpy.context.selected_ids:
            if selected_item.bl_rna.identifier == "Collection":
                tuple(bpy.data.collections[item.name].objects)
    elif oper_source == 'OBJECTS':
        return bpy.context.selected_objects
    else:
        raise Exception("Unknow oper_source.")

def _get_name_info_from_yyc_name(obj_name):
    pass

def _get_name_info_from_imengyu_name(obj_name):
    pass

def _get_name_info_from_group(obj_name):
    pass

def _set_for_yyc_name(name_info):
    pass

def _set_for_imengyu_name(name_info):
    pass

def _set_for_group(name_info):
    pass

