import bpy, mathutils
from . import UTILS_constants, UTILS_functions, UTILS_icons_manager

# =============== Common Class ================ 
class common_add_component_props(bpy.types.Operator):
    attentionElements = ("PC_TwoFlames", "PR_Resetpoint")
    uniqueElements = ("PS_FourFlames", "PE_Balloon")

    elements_sector: bpy.props.IntProperty(
        name="Sector",
        description="Define which sector the object will be grouped in",
        min=1, max=8,
        default=1,
    )

    def get_component_name(self, raw_comp_name):
        if raw_comp_name in self.uniqueElements:
            return raw_comp_name + "_01"
        elif raw_comp_name in self.attentionElements:
            return raw_comp_name + "_0" + str(self.elements_sector)
        else:
            return raw_comp_name + "_0" + str(self.elements_sector) + "_"

    def parent_draw(self, parent_layout, raw_comp_name):
        if raw_comp_name not in self.uniqueElements:
            parent_layout.prop(self, 'elements_sector')

class BALLANCE_OT_add_components(common_add_component_props):
    """Add Elements"""
    bl_idname = "ballance.add_components"
    bl_label = "Add Elements"
    bl_options = {'UNDO'}

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        #items=tuple(map(lambda x: (x, x, ""), UTILS_constants.bmfile_componentList)),
        items=tuple(
            # token, display name, descriptions, icon, index
            (blk, blk, "", UTILS_icons_manager.get_element_icon(blk), idx) 
            for idx, blk in enumerate(UTILS_constants.bmfile_componentList)
        ),
    )

    def execute(self, context):
        # get name
        finalObjectName = self.get_component_name(self.elements_type)

        # create object
        loadedMesh = UTILS_functions.load_component(
            UTILS_constants.bmfile_componentList.index(self.elements_type)
        )
        obj = bpy.data.objects.new(finalObjectName, loadedMesh)
        UTILS_functions.add_into_scene_and_move_to_cursor(obj)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # attension notice
        if self.elements_type in self.attentionElements:
            layout.label(text="NOTE: Check Sector ID carefully.")
        if self.elements_type in self.uniqueElements:
            layout.label(text="NOTE: This element have unique name.")

        # cfg
        layout.prop(self, "elements_type")
        self.parent_draw(layout, self.elements_type)

    @classmethod
    def draw_blc_menu(self, layout):
        for item in UTILS_constants.bmfile_componentList:
            cop = layout.operator(
                self.bl_idname, text=item, 
                icon_value = UTILS_icons_manager.get_element_icon(item))
            cop.elements_type = item


class BALLANCE_OT_add_components_dup(common_add_component_props):
    """Add Duplicated Elements"""
    bl_idname = "ballance.add_components_dup"
    bl_label = "Add Duplicated Elements"
    bl_options = {'UNDO'}

    can_duplicated_elements = (
        'P_Extra_Point', 'P_Modul_18', 'P_Modul_26'
    )

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        #items=tuple(map(lambda x: (x, x, ""), UTILS_constants.bmfile_componentList)),
        items=tuple(
            # token, display name, descriptions, icon, index
            (blk, blk, "", UTILS_icons_manager.get_element_icon(blk), idx) 
            for idx, blk in enumerate(can_duplicated_elements)
        ),
    )

    elements_dup_times: bpy.props.IntProperty(
        name="Duplication Count",
        description="How many this element should be duplicated.",
        min=2, max=64,
        soft_min=2, soft_max=32,
        default=2,
    )

    def execute(self, context):
        # get name
        finalObjectName = self.get_component_name(self.elements_type)

        # load mesh
        loadedMesh = UTILS_functions.load_component(
            UTILS_constants.bmfile_componentList.index(self.elements_type)
        )
        # create object
        for i in range(self.elements_dup_times):
            obj = bpy.data.objects.new(finalObjectName, loadedMesh)
            UTILS_functions.add_into_scene_and_move_to_cursor(obj)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "elements_type")
        self.parent_draw(layout, self.elements_type)
        layout.prop(self, "elements_dup_times")

    @classmethod
    def draw_blc_menu(self, layout):
        for item in self.can_duplicated_elements:
            cop = layout.operator(
                self.bl_idname, text=item, 
                icon_value = UTILS_icons_manager.get_element_icon(item))
            cop.elements_type = item


class BALLANCE_OT_add_components_series(common_add_component_props):
    """Add Elements with a Series."""
    bl_idname = "ballance.add_components_series"
    bl_label = "Add Series Elements"
    bl_options = {'REGISTER', 'UNDO'}

    supported_series = {
        # format: key: (description: str, real_component: str, unit_transition: mathutils.Vector, default_span: float)
        # key will become enum property's identifier
        "MODUL_41": ('Tilting Block Series', 'P_Modul_41', mathutils.Vector((1.0, 0.0, 0.0)), 6.0022),
        "MODUL_18_V": ('Fan Vertical Series', 'P_Modul_18', mathutils.Vector((0.0, 0.0, 1.0)), 15),
        "MODUL_18_H": ('Fan Horizonal Series', 'P_Modul_18', mathutils.Vector((1.0, 0.0, 0.0)), 30),
    }

    # the updator for default span
    def element_type_updated(self, context):
        # set span
        self.elements_span = BALLANCE_OT_add_components_series.supported_series[self.elements_type][3]

        # blender required
        return None

    elements_type: bpy.props.EnumProperty(
        name="Type",
        description="This element type",
        #items=tuple(map(lambda x: (x, x, ""), UTILS_constants.bmfile_componentList)),
        items=tuple(
            # token, display name, descriptions, icon, index
            (skey, sitem[0], "", UTILS_icons_manager.get_element_icon(sitem[1]), idx) 
            for (idx, (skey, sitem)) in enumerate(supported_series.items())
        ),
        default=0,
        update=element_type_updated
    )

    elements_dup_times: bpy.props.IntProperty(
        name="Duplication Count",
        description="How many this element should be duplicated.",
        min=2, max=64,
        soft_min=2, soft_max=32,
        default=2,
    )

    elements_span: bpy.props.FloatProperty(
        name="Elements Span",
        description="The span between each elements.",
        min=0.0,
        default=0.0,
    )

    def invoke(self, context, event):
        # force trigger span update once to treat span normally
        self.element_type_updated(context)

        return self.execute(context)

    def execute(self, context):
        # get unit span and real element name for loading mesh and creating name
        (_, real_element_name, unit_span, _) = self.supported_series[self.elements_type]

        # get name
        finalObjectName = self.get_component_name(real_element_name)
        # load mesh
        loadedMesh = UTILS_functions.load_component(
            UTILS_constants.bmfile_componentList.index(real_element_name)
        )

        # create object
        for i in range(self.elements_dup_times):
            obj = bpy.data.objects.new(finalObjectName, loadedMesh)
            UTILS_functions.add_into_scene_and_move_to_cursor(obj)
            obj.matrix_world.translation += unit_span * (self.elements_span * i)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "elements_type")
        self.parent_draw(layout, self.elements_type)
        layout.prop(self, "elements_dup_times")
        layout.prop(self, "elements_span")

    @classmethod
    def draw_blc_menu(self, layout):
        for key, item in self.supported_series.items():
            cop = layout.operator(
                self.bl_idname, text=item[0], 
                icon_value = UTILS_icons_manager.get_element_icon(item[1]))
            cop.elements_type = key
