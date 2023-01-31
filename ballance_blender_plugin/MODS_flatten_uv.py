import bpy,mathutils
import bmesh
import math
from . import UTILS_functions

class BALLANCE_OT_flatten_uv(bpy.types.Operator):
    """Flatten selected face UV. Only works for convex face"""
    bl_idname = "ballance.flatten_uv"
    bl_label = "Flatten UV"
    bl_options = {'REGISTER', 'UNDO'}

    normal_scale_correction = 5.0
    sink_scale_correction = 5.0 * (math.sqrt(2.5 ** 2 + 0.7 ** 2) / 2.5)

    scale_correction: bpy.props.EnumProperty(
        name="Scale Correction",
        description="Choose your UV scale.",
        items=(
            ("NORMAL", "Normal Floor", "Normal floor scale, 5.0"),
            ("SINK", "Sink Floor", "Sink floor scale, around 5.19")
        ),
        default='NORMAL',
    )

    reference_edge : bpy.props.IntProperty(
        name="Reference edge",
        description="The references edge of UV. It will be placed in V axis.",
        min=0,
        soft_min=0,
        soft_max=3,
        default=0,
    )

    @classmethod
    def poll(self, context):
        obj = bpy.context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.mode != 'EDIT':
            return False
        return True

    def get_scale_correction(self):
        if self.scale_correction == 'NORMAL':
            return BALLANCE_OT_flatten_uv.normal_scale_correction
        elif self.scale_correction == 'SINK':
            return BALLANCE_OT_flatten_uv.sink_scale_correction
        else:
            raise Exception("Unknow scale correction.")

    def execute(self, context):
        no_processed_count = _real_flatten_uv(bpy.context.active_object.data, self.reference_edge, self.get_scale_correction())
        if no_processed_count != 0:
            print("[Flatten UV] {} faces may not be processed correctly because they have problem.".format(no_processed_count))
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scale_correction")
        layout.prop(self, "reference_edge")

def _real_flatten_uv(mesh, reference_edge, scale_correction):
    no_processed_count = 0

    if mesh.uv_layers.active is None:
        # if no uv, create it
        mesh.uv_layers.new(do_init=False)

    bm = bmesh.from_edit_mesh(mesh)
    uv_lay = bm.loops.layers.uv.active
    for face in bm.faces:
        if not face.select:
            continue

        # check whether ref edge is legal
        allPoint = len(face.loops)
        if allPoint <= reference_edge:
            no_processed_count+=1
            continue

        # get correct new corrdinate system
        # yyc mark:
        # we use 3 points located in this face to calc 
        # the base of this local uv corredinate system.
        # however if this 3 points are set in a line, 
        # this method will cause a error, zero vector error. 
        # 
        # if z axis is zero vector, we will try using face normal instead 
        # to try getting correct data.
        # 
        # zero base is not important. because it will not raise any math exceptio
        # just a weird uv. user will notice this problem.

        # get point
        p1Relative = reference_edge
        p2Relative = reference_edge + 1
        p3Relative = reference_edge + 2
        if p2Relative >= allPoint:
            p2Relative -= allPoint
        if p3Relative >= allPoint:
            p3Relative -= allPoint

        p1=mathutils.Vector(tuple(face.loops[p1Relative].vert.co[x] for x in range(3)))
        p2=mathutils.Vector(tuple(face.loops[p2Relative].vert.co[x] for x in range(3)))
        p3=mathutils.Vector(tuple(face.loops[p3Relative].vert.co[x] for x in range(3)))

        # get y axis
        new_y_axis = p2 - p1
        new_y_axis.normalize()
        vec1 = p3 - p2
        vec1.normalize()

        # get z axis
        new_z_axis = new_y_axis.cross(vec1)
        new_z_axis.normalize()
        if not any(round(v, 7) for v in new_z_axis):
            new_z_axis = face.normal.normalized()

        # get x axis
        new_x_axis = new_y_axis.cross(new_z_axis)
        new_x_axis.normalize()

        # construct rebase matrix
        origin_base = mathutils.Matrix((
            (1.0, 0, 0),
            (0, 1.0, 0),
            (0, 0, 1.0)
        ))
        origin_base.invert_safe()
        new_base = mathutils.Matrix((
            (new_x_axis.x, new_y_axis.x, new_z_axis.x),
            (new_x_axis.y, new_y_axis.y, new_z_axis.y),
            (new_x_axis.z, new_y_axis.z, new_z_axis.z)
        ))
        transition_matrix = origin_base @ new_base
        transition_matrix.invert_safe()

        # process each face
        for loop_index in range(allPoint):
            pp = mathutils.Vector(tuple(face.loops[loop_index].vert.co[x] for x in range(3)))
            vec = pp-p1
            new_vec = transition_matrix @ vec

            # y axis always use 5.0 to scale
            # however, x need use custom scale correction.
            face.loops[loop_index][uv_lay].uv = (
                (new_vec.x if new_vec.x >=0 else -new_vec.x) / scale_correction,
                (new_vec.y) / 5.0
            )

    # Show the updates in the viewport
    bmesh.update_edit_mesh(mesh)

    return no_processed_count

