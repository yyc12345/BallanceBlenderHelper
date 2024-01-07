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

    rail_radius: bpy.props.FloatProperty(
        name = "Radius",
        description = "Define rail section radius",
        default = 0.35,
        min = 0,
        unit = 'LENGTH'
    ) # type: ignore

    rail_span: bpy.props.FloatProperty(
        name = "Span",
        description = "The length between 2 single rails.",
        default = 3.75,
        min = 0,
        unit = 'LENGTH'
    ) # type: ignore

    def draw_rail_section_input(self, layout: bpy.types.UILayout, force_monorail: bool | None) -> None:
        """
        Draw rail section properties

        @param force_monorail[in] Force this draw method for monorail if True, or for rail if False. Accept None if you want user to choose it.
        """
        if force_monorail is None:
            # show picker to allow user pick
            layout.prop(self, 'rail_type', expand = True)
            # show radius
            layout.prop(self, "rail_radius")
            # show span for rail
            if self.rail_type == 'RAIL':
                layout.prop(self, "rail_span")
        else:
            # according to force type to show
            # always show radius
            layout.prop(self, "rail_radius")
            # show span in condition
            if not force_monorail:
                layout.prop(self, "rail_span")

    def general_get_is_monorail(self) -> bool:
        return self.rail_type == 'MONORAIL'
    def general_get_rail_radius(self) -> float:
        return self.rail_radius
    def general_get_rail_span(self) -> float:
        return self.rail_span

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

    rail_screw_angle: bpy.props.FloatProperty(
        name = "Angle",
        description = "The angle of this screw rail rotated in one interation.",
        default = 90,
        subtype = 'ANGLE',
    ) # type: ignore

    rail_screw_screw: bpy.props.FloatProperty(
        name = "Screw",
        description = "The increased height in each iteration. Minus height also is accepted.",
        default = 6,
        unit = 'LENGTH'
    ) # type: ignore

    rail_screw_iterations: bpy.props.IntProperty(
        name = "Iterations",
        description = "The angle of this screw rail rotated in one interation.",
        default = 1,
        min = 1,
    ) # type: ignore

    rail_screw_steps: bpy.props.IntProperty(
        name = "Steps",
        description = "The segment count per iteration.",
        default = 20,
        min = 1,
    ) # type: ignore

    rail_screw_radius: bpy.props.FloatProperty(
        name = "Radius",
        description = "The screw radius. Minus radius will flip the built screw.",
        default = 10,
        unit = 'LENGTH'
    ) # type: ignore

    def draw_screw_rail_input(self, layout: bpy.types.UILayout, show_for_screw: bool) -> None:
        if show_for_screw:
            # screw do not need angle property
            layout.prop(self, "rail_screw_screw")
            layout.prop(self, "rail_screw_iterations")
            layout.prop(self, "rail_screw_radius")
            layout.prop(self, "rail_screw_steps")
        else:
            # curve do not need iterations (always is 1)
            # and do not need screw (always is 0)
            layout.prop(self, "rail_screw_angle")
            layout.prop(self, "rail_screw_radius")
            layout.prop(self, "rail_screw_steps")

    # Getter should return default value if corresponding field
    # is not existing in that mode.

    def general_get_rail_screw_angle(self, is_for_screw: bool) -> float:
        """This function return angle in degree unit."""
        return 360 if is_for_screw else self.rail_screw_angle
    def general_get_rail_screw_screw(self, is_for_screw: bool) -> float:
        return self.rail_screw_screw if is_for_screw else 0
    def general_get_rail_screw_iterations(self, is_for_screw: bool) -> int:
        return self.rail_screw_iterations if is_for_screw else 1
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
                bm, 
                self.general_get_is_monorail(), self.general_get_rail_radius(), self.general_get_rail_span()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_section_input(layout, None)

