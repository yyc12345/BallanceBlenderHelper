import bpy, mathutils
import math, typing
from . import UTIL_functions, UTIL_icons_manager, UTIL_naming_convension
from . import PROP_ballance_element, PROP_virtools_group

#region Param Help Classes

class ComponentSectorParam():
    component_sector: bpy.props.IntProperty(
        name = "Sector",
        description = "Define which sector the object will be grouped in",
        min = 1, max = 999,
        soft_min = 1, soft_max = 8,
        default = 1,
    )

    def general_get_component_sector(self) -> int:
        return self.component_sector
    
    def draw_component_sector_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'component_sector')

class ComponentCountParam():
    component_count: bpy.props.IntProperty(
        name = "Count",
        description = "The count of components you want to generate",
        min = 1, max = 64,
        soft_min = 1, soft_max = 32,
        default = 1,
    )

    def general_get_component_count(self) -> int:
        return self.component_count

    def draw_component_count_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'component_count')

#endregion

#region Help Classes & Functions

def _get_component_info(comp_type: PROP_ballance_element.BallanceElementType, comp_sector: int) -> UTIL_naming_convension.BallanceObjectInfo:
    match(comp_type):
        # process for 2 special unique components
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
            return UTIL_naming_convension.BallanceObjectInfo.create_from_component(
                PROP_ballance_element.get_ballance_element_name(comp_type), 
                comp_sector
            )
    
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

def _general_create_component(comp_type: PROP_ballance_element.BallanceElementType, comp_sector: int, comp_count: int, comp_offset: typing.Callable[[int], mathutils.Matrix]) -> None:
    """
    General component creation function.

    @param comp_type[in] The component type created.
    @param comp_sector[in] The sector param which passed to other functions. For non-sector component, pass any number.
    @param comp_count[in] The count of created component. For single component creation, please pass 1.
    @param comp_offset[in] The function pointer which receive 1 argument indicating the index of object which we want to get its offset.
        You can pass `lambda _: mathutils.Matrix.Identity(4)` to get zero offset for every items.
        You can pass `lambda _: mathutils.Matrix( xxx )` to get same offset for every items.
        You can pass `lambda i: mathutils.Matrix( func(i) )` to get index based offset for each items.
        The offset is the offset to the origin point, not the previous object.
    """
    # get element info first
    ele_info: UTIL_naming_convension.BallanceObjectInfo = _get_component_info(comp_type, comp_sector)
    # create blc element context
    with PROP_ballance_element.BallanceElementsHelper(bpy.context.scene) as creator:
        # object creation counter
        for i in range(comp_count):
            # get mesh from element context, and create with empty name first. we assign name later.
            obj: bpy.types.Object = bpy.data.objects.new('', creator.get_element(comp_type))
            # assign virtools group, object name by we gotten element info.
            _set_component_by_info(obj, ele_info)
            # add into scene and move to cursor
            UTIL_functions.add_into_scene_and_move_to_cursor(obj)
            # move with extra offset by calling offset getter
            obj.matrix_world = obj.matrix_world @ comp_offset(i)
        
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
                UTIL_icons_manager.get_component_icon(PROP_ballance_element.get_ballance_element_name(item)), 
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

#region Noemal Component Adder

class BBP_OT_add_component(bpy.types.Operator, ComponentSectorParam):
    """Add Component"""
    bl_idname = "bbp.add_component"
    bl_label = "Add Component"
    bl_options = {'UNDO'}

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
            self.draw_component_sector_params(layout)

        # check for some special components and show warning
        elename: str | None = _check_component_existance(EnumPropHelper.get_selection(self.component_type), self.general_get_component_sector())
        if elename is not None:
            layout.label(text = f'Warning: {elename} already exist.')

    def execute(self, context):
        # call general creator
        _general_create_component(
            EnumPropHelper.get_selection(self.component_type),
            self.general_get_component_sector(),
            1,  # only create one
            lambda _: mathutils.Matrix.Identity(4)
        )
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        for item in PROP_ballance_element.BallanceElementType:
            item_name: str = PROP_ballance_element.get_ballance_element_name(item)

            cop = layout.operator(
                self.bl_idname, text = item_name, 
                icon_value = UTIL_icons_manager.get_component_icon(item_name)
            )
            cop.component_type = EnumPropHelper.to_selection(item)

#endregion

#region Nong Comp Adder

class BBP_OT_add_nong_extra_point(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Nong Extra Point"""
    bl_idname = "bbp.add_nong_extra_point"
    bl_label = "Nong Extra Point"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)
        self.draw_component_count_params(layout)

    def execute(self, context):
        # create objects and rotate it by a certain degree calculated by its index
        # calc percent first
        percent: float = 1.0 / self.general_get_component_count()
        # create elements
        _general_create_component(
            PROP_ballance_element.BallanceElementType.P_Extra_Point,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Rotation(percent * i * math.pi * 2, 4, 'Z')
        )
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_nong_extra_point.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Extra_Point)
            )
        )

#endregion

#region Series Comp Adder

class BBP_OT_add_tilting_block_series(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Tilting Block Series"""
    bl_idname = "bbp.add_tilting_block_series"
    bl_label = "Tilting Block Series"
    bl_options = {'REGISTER', 'UNDO'}

    component_span: bpy.props.FloatProperty(
        name = "Span",
        description = "The distance between each titling blocks",
        min = 0.0, max = 100.0,
        soft_min = 0.0, soft_max = 12.0,
        default = 6.0022,
    )

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)
        self.draw_component_count_params(layout)
        layout.prop(self, 'component_span')

    def execute(self, context):
        # create objects and move it by delta
        # get span first
        span: float = self.component_span
        # create elements
        _general_create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_41,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Translation(mathutils.Vector((span * i, 0.0, 0.0)))  # move with extra delta in x axis
        )
            
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_tilting_block_series.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Modul_41)
            )
        )

