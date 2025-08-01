import bpy, mathutils
import math, typing
from . import UTIL_functions, UTIL_icons_manager, UTIL_naming_convention
from . import PROP_ballance_element, PROP_virtools_group, PROP_ballance_map_info

#region Param Help Classes

class ComponentSectorParam():
    component_sector: bpy.props.IntProperty(
        name = "Sector",
        description = "The sector which this component will be grouped in.",
        min = 1, max = 999,
        soft_min = 1, soft_max = 8,
        default = 1,
        translation_context = 'BBP/OP_ADDS_component.ComponentSectorParam/property'
    ) # type: ignore

    def general_get_component_sector(self) -> int:
        return self.component_sector
    
    def draw_component_sector_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'component_sector')

class ComponentCountParam():
    component_count: bpy.props.IntProperty(
        name = "Count",
        description = "The count of components which you want to generate",
        min = 1, max = 64,
        soft_min = 1, soft_max = 32,
        default = 1,
        translation_context = 'BBP/OP_ADDS_component.ComponentCountParam/property'
    ) # type: ignore

    def general_get_component_count(self) -> int:
        return self.component_count

    def draw_component_count_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'component_count')

#endregion

#region Help Classes & Functions

def _get_component_info(comp_type: PROP_ballance_element.BallanceElementType, comp_sector: int) -> UTIL_naming_convention.BallanceObjectInfo:
    match(comp_type):
        # process for 2 special unique components
        case PROP_ballance_element.BallanceElementType.PS_FourFlames:
            return UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.LEVEL_START)
        case PROP_ballance_element.BallanceElementType.PE_Balloon:
            return UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.LEVEL_END)
        # process naming convention required special components
        case PROP_ballance_element.BallanceElementType.PC_TwoFlames:
            return UTIL_naming_convention.BallanceObjectInfo.create_from_checkpoint(comp_sector)
        case PROP_ballance_element.BallanceElementType.PR_Resetpoint:
            return UTIL_naming_convention.BallanceObjectInfo.create_from_resetpoint(comp_sector)
        # process for other components
        case _:
            return UTIL_naming_convention.BallanceObjectInfo.create_from_component(
                PROP_ballance_element.get_ballance_element_name(comp_type), 
                comp_sector
            )
    
def _set_component_by_info(obj: bpy.types.Object, info: UTIL_naming_convention.BallanceObjectInfo) -> None:
    # set component name and grouping it into virtools group at the same time
    # set name first
    if not UTIL_naming_convention.YYCToolchainConvention.set_to_object(obj, info, None):
        raise UTIL_functions.BBPException('impossible fail to set component name.')

    # set vt group next
    if not UTIL_naming_convention.VirtoolsGroupConvention.set_to_object(obj, info, None):
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
    comp_info: UTIL_naming_convention.BallanceObjectInfo = _get_component_info(comp_type, comp_sector)
    
    # get expected name
    expect_name: str | None = UTIL_naming_convention.YYCToolchainConvention.set_to_name(comp_info, None)
    if expect_name is None:
        raise UTIL_functions.BBPException('impossible fail to get component name.')
    
    # check expected name
    if expect_name in bpy.data.objects: return expect_name
    else: return None

