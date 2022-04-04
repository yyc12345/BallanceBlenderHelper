import bpy, mathutils
from . import UTILS_constants, UTILS_functions

# ================================================= actual add

class BALLANCE_OT_add_components(bpy.types.Operator):
    """Add sector related elements"""
    bl_idname = "ballance.add_components"
    bl_label = "Add elements"
    bl_options = {'UNDO'}

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        items=tuple(map(lambda x: (x, x, ""), UTILS_constants.bmfile_componentList)),
    )

    attentionElements = ["PC_TwoFlames", "PR_Resetpoint"]
    uniqueElements = ["PS_FourFlames", "PE_Balloon"]

    elements_sector: bpy.props.IntProperty(
        name="Sector",
        description="Define which sector the object will be grouped in",
        min=1,
        max=8,
        default=1,
    )

    def execute(self, context):
        # get name
        if self.elements_type in self.uniqueElements:
            finalObjectName = self.elements_type + "_01"
        elif self.elements_type in self.attentionElements:
            finalObjectName = self.elements_type + "_0" + str(self.elements_sector)
        else:
            finalObjectName = self.elements_type + "_0" + str(self.elements_sector) + "_"

        # create object
        loadedMesh = UTILS_functions.load_component(
            UTILS_constants.bmfile_componentList.index(self.elements_type))
        obj = bpy.data.objects.new(finalObjectName, loadedMesh)
        UTILS_functions.add_into_scene_and_move_to_cursor(obj)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "elements_type")
        if self.elements_type not in self.uniqueElements:
            layout.prop(self, "elements_sector")
        if self.elements_type in self.attentionElements:
            layout.label(text="Please note that sector is suffix.")
