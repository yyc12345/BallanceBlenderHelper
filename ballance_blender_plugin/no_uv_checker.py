import bpy,bmesh
from . import utils

class BALLANCE_OT_no_uv_checker(bpy.types.Operator):
    """Check whether the currently selected object has UV"""
    bl_idname = "ballance.no_uv_checker"
    bl_label = "Check UV"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return check_valid_target()

    def execute(self, context):
        check_target()
        return {'FINISHED'}

# ====================== method

def check_valid_target():
    return (len(bpy.context.selected_objects) > 0)

def check_target():
    noUVObject = []
    invalidObjectCount = 0
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            invalidObjectCount+=1
            continue
        if obj.mode != 'OBJECT':
            invalidObjectCount+=1
            continue
        if obj.data.uv_layers.active is None:
            noUVObject.append(obj.name)

    if len(noUVObject) > 4:
        print("Following object don't have UV:")
        for item in noUVObject:
            print(item)

    utils.ShowMessageBox((
        "All objects: {}".format(len(bpy.context.selected_objects)),
        "Skipped: {}".format(invalidObjectCount),
        "No UV Count: {}".format(len(noUVObject)),
        "",
        "Following object don't have UV: "
    ) + tuple(noUVObject[:4]) + 
    (("Too much objects don't have UV. Please open terminal to browse them." if len(noUVObject) > 4 else "") ,), "Check result", 'INFO')
