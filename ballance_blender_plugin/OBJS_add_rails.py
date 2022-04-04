import bpy, mathutils
from . import UTILS_functions

class BALLANCE_OT_add_rails(bpy.types.Operator):
    """Add rail"""
    bl_idname = "ballance.add_rails"
    bl_label = "Add rail section"
    bl_options = {'UNDO'}

    rail_type: bpy.props.EnumProperty(
        name="Type",
        description="Rail type",
        items=(('MONO', "Monorail", ""),
                ('DOUBLE', "Rail", ""),
                ),
    )

    rail_radius: bpy.props.FloatProperty(
        name="Rail radius",
        description="Define rail section radius",
        default=0.375,
    )

    rail_span: bpy.props.FloatProperty(
        name="Rail span",
        description="Define rail span",
        default=3.75,
    )

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        # create one first
        bpy.ops.mesh.primitive_circle_add(vertices=8,
                                        radius=self.rail_radius,
                                        fill_type='NOTHING',
                                        calc_uvs=False,
                                        enter_editmode=False,
                                        align='WORLD',
                                        location=(0.0, 0.0, 0.0))

        firstObj = bpy.context.selected_objects[0]

        # for double rail
        if self.rail_type == 'DOUBLE':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.mesh.primitive_circle_add(vertices=8,
                                            radius=self.rail_radius,
                                            fill_type='NOTHING',
                                            calc_uvs=False,
                                            enter_editmode=False,
                                            align='WORLD',
                                            location=(self.rail_span, 0.0, 0.0))
            secondObj = bpy.context.selected_objects[0]

            # merge
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = firstObj
            firstObj.select_set(True)
            secondObj.select_set(True)
            bpy.ops.object.join()

        # apply 3d cursor
        UTILS_functions.move_to_cursor(firstObj)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "rail_type")
        layout.prop(self, "rail_radius")
        if self.rail_type == 'DOUBLE':
            layout.prop(self, "rail_span")