class BBP_OT_add_transition_section(SharedRailSectionInputProperty, bpy.types.Operator):
    """Add Transition Section"""
    bl_idname = "bbp.add_transition_section"
    bl_label = "Transition Section"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_transition_section(
                bm,
                self.general_get_rail_radius(), self.general_get_rail_span()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # force show double rail params
        self.draw_rail_section_input(layout, False)

class BBP_OT_add_straight_rail(SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedStraightRailInputProperty, bpy.types.Operator):
    """Add Straight Rail"""
    bl_idname = "bbp.add_straight_rail"
    bl_label = "Straight Rail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_straight_rail(
                bm,
                self.general_get_is_monorail(), self.general_get_rail_radius(), self.general_get_rail_span(),
                self.general_get_rail_length(),
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_section_input(layout, None)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_straight_rail_input(layout)

class BBP_OT_add_screw_rail(SharedRailSectionInputProperty, SharedRailCapInputProperty, SharedScrewRailInputProperty, bpy.types.Operator):
    """Add Screw Rail"""
    bl_idname = "bbp.add_screw_rail"
    bl_label = "Screw Rail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _rail_creator_wrapper(
            lambda bm: _create_screw_rail(
                bm,
                self.general_get_is_monorail(), self.general_get_rail_radius(), self.general_get_rail_span(),
                self.general_get_rail_start_cap(), self.general_get_rail_end_cap(),
                self.general_get_rail_screw_angle(True), self.general_get_rail_screw_screw(True), self.general_get_rail_screw_iterations(True),
                self.general_get_rail_screw_steps(), self.general_get_rail_screw_radius()
            )
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_section_input(layout, None)
        layout.separator()
        self.draw_rail_cap_input(layout)
        layout.separator()
        self.draw_screw_rail_input(layout, True)

#endregion

#region BMesh Operations Helper

def _bmesh_extrude(bm: bmesh.types.BMesh, start_edges: list[bmesh.types.BMEdge], direction: mathutils.Vector) -> list[bmesh.types.BMEdge]:
    # extrude
    ret: dict[str, typing.Any] = bmesh.ops.extrude_edge_only(
        bm,
        edges = start_edges, 
        use_normal_flip = False, use_select_history = False
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
    # screw
    ret: dict[str, typing.Any] = bmesh.ops.spin(
        bm,
        geom = start_edges,
        cent = center, 
        axis = mathutils.Vector((0, 0, 1)), # default to +Z
        dvec = mathutils.Vector((0, 0, screw_per_iteration / steps)), # conv to step delta
        angle = angle * iterations,
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

def _bmesh_cap(bm: bmesh.types.BMesh, edges: list[bmesh.types.BMEdge]) -> None:
    # fill holes
    bmesh.ops.triangle_fill(
        bm,
        use_beauty = False, use_dissolve = False,
        edges = edges
        # no pass to normal.
    )

def _bmesh_mark_sharp(bm: bmesh.types.BMesh, edges: typing.Iterable[list[bmesh.types.BMEdge]]) -> None:
    # Ref: https://blender.stackexchange.com/questions/41351/is-there-a-way-to-select-edges-marked-as-sharp-via-python/41352#41352

    # reset all edges to smooth
    edge: bmesh.types.BMEdge
    for edge in bm.edges:
        edge.smooth = True

    # and only set sharp for specified edges
    for subedges in edges:
        for edge in subedges:
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
        rail_length: float,
        rail_start_cap: bool, rail_end_cap: bool) -> None:
    """
    Add a straight rail.
    The original point is same as `_add_rail_section()`.
    The expand direction is +Y.
    If ordered is monorail, `rail_span` param will be ignored.
    """
    # create section first
    _create_rail_section(bm, is_monorail, rail_radius, rail_span)

    # get start edges
    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    # extrude and get end edges
    end_edges: list[bmesh.types.BMEdge] = _bmesh_extrude(
        bm, start_edges, mathutils.Vector((0, rail_length, 0))
    )

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

    # mark sharp
    _bmesh_mark_sharp(bm, (start_edges, end_edges, ))

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
    """
    # create section first
    _create_rail_section(bm, is_monorail, rail_radius, rail_span)

    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    end_edges: list[bmesh.types.BMEdge] = _bmesh_screw(
        bm,
        bm.verts[:], start_edges,
        math.radians(rail_screw_angle), 
        rail_screw_steps, rail_screw_iterations,
        mathutils.Vector((rail_screw_radius, 0, 0)),
        rail_screw_screw
    )

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

    _bmesh_mark_sharp(bm, (start_edges, end_edges, ))

#endregion

def register():
    bpy.utils.register_class(BBP_OT_add_rail_section)
    bpy.utils.register_class(BBP_OT_add_transition_section)
    bpy.utils.register_class(BBP_OT_add_straight_rail)
    bpy.utils.register_class(BBP_OT_add_screw_rail)


def unregister():
    bpy.utils.unregister_class(BBP_OT_add_screw_rail)
    bpy.utils.unregister_class(BBP_OT_add_straight_rail)
    bpy.utils.unregister_class(BBP_OT_add_transition_section)
    bpy.utils.unregister_class(BBP_OT_add_rail_section)
