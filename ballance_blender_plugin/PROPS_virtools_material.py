import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

class BALLANCE_OT_apply_virtools_material(bpy.types.Operator):
    """Apply Virtools Material to Blender Material."""
    bl_idname = "ballance.apply_virtools_material"
    bl_label = "Apply Virtools Material"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def execute(self, context):
        mtl = context.material
        mtl_data = UTILS_virtools_prop.get_virtools_material_data(mtl)
        UTILS_functions.create_material_nodes(mtl, *mtl_data)

        return {'FINISHED'}

class BALLANCE_PT_virtools_material(bpy.types.Panel):
    """Show Virtools Material Properties."""
    bl_label = "Virtools Material"
    bl_idname = "BALLANCE_PT_virtools_material"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        #target = bpy.context.active_object.active_material
        target = UTILS_virtools_prop.get_virtools_material(context.material)

        layout.prop(target, 'texture', emboss=True)
        layout.prop(target, 'ambient')
        layout.prop(target, 'diffuse')
        layout.prop(target, 'specular')
        layout.prop(target, 'emissive')
        layout.prop(target, 'specular_power')

        layout.operator("ballance.apply_virtools_material", icon="NODETREE")