class _GeneralComponentCreator():
    """
    The assist class for general component creation function.
    Because we need select all created component, thus we need collect all created object into a list.
    This is the reason why we create this class.
    """

    ## The list storing all created component within this creation.
    __mObjList: list[bpy.types.Object]

    def __init__(self):
        self.__mObjList = []
            
    def create_component(self,
            comp_type: PROP_ballance_element.BallanceElementType, 
            comp_sector: int, 
            comp_count: int, 
            comp_offset: typing.Callable[[int], mathutils.Matrix]
        ) -> None:
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
        @return The created component instance.
        """
        # get element info first
        ele_info: UTIL_naming_convention.BallanceObjectInfo = _get_component_info(comp_type, comp_sector)
        
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
                # put into created object list
                self.__mObjList.append(obj)

        # enlarge scene sector field for non-PS (start point) PE (end point) component
        # read from scene and create var for enlarged sector count
        map_info: PROP_ballance_map_info.RawBallanceMapInfo = PROP_ballance_map_info.get_raw_ballance_map_info(bpy.context.scene)
        enlarged_sector: int
        # check component type to get enlarged value
        match(ele_info.mBasicType):
            case UTIL_naming_convention.BallanceObjectType.COMPONENT:
                enlarged_sector = comp_sector
            case UTIL_naming_convention.BallanceObjectType.CHECKPOINT:
                # checkpoint 1 means that there is sector 2, so we plus 1 for it.
                enlarged_sector = comp_sector + 1
            case UTIL_naming_convention.BallanceObjectType.RESETPOINT:
                enlarged_sector = comp_sector
            case _:
                # this component is not a sector based component
                # so we do not change it (use original value)
                enlarged_sector = map_info.mSectorCount
        # enlarge it
        map_info.mSectorCount = max(map_info.mSectorCount, enlarged_sector)
        PROP_ballance_map_info.set_raw_ballance_map_info(bpy.context.scene, map_info)

    def finish_component(self) -> None:
        """
        Finish up component creation.
        Just deselect all objects and select all created components.
        """
        UTIL_functions.select_certain_objects(tuple(self.__mObjList))

#endregion

#region Normal Component Adder

# element enum prop helper

def _get_component_icon_by_name(elename: str):
    icon: int | None = UTIL_icons_manager.get_component_icon(elename)
    if icon is None: return UTIL_icons_manager.get_empty_icon()
    else: return icon
_g_EnumHelper_Component = UTIL_functions.EnumPropHelper(
    PROP_ballance_element.BallanceElementType,
    lambda x: str(x.value),
    lambda x: PROP_ballance_element.BallanceElementType(int(x)),
    lambda x: x.name,
    lambda x: '',
    lambda x: _get_component_icon_by_name(PROP_ballance_element.get_ballance_element_name(x)),
)

class BBP_OT_add_component(bpy.types.Operator, ComponentSectorParam):
    """Add ordinary Component"""
    bl_idname = "bbp.add_component"
    bl_label = "Add Component"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_add_component'

    component_type: bpy.props.EnumProperty(
        name = "Type",
        description = "The type of this component.",
        items = _g_EnumHelper_Component.generate_items(),
        translation_context = 'BBP_OT_add_component/property'
    ) # type: ignore

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # show type
        layout.prop(self, "component_type")

        # only show sector for non-PE/PS component
        eletype = _g_EnumHelper_Component.get_selection(self.component_type)
        if eletype != PROP_ballance_element.BallanceElementType.PS_FourFlames and eletype != PROP_ballance_element.BallanceElementType.PE_Balloon:
            self.draw_component_sector_params(layout)

        # check for some special components and show warning
        elename: str | None = _check_component_existance(_g_EnumHelper_Component.get_selection(self.component_type), self.general_get_component_sector())
        if elename is not None:
            tr_text: str = bpy.app.translations.pgettext_iface(
                'Warning: {0} already exist.', 'BBP_OT_add_component/draw')
            layout.label(text=tr_text.format(elename), translate=False)

    def execute(self, context):
        # call general creator
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            _g_EnumHelper_Component.get_selection(self.component_type),
            self.general_get_component_sector(),
            1,  # only create one
            lambda _: mathutils.Matrix.Identity(4)
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        for item in PROP_ballance_element.BallanceElementType:
            item_name: str = PROP_ballance_element.get_ballance_element_name(item)

            cop = layout.operator(
                BBP_OT_add_component.bl_idname,
                text = item_name, text_ctxt = 'BBP_OT_add_component/property',
                icon_value = UTIL_icons_manager.get_component_icon(item_name),
            )
            cop.component_type = _g_EnumHelper_Component.to_selection(item)

#endregion

#region Nong Comp Adder

class BBP_OT_add_nong_extra_point(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Nong Extra Point"""
    bl_idname = "bbp.add_nong_extra_point"
    bl_label = "Nong Extra Point"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_nong_extra_point'

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)
        self.draw_component_count_params(layout)

    def execute(self, context):
        # create objects and rotate it by a certain degree calculated by its index
        # calc percent first
        percent: float = 1.0 / self.general_get_component_count()
        # create elements
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            PROP_ballance_element.BallanceElementType.P_Extra_Point,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Rotation(percent * i * math.pi * 2, 4, 'Z')
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_nong_extra_point.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Extra_Point)
            )
        )

