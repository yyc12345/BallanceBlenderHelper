import bpy,bmesh
from . import utils

class BALLANCE_OT_rail_uv(bpy.types.Operator):
    """Create a UV for rail"""
    bl_idname = "ballance.rail_uv"
    bl_label = "Create Rail UV"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return check_rail_target()

    def execute(self, context):
        create_rail_uv()
        return {'FINISHED'}

# ====================== method

def check_rail_target():
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue
        if obj.mode != 'OBJECT':
            continue
        return True
    return False

def create_rail_uv():
    meshList = []
    ignoredObj = []
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            ignoredObj.append(obj.name)
            continue
        if obj.mode != 'OBJECT':
            ignoredObj.append(obj.name)
            continue
        if obj.data.uv_layers.active is None:
            # create a empty uv for it.
            obj.data.uv_layers.new(do_init=False)
        
        meshList.append(obj.data)
    
    for mesh in meshList:
        # vecList = mesh.vertices[:]
        uv_layer = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                # index = mesh.loops[loop_index].vertex_index
                uv_layer[loop_index].uv[0] = 0 # vecList[index].co[0]
                uv_layer[loop_index].uv[1] = 1 # vecList[index].co[1]

    if len(ignoredObj) != 0:
        utils.ShowMessageBox("Following objects are not processed due to they are not suit for this function now: " + ', '.join(ignoredObj), "Execution result", 'INFO')
