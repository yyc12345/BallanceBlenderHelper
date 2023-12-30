import bpy, mathutils, bmesh
from . import UTIL_virtools_types

#region Param Struct

class _FlattenParamBySize():
    mScaleSize: float

    def __init__(self, scale_size: float) -> None:
        self.mScaleSize = scale_size

class _FlattenParamByRefPoint():
    mReferencePoint: int
    mReferenceUV: float

    def __init__(self, ref_point: int, ref_point_uv: float) -> None:
        self.mReferencePoint = ref_point
        self.mReferenceUV = ref_point_uv

class _FlattenParam():
    mUseRefPoint: bool
    mParamData: _FlattenParamBySize | _FlattenParamByRefPoint

    def __init__(self, use_ref_point: bool, data: _FlattenParamBySize | _FlattenParamByRefPoint) -> None:
        self.mUseRefPoint = use_ref_point
        self.mParamData = data

    @classmethod
    def CreateByScaleSize(cls, scale_num: float):
        return cls(False, _FlattenParamBySize(scale_num))

    @classmethod
    def CreateByRefPoint(cls, ref_point: int, ref_point_uv: float):
        return cls(True, _FlattenParamByRefPoint(ref_point, ref_point_uv))

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
        soft_min = 0,
        soft_max = 3,
        default = 0,
    )

    scale_mode: bpy.props.EnumProperty(
        name = "Scale Mode",
        items = (
            ('NUM', "Scale Size", "Scale UV with specific number."),
            ('REF', "Ref. Point", "Scale UV with Reference Point feature."),
        ),
    )

    scale_number: bpy.props.FloatProperty(
        name = "Scale Size",
        description = "The size which will be applied for scale.",
        min = 0,
        soft_min = 0,
        soft_max = 5,
        default = 5.0,
        step = 0.1,
        precision = 1,
    )

    reference_point: bpy.props.IntProperty(
        name = "Reference Point",
        description = "The references point of UV.\nIt's U component will be set to the number specified by Reference Point UV.\nThis point index is related to the start point of reference edge.",
        min = 2,  # 0 and 1 is invalid. we can not order the reference edge to be set on the outside of uv axis
        soft_min = 2,
        soft_max = 3,
        default = 2,
    )

    reference_uv: bpy.props.FloatProperty(
        name = "Reference Point UV",
        description = "The U component which should be applied to references point in UV.",
        soft_min = 0,
        soft_max = 1,
        default = 0.5,
        step = 0.1,
        precision = 2,
    )

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
        if self.scale_mode == 'NUM':
            scale_data: _FlattenParam = _FlattenParam.CreateByScaleSize(self.scale_number)
        else:
            scale_data: _FlattenParam = _FlattenParam.CreateByRefPoint(self.reference_point, self.reference_uv)

        # do flatten uv and report
        # sync data first
        # ref: https://blender.stackexchange.com/questions/218086/data-vertices-returns-an-empty-collection-in-edit-mode
        this_obj: bpy.types.Object = bpy.context.active_object
        this_obj.update_from_editmode()
        no_processed_count = _real_flatten_uv(
            this_obj.data, 
            self.reference_edge, 
            scale_data
        )
        if no_processed_count != 0:
            print("[Flatten UV] {} faces are not be processed correctly because process failed."
                .format(no_processed_count))
            
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.emboss = 'NORMAL'
        layout.prop(self, "reference_edge")

        layout.separator()
        layout.label(text = "Scale Mode")
        layout.prop(self, "scale_mode", expand = True)

        layout.separator()
        layout.label(text = "Scale Config")
        if self.scale_mode == 'NUM':
            layout.prop(self, "scale_number")
        else:
            layout.prop(self, "reference_point")
            layout.prop(self, "reference_uv")

#region Real Worker Functions

def _set_face_vertex_uv(face: bmesh.types.BMFace, uv_layer: bmesh.types.BMLayerItem, idx: int, uv: UTIL_virtools_types.ConstVxVector2) -> None:
    """
    Help function to set UV data for face.

    @param face[in] The face to be set.
    @param uv_layer[in] The corresponding uv layer. Hint: it was gotten from BMesh.loops.layers.uv.verify()
    @param idx[in] The index of trying setting vertex.
    @param uv[in] The set UV data
    """
    face.loops[idx][uv_layer].uv = uv

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

