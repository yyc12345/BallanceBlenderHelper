import bpy
from . import UTILS_constants, UTILS_functions, UTILS_virtools_prop

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

        layout.prop(target, 'ambient')
        layout.prop(target, 'diffuse')
        layout.prop(target, 'specular')
        layout.prop(target, 'emissive')
        layout.prop(target, 'specular_power')

