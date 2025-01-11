import bpy, mathutils, math
import typing
from . import UTIL_rail_creator

## Const Value Hint:
#  Default Rail Radius: 0.35 (in measure)
#  Default Rail Span: 3.75 (in convention)
#  Default Monorail Sink Depth in Rail & Monorail Transition: 0.6259 (calculated by ImbalancedDream)
#      Equation: Sink = sqrt( ((RailRadius + BallRadius) ^ 2) - ((RailSpan / 2) ^ 2)  ) - BallRadius - RailRadius
#      BallRadius is the radius of player ball. It always is 2.
#      Ref: https://tieba.baidu.com/p/6557180791
#  
#  For Normal Side Rail (paper ball + wood ball can pass it):
#  Rail Span: 3.864
#  Angle (between rail panel and XY panel): 79.563 degree
#  For Special Side Rail (stone ball can pass it):
#  Rail Span: 3.864
#  Angle (between rail panel and XY panel): 57 degree
#  These infos are gotten from BallanceBug.
#  
#  For Side Spiral Rail, the distance between each layer is 3.6
#  Measured in Level 9 and Level 13.
#  For Spiral Rail, the distance between each layer is 5
#  Measured in Level 10.

c_DefaultRailRadius: float = 0.35
c_DefaultRailSpan: float = 3.75
c_SideRailSpan: float = 3.864
c_NormalSideRailAngle: float = 79.563
c_StoneSideRailAngle: float = 57
c_SpiralRailScrew: float = 5
c_SideSpiralRailScrew: float = 3.6

#region Operator Helpers

class SharedExtraTransform():
    """
    This class is served for all rail creation which allow user 
    provide extra transform after moving created rail to cursor.
    For "what you look is what you gotten" experience, this extra transform is essential.
    """

    extra_translation: bpy.props.FloatVectorProperty(
        name = "Extra Translation",
        description = "The extra translation applied to object after moving to cursor.",
        size = 3,
        subtype = 'TRANSLATION',
        step = 50, # same step as the float entry of BBP_PG_bme_adder_cfgs
        default = (0.0, 0.0, 0.0),
        translation_context = 'BBP/OP_ADDS_rail.SharedExtraTransform/property'
    ) # type: ignore
    extra_rotation: bpy.props.FloatVectorProperty(
        name = "Extra Rotation",
        description = "The extra rotation applied to object after moving to cursor.",
        size = 3,
        subtype = 'EULER',
        step = 100, # We choosen 100, mean 1. Sync with property window.
        default = (0.0, 0.0, 0.0),
        translation_context = 'BBP/OP_ADDS_rail.SharedExtraTransform/property'
    ) # type: ignore

    def draw_extra_transform_input(self, layout: bpy.types.UILayout) -> None:
        # show extra transform props
        # forcely order that each one are placed horizontally
        layout.label(text = "Extra Transform")
        # translation
        layout.label(text = 'Translation')
        row = layout.row()
        row.prop(self, 'extra_translation', text = '')
        # rotation
        layout.label(text = 'Rotation')
        row = layout.row()
        row.prop(self, 'extra_rotation', text = '')

    def general_get_extra_transform(self) -> mathutils.Matrix:
        return mathutils.Matrix.LocRotScale(
            mathutils.Vector(self.extra_translation),
            mathutils.Euler(self.extra_rotation, 'XYZ'),
            mathutils.Vector((1.0, 1.0, 1.0)) # no scale
        )

class SharedRailSectionInputProperty():
    """
    This class is served for user to pick the transition type of rail.
    And order rail radius and span accoridng to user picked rail type.
    """
    
    rail_type: bpy.props.EnumProperty(
        name = "Type",
        description = "Rail type",
        items = [
            ('MONORAIL', "Monorail", ""),
            ('RAIL', "Rail", ""),
        ],
        default = 'RAIL',
        translation_context = 'BBP/OP_ADDS_rail.SharedRailSectionInputProperty/property'
    ) # type: ignore

    def draw_rail_section_input(self, layout: bpy.types.UILayout) -> None:
        row = layout.row()
        row.prop(self, 'rail_type', expand = True)

    def general_get_is_monorail(self) -> bool:
        return self.rail_type == 'MONORAIL'

class SharedRailCapInputProperty():
    """
    This class provide properties for cap switch.
    Support head cap and tail cap. Both straight and screw rail can use this.
    """

    rail_start_cap: bpy.props.BoolProperty(
        name = 'Start Cap',
        description = 'Whether this rail should have cap at start terminal.',
        default = False,
        translation_context = 'BBP/OP_ADDS_rail.SharedRailCapInputProperty/property'
    ) # type: ignore

    rail_end_cap: bpy.props.BoolProperty(
        name = 'End Cap',
        description = 'Whether this rail should have cap at end terminal.',
        default = False,
        translation_context = 'BBP/OP_ADDS_rail.SharedRailCapInputProperty/property'
    ) # type: ignore

    def draw_rail_cap_input(self, layout: bpy.types.UILayout) -> None:
        layout.label(text = "Cap Options")
        row = layout.row()
        row.prop(self, "rail_start_cap", toggle = 1)
        row.prop(self, "rail_end_cap", toggle = 1)

    def general_get_rail_start_cap(self) -> bool:
        return self.rail_start_cap
    def general_get_rail_end_cap(self) -> bool:
        return self.rail_end_cap