class BBP_OT_add_nong_ventilator(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Nong Ventilator"""
    bl_idname = "bbp.add_nong_ventilator"
    bl_label = "Nong Ventilator"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_nong_ventilator'

    ventilator_count_source: bpy.props.EnumProperty(
        name = "Ventilator Count Source",
        items = [
            ('DEFINED', "Predefined", "Pre-defined ventilator count."),
            ('CUSTOM', "Custom", "User specified ventilator count."),
        ],
        translation_context = 'BBP_OT_add_nong_ventilator/property'
    ) # type: ignore
    
    preset_vetilator_count: bpy.props.EnumProperty(
        name = "Preset Count",
        description = "Pick preset ventilator count.",
        items = [
            # (token, display name, descriptions, icon, index)
            ('PAPER', 'Paper', 'The ventilator count (1) can push paper ball up.'),
            ('WOOD', 'Wood', 'The ventilator count (6) can push wood ball up.'),
            ('STONE', 'Stone', 'The ventilator count (32) can push stone ball up.'),
        ],
        translation_context = 'BBP_OT_add_nong_ventilator/property'
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        # draw sector settings
        self.draw_component_sector_params(layout)

        # draw count settings by different source
        layout.separator()
        layout.label(text='Count Source', text_ctxt='BBP_OT_add_nong_ventilator/draw')
        layout.prop(self, 'ventilator_count_source', expand = True)
        if (self.ventilator_count_source == 'CUSTOM'):
            self.draw_component_count_params(layout)
        else:
            layout.prop(self, 'preset_vetilator_count')
        
    def execute(self, context):
        # get ventilator count
        count: int = 0
        if (self.ventilator_count_source == 'CUSTOM'):
            count = self.general_get_component_count()
        else:
            match(self.preset_vetilator_count):
                case 'PAPER': count = 1
                case 'WOOD': count = 6
                case 'STONE': count = 32
                case _: raise UTIL_functions.BBPException('invalid enumprop data')
                
        # create elements without any move
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_18,
            self.general_get_component_sector(),
            count,
            lambda _: mathutils.Matrix.Identity(4)
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_nong_ventilator.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Modul_18)
            )
        )

#endregion

#region Series Comp Adder

class BBP_OT_add_tilting_block_series(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Tilting Block Series"""
    bl_idname = "bbp.add_tilting_block_series"
    bl_label = "Tilting Block Series"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_tilting_block_series'

    component_span: bpy.props.FloatProperty(
        name = "Span",
        description = "The distance between each titling blocks",
        min = 0.0, max = 100.0,
        soft_min = 0.0, soft_max = 12.0,
        default = 6.0022,
        translation_context = 'BBP_OT_add_tilting_block_series/property'
    ) # type: ignore

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
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_41,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Translation(mathutils.Vector((span * i, 0.0, 0.0)))  # move with extra delta in x axis
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_tilting_block_series.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Modul_41)
            )
        )

