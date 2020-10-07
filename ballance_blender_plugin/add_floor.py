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

    previous_floor_type = ''

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
        # get floor prototype
        floor_prototype = config.floor_block_dict[self.floor_type]

        # try sync default value
        if self.previous_floor_type != self.floor_type:
            self.previous_floor_type = self.floor_type

            default_sides = floor_prototype['DefaultSideConfig']
            self.use_2d_top = default_sides['UseTwoDTop']
            self.use_2d_right = default_sides['UseTwoDRight']
            self.use_2d_bottom = default_sides['UseTwoDBottom']
            self.use_2d_left = default_sides['UseTwoDLeft']
            self.use_3d_top = default_sides['UseThreeDTop']
            self.use_3d_bottom = default_sides['UseThreeDBottom']

        # show property
        layout = self.layout
        col = layout.column()
        col.label(text="Basic param")
        col.prop(self, "floor_type")
        col.prop(self, "rotation_inside_mesh")
        col.prop(self, "height_multiplier")

        col.separator()
        col.label(text="Expand")
        if floor_prototype['ExpandType'] == 'Column' or floor_prototype['ExpandType'] == 'Freedom':
            col.prop(self, "expand_length_1")
        if floor_prototype['ExpandType'] == 'Freedom':
            col.prop(self, "expand_length_2")
        col.label(text="Unit size: " + floor_prototype['UnitSize'])
        col.label(text="Expand mode: " + floor_prototype['ExpandType'])
        grids = col.grid_flow(row_major=True, columns=3)
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][0])
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][3])
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][1])
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][2])
        grids.separator()

        col.separator()
        col.label(text="Faces")
        row = col.row()
        row.prop(self, "use_3d_top")
        row.prop(self, "use_3d_bottom")

        col.separator()
        col.label(text="Sides")
        grids = col.grid_flow(row_major=True, columns=3)
        grids.separator()
        grids.prop(self, "use_2d_top")
        grids.separator()
        grids.prop(self, "use_2d_left")
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.prop(self, "use_2d_right")
        grids.separator()
        grids.prop(self, "use_2d_bottom")
        grids.separator()