class SharedStraightRailInputProperty():
    """
    The properties for straight rail.
    """

    rail_length: bpy.props.FloatProperty(
        name = "Length",
        description = "The length of this rail.",
        default = 5.0,
        min = 0,
        step = 50, # same unit as BME Struct
        unit = 'LENGTH',
        translation_context = 'BBP/OP_ADDS_rail.SharedStraightRailInputProperty/property'
    ) # type: ignore

    def draw_straight_rail_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_length")

    def general_get_rail_length(self) -> float:
        return self.rail_length

class SharedScrewRailInputProperty():
    """
    The properties for straight rail.
    """

    rail_screw_steps: bpy.props.IntProperty(
        name = "Steps",
        description = "The segment count per iteration. More segment, more smooth but lower performance.",
        default = 28,
        min = 1,
        translation_context = 'BBP/OP_ADDS_rail.SharedScrewRailInputProperty/property'
    ) # type: ignore

    rail_screw_radius: bpy.props.FloatProperty(
        name = "Radius",
        description = "The screw radius.",
        default = 5,
        min = 0,
        unit = 'LENGTH',
        translation_context = 'BBP/OP_ADDS_rail.SharedScrewRailInputProperty/property'
    ) # type: ignore

    rail_screw_flip_x: bpy.props.BoolProperty(
        name = 'Flip X',
        description = 'Whether flip this rail with X axis',
        default = False,
        translation_context = 'BBP/OP_ADDS_rail.SharedScrewRailInputProperty/property'
    ) # type: ignore

    rail_screw_flip_y: bpy.props.BoolProperty(
        name = 'Flip Y',
        description = 'Whether flip this rail with Y axis',
        default = False,
        translation_context = 'BBP/OP_ADDS_rail.SharedScrewRailInputProperty/property'
    ) # type: ignore

    rail_screw_flip_z: bpy.props.BoolProperty(
        name = 'Flip Z',
        description = 'Whether flip this rail with Z axis',
        default = False,
        translation_context = 'BBP/OP_ADDS_rail.SharedScrewRailInputProperty/property'
    ) # type: ignore

    def draw_screw_rail_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_screw_radius")
        layout.prop(self, "rail_screw_steps")

    def general_get_rail_screw_radius(self) -> float:
        return self.rail_screw_radius
    def general_get_rail_screw_steps(self) -> int:
        return self.rail_screw_steps
    
    def draw_screw_rail_flip_input(self, layout: bpy.types.UILayout) -> None:
        # flip options should placed horizontally
        layout.label(text = "Flip Options")
        row = layout.row()
        row.prop(self, "rail_screw_flip_x", toggle = 1)
        row.prop(self, "rail_screw_flip_y", toggle = 1)
        row.prop(self, "rail_screw_flip_z", toggle = 1)

    def general_get_rail_screw_flip_x(self) -> bool:
        return self.rail_screw_flip_x
    def general_get_rail_screw_flip_y(self) -> bool:
        return self.rail_screw_flip_y
    def general_get_rail_screw_flip_z(self) -> bool:
        return self.rail_screw_flip_z
    
#endregion

#region Operators

class BBP_OT_add_rail_section(SharedRailSectionInputProperty, bpy.types.Operator):
    """Add Rail Section"""
    bl_idname = "bbp.add_rail_section"
    bl_label = "Rail Section"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_rail_section'

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_rail_section(
                bm, self.general_get_is_monorail(), 
                c_DefaultRailRadius, c_DefaultRailSpan
            ),
            mathutils.Matrix.Identity(4)
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_section_input(layout)

class BBP_OT_add_transition_section(bpy.types.Operator):
    """Add Transition Section"""
    bl_idname = "bbp.add_transition_section"
    bl_label = "Transition Section"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_transition_section'

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_transition_section(bm, c_DefaultRailRadius, c_DefaultRailSpan),
            mathutils.Matrix.Identity(4)
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'No Options Available')