class BBP_OT_add_ventilator_series(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Ventilator Series"""
    bl_idname = "bbp.add_ventilator_series"
    bl_label = "Ventilator Series"
    bl_options = {'REGISTER', 'UNDO'}

    component_translation: bpy.props.FloatVectorProperty(
        name = "Delta Vector",
        description = "The translation between each ventilators. You can use this property to implement vertical or horizontal ventilator series. Set all factors to zero can get Nong ventilator.",
        size = 3, subtype = 'TRANSLATION',
        min = 0.0, max = 100.0,
        soft_min = 0.0, soft_max = 50.0,
        default = (0.0, 0.0, 15.0),
    )

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)
        self.draw_component_count_params(layout)
        layout.prop(self, 'component_translation')

    def execute(self, context):
        # create objects and move it by delta
        # get translation first
        translation: mathutils.Vector = mathutils.Vector(self.component_translation)
        # create elements
        _general_create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_18,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Translation(i * translation)  # move with extra translation
        )
        
        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_ventilator_series.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Modul_18)
            )
        )

#endregion

#region Comp Pair Adder

class BBP_OT_add_sector_component_pair(bpy.types.Operator, ComponentSectorParam):
    """Add Sector Pair, both check point and reset point."""
    bl_idname = "bbp.add_sector_component_pair"
    bl_label = "Sector Pair"
    bl_options = {'UNDO'}

    def __get_checkpoint(self) -> tuple[PROP_ballance_element.BallanceElementType, int]:
        if self.general_get_component_sector() == 1:
            return (PROP_ballance_element.BallanceElementType.PS_FourFlames, 1)
        else:
            # the sector of two flames should be `sector - 1` because first one was occupied by FourFlams
            return (PROP_ballance_element.BallanceElementType.PC_TwoFlames, self.general_get_component_sector() - 1)

    def __get_resetpoint(self) -> tuple[PROP_ballance_element.BallanceElementType, int]:
        # resetpoint's sector is just sector it self.
        return (PROP_ballance_element.BallanceElementType.PR_Resetpoint, self.general_get_component_sector())

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)

        # check checkpoint and resetpoint name conflict and show warnings
        (checkp_ty, checkp_sector) = self.__get_checkpoint()
        elename: str | None = _check_component_existance(checkp_ty, checkp_sector)
        if elename is not None:
            layout.label(text = f'Warning: {elename} already exist.')

        (resetp_ty, resetp_sector) = self.__get_resetpoint()
        elename = _check_component_existance(resetp_ty, resetp_sector)
        if elename is not None:
            layout.label(text = f'Warning: {elename} already exist.')

    def execute(self, context):
        # create checkpoint and resetpoint individually in element context
        # get type and sector data first
        (checkp_ty, checkp_sector) = self.__get_checkpoint()
        (resetp_ty, resetp_sector) = self.__get_resetpoint()
        # calc resetpoint offset
        # resetpoint need a extra offset between checkpoint
        # but it is different in FourFlams and TwoFlams
        resetp_offset: float
        if checkp_ty == PROP_ballance_element.BallanceElementType.PS_FourFlames:
            resetp_offset = 3.25
        else:
            resetp_offset = 2.0

        # add elements
        # create checkpoint
        _general_create_component(
            checkp_ty,
            checkp_sector,
            1,  # only create one
            lambda _: mathutils.Matrix.Identity(4)
        )
        # create resetpoint
        _general_create_component(
            resetp_ty,
            resetp_sector,
            1,  # only create one
            lambda _: mathutils.Matrix.Translation(mathutils.Vector((0.0, 0.0, resetp_offset))) # apply resetpoint offset
        )

        return {'FINISHED'}

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_sector_component_pair.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.PR_Resetpoint)
            )
        )

#endregion

def register():
    bpy.utils.register_class(BBP_OT_add_component)
    bpy.utils.register_class(BBP_OT_add_nong_extra_point)
    bpy.utils.register_class(BBP_OT_add_tilting_block_series)
    bpy.utils.register_class(BBP_OT_add_ventilator_series)
    bpy.utils.register_class(BBP_OT_add_sector_component_pair)

def unregister():
    bpy.utils.unregister_class(BBP_OT_add_sector_component_pair)
    bpy.utils.unregister_class(BBP_OT_add_ventilator_series)
    bpy.utils.unregister_class(BBP_OT_add_tilting_block_series)
    bpy.utils.unregister_class(BBP_OT_add_nong_extra_point)
    bpy.utils.unregister_class(BBP_OT_add_component)