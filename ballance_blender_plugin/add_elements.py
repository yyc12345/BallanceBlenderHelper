import bpy,mathutils
from . import utils

sectorRelatedElements = [
    "P_Extra_Life",
    "P_Extra_Point",
    "P_Trafo_Paper",
    "P_Trafo_Stone",
    "P_Trafo_Wood",
    "P_Ball_Paper",
    "P_Ball_Stone",
    "P_Ball_Wood",
    "P_Box",
    "P_Dome",
    "P_Modul_01",
    "P_Modul_03",
    "P_Modul_08",
    "P_Modul_17",
    "P_Modul_18",
    "P_Modul_19",
    "P_Modul_25",
    "P_Modul_26",
    "P_Modul_29",
    "P_Modul_30",
    "P_Modul_34",
    "P_Modul_37",
    "P_Modul_41",
    "PR_Resetpoint",
    "PC_TwoFlames"
]

uniqueElements = [
    "PE_Balloon",
    "PS_FourFlames"
]

# ================================================= actual add

class BALLANCE_OT_add_sector_related_elements(bpy.types.Operator):
    """Add sector related elements"""
    bl_idname = "ballance.add_sector_related_elements"
    bl_label = "Add normal elements"
    bl_options = {'UNDO'}

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        items=tuple(map(lambda x: (x, x, ""), sectorRelatedElements)),
    )

    elements_sector: bpy.props.IntProperty(
        name="Sector",
        description="Define which sector the object will be grouped in",
        min=1,
        max=8,
        default=1,
    )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "elements_type")
        layout.prop(self, "elements_sector")

class BALLANCE_OT_add_unique_elements(bpy.types.Operator):
    """Add unique elements"""
    bl_idname = "ballance.add_unique_elements"
    bl_label = "Add unique elements"
    bl_options = {'UNDO'}

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        items=tuple(map(lambda x: (x, x, ""), uniqueElements)),
    )

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "elements_type")

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