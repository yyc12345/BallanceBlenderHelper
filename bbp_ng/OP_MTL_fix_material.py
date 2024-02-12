import bpy
from . import PROP_virtools_material, PROP_preferences

class BBP_OT_fix_all_material(bpy.types.Operator):
    """Fix All Materials by Its Referred Ballance Texture Name."""
    bl_idname = "bbp.fix_all_material"
    bl_label = "Fix Material"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        # do work and count 
        counter_all: int = 0
        counter_suc: int = 0
        for mtl in bpy.data.materials:
            counter_all += 1
            if PROP_virtools_material.fix_material(mtl):
                PROP_virtools_material.apply_to_blender_material(mtl)
                counter_suc += 1

        # report and return
        self.report({'INFO'}, f'Fix {counter_suc}/{counter_all} materials.')
        return {'FINISHED'}

def register() -> None:
    bpy.utils.register_class(BBP_OT_fix_all_material)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_fix_all_material)
