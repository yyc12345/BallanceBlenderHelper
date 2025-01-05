import bpy
import typing, enum
from . import UTIL_functions, UTIL_icons_manager

#region Virtools Groups Define & Help Class

class BBP_PG_virtools_group(bpy.types.PropertyGroup):
    group_name: bpy.props.StringProperty(
        name = "Group Name",
        default = ""
    ) # type: ignore

def get_virtools_groups(obj: bpy.types.Object) -> bpy.types.CollectionProperty:
    return obj.virtools_groups

def get_active_virtools_groups(obj: bpy.types.Object) -> int:
    return obj.active_virtools_groups

def set_active_virtools_groups(obj: bpy.types.Object, val: int) -> None:
    obj.active_virtools_groups = val

class VirtoolsGroupsHelper():
    """
    A helper for object's Virtools groups adding, removal and checking.

    All Virtools group operations should be done by this class.
    Do NOT manipulate object's Virtools group properties directly.
    """
    __mSingletonMutex: typing.ClassVar[bool] = False
    __mIsValid: bool
    __mNoChange: bool ##< A bool indicate whether any change happended during lifetime. If no change, skip the writing when exiting.
    __mAssocObj: bpy.types.Object
    __mGroupsSet: set[str]
    
    def __init__(self, assoc: bpy.types.Object):
        self.__mGroupsSet = set()
        self.__mAssocObj = assoc
        self.__mNoChange = True
        
        # check singleton
        if VirtoolsGroupsHelper.__mSingletonMutex:
            self.__mIsValid = False
            raise UTIL_functions.BBPException('VirtoolsGroupsHelper is mutex.')
        
        # set validation and read ballance elements property
        VirtoolsGroupsHelper.__mSingletonMutex = True
        self.__mIsValid = True
        self.__read_from_virtools_groups()
    
    def is_valid(self) -> bool:
        return self.__mIsValid
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self) -> None:
        if self.is_valid():
            # if have changes,
            # write to ballance elements property and reset validation
            if not self.__mNoChange:
                self.__write_to_virtools_groups()
            self.__mIsValid = False
            VirtoolsGroupsHelper.__mSingletonMutex = False
    
    def __check_valid(self) -> None:
        if not self.is_valid():
            raise UTIL_functions.BBPException('calling invalid VirtoolsGroupsHelper')
    
    def add_group(self, gname: str) -> None:
        self.__check_valid()
        self.__mNoChange = False
        self.__mGroupsSet.add(gname)
    
    def add_groups(self, gnames: typing.Iterable[str]) -> None:
        self.__check_valid()
        self.__mNoChange = False
        self.__mGroupsSet.update(gnames)
    
    def remove_group(self, gname: str) -> None:
        self.__check_valid()
        self.__mNoChange = False
        self.__mGroupsSet.discard(gname)
    
    def remove_groups(self, gnames: typing.Iterable[str]) -> None:
        self.__check_valid()
        self.__mNoChange = False
        for gname in gnames:
            self.__mGroupsSet.discard(gname)
    
    def contain_group(self, gname: str) -> bool:
        self.__check_valid()
        return gname in self.__mGroupsSet
    
    def contain_groups(self, gnames: typing.Iterable[str]) -> bool:
        """
        Check existing intersection between group names and given collection.

        In other words, check whether group name of given paramter is in group names with OR operator.

        @param gnames[in] Iterable group names to check.
        @return return True if the length of the intersection between group names and given group names is not zero.
        """
        self.__check_valid()
        for gname in gnames:
            if gname in self.__mGroupsSet:
                return True
        return False
    
    def intersect_groups(self, gnames: set[str]) -> set[str]:
        self.__check_valid()
        return self.__mGroupsSet.intersection(gnames)
    
    def iterate_groups(self) -> typing.Iterator[str]:
        self.__check_valid()
        return iter(self.__mGroupsSet)

    def clear_groups(self) -> None:
        self.__check_valid()
        self.__mNoChange = False
        self.__mGroupsSet.clear()

    def get_count(self) -> int:
        self.__check_valid()
        return len(self.__mGroupsSet)
    
    def __write_to_virtools_groups(self) -> None:
        groups: bpy.types.CollectionProperty = get_virtools_groups(self.__mAssocObj)
        sel: int = get_active_virtools_groups(self.__mAssocObj)
        groups.clear()
        
        for gname in self.__mGroupsSet:
            item: BBP_PG_virtools_group = groups.add()
            item.group_name = gname
        
        # restore selection if necessary
        if sel >= len(self.__mGroupsSet):
            sel = len(self.__mGroupsSet) - 1
        if sel < 0:
            sel = 0
        set_active_virtools_groups(self.__mAssocObj, sel)
    
    def __read_from_virtools_groups(self) -> None:
        groups: bpy.types.CollectionProperty = get_virtools_groups(self.__mAssocObj)
        self.__mGroupsSet.clear()
        
        item: BBP_PG_virtools_group
        for item in groups:
            self.__mGroupsSet.add(item.group_name)

