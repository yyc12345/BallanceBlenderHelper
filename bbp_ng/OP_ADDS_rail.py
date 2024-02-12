import bpy, bmesh, mathutils, math
import typing
from . import UTIL_functions, UTIL_naming_convension

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
        default = False
    ) # type: ignore

    rail_end_cap: bpy.props.BoolProperty(
        name = 'End Cap',
        description = 'Whether this rail should have cap at end terminal.',
        default = False
    ) # type: ignore

    def draw_rail_cap_input(self, layout: bpy.types.UILayout) -> None:
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
        unit = 'LENGTH'
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
        default = 16,
        min = 1,
    ) # type: ignore

    rail_screw_radius: bpy.props.FloatProperty(
        name = "Radius",
        description = "The screw radius. Minus radius will flip the built screw.",
        default = 5,
        unit = 'LENGTH'
    ) # type: ignore

    def draw_screw_rail_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_screw_radius")
        layout.prop(self, "rail_screw_steps")

    def general_get_rail_screw_radius(self) -> float:
        return self.rail_screw_radius
    def general_get_rail_screw_steps(self) -> int:
        return self.rail_screw_steps
    
#endregion

#region Operators

class BBP_OT_add_rail_section(SharedRailSectionInputProperty, bpy.types.Operator):
    """Add Rail Section"""
    bl_idname = "bbp.add_rail_section"
    bl_label = "Rail Section"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_rail_section(
                bm, self.general_get_is_monorail(), 
                c_DefaultRailRadius, c_DefaultRailSpan
            )
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

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_transition_section(bm, c_DefaultRailRadius, c_DefaultRailSpan)
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'No Options Available')

