import bpy, mathutils, bmesh
import typing, enum, collections
from . import UTIL_virtools_types, UTIL_functions

#region Param Struct

class FlattenMethod(enum.IntEnum):
    # The legacy flatten uv mode. Only just do space convertion for each individual faces.
    Raw = enum.auto()
    # The floor specific flatten uv.
    # This method will make sure the continuity in V axis in uv when flatten uv.
    # Only support rectangle faces.
    Floor = enum.auto()
    # The wood specific flatten uv.
    # Similar floor, but it will force all horizontal uv edge parallel with U axis.
    # Not only V axis, but also U axis' continuity will been make sure.
    Wood = enum.auto()

class NeighborType(enum.IntEnum):
    """
    NeighborType is used by special flatten uv to describe the direction of neighbor.

    Normally we find neighbor by +V, +U direction (in UV world), these neighbors are "forward" neighbors and marked as Forward.
    But if we try finding neighbor by -V, -U direction, we call these neighbors are "backward" neighbors,
    and marked as VerticalBackward or HorizontalBackward by its direction.

    The UV of Backward neighbor need to be processed specially so we need distinguish them with Forward neighbors.
    """
    # +V, +U direction neighbor.
    Forward = enum.auto()
    # -V direction neighbor.
    VerticalBackward = enum.auto()
    # -U direction neighbor.
    HorizontalBackward = enum.auto()

class FlattenParam():
    mReferenceEdge: int
    mUseRefPoint: bool
    mFlattenMethod: FlattenMethod

    mScaleSize: float

    mReferencePoint: int
    mReferenceUV: float

    def __init__(self, use_ref_point: bool, reference_edge: int, flatten_method: FlattenMethod) -> None:
        self.mReferenceEdge = reference_edge
        self.mUseRefPoint = use_ref_point
        self.mFlattenMethod = flatten_method

    def is_valid(self) -> bool:
        """Check whether flatten params is valid"""
        if self.mUseRefPoint:
            # ref point should be great than 1.
            # because 0 and 1 is located at the same line with reference edge.
            return self.mReferencePoint > 1
        else:
            # zero scale size make no sense.
            return round(self.mScaleSize, 7) != 0.0

    @classmethod
    def create_by_scale_size(cls, reference_edge: int, flatten_method: FlattenMethod, scale_num: float):
        val = cls(False, reference_edge, flatten_method)
        val.mScaleSize = scale_num
        return val

    @classmethod
    def create_by_ref_point(cls, reference_edge: int, flatten_method: FlattenMethod, ref_point: int, ref_point_uv: float):
        val = cls(True, reference_edge, flatten_method)
        val.mReferencePoint = ref_point
        val.mReferenceUV = ref_point_uv
        return val

#endregion