#endregion

#region Preset Group Names

class VirtoolsGroupsPreset(enum.Enum):
    Sector_01 = "Sector_01"
    Sector_02 = "Sector_02"
    Sector_03 = "Sector_03"
    Sector_04 = "Sector_04"
    Sector_05 = "Sector_05"
    Sector_06 = "Sector_06"
    Sector_07 = "Sector_07"
    Sector_08 = "Sector_08"
    
    P_Extra_Life = "P_Extra_Life"
    P_Extra_Point = "P_Extra_Point"
    P_Trafo_Paper = "P_Trafo_Paper"
    P_Trafo_Stone = "P_Trafo_Stone"
    P_Trafo_Wood = "P_Trafo_Wood"
    P_Ball_Paper = "P_Ball_Paper"
    P_Ball_Stone = "P_Ball_Stone"
    P_Ball_Wood = "P_Ball_Wood"
    P_Box = "P_Box"
    P_Dome = "P_Dome"
    P_Modul_01 = "P_Modul_01"
    P_Modul_03 = "P_Modul_03"
    P_Modul_08 = "P_Modul_08"
    P_Modul_17 = "P_Modul_17"
    P_Modul_18 = "P_Modul_18"
    P_Modul_19 = "P_Modul_19"
    P_Modul_25 = "P_Modul_25"
    P_Modul_26 = "P_Modul_26"
    P_Modul_29 = "P_Modul_29"
    P_Modul_30 = "P_Modul_30"
    P_Modul_34 = "P_Modul_34"
    P_Modul_37 = "P_Modul_37"
    P_Modul_41 = "P_Modul_41"
    
    PS_Levelstart = "PS_Levelstart"
    PE_Levelende = "PE_Levelende"
    PC_Checkpoints = "PC_Checkpoints"
    PR_Resetpoints = "PR_Resetpoints"
    
    Sound_HitID_01 = "Sound_HitID_01"
    Sound_RollID_01 = "Sound_RollID_01"
    Sound_HitID_02 = "Sound_HitID_02"
    Sound_RollID_02 = "Sound_RollID_02"
    Sound_HitID_03 = "Sound_HitID_03"
    Sound_RollID_03 = "Sound_RollID_03"
    
    DepthTestCubes = "DepthTestCubes"
    
    Phys_Floors = "Phys_Floors"
    Phys_FloorRails = "Phys_FloorRails"
    Phys_FloorStopper = "Phys_FloorStopper"
    
    Shadow = "Shadow"

_g_VtGrpPresetValues: tuple[str] = tuple(map(lambda x: x.value, VirtoolsGroupsPreset))

## Some of group names are not matched with icon name
#  So we create a convertion map to convert them.
_g_GroupIconNameConvMap: dict[str, str] = {
    "PS_Levelstart": "PS_FourFlames",
    "PE_Levelende": "PE_Balloon",
    "PC_Checkpoints": "PC_TwoFlames",
    "PR_Resetpoints": "PR_Resetpoint",

    "Sound_HitID_01": "SoundID_01",
    "Sound_RollID_01": "SoundID_01",
    "Sound_HitID_02": "SoundID_02",
    "Sound_RollID_02": "SoundID_02",
    "Sound_HitID_03": "SoundID_03",
    "Sound_RollID_03": "SoundID_03"
}
def _get_group_icon_by_name(gp_name: str) -> int:
    # try converting group name
    # if not found, return self
    gp_name = _g_GroupIconNameConvMap.get(gp_name, gp_name)
    
    # get from extra group icon first
    value: int | None = UTIL_icons_manager.get_group_icon(gp_name)
    if value is not None: return value

    # if failed, get from component. if still failed, return empty icon
    value = UTIL_icons_manager.get_component_icon(gp_name)
    if value is not None: return value
    else: return UTIL_icons_manager.get_empty_icon()
# blender group name prop helper
_g_EnumHelper_Group: UTIL_functions.EnumPropHelper = UTIL_functions.EnumPropHelper(
    VirtoolsGroupsPreset,
    lambda x: x.value,  # member is string self
    lambda x: VirtoolsGroupsPreset(x),   # convert directly because it is StrEnum.
    lambda x: x.value,
    lambda _: '',
    lambda x: _get_group_icon_by_name(x.value)
)

class SharedGroupNameInputProperties():
    group_name_source: bpy.props.EnumProperty(
        name = "Group Name Source",
        items = (
            ('DEFINED', "Predefined", "Pre-defined group name."),
            ('CUSTOM', "Custom", "User specified group name."),
        ),
    ) # type: ignore
    
    preset_group_name: bpy.props.EnumProperty(
        name = "Group Name",
        description = "Pick vanilla Ballance group name.",
        items = _g_EnumHelper_Group.generate_items(),
    ) # type: ignore
    
    custom_group_name: bpy.props.StringProperty(
        name = "Custom Group Name",
        description = "Input your custom group name.",
        default = "",
    ) # type: ignore
    
    def draw_group_name_input(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'group_name_source', expand = True)
        if (self.group_name_source == 'CUSTOM'):
            layout.prop(self, 'custom_group_name')
        else:
            layout.prop(self, 'preset_group_name')
    
    def general_get_group_name(self) -> str:
        if self.group_name_source == 'CUSTOM':
            return self.custom_group_name
        else:
            return _g_EnumHelper_Group.get_selection(self.preset_group_name).value