class BBP_OT_add_straight_rail(SharedExtraTransform, SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Straight Rail"""
    bl_idname = "bbp.add_straight_rail"
    bl_label = "Straight Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_straight_rail'

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_straight_rail(
                bm,
                self.general_get_is_monorail(), c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(), 0,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Straight Rail')
        self.draw_rail_section_input(layout)
        self.draw_straight_rail_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

class BBP_OT_add_transition_rail(SharedExtraTransform, SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Transition Rail"""
    bl_idname = "bbp.add_transition_rail"
    bl_label = "Transition Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_transition_rail'

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_transition_rail(
                bm,
                c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(),
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Transition Rail')
        self.draw_straight_rail_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

class BBP_OT_add_side_rail(SharedExtraTransform, SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Side Rail"""
    bl_idname = "bbp.add_side_rail"
    bl_label = "Side Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_side_rail'

    side_rail_type: bpy.props.EnumProperty(
        name = "Side Type",
        description = "Side rail type",
        items = [
            ('NORMAL', "Normal", "The normal side rail."),
            ('STONE', "Stone Specific", "The side rail which also allow stone ball passed."),
        ],
        default = 'NORMAL',
        translation_context = 'BBP_OT_add_side_rail/property'
    ) # type: ignore

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_straight_rail(
                bm,
                False, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(), 
                c_NormalSideRailAngle if self.side_rail_type == 'NORMAL' else c_StoneSideRailAngle,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Side Rail')
        layout.prop(self, 'side_rail_type')
        self.draw_straight_rail_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

class BBP_OT_add_arc_rail(SharedExtraTransform, SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Arc Rail"""
    bl_idname = "bbp.add_arc_rail"
    bl_label = "Arc Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_arc_rail'

    rail_screw_angle: bpy.props.FloatProperty(
        name = "Angle",
        description = "The angle of this arc rail rotated.",
        default = math.radians(90),
        min = 0, max = math.radians(360),
        subtype = 'ANGLE',
        translation_context = 'BBP_OT_add_arc_rail/property'
    ) # type: ignore

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_screw_rail(
                bm,
                self.general_get_is_monorail(), c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                math.degrees(self.rail_screw_angle), 0, 1,  # blender passed value is in radians
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius(),
                self.general_get_rail_screw_flip_x(), self.general_get_rail_screw_flip_y(), self.general_get_rail_screw_flip_z()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Arc Rail')
        self.draw_rail_section_input(layout)
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_angle")
        layout.separator()
        self.draw_screw_rail_flip_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

class BBP_OT_add_spiral_rail(SharedExtraTransform, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Spiral Rail"""
    bl_idname = "bbp.add_spiral_rail"
    bl_label = "Spiral Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_spiral_rail'

    rail_screw_screw: bpy.props.FloatProperty(
        name = "Screw",
        description = "The increased height in each iteration. Minus height also is accepted.",
        default = c_SpiralRailScrew,
        unit = 'LENGTH',
        translation_context = 'BBP_OT_add_spiral_rail/property'
    ) # type: ignore

    rail_screw_iterations: bpy.props.IntProperty(
        name = "Iterations",
        description = "Indicate how many layers of this spiral rail should be generated.",
        default = 1,
        min = 1,
        translation_context = 'BBP_OT_add_spiral_rail/property'
    ) # type: ignore

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_screw_rail(
                bm,
                False, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                360, self.rail_screw_screw, self.rail_screw_iterations,
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius(),
                self.general_get_rail_screw_flip_x(), self.general_get_rail_screw_flip_y(), self.general_get_rail_screw_flip_z()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Spiral Rail')
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_screw")
        layout.prop(self, "rail_screw_iterations")
        layout.separator()
        self.draw_screw_rail_flip_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

class BBP_OT_add_side_spiral_rail(SharedExtraTransform, SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Side Spiral Rail"""
    bl_idname = "bbp.add_side_spiral_rail"
    bl_label = "Side Spiral Rail"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_side_spiral_rail'

    rail_screw_iterations: bpy.props.IntProperty(
        name = "Iterations",
        description = "Indicate how many layers of this spiral rail should be generated.",
        default = 2,
        # at least 2 ietrations can create 1 useful side spiral rail.
        # becuase side spiral rail is edge shared.
        min = 2,
        translation_context = 'BBP_OT_add_side_spiral_rail/property'
    ) # type: ignore

    def execute(self, context):
        UTIL_rail_creator.rail_creator_wrapper(
            lambda bm: UTIL_rail_creator.create_screw_rail(
                bm,
                True, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                360, c_SideSpiralRailScrew, self.rail_screw_iterations,
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius(),
                self.general_get_rail_screw_flip_x(), self.general_get_rail_screw_flip_y(), self.general_get_rail_screw_flip_z()
            ),
            self.general_get_extra_transform()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Spiral Rail')
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_iterations")
        layout.separator()
        self.draw_screw_rail_flip_input(layout)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_extra_transform_input(layout)

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_add_rail_section)
    bpy.utils.register_class(BBP_OT_add_transition_section)

    bpy.utils.register_class(BBP_OT_add_straight_rail)
    bpy.utils.register_class(BBP_OT_add_transition_rail)
    bpy.utils.register_class(BBP_OT_add_side_rail)

    bpy.utils.register_class(BBP_OT_add_arc_rail)
    bpy.utils.register_class(BBP_OT_add_spiral_rail)
    bpy.utils.register_class(BBP_OT_add_side_spiral_rail)


def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_add_side_spiral_rail)
    bpy.utils.unregister_class(BBP_OT_add_spiral_rail)
    bpy.utils.unregister_class(BBP_OT_add_arc_rail)

    bpy.utils.unregister_class(BBP_OT_add_side_rail)
    bpy.utils.unregister_class(BBP_OT_add_transition_rail)
    bpy.utils.unregister_class(BBP_OT_add_straight_rail)

    bpy.utils.unregister_class(BBP_OT_add_transition_section)
    bpy.utils.unregister_class(BBP_OT_add_rail_section)
