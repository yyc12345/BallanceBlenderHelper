import bpy,mathutils
import bmesh
from . import utils

class BALLANCE_OT_flatten_uv(bpy.types.Operator):
    """Flatten selected face UV. Only works for convex face"""
    bl_idname = "ballance.flatten_uv"
    bl_label = "Flatten UV"
    bl_options = {'UNDO'}

    reference_edge : bpy.props.IntProperty(
        name="Reference_edge",
        description="The references edge of UV. It will be placed in V axis.",
        min=0,
        soft_min=0,
        soft_max=3,
        default=0,
    )

    @classmethod
    def poll(self, context):
        obj = bpy.context.active_object
        if obj == None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.mode != 'EDIT':
            return False
        return True

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        no_processed_count = real_flatten_uv(bpy.context.active_object.data, self.reference_edge)
        if no_processed_count != 0:
            utils.ShowMessageBox(("{} faces may not be processed correctly because they have problem.".format(no_processed_count), ), "Warning", 'ERROR')
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "reference_edge")

def real_flatten_uv(mesh, reference_edge):
    no_processed_count = 0

    if mesh.uv_layers.active is None:
        # if no uv, create it
        mesh.uv_layers.new(do_init=True)
    uv_layer = mesh.uv_layers.active

    selectedFace = []
    bm = bmesh.from_edit_mesh(mesh)
    for face, index in ((face, index) for index, face in enumerate(bm.faces)):
        if face.select:
            selectedFace.append(index)
    
    vecList=mesh.vertices[:]
    for ind in selectedFace:
        face = mesh.polygons[ind]
        allPoint = face.loop_total

        if allPoint <= reference_edge:
            no_processed_count+=1
            continue

        # get correct new corrdinate system
        p1Relative = reference_edge
        p2Relative = reference_edge + 1
        p3Relative = reference_edge + 2
        if p2Relative >= allPoint:
            p2Relative -= allPoint
        if p3Relative >= allPoint:
            p3Relative -= allPoint

        p1=mathutils.Vector(tuple(vecList[mesh.loops[face.loop_start + p1Relative].vertex_index].co[x] for x in range(3)))
        p2=mathutils.Vector(tuple(vecList[mesh.loops[face.loop_start + p2Relative].vertex_index].co[x] for x in range(3)))
        p3=mathutils.Vector(tuple(vecList[mesh.loops[face.loop_start + p3Relative].vertex_index].co[x] for x in range(3)))

        new_y_axis = p2 - p1
        new_y_axis.normalize()
        vec1 = p3 - p2
        vec1.normalize()

        new_z_axis = new_y_axis.cross(vec1)
        new_z_axis.normalize()
        new_x_axis = new_y_axis.cross(new_z_axis)
        new_x_axis.normalize()

        # construct transition matrix
        origin_base = mathutils.Matrix((
            (1.0, 0, 0),
            (0, 1.0, 0),
            (0, 0, 1.0)
        ))
        origin_base.invert()
        new_base = mathutils.Matrix((
            (new_x_axis.x, new_y_axis.x, new_z_axis.x),
            (new_x_axis.y, new_y_axis.y, new_z_axis.y),
            (new_x_axis.z, new_y_axis.z, new_z_axis.z)
        ))
        transition_matrix = origin_base @ new_base
        transition_matrix.invert()

        # process each face
        for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
            pp = mathutils.Vector(tuple(vecList[mesh.loops[loop_index].vertex_index].co[x] for x in range(3)))
            vec = pp-p1
            new_vec = transition_matrix @ vec

            uv_layer.data[0].uv = (
                (new_vec.x if new_vec.x >=0 else -new_vec.x) / 5,
                (new_vec.y) / 5
            )

    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=False, calc_edges_loose=False)

    return no_processed_count

