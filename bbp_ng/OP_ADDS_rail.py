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

#region Operators

class SharedRailInputProperty():
    rail_radius: bpy.props.FloatProperty(
        name = "Rail Radius",
        description = "Define rail section radius",
        default = 0.35,
        min = 0,
    ) # type: ignore

    rail_span: bpy.props.FloatProperty(
        name = "Rail Span",
        description = "The length between 2 single rails.",
        default = 3.75,
        min = 0,
    ) # type: ignore

    rail_length: bpy.props.FloatProperty(
        name = "Rail Length",
        description = "The length of this rail.",
        default = 5.0,
        min = 0,
        step = 50, # same unit as BME Struct
    ) # type: ignore

    rail_cap: bpy.props.BoolProperty(
        name = 'Rail Cap',
        description = 'Whether this rail should have terminal cap.',
        default = False
    ) # type: ignore

    def draw_rail_radius_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_radius")
    def draw_rail_span_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_span")
    def draw_rail_length_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_length")
    def draw_rail_cap_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, "rail_cap")

    def general_get_rail_radius(self) -> float:
        return self.rail_radius
    def general_get_rail_span(self) -> float:
        return self.rail_span
    def general_get_rail_length(self) -> float:
        return self.rail_length
    def general_get_rail_cap(self) -> bool:
        return self.rail_cap

class BBP_OT_add_monorail_section(SharedRailInputProperty, bpy.types.Operator):
    """Add Monorail Section"""
    bl_idname = "bbp.add_monorail_section"
    bl_label = "Monorail Section"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _create_monorail_section(self.general_get_rail_radius())
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_radius_input(layout)

class BBP_OT_add_rail_section(SharedRailInputProperty, bpy.types.Operator):
    """Add Rail Section"""
    bl_idname = "bbp.add_rail_section"
    bl_label = "Rail Section"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _create_rail_section(self.general_get_rail_radius(), self.general_get_rail_span())
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_radius_input(layout)
        self.draw_rail_span_input(layout)

class BBP_OT_add_transition_section(SharedRailInputProperty, bpy.types.Operator):
    """Add Transition Section"""
    bl_idname = "bbp.add_transition_section"
    bl_label = "Transition Section"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # calc sink
        radius_: float = self.general_get_rail_radius()
        span_: float = self.general_get_rail_span()
        sink_: float
        try:
            sink_ = math.sqrt((radius_ + 2) ** 2 - (span_ / 2) ** 2) - 2 - radius_
        except:
            sink_ = -2 # if sqrt(minus number) happended, it mean no triangle relation. the depth should always be -2.

        # create section
        _create_transition_section(radius_, span_, sink_)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_radius_input(layout)
        self.draw_rail_span_input(layout)

class BBP_OT_add_straight_monorail(SharedRailInputProperty, bpy.types.Operator):
    """Add Straight Monorail"""
    bl_idname = "bbp.add_straight_monorail"
    bl_label = "Straight Monorail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _create_straight_monorail(
            self.general_get_rail_radius(),
            self.general_get_rail_length(),
            self.general_get_rail_cap()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_radius_input(layout)
        self.draw_rail_length_input(layout)
        self.draw_rail_cap_input(layout)

class BBP_OT_add_straight_rail(SharedRailInputProperty, bpy.types.Operator):
    """Add Straight Rail"""
    bl_idname = "bbp.add_straight_rail"
    bl_label = "Straight Rail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _create_straight_rail(
            self.general_get_rail_radius(),
            self.general_get_rail_span(),
            self.general_get_rail_length(),
            self.general_get_rail_cap()
        )
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        self.draw_rail_radius_input(layout)
        self.draw_rail_span_input(layout)
        self.draw_rail_length_input(layout)
        self.draw_rail_cap_input(layout)

#endregion

#region Modifier Adder

def _set_screw_modifier(obj: bpy.types.Object) -> None:
    pass

#endregion

#region Polygon Adders

def _polygon_adder_wrapper(fct_poly_cret: typing.Callable[[bmesh.types.BMesh], None]) -> bpy.types.Object:
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

