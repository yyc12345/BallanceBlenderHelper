import bpy
from . import UTIL_functions, UTIL_icons_manager
from . import PROP_preferences, PROP_ballance_element, PROP_virtools_group

_g_UniqueElements = {
    "PS_FourFlames": 'PS_FourFlames_01', 
    "PE_Balloon": 'PE_Balloon_01'
}

def _get_component_name(comp_name: str, comp_sector: int) -> str:
    return '{}_{:0>2d}_'.format(comp_name, comp_sector)

class BBP_OT_add_component(bpy.types.Operator):
    """Add Element"""
    bl_idname = "bbp.add_component"
    bl_label = "Add Element"
    bl_options = {'UNDO'}

    element_sector: bpy.props.IntProperty(
        name = "Sector",
        description = "Define which sector the object will be grouped in",
        min = 1, max = 999,
        soft_min = 1, soft_max = 8,
        default = 1,
    )

    element_type: bpy.props.EnumProperty(
        name = "Type",
        description = "This element type",
        #items=tuple(map(lambda x: (x, x, ""), UTILS_constants.bmfile_componentList)),
        items = tuple(
            # token, display name, descriptions, icon, index
            (str(item.value), item.name, "", UTIL_icons_manager.get_element_icon(item.name), item.value) 
            for item in PROP_ballance_element.BallanceElementType
        ),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "element_type")
        layout.prop(self, "element_sector")

        # check for unique name and show warning
        elename: str | None = _g_UniqueElements.get(PROP_ballance_element.BallanceElementType(int(self.element_type)).name, None)
        if elename is not None and elename in bpy.data.objects:
            layout.label(f'Warning: {elename} already exist.')

    def execute(self, context):
        # create by ballance elements
        eletype: PROP_ballance_element.BallanceElementType = PROP_ballance_element.BallanceElementType(int(self.element_type))
        with PROP_ballance_element.BallanceElementsHelper(bpy.context.scene) as creator:
            obj = bpy.data.objects.new(
                _get_component_name(eletype.name, self.element_sector),
                creator.get_element(eletype.value)
            )
            UTIL_functions.add_into_scene_and_move_to_cursor(obj)
            
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        for item in PROP_ballance_element.BallanceElementType:
            cop = layout.operator(
                self.bl_idname, text = item.name, 
                icon_value = UTIL_icons_manager.get_element_icon(item.name))
            cop.element_type = str(item.value)

def register():
    # register all classes
    bpy.utils.register_class(BBP_OT_add_component)

def unregister():
    bpy.utils.unregister_class(BBP_OT_add_component)
