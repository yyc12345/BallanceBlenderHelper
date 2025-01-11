import bpy, bmesh, mathutils
import typing
from . import PROP_ptrprop_resolver
from . import UTIL_virtools_types, UTIL_icons_manager, UTIL_functions

class BBP_OT_rail_uv(bpy.types.Operator):
    """Create UV for Rail as Ballance Showen (TT_ReflectionMapping)"""
    bl_idname = "bbp.rail_uv"
    bl_label = "Rail UV"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_rail_uv'

    @classmethod
    def poll(cls, context):
        return _check_rail_target(context)

    def invoke(self, context, event):
        wm: bpy.types.WindowManager = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        # check material
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        mtl: bpy.types.Material = ptrprops.get_rail_uv_material()
        if mtl is None:
            self.report({'ERROR'}, "Specified material is empty.")
            return {'CANCELLED'}
        
        # apply rail uv
        (has_invalid_objs, meshes) = _get_rail_target(context)
        _create_rail_uv(meshes, mtl)

        # show warning if there is invalid objects
        if has_invalid_objs:
            self.report({'WARNING'}, 'Some objects are invalid for this operation. See Console for more details.')

        return {'FINISHED'}

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        ptrprops.draw_rail_uv_material(layout)

#region Real Worker Functions

def _check_rail_target(context: bpy.types.Context) -> bool:
    for obj in context.selected_objects:
        if obj.type != 'MESH':
            continue
        if obj.mode != 'OBJECT':
            continue
        if obj.data is None:
            continue
        return True
    return False

def _get_rail_target(context: bpy.types.Context) -> tuple[bool, typing.Iterable[bpy.types.Mesh]]:
    # collect objects
    meshes: list[bpy.types.Mesh] = []
    error_objname: list[str] = []
    for obj in context.selected_objects:
        if obj.type != 'MESH':
            error_objname.append(obj.name)
            continue
        if obj.mode != 'OBJECT':
            error_objname.append(obj.name)
            continue
        if obj.data is None:
            error_objname.append(obj.name)
            continue
        
        meshes.append(typing.cast(bpy.types.Mesh, obj.data))
    
    # display warning window if necessary
    has_invalid_objs = len(error_objname) != 0
    if has_invalid_objs:
        # output to console
        print('')
        print('========== Rail UV Report ==========')
        print('Following objects are not processed by Rail UV because they do not meet the requirements of Rail UV.')
        for objname in error_objname:
            print(objname)
        print('')

    # return valid
    return (has_invalid_objs, meshes)

def _tt_reflection_mapping_compute(
        point_: UTIL_virtools_types.ConstVxVector3, 
        nml_: UTIL_virtools_types.ConstVxVector3, 
        refobj_: UTIL_virtools_types.ConstVxVector3) -> UTIL_virtools_types.ConstVxVector2:
    # switch blender coord to virtools coord for convenient calc
    point: mathutils.Vector = mathutils.Vector((point_[0], point_[2], point_[1]))
    nml: mathutils.Vector = mathutils.Vector((nml_[0], nml_[2], nml_[1])).normalized()
    refobj: mathutils.Vector = mathutils.Vector((refobj_[0], refobj_[2], refobj_[1]))

    p: mathutils.Vector = (refobj - point).normalized()
    b: mathutils.Vector = (((2 * (p * nml)) * nml) - p)
    b.normalize()
    
    # convert back to blender coord
    return ((b.x + 1.0) / 2.0, -(b.z + 1.0) / 2.0)


def _set_face_vertex_uv(face: bpy.types.MeshPolygon, uv_layer: bpy.types.MeshUVLoopLayer, idx: int, uv: UTIL_virtools_types.ConstVxVector2) -> None:
    """
    Help function to set face vertex uv by index.

    @param face[in] The face to be set.
    @param uv_layer[in] The uv layer to be set gotten from `Mesh.uv_layers.active`
    @param idx[in] The index related to face to set uv.
    @param uv[in] The uv data.
    """
    uv_layer.uv[face.loop_start + idx].vector = uv

def _get_face_vertex_pos(face: bpy.types.MeshPolygon, loops: bpy.types.MeshLoops, vecs: bpy.types.MeshVertices, idx: int) -> UTIL_virtools_types.ConstVxVector3:
    """
    Help function. Get face referenced vertex position data by index

    @param face[in] The face to be set.
    @param loops[in] Mesh loops gotten from `Mesh.loops`
    @param vecs[in] Mesh vertices gotten from `Mesh.vertices`
    @param idx[in] The index related to face to get position.
    """
    v: mathutils.Vector = vecs[loops[face.loop_start + idx].vertex_index].co
    return (v[0], v[1], v[2])

def _get_face_vertex_nml(face: bpy.types.MeshPolygon, loops: bpy.types.MeshLoops, idx: int) -> UTIL_virtools_types.ConstVxVector3:
    """
    Help function to get face vertex normal.

    Similar to _get_face_vertex_pos, just get normal, not position.

    @param face[in] The face to be set.
    @param loops[in] Mesh loops gotten from `Mesh.loops`
    @param idx[in] The index related to face to get normal.
    """
    v: mathutils.Vector = loops[face.loop_start + idx].normal
    return (v[0], v[1], v[2])

def _get_face_vertex_count(face: bpy.types.MeshPolygon) -> int:
    """
    Help function to get how many vertex used by this face.

    @return The count of used vertex. At least 3.
    """
    return face.loop_total

def _create_rail_uv(meshes: typing.Iterable[bpy.types.Mesh], mtl: bpy.types.Material):
    for mesh in meshes:
        # clean it material and set rail first
        mesh.materials.clear()
        mesh.materials.append(mtl)
        # and validate face mtl idx ref
        mesh.validate_material_indices()
        
        # get uv and make sure at least one uv
        if mesh.uv_layers.active is None:
            mesh.uv_layers.new(do_init = False)
        uv_layer: bpy.types.MeshUVLoopLayer = mesh.uv_layers.active
        # get other useful data
        loops: bpy.types.MeshLoops = mesh.loops
        vecs: bpy.types.MeshVertices = mesh.vertices

        refobj: UTIL_virtools_types.ConstVxVector3 = (0.0, 0.0, 0.0)
        for face in mesh.polygons:
            for idx in range(_get_face_vertex_count(face)):
                _set_face_vertex_uv(
                    face,
                    uv_layer,
                    idx,
                    _tt_reflection_mapping_compute(
                        _get_face_vertex_pos(face, loops, vecs, idx),
                        _get_face_vertex_nml(face, loops, idx),
                        refobj
                    )
                )

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_rail_uv)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_rail_uv)

