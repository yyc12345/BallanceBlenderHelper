import bpy,bmesh
import mathutils
import bpy.types
from . import UTILS_functions

class BALLANCE_OT_rail_uv(bpy.types.Operator):
    """Create a UV for rail"""
    bl_idname = "ballance.rail_uv"
    bl_label = "Create Rail UV"
    bl_options = {'UNDO'}

    uv_type: bpy.props.EnumProperty(
        name="Type",
        description="Define how to create UV",
        items=(
            ("POINT", "Point", "All UV will be created in a specific point"),
            ("UNIFORM", "Uniform", "All UV will be created within 1x1"),
            ("SCALE", "Scale", "Give a scale number to scale UV"),
            ("TT", "TT_ReflectionMapping", "The real internal process of Ballance rail")
            ),
    )

    projection_axis: bpy.props.EnumProperty(
        name="Projection axis",
        description="Projection axis",
        items=(
            ("X", "X axis", "X axis"),
            ("Y", "Y axis", "Y axis"),
            ("Z", "Z axis", "Z axis")
            ),
    )

    uv_scale : bpy.props.FloatProperty(
        name="Scale",
        description="The scale of UV",
        min=0.0,
        default=1.0,
    )

    @classmethod
    def poll(self, context):
        return _check_rail_target()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if context.scene.BallanceBlenderPluginProperty.material_picker == None:
            UTILS_functions.show_message_box(("No specific material", ), "Lost parameter", 'ERROR')
        else:
            _create_rail_uv(self.uv_type, context.scene.BallanceBlenderPluginProperty.material_picker, self.uv_scale, self.projection_axis)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "uv_type")
        layout.prop(context.scene.BallanceBlenderPluginProperty, "material_picker")
        if self.uv_type == 'SCALE' or self.uv_type == 'UNIFORM':
            layout.prop(self, "projection_axis")        
        if self.uv_type == 'SCALE':
            layout.prop(self, "uv_scale")

# ====================== method

def _check_rail_target():
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue
        if obj.mode != 'OBJECT':
            continue
        return True
    return False

def _get_distance(iterator):
    is_first_min = True
    is_first_max = True
    max_value = 0.0
    min_value = 0.0

    for item in iterator:
        if is_first_max:
            is_first_max = False
            max_value = item
        else:
            if item > max_value:
                max_value = item
        if is_first_min:
            is_first_min = False
            min_value = item
        else:
            if item < min_value:
                min_value = item

    return max_value - min_value

def _create_rail_uv(rail_type, material_pointer, scale_size, projection_axis):
    objList = []
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
        
        objList.append(obj)
    
    for obj in objList:
        mesh = obj.data

        # clean it material and set rail first
        obj.data.materials.clear()
        obj.data.materials.append(material_pointer)

        # copy mesh vec for scale or uniform mode
        vecList = mesh.vertices[:]
        real_scale = 1.0
        if rail_type == 'SCALE':
            real_scale = scale_size
        elif rail_type == 'UNIFORM':
            # calc proper scale
            if projection_axis == 'X':
                maxLength = max(
                    _get_distance(vec.co[1] for vec in vecList),
                    _get_distance(vec.co[2] for vec in vecList)
                )
            elif projection_axis == 'Y':
                maxLength = max(
                    _get_distance(vec.co[0] for vec in vecList),
                    _get_distance(vec.co[2] for vec in vecList)
                )
            elif projection_axis == 'Z':
                maxLength = max(
                    _get_distance(vec.co[0] for vec in vecList),
                    _get_distance(vec.co[1] for vec in vecList)
                )
            real_scale = 1.0 / maxLength

        uv_layer = mesh.uv_layers.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                # get correspond vec index
                index = mesh.loops[loop_index].vertex_index
                if rail_type == 'POINT':
                    # set to 1 point
                    uv_layer[loop_index].uv[0] = 0
                    uv_layer[loop_index].uv[1] = 1
                elif rail_type == 'SCALE' or rail_type == 'UNIFORM':
                    # following xy -> uv scale
                    # 
                    # use Z axis: X->U Y->V
                    # use X axis: Y->U Z->V
                    # use Y axis: X->U Z->V
                    if projection_axis == 'X':
                        uv_layer[loop_index].uv[0] = vecList[index].co[1] * real_scale
                        uv_layer[loop_index].uv[1] = vecList[index].co[2] * real_scale
                    elif projection_axis == 'Y':
                        uv_layer[loop_index].uv[0] = vecList[index].co[0] * real_scale
                        uv_layer[loop_index].uv[1] = vecList[index].co[2] * real_scale
                    elif projection_axis == 'Z':
                        uv_layer[loop_index].uv[0] = vecList[index].co[0] * real_scale
                        uv_layer[loop_index].uv[1] = vecList[index].co[1] * real_scale
                elif rail_type == 'TT':
                    (uv_layer[loop_index].uv[0], uv_layer[loop_index].uv[1]) = _tt_reflection_mapping_compute(
                         vecList[index].co,
                         mesh.loops[loop_index].normal,
                         (0.0, 0.0, 0.0)
                    )

    if len(ignoredObj) != 0:
        UTILS_functions.show_message_box(
            ("Following objects are not processed due to they are not suit for this function now: ", ) + tuple(ignoredObj), 
            "Execution result", 'INFO'
        )

def _tt_reflection_mapping_compute(_point, _n, _refobj):
    # switch blender coord to virtools coord for convenient calc
    point = mathutils.Vector((_point[0], _point[2], _point[1]))
    n = mathutils.Vector((_n[0], _n[2], _n[1])).normalized()
    refobj = mathutils.Vector((_refobj[0], _refobj[2], _refobj[1]))

    p = (refobj - point).normalized()
    b=(((2*(p*n))*n)-p).normalized()
    
    # convert back to blender coord
    return ((b.x + 1.0) / 2.0, -(b.z + 1.0) / 2.0)