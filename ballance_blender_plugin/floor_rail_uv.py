import bpy,bmesh
from . import utils

def create_rail_uv():
    meshList = []
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue

        if obj.data.uv_layers.active.data == None:
            utils.ShowMessageBox("You should create a UV layer for this object firstly. Then execute this operator.", "No UV layer", 'ERROR')
            return
        
        meshList.append(obj.data)
    
    for mesh in meshList:
        # vecList = mesh.vertices[:]
        uv_layer = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                # index = mesh.loops[loop_index].vertex_index
                uv_layer[loop_index].uv[0] = 0 # vecList[index].co[0]
                uv_layer[loop_index].uv[1] = 1 # vecList[index].co[1]


def virtoolize_floor_uv():
    pass

def mesh_triangulate(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()