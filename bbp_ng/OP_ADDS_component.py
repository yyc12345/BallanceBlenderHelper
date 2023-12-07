import bpy
from . import UTIL_functions, UTIL_icons_manager, UTIL_naming_convension
from . import PROP_ballance_element, PROP_virtools_group

#region Help Classes & Functions

def _get_component_info(comp_type: PROP_ballance_element.BallanceElementType, comp_sector: int) -> UTIL_naming_convension.BallanceObjectInfo:
    match(comp_type):
        # process special for 2 unique components
        case PROP_ballance_element.BallanceElementType.PS_FourFlames:
            return UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.LEVEL_START)
        case PROP_ballance_element.BallanceElementType.PE_Balloon:
            return UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.LEVEL_END)
        # process naming convention required special components
        case PROP_ballance_element.BallanceElementType.PC_TwoFlames:
            return UTIL_naming_convension.BallanceObjectInfo.create_from_checkpoint(comp_sector)
        case PROP_ballance_element.BallanceElementType.PR_Resetpoint:
            return UTIL_naming_convension.BallanceObjectInfo.create_from_resetpoint(comp_sector)
        # process for other components
        case _:
            return UTIL_naming_convension.BallanceObjectInfo.create_from_component(comp_type.name, comp_sector)
    
def _set_component_by_info(obj: bpy.types.Object, info: UTIL_naming_convension.BallanceObjectInfo) -> None:
    # set component name and grouping it into virtools group at the same time
    # set name first
    if not UTIL_naming_convension.YYCToolchainConvention.set_to_object(obj, info, None):
        raise UTIL_functions.BBPException('impossible fail to set component name.')

    # set vt group next
    if not UTIL_naming_convension.VirtoolsGroupConvention.set_to_object(obj, info, None):
        raise UTIL_functions.BBPException('impossible fail to set component virtools groups.')

def _check_component_existance(comp_type: PROP_ballance_element.BallanceElementType, comp_sector: int) -> str | None:
    """
    Check the existance of 4 special components name, PS, PE, PC, PR
    These 4 components will have special name.

    @return Return name if selected component is one of PS, PE, PC, PR and there already is a name conflict, otherwise None.
    """
    # check component type requirements
    match(comp_type):
        case PROP_ballance_element.BallanceElementType.PS_FourFlames | PROP_ballance_element.BallanceElementType.PE_Balloon | PROP_ballance_element.BallanceElementType.PC_TwoFlames | PROP_ballance_element.BallanceElementType.PR_Resetpoint:
            pass    # exit match and start check
        case _:
            return None # return, do not check
    
    # get info
    comp_info: UTIL_naming_convension.BallanceObjectInfo = _get_component_info(comp_type, comp_sector)
    
    # get expected name
    expect_name: str | None = UTIL_naming_convension.YYCToolchainConvention.set_to_name(comp_info, None)
    if expect_name is None:
        raise UTIL_functions.BBPException('impossible fail to get component name.')
    
    # check expected name
    if expect_name in bpy.data.objects: return expect_name
    else: return None


class EnumPropHelper():
    """
    Generate component types for this module's operator
    """
    @staticmethod
    def generate_items() -> tuple[tuple, ...]:
        # token, display name, descriptions, icon, index
        return tuple(
            (
                str(item.value), 
                item.name, 
                "", 
                UTIL_icons_manager.get_element_icon(item.name), 
                item.value
            ) for item in PROP_ballance_element.BallanceElementType
        )
    
    @staticmethod
    def get_selection(prop: str) -> PROP_ballance_element.BallanceElementType:
        # prop will return identifier which is defined as the string type of int value.
        # so we parse it to int and then parse it to enum type.
        return PROP_ballance_element.BallanceElementType(int(prop))
    
    @staticmethod
    def to_selection(val: PROP_ballance_element.BallanceElementType) -> str:
        # like get_selection, we need get it int value, then convert it to string as the indetifier of enum props
        # them enum property will accept it.
        return str(val.value)

#endregion

class BBP_OT_add_component(bpy.types.Operator):
    """Add Component"""
    bl_idname = "bbp.add_component"
    bl_label = "Add Component"
    bl_options = {'UNDO'}

    component_sector: bpy.props.IntProperty(
        name = "Sector",
        description = "Define which sector the object will be grouped in",
        min = 1, max = 999,
        soft_min = 1, soft_max = 8,
        default = 1,
    )

    component_type: bpy.props.EnumProperty(
        name = "Type",
        description = "This component type",
        items = EnumPropHelper.generate_items(),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # show type
        layout.prop(self, "component_type")

        # only show sector for non-PE/PS component
        eletype: PROP_ballance_element.BallanceElementType = EnumPropHelper.get_selection(self.component_type)
        if eletype != PROP_ballance_element.BallanceElementType.PS_FourFlames and eletype != PROP_ballance_element.BallanceElementType.PE_Balloon:
            layout.prop(self, "component_sector")

        # check for some special components and show warning
        elename: str | None = _check_component_existance(EnumPropHelper.get_selection(self.component_type), self.component_sector)
        if elename is not None:
            layout.label(text = f'Warning: {elename} already exist.')

    def execute(self, context):
        # create by ballance components
        eletype: PROP_ballance_element.BallanceElementType = EnumPropHelper.get_selection(self.component_type)
        eleinfo: UTIL_naming_convension.BallanceObjectInfo = _get_component_info(eletype, self.component_sector)

        with PROP_ballance_element.BallanceElementsHelper(bpy.context.scene) as creator:
            # create with empty name first
            obj = bpy.data.objects.new('', creator.get_element(eletype.value))
            # assign its props, including name
            _set_component_by_info(obj, eleinfo)
            # scene cursor
            UTIL_functions.add_into_scene_and_move_to_cursor(obj)
            
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        for item in PROP_ballance_element.BallanceElementType:
            cop = layout.operator(
                self.bl_idname, text = item.name, 
                icon_value = UTIL_icons_manager.get_element_icon(item.name))
            cop.component_type = EnumPropHelper.to_selection(item)

def register():
    # register all classes
    bpy.utils.register_class(BBP_OT_add_component)

def unregister():
    bpy.utils.unregister_class(BBP_OT_add_component)
