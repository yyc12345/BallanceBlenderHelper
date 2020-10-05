import bpy,mathutils
from . import utils, config

class BALLANCE_OT_add_floor(bpy.types.Operator):
    """Add Ballance floor"""
    bl_idname = "ballance.add_floor"
    bl_label = "Add floor"
    bl_options = {'UNDO'}

    floor_type: bpy.props.EnumProperty(
        name="Type",
        description="Floor type",
        items=tuple((x, x, "") for x in config.floor_block_dict.keys()),
    )

    expand_length_1 : bpy.props.IntProperty(
        name="D1 length",
        description="The length of expand direction 1",
        default=0,
    )

    expand_length_2 : bpy.props.IntProperty(
        name="D2 length",
        description="The length of expand direction 2",
        default=0,
    )

    height_multiplier : bpy.props.FloatProperty(
        name="Height",
        description="The multiplier for height. Default height is 5",
        default=1.0,
    )

    rotation_inside_mesh: bpy.props.EnumProperty(
        name="Rotation",
        description="Rotation inside mesh",
        items=(
            ("R0", "0 degree", ""),
            ("R90", "90 degree", ""),
            ("R180", "180 degree", ""),
            ("R270", "270 degree", "")
        ),
        default="R0"
    )

    use_2d_top : bpy.props.BoolProperty(
        name="Top side"
    )
    use_2d_right : bpy.props.BoolProperty(
        name="Right side"
    )
    use_2d_bottom : bpy.props.BoolProperty(
        name="Bottom side"
    )
    use_2d_left : bpy.props.BoolProperty(
        name="Left side"
    )
    use_3d_top : bpy.props.BoolProperty(
        name="Top face"
    )
    use_3d_bottom : bpy.props.BoolProperty(
        name="Bottom face"
    )


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Basic param")
        col.prop(self, "floor_type")
        col.prop(self, "expand_length_1")
        col.prop(self, "expand_length_2")
        col.prop(self, "height_multiplier")
        col.prop(self, "rotation_inside_mesh")

        col.separator()
        col.label(text="Faces")
        row = col.row()
        row.prop(self, "use_3d_top")
        row.prop(self, "use_3d_bottom")

        col.separator()
        col.label(text="Sides")
        row = col.row(align=True)
        row.label(text="")
        row.prop(self, "use_2d_top")
        row.label(text="")
        row = col.row(align=True)
        row.prop(self, "use_2d_left")
        row.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        row.prop(self, "use_2d_right")
        row = col.row(align=True)
        row.label(text="")
        row.prop(self, "use_2d_bottom")
        row.label(text="")