class BBP_OT_add_straight_rail(SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Straight Rail"""
    bl_idname = "bbp.add_straight_rail"
    bl_label = "Straight Rail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_straight_rail(
                bm,
                self.general_get_is_monorail(), c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(), 0,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Straight Rail')
        self.draw_rail_section_input(layout)
        self.draw_straight_rail_input(layout)
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

class BBP_OT_add_transition_rail(SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Transition Rail"""
    bl_idname = "bbp.add_transition_rail"
    bl_label = "Transition Rail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_transition_rail(
                bm,
                c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(),
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Transition Rail')
        self.draw_straight_rail_input(layout)
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

class BBP_OT_add_side_rail(SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Side Rail"""
    bl_idname = "bbp.add_side_rail"
    bl_label = "Side Rail"
    bl_options = {'REGISTER', 'UNDO'}

    side_rail_type: bpy.props.EnumProperty(
        name = "Side Type",
        description = "Side rail type",
        items = [
            ('NORMAL', "Normal", "The normal side rail."),
            ('STONE', "Stone Specific", "The side rail which also allow stone ball passed."),
        ],
        default = 'NORMAL',
    ) # type: ignore

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_straight_rail(
                bm,
                False, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_length(), 
                c_NormalSideRailAngle if self.side_rail_type == 'NORMAL' else c_StoneSideRailAngle,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Side Rail')
        layout.prop(self, 'side_rail_type')
        self.draw_straight_rail_input(layout)
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

class BBP_OT_add_arc_rail(SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Arc Rail"""
    bl_idname = "bbp.add_arc_rail"
    bl_label = "Arc Rail"
    bl_options = {'REGISTER', 'UNDO'}

    rail_screw_angle: bpy.props.FloatProperty(
        name = "Angle",
        description = "The angle of this arc rail rotated.",
        default = math.radians(90),
        min = 0, max = math.radians(360),
        subtype = 'ANGLE',
    ) # type: ignore

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_screw_rail(
                bm,
                self.general_get_is_monorail(), c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                math.degrees(self.rail_screw_angle), 0, 1,  # blender passed value is in radians
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Arc Rail')
        self.draw_rail_section_input(layout)
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_angle")
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

class BBP_OT_add_spiral_rail(SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Spiral Rail"""
    bl_idname = "bbp.add_spiral_rail"
    bl_label = "Spiral Rail"
    bl_options = {'REGISTER', 'UNDO'}

    rail_screw_screw: bpy.props.FloatProperty(
        name = "Screw",
        description = "The increased height in each iteration. Minus height also is accepted.",
        default = c_SpiralRailScrew,
        unit = 'LENGTH'
    ) # type: ignore

    rail_screw_iterations: bpy.props.IntProperty(
        name = "Iterations",
        description = "Indicate how many layers of this spiral rail should be generated.",
        default = 1,
        min = 1,
    ) # type: ignore

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_screw_rail(
                bm,
                False, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                360, self.rail_screw_screw, self.rail_screw_iterations,
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Spiral Rail')
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_screw")
        layout.prop(self, "rail_screw_iterations")
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

class BBP_OT_add_side_spiral_rail(SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Side Spiral Rail"""
    bl_idname = "bbp.add_side_spiral_rail"
    bl_label = "Side Spiral Rail"
    bl_options = {'REGISTER', 'UNDO'}

    rail_screw_iterations: bpy.props.IntProperty(
        name = "Iterations",
        description = "Indicate how many layers of this spiral rail should be generated.",
        default = 2,
        # at least 2 ietrations can create 1 useful side spiral rail.
        # becuase side spiral rail is edge shared.
        min = 2,
    ) # type: ignore

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_screw_rail(
                bm,
                True, c_DefaultRailRadius, c_DefaultRailSpan,
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                360, c_SideSpiralRailScrew, self.rail_screw_iterations,
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Spiral Rail')
        self.draw_screw_rail_input(layout)
        layout.prop(self, "rail_screw_iterations")
        layout.separator()
        layout.label(text = 'Rail Cap')
        self.draw_rail_cap_input(layout)

#endregion

#region BMesh Operations Helper

def _bmesh_extrude(bm: bmesh.types.BMesh, start_edges: list[bmesh.types.BMEdge], direction: mathutils.Vector) -> list[bmesh.types.BMEdge]:
    # extrude
    ret: dict[str, typing.Any] = bmesh.ops.extrude_edge_only(
        bm,
        edges = start_edges, 
        use_normal_flip = True, # NOTE: flip normal according to test result.
        use_select_history = False
    )

    # get end edges
    ret_geom = ret['geom']
    del ret
    end_verts: list[bmesh.types.BMVert] = list(filter(lambda x: isinstance(x, bmesh.types.BMVert), ret_geom))
    end_edges: list[bmesh.types.BMEdge] = list(filter(lambda x: isinstance(x, bmesh.types.BMEdge) and x.is_boundary, ret_geom))
    # and move it
    bmesh.ops.translate(
        bm,
        vec = direction, space = mathutils.Matrix.Identity(4),
        verts = end_verts,
        use_shapekey = False
    )

    # return value
    return end_edges

def _bmesh_screw(
        bm: bmesh.types.BMesh,
        start_verts: list[bmesh.types.BMVert], start_edges: list[bmesh.types.BMEdge],
        angle: float, steps: int, iterations: int,
        center: mathutils.Vector, screw_per_iteration: float) -> list[bmesh.types.BMEdge]:
    """
    Hints: Angle is input as degree unit.
    """
    # screw
    ret: dict[str, typing.Any] = bmesh.ops.spin(
        bm,
        geom = start_edges,
        cent = center, 
        axis = mathutils.Vector((0, 0, 1)), # default to +Z
        dvec = mathutils.Vector((0, 0, screw_per_iteration / steps)), # conv to step delta
        angle = math.radians(angle) * iterations,
        space = mathutils.Matrix.Identity(4),
        steps = steps * iterations,
        use_merge = False,
        use_normal_flip = True, # NOTE: flip nml according to real test result
        use_duplicate = False
    )

    # return last segment
    geom_last = ret['geom_last']
    del ret
    return list(filter(lambda x: isinstance(x, bmesh.types.BMEdge), geom_last))

def _bmesh_smooth_all_edges(bm: bmesh.types.BMesh) -> None:
    """
    Resrt all edges to smooth. Call this before calling edge cap function.
    """
    # reset all edges to smooth
    edge: bmesh.types.BMEdge
    for edge in bm.edges:
        edge.smooth = True

def _bmesh_cap(bm: bmesh.types.BMesh, edges: list[bmesh.types.BMEdge]) -> None:
    """
    Cap given edges. And mark it as sharp edge.
    Please reset all edges to smooth one before calling this.
    """
    # fill holes
    bmesh.ops.triangle_fill(
        bm,
        use_beauty = False, use_dissolve = False,
        edges = edges
        # no pass to normal.
    )
    
    # and only set sharp for cap's edges
    for edge in edges:
        edge.smooth = False

#endregion

#region Real Rail Creators

def _rail_creator_wrapper(fct_poly_cret: typing.Callable[[bmesh.types.BMesh], None]) -> bpy.types.Object:
    # create mesh first
    bm: bmesh.types.BMesh = bmesh.new()

    # call cret fct
    fct_poly_cret(bm)

    # finish up
    mesh: bpy.types.Mesh = bpy.data.meshes.new('Rail')
    bm.to_mesh(mesh)
    bm.free()
    
    # setup smooth for mesh
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(50)
    mesh.shade_smooth()

    # create object and assoc with it
    # create info first
    rail_info: UTIL_naming_convension.BallanceObjectInfo = UTIL_naming_convension.BallanceObjectInfo.create_from_others(
        UTIL_naming_convension.BallanceObjectType.RAIL
    )
    # then get object name
    rail_name: str | None = UTIL_naming_convension.YYCToolchainConvention.set_to_name(rail_info, None)
    if rail_name is None: raise UTIL_functions.BBPException('impossible null name')
    # create object by name
    obj: bpy.types.Object = bpy.data.objects.new(rail_name, mesh)
    # assign virtools groups
    UTIL_naming_convension.VirtoolsGroupConvention.set_to_object(obj, rail_info, None)

    # move to cursor
    UTIL_functions.add_into_scene_and_move_to_cursor(obj)
    # select created object
    UTIL_functions.select_certain_objects((obj, ))
    
    # return rail
    return obj

def _create_rail_section(
        bm: bmesh.types.BMesh,
        is_monorail: bool, rail_radius: float, rail_span: float, 
        matrix: mathutils.Matrix = mathutils.Matrix.Identity(4)) -> None:
    """
    Add a rail section.

    If created is monorail, the original point locate at the center of section.
    Otherwise, the original point locate at the center point of the line connecting between left rail section and right rail section.
    The section will be placed in XZ panel.

    If ordered is monorail, `rail_span` param will be ignored.
    """
    if is_monorail:
        # create monorail
        bmesh.ops.create_circle(
            bm, cap_ends = False, cap_tris = False, segments = 8, radius = rail_radius,
            matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
                None,
                mathutils.Euler((math.radians(90), math.radians(22.5), 0), 'XYZ'),
                None
            )), 
            calc_uvs = False
        )
    else:
        # create rail
        # create left rail
        bmesh.ops.create_circle(
            bm, cap_ends = False, cap_tris = False, segments = 8, radius = rail_radius,
            matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
                mathutils.Vector((-rail_span / 2, 0, 0)), 
                mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
                None
            )),
            calc_uvs = False
        )
        # create right rail
        bmesh.ops.create_circle(
            bm, cap_ends = False, cap_tris = False, segments = 8, radius = rail_radius,
            matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
                mathutils.Vector((rail_span / 2, 0, 0)), 
                mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
                None
            )),
            calc_uvs = False
        )