class BBP_OT_add_swing_series(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Swing Series"""
    bl_idname = "bbp.add_swing_series"
    bl_label = "Swing Series"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_swing_series'

    component_span: bpy.props.FloatProperty(
        name = "Span",
        description = "The distance between each swing",
        min = 0.0, max = 100.0,
        soft_min = 0.0, soft_max = 30.0,
        default = 15.0,
        translation_context = 'BBP_OT_add_swing_series/property'
    ) # type: ignore

    staggered_swing: bpy.props.BoolProperty(
        name = 'Staggered', 
        description = 'Whether place Swing staggered. Staggered Swing accept any ball however Non-Staggered Swing only accept Wood and Paper ball.',
        default = True,
        translation_context = 'BBP_OT_add_swing_series/property'
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        self.draw_component_sector_params(layout)
        self.draw_component_count_params(layout)
        layout.prop(self, 'component_span')
        layout.prop(self, 'staggered_swing')

    def execute(self, context):
        # create objects and move it by delta
        # get span first
        span: float = self.component_span
        staggered: bool = self.staggered_swing
        # create elements
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_08,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.LocRotScale(
                # move with extra delta in x axis
                mathutils.Vector((span * i, 0.0, 0.0)),
                # and rotate 90 degree for even one if staggered placement.
                mathutils.Euler((0, 0, math.radians(180) if (staggered and (i % 2 == 0)) else 0)),
                None
            )
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_swing_series.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.P_Modul_08)
            )
        )

class BBP_OT_add_ventilator_series(bpy.types.Operator, ComponentSectorParam, ComponentCountParam):
    """Add Ventilator Series"""
    bl_idname = "bbp.add_ventilator_series"
    bl_label = "Ventilator Series"
    bl_options = {'REGISTER', 'UNDO'}
    bl_translation_context = 'BBP_OT_add_ventilator_series'

    component_translation: bpy.props.FloatVectorProperty(
        name = "Delta Vector",
        description = "The translation between each ventilators. You can use this property to implement vertical or horizontal ventilator series. Set all factors to zero can get Nong ventilator.",
        size = 3, subtype = 'TRANSLATION',
        min = 0.0, max = 100.0,
        soft_min = 0.0, soft_max = 50.0,
        default = (0.0, 0.0, 15.0),
        translation_context = 'BBP_OT_add_ventilator_series/property'
    ) # type: ignore

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
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            PROP_ballance_element.BallanceElementType.P_Modul_18,
            self.general_get_component_sector(),
            self.general_get_component_count(),
            lambda i: mathutils.Matrix.Translation(i * translation)  # move with extra translation
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
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
    bl_translation_context = 'BBP_OT_add_sector_component_pair'

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

        # fetch warning string
        tr_text: str = bpy.app.translations.pgettext_iface(
            'Warning: {0} already exist.', 'BBP_OT_add_sector_component_pair/draw')

        # check checkpoint and resetpoint name conflict and show warnings
        (checkp_ty, checkp_sector) = self.__get_checkpoint()
        elename: str | None = _check_component_existance(checkp_ty, checkp_sector)
        if elename is not None:
            layout.label(text=tr_text.format(elename), translate=False)

        (resetp_ty, resetp_sector) = self.__get_resetpoint()
        elename = _check_component_existance(resetp_ty, resetp_sector)
        if elename is not None:
            layout.label(text=tr_text.format(elename), translate=False)

    def execute(self, context):
        # create checkpoint and resetpoint individually in element context
        # get type and sector data first
        (checkp_ty, checkp_sector) = self.__get_checkpoint()
        (resetp_ty, resetp_sector) = self.__get_resetpoint()
        # calc resetpoint offset and checkpoint rotation
        # resetpoint need a extra offset between checkpoint but it is different in FourFlams and TwoFlams.
        # 4 flames startpoint need a extra 90 degree rotation to correspond with ballance asset library (and the direction of resetpoint).
        resetp_offset: float
        checkp_degree: float
        if checkp_ty == PROP_ballance_element.BallanceElementType.PS_FourFlames:
            resetp_offset = 3.65
            checkp_degree = 90
        else:
            resetp_offset = 3.3258
            checkp_degree = 0

        # add elements
        # create checkpoint
        creator: _GeneralComponentCreator = _GeneralComponentCreator()
        creator.create_component(
            checkp_ty,
            checkp_sector,
            1,  # only create one
            lambda _: mathutils.Matrix.Rotation(math.radians(checkp_degree), 4, 'Z')
        )
        # create resetpoint
        creator.create_component(
            resetp_ty,
            resetp_sector,
            1,  # only create one
            lambda _: mathutils.Matrix.Translation(mathutils.Vector((0.0, 0.0, resetp_offset))) # apply resetpoint offset
        )
        creator.finish_component()
        return {'FINISHED'}

    @staticmethod
    def draw_blc_menu(layout: bpy.types.UILayout):
        layout.operator(
            BBP_OT_add_sector_component_pair.bl_idname,
            icon_value = UTIL_icons_manager.get_component_icon(
                PROP_ballance_element.get_ballance_element_name(PROP_ballance_element.BallanceElementType.PR_Resetpoint)
            )
        )

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_OT_add_component)
    bpy.utils.register_class(BBP_OT_add_nong_extra_point)
    bpy.utils.register_class(BBP_OT_add_nong_ventilator)
    bpy.utils.register_class(BBP_OT_add_tilting_block_series)
    bpy.utils.register_class(BBP_OT_add_swing_series)
    bpy.utils.register_class(BBP_OT_add_ventilator_series)
    bpy.utils.register_class(BBP_OT_add_sector_component_pair)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_add_sector_component_pair)
    bpy.utils.unregister_class(BBP_OT_add_ventilator_series)
    bpy.utils.unregister_class(BBP_OT_add_swing_series)
    bpy.utils.unregister_class(BBP_OT_add_tilting_block_series)
    bpy.utils.unregister_class(BBP_OT_add_nong_ventilator)
    bpy.utils.unregister_class(BBP_OT_add_nong_extra_point)
    bpy.utils.unregister_class(BBP_OT_add_component)