class BBP_OT_flatten_uv(bpy.types.Operator):
    """Flatten selected face UV. Only works for convex face"""
    bl_idname = "bbp.flatten_uv"
    bl_label = "Flatten UV"
    bl_options = {'REGISTER', 'UNDO'}

    reference_edge: bpy.props.IntProperty(
        name = "Reference Edge",
        description = "The references edge of UV.\nIt will be placed in V axis.",
        min = 0,
        soft_min = 0, soft_max = 3,
        default = 0,
    ) # type: ignore

    flatten_method: bpy.props.EnumProperty(
        name = "Flatten Method",
        items = [
            ('RAW', "Raw", "Legacy flatten UV."),
            ('FLOOR', "Floor", "Floor specific flatten UV."),
            ('WOOD', "Wood", "Wood specific flatten UV."),
        ],
        default = 'RAW'
    ) # type: ignore

    scale_mode: bpy.props.EnumProperty(
        name = "Scale Mode",
        items = [
            ('NUM', "Scale Size", "Scale UV with specific number."),
            ('REF', "Ref. Point", "Scale UV with Reference Point feature."),
        ],
        default = 'NUM'
    ) # type: ignore

    scale_number: bpy.props.FloatProperty(
        name = "Scale Size",
        description = "The size which will be applied for scale.",
        min = 0,
        soft_min = 0, soft_max = 5,
        default = 5.0,
        step = 10,
        precision = 1,
    ) # type: ignore

    reference_point: bpy.props.IntProperty(
        name = "Reference Point",
        description = "The references point of UV.\nIt's U component will be set to the number specified by Reference Point UV.\nThis point index is related to the start point of reference edge.",
        min = 2,  # 0 and 1 is invalid. we can not order the reference edge to be set on the outside of uv axis
        soft_min = 2, soft_max = 3,
        default = 2,
    ) # type: ignore

    reference_uv: bpy.props.FloatProperty(
        name = "Reference Point UV",
        description = "The U component which should be applied to references point in UV.",
        soft_min = 0, soft_max = 1,
        default = 0.5,
        step = 10,
        precision = 2,
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.mode != 'EDIT':
            return False
        return True

    def execute(self, context):
        # construct scale data
        flatten_method_: FlattenMethod
        match(self.flatten_method):
            case 'RAW': flatten_method_ = FlattenMethod.Raw
            case 'FLOOR': flatten_method_ = FlattenMethod.Floor
            case 'WOOD': flatten_method_ = FlattenMethod.Wood
            case _: return {'CANCELLED'}

        flatten_param_: FlattenParam
        if self.scale_mode == 'NUM':
            flatten_param_ = FlattenParam.create_by_scale_size(self.reference_edge, flatten_method_, self.scale_number)
        else:
            flatten_param_ = FlattenParam.create_by_ref_point(self.reference_edge, flatten_method_, self.reference_point, self.reference_uv)
        if not flatten_param_.is_valid():
            return {'CANCELLED'}

        # do flatten uv and report
        failed: int = _flatten_uv_wrapper(bpy.context.active_object.data, flatten_param_)
        if failed != 0:
            print(f'[Flatten UV] {failed} faces are not be processed correctly because process failed.')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.emboss = 'NORMAL'
        layout.label(text = "Flatten Method")
        sublayout = layout.row()
        sublayout.prop(self, "flatten_method", expand = True)
        layout.prop(self, "reference_edge")

        layout.separator()
        layout.label(text = "Scale Mode")
        sublayout = layout.row()
        sublayout.prop(self, "scale_mode", expand = True)

        layout.separator()
        layout.label(text = "Scale Config")
        if self.scale_mode == 'NUM':
            layout.prop(self, "scale_number")
        else:
            layout.prop(self, "reference_point")
            layout.prop(self, "reference_uv")

#region BMesh Visitor Helper

def _set_face_vertex_uv(face: bmesh.types.BMFace, uv_layer: bmesh.types.BMLayerItem, idx: int, uv: UTIL_virtools_types.ConstVxVector2) -> None:
    """
    Help function to set UV data for face.

    @param face[in] The face to be set.
    @param uv_layer[in] The corresponding uv layer. Hint: it was gotten from BMesh.loops.layers.uv.verify()
    @param idx[in] The index of trying setting vertex.
    @param uv[in] The set UV data
    """
    face.loops[idx][uv_layer].uv = uv

def _get_face_vertex_uv(face: bmesh.types.BMFace, uv_layer: bmesh.types.BMLayerItem, idx: int) -> UTIL_virtools_types.ConstVxVector2:
    """
    Help function to get UV data for face.

    @param face[in] The face to be set.
    @param uv_layer[in] The corresponding uv layer. Hint: it was gotten from BMesh.loops.layers.uv.verify()
    @param idx[in] The index of trying setting vertex.
    @return The UV data
    """
    v: mathutils.Vector = face.loops[idx][uv_layer].uv
    return (v[0], v[1])

def _get_face_vertex_pos(face: bmesh.types.BMFace, idx: int) -> UTIL_virtools_types.ConstVxVector3:
    """
    Help function to get vertex position from face by provided index.
    No index overflow checker. Caller must make sure the provided index is not overflow.

    @param face[in] Bmesh face struct.
    @param idx[in] The index of trying getting vertex.
    @return The gotten vertex position.
    """
    v: mathutils.Vector = face.loops[idx].vert.co
    return (v[0], v[1], v[2])

def _circular_clamp_index(v: int, vmax: int) -> int:
    """
    Circular clamp face vertex index.
    Used by _real_flatten_uv.

    @param v[in] The index to clamp
    @param vmax[in] The count of used face vertex. At least 3.
    @return The circular clamped value ranging from 0 to vmax.
    """
    return v % vmax

#endregion

#region Real Worker Functions

def _flatten_uv_wrapper(mesh: bpy.types.Mesh, flatten_param: FlattenParam) -> int:
    # create bmesh modifier
    bm: bmesh.types.BMesh = bmesh.from_edit_mesh(mesh)
    # use verify() to make sure there is a uv layer to write data
    # verify() will return existing one or create one if no layer existing.
    uv_layers: bmesh.types.BMLayerCollection = bm.loops.layers.uv
    uv_layer: bmesh.types.BMLayerItem = uv_layers.verify()

    # invoke core
    failed: int
    match(flatten_param.mFlattenMethod):
        case FlattenMethod.Raw:
            failed = _raw_flatten_uv(bm, uv_layer, flatten_param)
        case FlattenMethod.Floor | FlattenMethod.Wood:
            failed = _specific_flatten_uv(bm, uv_layer, flatten_param)

    # show the updates in the viewport
    bmesh.update_edit_mesh(mesh)
    # return process result
    return failed

def _raw_flatten_uv(bm: bmesh.types.BMesh, uv_layer: bmesh.types.BMLayerItem, flatten_param: FlattenParam) -> int:
    # failed counter
    failed: int = 0
    # raw flatten uv always use zero offset
    c_ZeroOffset: mathutils.Vector = mathutils.Vector((0, 0))

    # process each face
    face: bmesh.types.BMFace
    for face in bm.faces:
        # check requirement
        # skip not selected face
        if not face.select: continue
        # skip the face that not fufill reference edge requirement
        edge_count: int = len(face.loops)
        if flatten_param.mReferenceEdge >= edge_count:
            failed += 1
            continue
        # skip ref point overflow when using ref point mode
        if flatten_param.mUseRefPoint and (flatten_param.mReferencePoint >= edge_count):
            failed += 1
            continue

        # process this face
        _flatten_face_uv(face, uv_layer, flatten_param, c_ZeroOffset)

    return failed

def _specific_flatten_uv(bm: bmesh.types.BMesh, uv_layer: bmesh.types.BMLayerItem, flatten_param: FlattenParam) -> int:
    # failed counter
    failed: int = 0

    # reset selected face's tag to False to indicate these face is not processed
    face: bmesh.types.BMFace
    for face in bm.faces:
        if face.select:
            face.tag = False
    
    # prepare a function to check whether face is valid
    def face_validator(f: bmesh.types.BMFace) -> bool:
        # specify using external failed counter
        nonlocal failed
        # a valid face must be
        # selected, not processed, and should be rectangle
        # we check selection first
        # then check tag. if tag == True, it mean this face has been processed.
        if not f.select or f.tag: return False
        # now this face can be processed, we need check whether it is rectangle
        if len(f.loops) == 4:
            # yes it is rectangle
            return True
        else:
            # no, it is not rectangle
            # we need mark its tag as True to prevent any possible recursive checking
            # because it definately can not be processed in future.
            f.tag = True
            # then we report this face failed
            failed = failed + 1
            # return false
            return False
    # prepare face getter which will be used when stack is empty
    face_getter: typing.Iterator[bmesh.types.BMFace] = filter(
        lambda f: face_validator(f), 
        typing.cast(typing.Iterable[bmesh.types.BMFace], bm.faces)
    )
    # prepare a neighbor getter.
    # this function will help finding the valid neighbor of specified face
    # `loop_idx` is the index of loop getting from given face.
    # `exp_loop_idx` is the expected index of neighbor loop in neighbor face.
    def face_neighbor_getter(f: bmesh.types.BMFace, loop_idx: int, exp_loop_idx: int) -> bmesh.types.BMFace | None:
        # get this face's loop
        this_loop: bmesh.types.BMLoop = f.loops[loop_idx]
        # check requirement for this loop
        # this edge should be shared exactly by 2 faces.
        # 
        # Manifold: For a mesh to be manifold, every edge must have exactly two adjacent faces.
        # Ref: https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Manifold-Meshes
        if not this_loop.edge.is_manifold:
            return None

        # get neighbor loop
        neighbor_loop: bmesh.types.BMLoop = this_loop.link_loop_radial_next
        # get neighbor face and check it
        neighbor_f: bmesh.types.BMFace = neighbor_loop.face
        if not face_validator(neighbor_f):
            return None

        # check expected neighbor index
        if neighbor_loop != neighbor_f.loops[exp_loop_idx]:
            return None

        # all check done, return face
        return neighbor_f
    # prepare face stack.
    # NOTE: all face inserted into this stack should be marked as processed first.
    face_stack: collections.deque[tuple[bmesh.types.BMFace, mathutils.Vector, NeighborType]] = collections.deque()
    # start process faces
    while True:
        # if no item in face stack, pick one from face getter and mark it as processed
        # if face getter failed, it mean that no more face, exit.
        if len(face_stack) == 0:
            try:
                f = next(face_getter)
                f.tag = True
                face_stack.append((f, mathutils.Vector((0, 0)), NeighborType.Forward))
            except StopIteration:
                break

        # pick one face from stack and process it
        (face, face_offset, face_backward) = face_stack.pop()
        _flatten_face_uv(face, uv_layer, flatten_param, face_offset)

        # get 4 point uv because we need use them later
        # NOTE: 4 uv point following this order
        #  +-----------+
        #  |(1)        |(2)
        #  |           |
        #  |(0)        |(3)
        #  +-----------+
        # So the loop index is
        #        (1)
        #  +---------->+
        #  ^           |
        #  |(0)        |(2)
        #  |           v
        #  +<----------+
        #        (3)
        ind0 = _circular_clamp_index(flatten_param.mReferenceEdge, 4)
        ind1 = _circular_clamp_index(flatten_param.mReferenceEdge + 1, 4)
        ind2 = _circular_clamp_index(flatten_param.mReferenceEdge + 2, 4)
        ind3 = _circular_clamp_index(flatten_param.mReferenceEdge + 3, 4)
        uv0 = _get_face_vertex_uv(face, uv_layer, ind0)
        uv1 = _get_face_vertex_uv(face, uv_layer, ind1)
        uv2 = _get_face_vertex_uv(face, uv_layer, ind2)
        uv3 = _get_face_vertex_uv(face, uv_layer, ind3)

        # correct rectangle shape when in wood mode
        if flatten_param.mFlattenMethod == FlattenMethod.Wood:
            # make its uv geometry to rectangle from a trapezium.
            # get the average U factor from its right edge.
            # and make top + bottom uv edge be parallel with U axis by using left edge V factor.
            average_u = (uv2[0] + uv3[0]) / 2
            uv2 = (average_u, uv1[1])
            uv3 = (average_u, uv0[1])
            _set_face_vertex_uv(face, uv_layer, ind2, uv2)
            _set_face_vertex_uv(face, uv_layer, ind3, uv3)
        
        # do backward correction
        # in backward mode, we can not know how many space backward one will occupied,
        # thus we can not pass it by offset because we don't know the offset,
        # so we only can patch it after computing its real size.
        if face_backward != NeighborType.Forward:
            if face_backward == NeighborType.VerticalBackward:
                # in vertical backward patch,
                # minus self height for all uv.
                self_height: float = uv1[1] - uv0[1]
                uv0 = (uv0[0], uv0[1] - self_height)
                uv1 = (uv1[0], uv1[1] - self_height)
                uv2 = (uv2[0], uv2[1] - self_height)
                uv3 = (uv3[0], uv3[1] - self_height)
            if face_backward == NeighborType.HorizontalBackward:
                # in horizontal backward patch, minus self width for all uv.
                # because we have process rectangle shape issue before this,
                # so we can pick uv2 or uv3 to get width directly.
                self_width: float = uv3[0] - uv0[0]
                uv0 = (uv0[0] - self_width, uv0[1])
                uv1 = (uv1[0] - self_width, uv1[1])
                uv2 = (uv2[0] - self_width, uv2[1])
                uv3 = (uv3[0] - self_width, uv3[1])
            # set modified uv to geometry
            _set_face_vertex_uv(face, uv_layer, ind0, uv0)
            _set_face_vertex_uv(face, uv_layer, ind1, uv1)
            _set_face_vertex_uv(face, uv_layer, ind2, uv2)
            _set_face_vertex_uv(face, uv_layer, ind3, uv3)
            
        # insert horizontal neighbor only in wood mode.
        if flatten_param.mFlattenMethod == FlattenMethod.Wood:
            # insert right neighbor (forward)
            r_face: bmesh.types.BMFace | None = face_neighbor_getter(face, ind2, ind0)
            if r_face is not None:
                # mark it as processed
                r_face.tag = True
                # insert face with extra horizontal offset.
                face_stack.append((r_face, mathutils.Vector((uv3[0], uv3[1])), NeighborType.Forward))
            # insert left neighbor (backward)
            # swap the index param of neighbor getter
            l_face: bmesh.types.BMFace | None = face_neighbor_getter(face, ind0, ind2)
            if l_face is not None:
                l_face.tag = True
                # pass origin pos, and order backward correction
                face_stack.append((l_face, mathutils.Vector((uv0[0], uv0[1])), NeighborType.HorizontalBackward))

        # insert vertical neighbor
        # insert top neighbor (forward)
        t_face: bmesh.types.BMFace | None = face_neighbor_getter(face, ind1, ind3)
        if t_face is not None:
            # mark it as processed
            t_face.tag = True
            # insert face with extra vertical offset.
            face_stack.append((t_face, mathutils.Vector((uv1[0], uv1[1])), NeighborType.Forward))
        # insert bottom neighbor (backward)
        # swap the index param of neighbor getter
        b_face: bmesh.types.BMFace | None = face_neighbor_getter(face, ind3, ind1)
        if b_face is not None:
            b_face.tag = True
            # pass origin pos, and order backward correction
            face_stack.append((b_face, mathutils.Vector((uv0[0], uv0[1])), NeighborType.VerticalBackward))

    return failed

def _flatten_face_uv(face: bmesh.types.BMFace, uv_layer: bmesh.types.BMLayerItem, flatten_param: FlattenParam, offset: mathutils.Vector) -> None:
    # ========== get correct new corrdinate system ==========
    # yyc mark:
    # we use 3 points located in this face to calc
    # the base of this local uv corredinate system.
    # however if this 3 points are set in a line,
    # this method will cause a error, zero vector error.
    #
    # if z axis is zero vector, we will try using face normal instead
    # to try getting correct data.
    #
    # zero base is not important. because it will not raise any math exception
    # just a weird uv. user will notice this problem.

    # get point
    all_point: int = len(face.loops)
    pidx_start: int = _circular_clamp_index(flatten_param.mReferenceEdge, all_point)
    p1: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, pidx_start))
    p2: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, _circular_clamp_index(flatten_param.mReferenceEdge + 1, all_point)))
    p3: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, _circular_clamp_index(flatten_param.mReferenceEdge + 2, all_point)))

    # get y axis
    new_y_axis: mathutils.Vector = p2 - p1
    new_y_axis.normalize()
    vec1: mathutils.Vector = p3 - p2
    vec1.normalize()

    # get z axis
    new_z_axis: mathutils.Vector = vec1.cross(new_y_axis)
    new_z_axis.normalize()
    # if z is a zero vector, use face normal instead
    # please note we need use inverted face normal.
    if not any(round(v, 7) for v in new_z_axis):
        new_z_axis = typing.cast(mathutils.Vector, face.normal).normalized()
        new_z_axis.negate()

    # get x axis
    new_x_axis: mathutils.Vector = new_y_axis.cross(new_z_axis)
    new_x_axis.normalize()

    # construct rebase matrix
    origin_base: mathutils.Matrix = mathutils.Matrix((
        (1.0, 0, 0), 
        (0, 1.0, 0), 
        (0, 0, 1.0)
    ))
    origin_base.invert_safe()
    new_base: mathutils.Matrix = mathutils.Matrix((
        (new_x_axis.x, new_y_axis.x,  new_z_axis.x), 
        (new_x_axis.y, new_y_axis.y, new_z_axis.y),
        (new_x_axis.z, new_y_axis.z, new_z_axis.z)
    ))
    transition_matrix: mathutils.Matrix = typing.cast(mathutils.Matrix, origin_base @ new_base)
    transition_matrix.invert_safe()

    # ===== rescale correction =====
    rescale: float = 0.0
    if flatten_param.mUseRefPoint:
        # ref point method
        # get reference point from loop
        pidx_refp: int = _circular_clamp_index(pidx_start + flatten_param.mReferencePoint, all_point)
        pref: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, pidx_refp)) - p1

        # calc its U component
        vec_u: float = abs(typing.cast(mathutils.Vector, transition_matrix @ pref).x)
        if round(vec_u, 7) == 0.0:
            rescale = 1.0  # fallback. rescale = 1 will not affect anything
        else:
            rescale = flatten_param.mReferenceUV / vec_u
    else:
        # scale size method
        # apply rescale directly
        rescale = 1.0 / flatten_param.mScaleSize

    # construct matrix
    # we only rescale U component (X component)
    # and constant 5.0 scale for V component (Y component)
    scale_matrix: mathutils.Matrix = mathutils.Matrix((
        (rescale, 0, 0), 
        (0, 1.0 / 5.0, 0), 
        (0, 0, 1.0)
    ))
    # order can not be changed. we order do transition first, then scale it.
    rescale_transition_matrix: mathutils.Matrix = typing.cast(mathutils.Matrix, scale_matrix @ transition_matrix)

    # ========== process each face ==========
    for idx in range(all_point):
        # compute uv
        pp: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, idx)) - p1
        ppuv: mathutils.Vector = typing.cast(mathutils.Vector, rescale_transition_matrix @ pp)
        # u and v component has been calculated properly. no extra process needed.
        # just get abs for the u component
        ppuv.x = abs(ppuv.x)
        # add offset and assign to uv
        _set_face_vertex_uv(face, uv_layer, idx, (ppuv.x + offset.x, ppuv.y + offset.y))

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_flatten_uv)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_flatten_uv)
