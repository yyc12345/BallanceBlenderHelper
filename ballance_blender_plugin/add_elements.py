import bpy,mathutils
from . import utils, config, bm_import_export

# ================================================= actual add

class BALLANCE_OT_add_elements(bpy.types.Operator):
    """Add sector related elements"""
    bl_idname = "ballance.add_elements"
    bl_label = "Add elements"
    bl_options = {'UNDO'}

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        items=tuple(map(lambda x: (x, x, ""), config.component_list)),
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
        else:
            finalObjectName = self.elements_type + "_0" + str(self.elements_sector) + "_"

        # create object
        loadedMesh = bm_import_export.load_component(config.component_list.index(self.elements_type))
        obj = bpy.data.objects.new(finalObjectName, loadedMesh)
        addSceneAndChangePos(obj)

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

class BALLANCE_OT_add_rail(bpy.types.Operator):
    """Add rail"""
    bl_idname = "ballance.add_rail"
    bl_label = "Add unique elements"
    bl_options = {'UNDO'}

    rail_type: bpy.props.EnumProperty(
        name="Type",
        description="Rail type",
        items=(('MONO', "Monorail", ""),
                ('DOUBLE', "Rail", ""),
                ),
    )

    rail_radius: bpy.props.FloatProperty(
        name="Rail radius",
        description="Define rail section radius",
        default=0.375,
    )

    rail_span: bpy.props.FloatProperty(
        name="Rail span",
        description="Define rail span",
        default=3.75,
    )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "rail_type")
        layout.prop(self, "rail_radius")
        layout.prop(self, "rail_span")

def addSceneAndChangePos(obj):
    obj.matrix_world = bpy.context.scene.cursor.matrix

    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)