def _create_transition_section(
        bm: bmesh.types.BMesh,
        rail_radius: float, rail_span: float) -> None:
    """
    Create the transition section between rail and monorail.
    """
    # create rail section
    _create_rail_section(bm, False, rail_radius, rail_span)

    # create monorail
    # calc sink first
    monorail_sink: float
    try:
        monorail_sink = math.sqrt((rail_radius + 2) ** 2 - (rail_span / 2) ** 2) - 2 - rail_radius
    except:
        monorail_sink = -2 # if sqrt(minus number) happended, it mean no triangle relation. the depth should always be -2.
    # create monorail with calculated sink
    _create_rail_section(
        bm, True, rail_radius, rail_span,
        mathutils.Matrix.Translation((0, 0, monorail_sink))
    )

def _create_straight_rail(
        bm: bmesh.types.BMesh,
        is_monorail: bool, rail_radius: float, rail_span: float,
        rail_length: float, rail_angle: float,
        rail_start_cap: bool, rail_end_cap: bool) -> None:
    """
    Add a straight rail.

    The original point is same as `_add_rail_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.

    If ordered is monorail, `rail_span` param will be ignored.

    The rail angle is in degree unit and indicate how any angle this rail should rotated by its axis.
    It usually used to create side rail.
    """
    # create section first
    _create_rail_section(
        bm, is_monorail, rail_radius, rail_span,
        mathutils.Matrix.LocRotScale(
            None,
            mathutils.Euler((0, math.radians(rail_angle), 0), 'XYZ'),
            None
        )
    )

    # get start edges
    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    # extrude and get end edges
    end_edges: list[bmesh.types.BMEdge] = _bmesh_extrude(
        bm, start_edges, mathutils.Vector((0, rail_length, 0))
    )

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

def _create_transition_rail(
        bm: bmesh.types.BMesh,
        rail_radius: float, rail_span: float,
        rail_length: float,
        rail_start_cap: bool, rail_end_cap: bool) -> None:
    """
    Add a transition rail.

    The original point is same as `_add_transition_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.
    """
    # create section first
    _create_transition_section(bm, rail_radius, rail_span)

    # get start edges
    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    # extrude and get end edges
    end_edges: list[bmesh.types.BMEdge] = _bmesh_extrude(
        bm, start_edges, mathutils.Vector((0, rail_length, 0))
    )

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

def _create_screw_rail(
        bm: bmesh.types.BMesh, 
        is_monorail: bool, rail_radius: float, rail_span: float,
        rail_start_cap: bool, rail_end_cap: bool,
        rail_screw_angle: float, rail_screw_screw: float, rail_screw_iterations: int,
        rail_screw_steps: int, rail_screw_radius: float) -> None:
    """
    Add a screw rail.

    The original point is same as `_add_rail_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.

    If ordered is monorail, `rail_span` param will be ignored.

    Angle is input as degree unit.
    """
    # create section first
    _create_rail_section(bm, is_monorail, rail_radius, rail_span)

    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    end_edges: list[bmesh.types.BMEdge] = _bmesh_screw(
        bm,
        bm.verts[:], start_edges,
        rail_screw_angle, 
        rail_screw_steps, rail_screw_iterations,
        mathutils.Vector((rail_screw_radius, 0, 0)),
        rail_screw_screw
    )

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

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
