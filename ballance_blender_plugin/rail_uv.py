import bpy,bmesh
import mathutils
import bpy.types
from . import utils, preferences

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
            ("SCALE", "Scale", "Give a scale number to scale UV")
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
        return check_rail_target()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        if context.scene.BallanceBlenderPluginProperty.material_picker == None:
            utils.ShowMessageBox(("No specific material", ), "Lost parameter", 'ERROR')
        else:
            create_rail_uv(self.uv_type, context.scene.BallanceBlenderPluginProperty.material_picker, self.uv_scale)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "uv_type")
        layout.prop(context.scene.BallanceBlenderPluginProperty, "material_picker")
        if self.uv_type == 'SCALE':
            layout.prop(self, "uv_scale")

# ====================== method

def check_rail_target():
    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue
        if obj.mode != 'OBJECT':
            continue
        return True
    return False

def get_distance(iterator):
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

def create_rail_uv(rail_type, material_pointer, scale_size):
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
            maxLength = max(
                get_distance(vec.co[0] for vec in vecList),
                get_distance(vec.co[1] for vec in vecList)
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
                else:
                    # following xy -> uv scale
                    uv_layer[loop_index].uv[0] = vecList[index].co[0] * real_scale
                    uv_layer[loop_index].uv[1] = vecList[index].co[1] * real_scale

    if len(ignoredObj) != 0:
        utils.ShowMessageBox(("Following objects are not processed due to they are not suit for this function now: ", ) + tuple(ignoredObj), "Execution result", 'INFO')
