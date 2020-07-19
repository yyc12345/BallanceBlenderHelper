import bpy,mathutils
from . import utils

def check_align_target():
    if bpy.context.active_object is None:
        return False

    selected = bpy.context.selected_objects[:]
    length = len(selected)
    if bpy.context.active_object in selected:
        length -= 1
    if length == 0:
        return False
    
    return True

def align_object(use_x, use_y, use_z, currentMode, targetMode):
    if not (use_x or use_y or use_z):
        return

    # calc active object data
    currentObj = bpy.context.active_object
    currentObjBbox = [currentObj.matrix_world @ mathutils.Vector(corner) for corner in currentObj.bound_box]
    currentObjRef = provideObjRefPoint(currentObj, currentObjBbox, currentMode)

    # calc target
    targetObjList = bpy.context.selected_objects[:]
    if currentObj in targetObjList:
        targetObjList.remove(currentObj)
        
    # process each obj
    for targetObj in targetObjList:
        targetObjBbox = [targetObj.matrix_world @ mathutils.Vector(corner) for corner in targetObj.bound_box]
        targetObjRef = provideObjRefPoint(targetObj, targetObjBbox, targetMode)

        if use_x:
            targetObj.location.x += currentObjRef.x - targetObjRef.x
        if use_y:
            targetObj.location.y += currentObjRef.y - targetObjRef.y
        if use_z:
            targetObj.location.z += currentObjRef.z - targetObjRef.z

def provideObjRefPoint(obj, vecList, mode):
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