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

        # check enable, [0] is enable_virtools_material
        if mtl_data[0]:
            UTILS_functions.create_material_nodes(mtl, mtl_data)
        else:
            UTILS_functions.show_message_box(("Virtools Material is not enabled.", ), "Apply Failed", 'ERROR')

        return {'FINISHED'}

class BALLANCE_OT_parse_virtools_material(bpy.types.Operator):
    """Apply Virtools Material to Blender Material."""
    bl_idname = "ballance.parse_virtools_material"
    bl_label = "Parse from Blender Principled BSDF"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def execute(self, context):
        mtl = context.material
        mtl_data = UTILS_functions.parse_material_nodes(mtl)
        if mtl_data is None:
            UTILS_functions.show_message_box(("Fail to parse Principled BSDF.", ), "Parsing Failed", 'ERROR')
        else:
            UTILS_virtools_prop.set_virtools_material_data(mtl, mtl_data)

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

    def draw_header(self, context):
        # draw a checkbox in header
        target = UTILS_virtools_prop.get_virtools_material(context.material)
        self.layout.prop(target, "enable_virtools_material", text="")

    def draw(self, context):
        # get layout and target
        layout = self.layout
        target = UTILS_virtools_prop.get_virtools_material(context.material)

        # decide visible
        layout.enabled = target.enable_virtools_material

        # draw layout
        layout.label(text="Basic Parameters")
        layout.prop(target, 'ambient')
        layout.prop(target, 'diffuse')
        layout.prop(target, 'specular')
        layout.prop(target, 'emissive')
        layout.prop(target, 'specular_power')
        layout.prop(target, 'texture', emboss=True)

        layout.separator()
        layout.label(text="Advanced Parameters")
        layout.prop(target, 'alpha_test')
        layout.prop(target, 'alpha_blend')
        layout.prop(target, 'z_buffer')
        layout.prop(target, 'two_sided')

        layout.separator()
        layout.label(text="Operations")
        layout.operator("ballance.apply_virtools_material", icon="NODETREE")
        layout.operator("ballance.parse_virtools_material", icon="HIDE_OFF")

