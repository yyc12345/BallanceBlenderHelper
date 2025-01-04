import bpy, bmesh, mathutils, math
import typing
from . import UTIL_functions, UTIL_naming_convension
from . import PROP_bme_material

#region BMesh Operations Helper

def _bmesh_extrude(
        bm: bmesh.types.BMesh, 
        start_edges: list[bmesh.types.BMEdge], 
        direction: mathutils.Vector) -> list[bmesh.types.BMEdge]:
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
        use_normal_flip = True, # NOTE: flip normal according to test result.
        use_duplicate = False
    )

    # return last segment
    geom_last = ret['geom_last']
    del ret
    return list(filter(lambda x: isinstance(x, bmesh.types.BMEdge), geom_last))

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

def _bmesh_smooth_all_edges(bm: bmesh.types.BMesh) -> None:
    """
    Reset all edges to smooth. Call this before calling edge cap function.
    """
    # reset all edges to smooth
    edge: bmesh.types.BMEdge
    for edge in bm.edges:
        edge.smooth = True

def _bmesh_flip_all_faces(bm: bmesh.types.BMesh, flip_x: bool, flip_y: bool, flip_z: bool) -> None:
    """
    Flip the whole geometry in given bmesh with given axis.
    """
    # get mirror result
    scale_factor: mathutils.Vector = mathutils.Vector((
        (-1 if flip_x else 1),
        (-1 if flip_y else 1),
        (-1 if flip_z else 1)
    ))
    bmesh.ops.scale(bm, vec = scale_factor, verts = bm.verts[:])

    # check whether we need perform normal flip.
    # see UTIL_bme._is_mirror_matrix for more detail
    test_matrix: mathutils.Matrix = mathutils.Matrix.LocRotScale(None, None, scale_factor)
    if test_matrix.is_negative:
        bmesh.ops.reverse_faces(bm, faces = bm.faces[:])

#endregion

#region Real Rail Creators

def rail_creator_wrapper(fct_poly_cret: typing.Callable[[bmesh.types.BMesh], None], extra_transform: mathutils.Matrix) -> bpy.types.Object:
    # create mesh first
    bm: bmesh.types.BMesh = bmesh.new()

    # call cret fct
    fct_poly_cret(bm)

    # finish up
    mesh: bpy.types.Mesh = bpy.data.meshes.new('Rail')
    bm.to_mesh(mesh)
    bm.free()
    
    # setup smooth for mesh
    mesh.shade_smooth()

    # setup default material
    with PROP_bme_material.BMEMaterialsHelper(bpy.context.scene) as bmemtl:
        mesh.materials.clear()
        mesh.materials.append(bmemtl.get_material('Rail'))
        mesh.validate_material_indices()

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
    # add extra transform
    obj.matrix_world = obj.matrix_world @ extra_transform
    # select created object
    UTIL_functions.select_certain_objects((obj, ))
    
    # return rail
    return obj

def create_rail_section(
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

def create_transition_section(
        bm: bmesh.types.BMesh,
        rail_radius: float, rail_span: float) -> None:
    """
    Create the transition section between rail and monorail.
    """
    # create rail section
    create_rail_section(bm, False, rail_radius, rail_span)

    # create monorail
    # calc sink first
    monorail_sink: float
    try:
        monorail_sink = math.sqrt((rail_radius + 2) ** 2 - (rail_span / 2) ** 2) - 2 - rail_radius
    except:
        monorail_sink = -2 # if sqrt(minus number) happended, it mean no triangle relation. the depth should always be -2.
    # create monorail with calculated sink
    create_rail_section(
        bm, True, rail_radius, rail_span,
        mathutils.Matrix.Translation((0, 0, monorail_sink))
    )

def create_straight_rail(
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
    create_rail_section(
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
        bm, 
        start_edges, 
        mathutils.Vector((0, rail_length, 0))
    )

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

def create_transition_rail(
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
    create_transition_section(bm, rail_radius, rail_span)

    # get start edges
    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    # extrude and get end edges
    end_edges: list[bmesh.types.BMEdge] = _bmesh_extrude(
        bm, 
        start_edges, 
        mathutils.Vector((0, rail_length, 0))
    )

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

def create_screw_rail(
        bm: bmesh.types.BMesh, 
        is_monorail: bool, rail_radius: float, rail_span: float,
        rail_start_cap: bool, rail_end_cap: bool,
        rail_screw_angle: float, rail_screw_screw: float, rail_screw_iterations: int,
        rail_screw_steps: int, rail_screw_radius: float,
        rail_screw_flip_x: bool, rail_screw_flip_y: bool, rail_screw_flip_z: bool) -> None:
    """
    Add a screw rail.

    The original point is same as `_add_rail_section()`.
    The start terminal of this straight will be placed in XZ panel.
    The expand direction is +Y.

    If ordered is monorail, `rail_span` param will be ignored.

    Angle is input as degree unit.
    """
    # create section first
    create_rail_section(bm, is_monorail, rail_radius, rail_span)

    start_edges: list[bmesh.types.BMEdge] = bm.edges[:]
    end_edges: list[bmesh.types.BMEdge] = _bmesh_screw(
        bm,
        bm.verts[:], start_edges,
        rail_screw_angle, 
        rail_screw_steps, rail_screw_iterations,
        mathutils.Vector((rail_screw_radius, 0, 0)),
        rail_screw_screw
    )

    # flip geometry
    if rail_screw_flip_x or rail_screw_flip_y or rail_screw_flip_z:
        _bmesh_flip_all_faces(bm, rail_screw_flip_x, rail_screw_flip_y, rail_screw_flip_z)

    # smooth geometry
    _bmesh_smooth_all_edges(bm)

    # cap start and end edges if needed
    if rail_start_cap:
        _bmesh_cap(bm, start_edges)
    if rail_end_cap:
        _bmesh_cap(bm, end_edges)

#endregion