def _add_monorail_section(
        bm: bmesh.types.BMesh, 
        matrix: mathutils.Matrix,
        rail_radius: float) -> None:
    """
    Add a monorail section.
    The original point locate at the center of section. The section will be placed in XZ panel.
    """
    # create
    bmesh.ops.create_circle(
        bm,
        cap_ends = False, cap_tris = False,
        segments = 8,
        radius = rail_radius,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            None,
            mathutils.Euler((math.radians(90), math.radians(22.5), 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )

def _add_rail_section(
        bm: bmesh.types.BMesh, 
        matrix: mathutils.Matrix,
        rail_radius: float,
        rail_span: float) -> None:
    """
    Add a rail section.
    The original point locate at the center point of the line connecting between left rail section and right rail section.
    The section will be placed in XZ panel.
    """
    # create left one
    bmesh.ops.create_circle(
        bm,
        cap_ends = False, cap_tris = False,
        segments = 8,
        radius = rail_radius,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            mathutils.Vector((-rail_span / 2, 0, 0)), 
            mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )
    # create right one
    bmesh.ops.create_circle(
        bm,
        cap_ends = False, cap_tris = False,
        segments = 8,
        radius = rail_radius,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            mathutils.Vector((rail_span / 2, 0, 0)), 
            mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )

def _add_straight_monorail(
        bm: bmesh.types.BMesh, 
        length: float, 
        matrix: mathutils.Matrix,
        has_cap: bool,
        rail_radius: float) -> None:
    """
    Add a straight monorail.
    The original point is same as `_add_monorail_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.
    """
    # create left one
    bmesh.ops.create_cone(
        bm,
        cap_ends = has_cap, cap_tris = True,
        segments = 8,
        radius1 = rail_radius, radius2 = rail_radius,
        depth = length,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            mathutils.Vector((0, length / 2, 0)), 
            mathutils.Euler((math.radians(90), math.radians(22.5), 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )

def _add_straight_rail(
        bm: bmesh.types.BMesh, 
        length: float, 
        matrix: mathutils.Matrix,
        has_cap: bool,
        rail_radius: float, rail_span: float) -> None:
    """
    Add a straight rail.
    The original point is same as `_add_rail_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.
    """
    # create left one
    bmesh.ops.create_cone(
        bm,
        cap_ends = has_cap, cap_tris = True,
        segments = 8,
        radius1 = rail_radius, radius2 = rail_radius,
        depth = length,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            mathutils.Vector((-rail_span / 2, length / 2, 0)), 
            mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )
    # create right one
    bmesh.ops.create_cone(
        bm,
        cap_ends = has_cap, cap_tris = True,
        segments = 8,
        radius1 = rail_radius, radius2 = rail_radius,
        depth = length,
        matrix = typing.cast(mathutils.Matrix, matrix @ mathutils.Matrix.LocRotScale(
            mathutils.Vector((rail_span / 2, length / 2, 0)), 
            mathutils.Euler((math.radians(90), 0, 0), 'XYZ'),
            None
        )),
        calc_uvs = False
    )

#endregion

#region Rail Adder

def _create_monorail_section(rail_radius: float) -> bpy.types.Object:
    return _polygon_adder_wrapper(
        lambda bm: _add_monorail_section(bm, mathutils.Matrix.Identity(4), rail_radius)
    )

def _create_rail_section(rail_radius: float, rail_span: float) -> bpy.types.Object:
    return _polygon_adder_wrapper(
        lambda bm: _add_rail_section(bm, mathutils.Matrix.Identity(4), rail_radius, rail_span)
    )

def _create_transition_section(rail_radius: float, rail_span: float, monorail_sink: float) -> bpy.types.Object:
    def invoker(bm: bmesh.types.BMesh) -> None:
        _add_rail_section(bm, mathutils.Matrix.Identity(4), rail_radius, rail_span)
        _add_monorail_section(bm, mathutils.Matrix.Translation((0, 0, monorail_sink)), rail_radius)
    return _polygon_adder_wrapper(invoker)

def _create_straight_monorail(rail_radius: float, rail_length: float, rail_cap: bool) -> bpy.types.Object:
    return _polygon_adder_wrapper(
        lambda bm: _add_straight_monorail(bm, rail_length, mathutils.Matrix.Identity(4), rail_cap, rail_radius)
    )

def _create_straight_rail(rail_radius: float, rail_span: float, rail_length: float, rail_cap: bool) -> bpy.types.Object:
    return _polygon_adder_wrapper(
        lambda bm: _add_straight_rail(bm, rail_length, mathutils.Matrix.Identity(4), rail_cap, rail_radius, rail_span)
    )

#endregion

def register():
    bpy.utils.register_class(BBP_OT_add_monorail_section)
    bpy.utils.register_class(BBP_OT_add_rail_section)
    bpy.utils.register_class(BBP_OT_add_transition_section)

    bpy.utils.register_class(BBP_OT_add_straight_monorail)
    bpy.utils.register_class(BBP_OT_add_straight_rail)


def unregister():
    bpy.utils.unregister_class(BBP_OT_add_straight_rail)
    bpy.utils.unregister_class(BBP_OT_add_straight_monorail)

    bpy.utils.unregister_class(BBP_OT_add_transition_section)
    bpy.utils.unregister_class(BBP_OT_add_rail_section)
    bpy.utils.unregister_class(BBP_OT_add_monorail_section)
