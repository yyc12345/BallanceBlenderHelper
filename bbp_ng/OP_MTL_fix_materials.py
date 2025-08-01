import bpy
from . import UTIL_functions
from . import PROP_virtools_material, PROP_preferences

class BBP_OT_fix_all_materials(bpy.types.Operator):
    """Fix All Materials by Its Referred Ballance Texture Name."""
    bl_idname = "bbp.fix_all_materials"
    bl_label = "Fix All Materials"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_fix_all_materials'
    
    @classmethod
    def poll(cls, context):
        # only enable this when plugin have a valid ballance texture folder
        # and we are in object mode
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder() and UTIL_functions.is_in_object_mode()
    
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
        tr_text: str = bpy.app.translations.pgettext_rpt(
            'Fix {0}/{1} materials.', 'BBP_OT_fix_all_materials/draw')
        self.report({'INFO'}, tr_text.format(counter_suc, counter_all))
        return {'FINISHED'}

def register() -> None:
    bpy.utils.register_class(BBP_OT_fix_all_materials)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_fix_all_materials)
