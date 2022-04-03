import bpy, mathutils
from . import UTILS_functions

class BALLANCE_OT_super_align(bpy.types.Operator):
    """Align object with 3ds Max way"""
    bl_idname = "ballance.super_align"
    bl_label = "3ds Max Align"
    bl_options = {'UNDO'}

    align_x: bpy.props.BoolProperty(name="X position")
    align_y: bpy.props.BoolProperty(name="Y position")
    align_z: bpy.props.BoolProperty(name="Z position")

    current_references: bpy.props.EnumProperty(
        name="Reference",
        items=(('MIN', "Min", ""),
                ('CENTER', "Center (bound box)", ""),
                ('POINT', "Center (axis)", ""),
                ('MAX', "Max", "")
                ),
        )

    target_references: bpy.props.EnumProperty(
        name="Target",
        items=(('MIN', "Min", ""),
                ('CENTER', "Center (bound box)", ""),
                ('POINT', "Center (axis)", ""),
                ('MAX', "Max", "")
                ),
        )

    @classmethod
    def poll(self, context):
        return _check_align_target()

    def execute(self, context):
        _align_object(self.align_x, self.align_y, self.align_z, self.current_references, self.target_references)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Align axis")

        row = col.row()
        row.prop(self, "align_x")
        row.prop(self, "align_y")
        row.prop(self, "align_z")

        col.prop(self, "current_references")
        col.prop(self, "target_references")

# ============================== method

def _check_align_target():
    if bpy.context.active_object is None:
        return False

    selected = bpy.context.selected_objects[:]
    length = len(selected)
    if bpy.context.active_object in selected:
        length -= 1
    if length == 0:
        return False
    
    return True

def _align_object(use_x, use_y, use_z, currentMode, targetMode):
    if not (use_x or use_y or use_z):
        return

    # calc active object data
    currentObj = bpy.context.active_object
    currentObjBbox = [currentObj.matrix_world @ mathutils.Vector(corner) for corner in currentObj.bound_box]
    currentObjRef = _provide_obj_reference_point(currentObj, currentObjBbox, currentMode)

    # calc target
    targetObjList = bpy.context.selected_objects[:]
    if currentObj in targetObjList:
        targetObjList.remove(currentObj)
        
    # process each obj
    for targetObj in targetObjList:
        targetObjBbox = [targetObj.matrix_world @ mathutils.Vector(corner) for corner in targetObj.bound_box]
        targetObjRef = _provide_obj_reference_point(targetObj, targetObjBbox, targetMode)

        if use_x:
            targetObj.location.x += currentObjRef.x - targetObjRef.x
        if use_y:
            targetObj.location.y += currentObjRef.y - targetObjRef.y
        if use_z:
            targetObj.location.z += currentObjRef.z - targetObjRef.z

def _provide_obj_reference_point(obj, vecList, mode):
    refPoint = mathutils.Vector((0, 0, 0))

    if (mode == 'MIN'):
        refPoint.x = min([vec.x for vec in vecList])
        refPoint.y = min([vec.y for vec in vecList])
        refPoint.z = min([vec.z for vec in vecList])
    elif (mode == 'MAX'):
        refPoint.x = max([vec.x for vec in vecList])
        refPoint.y = max([vec.y for vec in vecList])
        refPoint.z = max([vec.z for vec in vecList])
    elif (mode == 'CENTER'):
        maxVecCache = mathutils.Vector((0, 0, 0))
        minVecCache = mathutils.Vector((0, 0, 0))

        minVecCache.x = min([vec.x for vec in vecList])
        minVecCache.y = min([vec.y for vec in vecList])
        minVecCache.z = min([vec.z for vec in vecList])
        maxVecCache.x = max([vec.x for vec in vecList])
        maxVecCache.y = max([vec.y for vec in vecList])
        maxVecCache.z = max([vec.z for vec in vecList])

        refPoint.x = (maxVecCache.x + minVecCache.x) / 2
        refPoint.y = (maxVecCache.y + minVecCache.y) / 2
        refPoint.z = (maxVecCache.z + minVecCache.z) / 2
    else:
        refPoint.x = obj.location.x
        refPoint.y = obj.location.y
        refPoint.z = obj.location.z

    return refPoint