def _real_flatten_uv(mesh: bpy.types.Mesh, reference_edge: int, scale_data: _FlattenParam) -> int:
    no_processed_count: int = 0

    # create bmesh modifier
    bm: bmesh.types.BMesh = bmesh.from_edit_mesh(mesh)
    # use verify() to make sure there is a uv layer to write data
    # verify() will return existing one or create one if no layer existing.
    uv_layers: bmesh.types.BMLayerCollection = bm.loops.layers.uv
    uv_layer: bmesh.types.BMLayerItem = uv_layers.verify()

    # process each face
    face: bmesh.types.BMFace
    for face in bm.faces:
        # ===== check requirement =====
        # check whether face selected
        # only process selected face
        if not face.select:
            continue

        # ===== resolve reference edge and point =====
        # check reference validation
        all_point: int = len(face.loops)
        if reference_edge >= all_point: # reference edge overflow
            no_processed_count += 1
            continue

        # check scale validation
        if scale_data.mUseRefPoint:
            if ((scale_data.mParamData.mReferencePoint <= 1)  # reference point too low
                or (scale_data.mParamData.mReferencePoint >= all_point)):  # reference point overflow
                no_processed_count += 1
                continue
        else:
            if round(scale_data.mParamData.mScaleSize, 7) == 0.0:  # invalid scale size
                no_processed_count += 1
                continue

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
        pidx_start: int = _circular_clamp_index(reference_edge, all_point)
        p1: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, pidx_start))
        p2: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, _circular_clamp_index(reference_edge + 1, all_point)))
        p3: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, _circular_clamp_index(reference_edge + 2, all_point)))

        # get y axis
        new_y_axis: mathutils.Vector = p2 - p1
        new_y_axis.normalize()
        vec1: mathutils.Vector = p3 - p2
        vec1.normalize()

        # get z axis
        new_z_axis: mathutils.Vector = new_y_axis.cross(vec1)
        new_z_axis.normalize()
        if not any(round(v, 7) for v in new_z_axis):  # if z is a zero vector, use face normal instead
            new_z_axis = face.normal.normalized()

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
        transition_matrix: mathutils.Matrix = origin_base @ new_base
        transition_matrix.invert_safe()

        # ===== rescale correction =====
        rescale: float = 0.0
        if scale_data.mUseRefPoint:
            # ref point method
            # get reference point from loop
            pidx_refp: int = _circular_clamp_index(pidx_start + scale_data.mParamData.mReferencePoint, all_point)
            pref: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, pidx_refp)) - p1

            # calc its U component
            vec_u: float = abs((transition_matrix @ pref).x)
            if round(vec_u, 7) == 0.0:
                rescale = 1.0  # fallback. rescale = 1 will not affect anything
            else:
                rescale = scale_data.mParamData.mReferenceUV / vec_u
        else:
            # scale size method
            # apply rescale directly
            rescale = 1.0 / scale_data.mParamData.mScaleSize

        # construct matrix
        # we only rescale U component (X component)
        # and constant 5.0 scale for V component (Y component)
        scale_matrix: mathutils.Matrix = mathutils.Matrix((
            (rescale, 0, 0), 
            (0, 1.0 / 5.0, 0), 
            (0, 0, 1.0)
        ))
        # order can not be changed. we order do transition first, then scale it.
        rescale_transition_matrix: mathutils.Matrix = scale_matrix @ transition_matrix

        # ========== process each face ==========
        for idx in range(all_point):
            pp: mathutils.Vector = mathutils.Vector(_get_face_vertex_pos(face, idx)) - p1
            ppuv: mathutils.Vector = rescale_transition_matrix @ pp

            # u and v component has been calculated properly. no extra process needed.
            # just get abs for the u component
            _set_face_vertex_uv(face, uv_layer, idx, (abs(ppuv.x), ppuv.y))

    # show the updates in the viewport
    bmesh.update_edit_mesh(mesh)
    # return process result
    return no_processed_count

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_flatten_uv)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_flatten_uv)