#endregion

#region Display Panel and Simple Operator

class BBP_UL_virtools_groups(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item: BBP_PG_virtools_group, icon, active_data, active_propname):
        layout.label(text = item.group_name, translate = False, icon_value = _get_group_icon_by_name(item.group_name))

class BBP_OT_add_virtools_group(bpy.types.Operator, SharedGroupNameInputProperties):
    """Add a Virtools Group for Active Object."""
    bl_idname = "bbp.add_virtools_groups"
    bl_label = "Add to Virtools Groups"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.object is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def execute(self, context):
        # add group
        with VirtoolsGroupsHelper(context.object) as hlp:
            hlp.add_group(self.general_get_group_name())
        return {'FINISHED'}
    
    def draw(self, context):
        self.draw_group_name_input(self.layout)

class BBP_OT_rm_virtools_group(bpy.types.Operator):
    """Remove a Virtools Group for Active Object."""
    bl_idname = "bbp.rm_virtools_groups"
    bl_label = "Remove from Virtools Groups"
    bl_options = {'UNDO'}
    
    ## This class is slightly unique.
    #  Because we need get user selected group name first.
    #  Then pass it to helper.
    
    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.object is None:
            return False
        
        obj = context.object
        gp = get_virtools_groups(obj)
        active_gp = get_active_virtools_groups(obj)
        return active_gp >= 0 and active_gp < len(gp)
    
    def execute(self, context):
        # get selected group name first
        obj = context.object
        item: BBP_PG_virtools_group = get_virtools_groups(obj)[get_active_virtools_groups(obj)]
        gname: str = item.group_name
        # then delete it
        with VirtoolsGroupsHelper(obj) as hlp:
            hlp.remove_group(gname)
        
        return {'FINISHED'}

class BBP_OT_clear_virtools_groups(bpy.types.Operator):
    """Clear All Virtools Group for Active Object."""
    bl_idname = "bbp.clear_virtools_groups"
    bl_label = "Clear Virtools Groups"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.object is not None
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)
    
    def execute(self, context):
        with VirtoolsGroupsHelper(context.object) as hlp:
            hlp.clear_groups()
        return {'FINISHED'}

class BBP_PT_virtools_groups(bpy.types.Panel):
    """Show Virtools Groups Properties."""
    bl_label = "Virtools Groups"
    bl_idname = "BBP_PT_virtools_groups"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def draw(self, context):
        layout = self.layout
        target = typing.cast(bpy.types.Object, context.active_object)

        # notify on non-mesh object
        if target.type != 'MESH':
            layout.label(text = 'Virtools Group is invalid on non-mesh object!', icon = 'ERROR')

        # draw main body
        
        row = layout.row()
        row.template_list(
            "BBP_UL_virtools_groups", "", 
            target, "virtools_groups",
            target, "active_virtools_groups",
            rows = 6,
            maxrows = 6,
        )
        
        col = row.column(align=True)
        col.operator(BBP_OT_add_virtools_group.bl_idname, icon='ADD', text="")
        col.operator(BBP_OT_rm_virtools_group.bl_idname, icon='REMOVE', text="")
        col.separator()
        col.operator(BBP_OT_clear_virtools_groups.bl_idname, icon='TRASH', text="")

#endregion

def register() -> None:
    # register all classes
    bpy.utils.register_class(BBP_PG_virtools_group)
    bpy.utils.register_class(BBP_UL_virtools_groups)
    bpy.utils.register_class(BBP_OT_add_virtools_group)
    bpy.utils.register_class(BBP_OT_rm_virtools_group)
    bpy.utils.register_class(BBP_OT_clear_virtools_groups)
    bpy.utils.register_class(BBP_PT_virtools_groups)
    
    # add into object metadata
    bpy.types.Object.virtools_groups = bpy.props.CollectionProperty(type = BBP_PG_virtools_group)
    bpy.types.Object.active_virtools_groups = bpy.props.IntProperty()

def unregister() -> None:
    # del from object metadata
    del bpy.types.Object.active_virtools_groups
    del bpy.types.Object.virtools_groups
    
    bpy.utils.unregister_class(BBP_PT_virtools_groups)
    bpy.utils.unregister_class(BBP_OT_clear_virtools_groups)
    bpy.utils.unregister_class(BBP_OT_rm_virtools_group)
    bpy.utils.unregister_class(BBP_OT_add_virtools_group)
    bpy.utils.unregister_class(BBP_UL_virtools_groups)
    bpy.utils.unregister_class(BBP_PG_virtools_group)
