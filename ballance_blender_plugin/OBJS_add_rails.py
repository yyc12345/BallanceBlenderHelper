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
        items=(
            ('MONO', "Monorail", ""),
            ('DOUBLE', "Rail", ""),
        ),
        default='DOUBLE',
    )

    rail_radius: bpy.props.FloatProperty(
        name="Rail Radius",
        description="Define rail section radius",
        default=0.375,
    )

    rail_span: bpy.props.FloatProperty(
        name="Rail Span",
        description="The length between 2 single rails.",
        default=3.75,
    )

    def execute(self, context):
        # create one first
        firstObj = _create_ballance_circle(self.rail_radius, (0.0, 0.0, 0.0))

        # for double rail
        if self.rail_type == 'DOUBLE':
            # create another one
            secondObj = _create_ballance_circle(self.rail_radius, (self.rail_span, 0.0, 0.0))
            # merge
            firstObj = _merge_two_circle(firstObj, secondObj)

        # rename
        if self.rail_type == 'DOUBLE':
            firstObj.name = "A_Rail_"
        else:
            firstObj.name = "A_Rail_Mono_"
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

class BALLANCE_OT_add_tunnels(bpy.types.Operator):
    """Add rail"""
    bl_idname = "ballance.add_tunnels"
    bl_label = "Add tunnel section"
    bl_options = {'UNDO'}

    use_outside: bpy.props.BoolProperty(
        name="Double Sides",
        description="Create tunnel section with double sides, not a single face.",
        default=True,
    )

    inside_radius: bpy.props.FloatProperty(
        name="Inside Radius",
        description="Tunnel inside radius",
        default=2.5,
    )

    outside_radius: bpy.props.FloatProperty(
        name="Outside Radius",
        description="Tunnel outside radius",
        default=2.6,
    )

    def execute(self, context):
        # create one first
        firstObj = _create_ballance_circle(self.inside_radius, (0.0, 0.0, 0.0))

        # for double rail
        if self.use_outside:
            # create another one
            secondObj = _create_ballance_circle(self.outside_radius, (0.0, 0.0, 0.0))
            # merge
            firstObj = _merge_two_circle(firstObj, secondObj)

        # rename
        firstObj.name = "A_Rail_Tunnel_"
        # apply 3d cursor
        UTILS_functions.move_to_cursor(firstObj)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_outside")
        layout.prop(self, "inside_radius")
        if self.use_outside:
            layout.prop(self, "outside_radius")

def _create_ballance_circle(radius, loc):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_circle_add(
        vertices=8,
        radius=radius,
        fill_type='NOTHING',
        calc_uvs=False,
        enter_editmode=False,
        align='WORLD',
        location=loc
    )
    
    created_obj = bpy.context.selected_objects[0]
    bpy.ops.object.select_all(action='DESELECT')
    return created_obj

def _merge_two_circle(obj1, obj2):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj1
    obj1.select_set(True)
    obj2.select_set(True)
    bpy.ops.object.join()

    return obj1
