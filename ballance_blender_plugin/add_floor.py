import bpy,mathutils
import os
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
        min=0,
        default=0,
    )

    expand_length_2 : bpy.props.IntProperty(
        name="D2 length",
        description="The length of expand direction 2",
        min=0,
        default=0,
    )

    height_multiplier : bpy.props.FloatProperty(
        name="Height",
        description="The multiplier for height. Default height is 5",
        min=0.0,
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

    @classmethod
    def poll(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        return os.path.isdir(prefs.external_folder)

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
        col.prop(self, "rotation_inside_mesh")
        col.prop(self, "height_multiplier")

        col.separator()
        col.label(text="Expand")
        col.prop(self, "expand_length_1")
        col.prop(self, "expand_length_2")
        grids = col.grid_flow(columns=3)
        grids.separator()
        grids.label(text="X")
        grids.separator()
        grids.label(text="X")
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.label(text="X")
        grids.separator()
        grids.label(text="X")
        grids.separator()

        col.separator()
        col.label(text="Faces")
        row = col.row()
        row.prop(self, "use_3d_top")
        row.prop(self, "use_3d_bottom")

        col.separator()
        col.label(text="Sides")
        grids = col.grid_flow(columns=3)
        grids.separator()
        grids.prop(self, "use_2d_top")
        grids.separator()
        grids.prop(self, "use_2d_left")
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.prop(self, "use_2d_right")
        grids.separator()
        grids.prop(self, "use_2d_bottom")
        grids.separator()


