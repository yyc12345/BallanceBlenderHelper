import bpy
import typing, enum, re
from . import UTIL_functions, UTIL_icons_manager
from . import PROP_virtools_group

#region Rename Error Reporter

class _RenameErrorType(enum.IntEnum):
    ERROR = enum.auto()
    WARNING = enum.auto()
    INFO = enum.auto()

class _RenameErrorItem():
    mErrType: _RenameErrorType
    mDescription: str

    def __init__(self, err_t: _RenameErrorType, description: str):
        self.mErrType = err_t
        self.mDescription = description

class _RenameErrorReporter():
    mErrList: list[_RenameErrorItem]
    mOldName: str

    def __init__(self):
        self.mErrList = []
        self.mOldName = ""

    def add_error(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.ERROR, description))
    def add_warning(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.WARNING, description))
    def add_info(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.INFO, description))

    def begin_object(self, obj: bpy.types.Object) -> None:
        # assign old name
        self.mOldName = obj.name
    def end_object(self, obj:bpy.types.Object) -> None:
        # if error list is empty, no need to report
        if len(self.mErrList) == 0: return

        # output header
        # if new name is different with old name, output both of them
        new_name: str = obj.name
        if self.mOldName == new_name:
            print(f'For object "{new_name}"')
        else:
            print(f'For object "{new_name}" (Old name: "{self.mOldName}")')

        # output error list with indent
        for item in self.mErrList:
            print('\t' + _RenameErrorReporter.__erritem_to_string(item))

        # clear error list for next object
        self.mErrList.clear()

    @staticmethod
    def __errtype_to_string(err_v: _RenameErrorType) -> str:
        match(err_v):
            case _RenameErrorType.ERROR: return 'ERROR'
            case _RenameErrorType.WARNING: return 'WARN'
            case _RenameErrorType.INFO: return 'INFO'
            case _: raise UTIL_functions.BBPException("Unknown error type.")
    @staticmethod
    def __erritem_to_string(item: _RenameErrorItem) -> str:
        return f'[{_RenameErrorReporter.__errtype_to_string(item.mErrType)}]\t{item.mDescription}'

#endregion

#region Naming Convention Used Types

class BallanceObjectType(enum.IntEnum):
    COMPONENT = enum.auto()

    FLOOR = enum.auto()
    RAIL = enum.auto()
    WOOD = enum.auto()
    STOPPER = enum.auto()

    LEVEL_START = enum.auto()
    LEVEL_END = enum.auto()
    CHECKPOINT = enum.auto()
    RESETPOINT = enum.auto()

    DEPTH_CUBE = enum.auto()
    SKYLAYER = enum.auto()

    DECORATION = enum.auto()

class BallanceObjectInfo():
    mBasicType: BallanceObjectType

    ## Only available for COMPONENT basic type
    mComponentType: str | None
    ## Only available for COMPONENT, CHECKPOINT, RESETPOINT basic type
    #  For COMPONENT, it indicate which sector this component belong to.
    #  For CHECKPOINT, RESETPOINT, it indicate the index of this object.
    #  In CHECKPOINT, RESETPOINT mode, the sector actually is the suffix number of these objects' name. So checkpoint starts with 1, not 0.
    mSector: int | None

    def __init__(self, basic_type: BallanceObjectType):
        self.mBasicType = basic_type

    @classmethod
    def create_from_component(cls, comp_type: str, sector: int):
        inst = cls(BallanceObjectType.COMPONENT)
        inst.mComponentType = comp_type
        inst.mSector = sector
        return inst
    
    @classmethod
    def create_from_checkpoint(cls, sector: int):
        inst = cls(BallanceObjectType.CHECKPOINT)
        inst.mSector = sector
        return inst
    @classmethod
    def create_from_resetpoint(cls, sector: int):
        inst = cls(BallanceObjectType.RESETPOINT)
        inst.mSector = sector
        return inst

    @classmethod
    def create_from_others(cls, basic_type: BallanceObjectType):
        return cls(basic_type)

class _NamingConventionProfile():
    _TParseFct = typing.Callable[[bpy.types.Object, _RenameErrorReporter | None], BallanceObjectInfo | None]
    _TSetFct = typing.Callable[[bpy.types.Object,BallanceObjectInfo, _RenameErrorReporter | None], bool]

    mName: str
    mDesc: str
    mParseFct: _TParseFct
    mSetFct: _TSetFct

    def __init__(self, name: str, desc: str, parse_fct: _TParseFct, set_fct: _TSetFct):
        self.mName = name
        self.mDesc = desc
        self.mParseFct = parse_fct
        self.mSetFct = set_fct

#endregion

#region Naming Convention Declaration

_g_BlcNormalComponents: set[str] = set((
    PROP_virtools_group.VirtoolsGroupsPreset.P_Extra_Life.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Extra_Point.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Trafo_Paper.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Trafo_Stone.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Trafo_Wood.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Ball_Paper.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Ball_Stone.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Ball_Wood.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Box.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Dome.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_01.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_03.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_08.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_17.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_18.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_19.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_25.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_26.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_29.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_30.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_34.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_37.value,
    PROP_virtools_group.VirtoolsGroupsPreset.P_Modul_41.value,
))
_g_BlcUniqueComponents: set[str] = set((
    PROP_virtools_group.VirtoolsGroupsPreset.PS_Levelstart.value,
    PROP_virtools_group.VirtoolsGroupsPreset.PE_Levelende.value,
    PROP_virtools_group.VirtoolsGroupsPreset.PC_Checkpoints.value,
    PROP_virtools_group.VirtoolsGroupsPreset.PR_Resetpoints.value,
))
_g_BlcFloor: set[str] = set((
    PROP_virtools_group.VirtoolsGroupsPreset.Sound_HitID_01.value,
    PROP_virtools_group.VirtoolsGroupsPreset.Sound_RollID_01.value,
))
_g_BlcWood: set[str] = set((
    PROP_virtools_group.VirtoolsGroupsPreset.Sound_HitID_02.value,
    PROP_virtools_group.VirtoolsGroupsPreset.Sound_RollID_02.value,
))

class _VirtoolsGroupConvention():
    cRegexGroupSector: typing.ClassVar[re.Pattern] = re.compile('^Sector_(0[1-8]|[1-9][0-9]{1,2}|9)$')
    cRegexComponent: typing.ClassVar[re.Pattern] = re.compile('^(' + '|'.join(_g_BlcNormalComponents) + ')_(0[1-9]|[1-9][0-9])_.*$')
    cRegexPC: typing.ClassVar[re.Pattern] = re.compile('^PC_TwoFlames_(0[1-7])$')
    cRegexPR: typing.ClassVar[re.Pattern] = re.compile('^PR_Resetpoint_(0[1-8])$')

    @staticmethod
    def __get_pcpr_from_name(name: str, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        regex_result = _VirtoolsGroupConvention.cRegexPC.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = _VirtoolsGroupConvention.cRegexPR.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_resetpoint(
                int(regex_result.group(1))
            )
        
        if reporter: reporter.add_error("PC_Checkpoints or PR_Resetpoints detected. But couldn't get sector from name.")
        return None
    
    @staticmethod
    def __get_sector_from_groups(gps: typing.Iterator[str]) -> int | None:
        # this counter is served for stupid 
        # multi-sector-grouping accident.
        counter: int = 0
        last_matched_sector: int = 0
        for i in gps:
            regex_result = _VirtoolsGroupConvention.cRegexGroupSector.match(i)
            if regex_result is not None:
                last_matched_sector = int(regex_result.group(1))
                counter += 1
                
        if counter != 1: return None
        else: return last_matched_sector


    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        # create visitor
        with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
            # if no group, we should consider it is decoration or skylayer
            if gp.get_count() == 0:
                if obj.name == 'SkyLayer': return BallanceObjectInfo.create_from_others(BallanceObjectType.SKYLAYER)
                else: return BallanceObjectInfo.create_from_others(BallanceObjectType.DECORATION)

            # try to filter unique elements first
            inter_gps: set[str] = gp.intersect_groups(_g_BlcUniqueComponents)
            if len(inter_gps) == 1:
                # get it
                match((tuple(inter_gps))[0]):
                    case PROP_virtools_group.VirtoolsGroupsPreset.PS_Levelstart.value:
                        return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
                    case PROP_virtools_group.VirtoolsGroupsPreset.PE_Levelende.value:
                        return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)
                    case PROP_virtools_group.VirtoolsGroupsPreset.PC_Checkpoints.value | PROP_virtools_group.VirtoolsGroupsPreset.PR_Resetpoints.value:
                        # these type's data should be gotten from its name
                        return _VirtoolsGroupConvention.__get_pcpr_from_name(obj.name, reporter)
                    case _:
                        if reporter: reporter.add_error("The match of Unique Component lost.")
                        return None
            elif len(inter_gps) != 0:
                if reporter: reporter.add_error("A Multi-grouping Unique Component.")
                return None
            
            # distinguish normal elements
            inter_gps = gp.intersect_groups(_g_BlcNormalComponents)
            if len(inter_gps) == 1:
                # get it
                # now try get its sector
                gotten_elements: str = (tuple(inter_gps))[0]
                gotten_sector: int | None = _VirtoolsGroupConvention.__get_sector_from_groups(gp.iterate_groups())
                if gotten_sector is None:
                    # fail to get sector
                    if reporter: reporter.add_error("Component detected. But couldn't get sector from CKGroup data.")
                    return None
                return BallanceObjectInfo.create_from_component(
                    gotten_elements,
                    gotten_sector
                )
            elif len(inter_gps) != 0:
                # must be a weird grouping, report it
                if reporter: reporter.add_error("A Multi-grouping Component.")
                return None

            # distinguish road
            if gp.contain_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_FloorRails.value):
                # rail
                return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
            elif gp.contain_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_Floors.value):
                # distinguish it between Floor and Wood
                floor_result = gp.intersect_groups(_g_BlcFloor)
                rail_result = gp.intersect_groups(_g_BlcWood)
                if len(floor_result) > 0 and len(rail_result) == 0:
                    return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
                elif len(floor_result) == 0 and len(rail_result) > 0:
                    return BallanceObjectInfo.create_from_others(BallanceObjectType.WOOD)
                else:
                    if reporter: reporter.add_warning("Can't distinguish object between Floors and Rails. Suppose it is Floors.")
                    return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
            elif gp.contain_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_FloorStopper.value):
                return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)
            elif gp.contain_group(PROP_virtools_group.VirtoolsGroupsPreset.DepthTestCubes.value):
                return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)

            # no matched
            if reporter: reporter.add_error("Group match lost.")
            return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        # create visitor
        with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
            # match by basic type
            match(info.mBasicType):
                case BallanceObjectType.DECORATION: pass    # decoration do not need group
                case BallanceObjectType.SKYLAYER: pass  # sky layer do not need group
                
                case BallanceObjectType.LEVEL_START:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.PS_Levelstart.value)
                case BallanceObjectType.LEVEL_END:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.PE_Levelende.value)
                case BallanceObjectType.CHECKPOINT:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.PC_Checkpoints.value)
                case BallanceObjectType.RESETPOINT:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.PR_Resetpoints.value)

                case BallanceObjectType.DEPTH_CUBE:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.PE_Levelende.value)

                case BallanceObjectType.FLOOR:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_Floors.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_HitID_01.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_RollID_01.value)
                case BallanceObjectType.RAIL:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_FloorRails.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_HitID_02.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_RollID_02.value)
                case BallanceObjectType.WOOD:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_Floors.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_HitID_03.value)
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Sound_RollID_03.value)
                case BallanceObjectType.STOPPER:
                    gp.add_group(PROP_virtools_group.VirtoolsGroupsPreset.Phys_FloorStopper.value)

                case BallanceObjectType.COMPONENT:
                    # group into component type
                    gp.add_group(info.mComponentType)

                    # group to sector
                    if info.mSector == 9:
                        gp.add_group('Sector_9')
                    else:
                        gp.add_group(f'Sector_{info.mSector:0>2d}')

                case _:
                    if reporter is not None:
                        reporter.add_error('No matched info.')
                    return False
                
        return True

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            'Virtools Group',
            'Virtools Group',
            _VirtoolsGroupConvention.parse_from_object,
            _VirtoolsGroupConvention.set_to_object
        )

class _YYCToolchainConvention():
    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        # check component first
        regex_result = _VirtoolsGroupConvention.cRegexComponent.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_component(
                regex_result.group(1),
                int(regex_result.group(2))
            )

        # check PC PR elements
        regex_result = _VirtoolsGroupConvention.cRegexPC.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = _VirtoolsGroupConvention.cRegexPR.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_resetpoint(
                int(regex_result.group(1))
            )

        # check other unique elements
        if obj.name == "PS_FourFlames_01":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
        if obj.name == "PE_Balloon_01":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)

        # process floors
        if obj.name.startswith("A_Floor"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
        if obj.name.startswith("A_Rail"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
        if obj.name.startswith("A_Wood"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.WOOD)
        if obj.name.startswith("A_Stopper"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)

        # process others
        if obj.name.startswith("DepthCubes"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)
        if obj.name.startswith("D_"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DECORATION)
        if obj.name == 'SkyLayer':
            return BallanceObjectInfo.create_from_others(BallanceObjectType.SKYLAYER)

        if reporter is not None:
            reporter.add_error("Name match lost.")
        return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        match(info.mBasicType):
            case BallanceObjectType.DECORATION:
                obj.name = 'D_'
            case BallanceObjectType.SKYLAYER:
                obj.name = 'SkyLayer'
            
            case BallanceObjectType.LEVEL_START:
                obj.name = 'PS_FourFlames_01'
            case BallanceObjectType.LEVEL_END:
                obj.name = 'PE_Balloon_01'
            case BallanceObjectType.CHECKPOINT:
                obj.name = f'PR_Resetpoint_{info.mSector:0>2d}'
            case BallanceObjectType.RESETPOINT:
                obj.name = f'PC_TwoFlames_{info.mSector:0>2d}'

            case BallanceObjectType.DEPTH_CUBE:
                obj.name = 'DepthCubes_'

            case BallanceObjectType.FLOOR:
                obj.name = 'A_Floor_'
            case BallanceObjectType.RAIL:
                obj.name = 'A_Wood_'
            case BallanceObjectType.WOOD:
                obj.name = 'A_Rail_'
            case BallanceObjectType.STOPPER:
                obj.name = 'A_Stopper_'

            case BallanceObjectType.COMPONENT:
                obj.name = '{}_{:0>2d}_'.format(
                    info.mComponentType, info.mSector)
                
            case _:
                if reporter is not None:
                    reporter.add_error('No matched info.')
                return False
            
        return True

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            'YYC Toolchain',
            'YYC Toolchain name standard.',
            _YYCToolchainConvention.parse_from_object,
            _YYCToolchainConvention.set_to_object
        )

class _ImengyuConvention():
    cRegexComponent: typing.ClassVar[re.Pattern] = re.compile('^(' + '|'.join(_g_BlcNormalComponents) + '):[^:]*:([1-9]|[1-9][0-9])$')
    cRegexPC: typing.ClassVar[re.Pattern] = re.compile('^PC_CheckPoint:([0-9]+)$')
    cRegexPR: typing.ClassVar[re.Pattern] = re.compile('^PR_ResetPoint:([0-9]+)$')

    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        # check component first
        regex_result = _ImengyuConvention.cRegexComponent.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_component(
                regex_result.group(1),
                int(regex_result.group(2))
            )

        # check PC PR elements
        regex_result = _ImengyuConvention.cRegexPC.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = _ImengyuConvention.cRegexPR.match(obj.name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_resetpoint(
                int(regex_result.group(1))
            )

        # check other unique elements
        if obj.name == "PS_LevelStart":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
        if obj.name == "PE_LevelEnd":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)

        # process floors
        if obj.name.startswith("S_Floors"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
        if obj.name.startswith("S_FloorRails"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
        if obj.name.startswith("S_FloorWoods"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.WOOD)
        if obj.name.startswith("S_FloorStopper"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)

        # process others
        if obj.name.startswith("DepthTestCubes"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)
        if obj.name.startswith("O_"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DECORATION)
        if obj.name == 'SkyLayer':
            return BallanceObjectInfo.create_from_others(BallanceObjectType.SKYLAYER)

        if reporter is not None:
            reporter.add_error("Name match lost.")
        return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        match(info.mBasicType):
            case BallanceObjectType.DECORATION:
                obj.name = 'O_'
            case BallanceObjectType.SKYLAYER:
                obj.name = 'SkyLayer'
            
            case BallanceObjectType.LEVEL_START:
                obj.name = 'PS_LevelStart'
            case BallanceObjectType.LEVEL_END:
                obj.name = 'PE_LevelEnd'
            case BallanceObjectType.CHECKPOINT:
                obj.name = f'PR_ResetPoint:{info.mSector:d}'
            case BallanceObjectType.RESETPOINT:
                obj.name = f'PC_CheckPoint:{info.mSector:d}'

            case BallanceObjectType.DEPTH_CUBE:
                obj.name = 'DepthTestCubes'

            case BallanceObjectType.FLOOR:
                obj.name = 'S_Floors'
            case BallanceObjectType.RAIL:
                obj.name = 'S_FloorWoods'
            case BallanceObjectType.WOOD:
                obj.name = 'S_FloorRails'
            case BallanceObjectType.STOPPER:
                obj.name = 'S_FloorStopper'

            case BallanceObjectType.COMPONENT:
                obj.name = '{}:{}:{:d}'.format(
                    info.mComponentType, obj.name.replace(':', '_'), info.mSector)
                
            case _:
                if reporter is not None:
                    reporter.add_error('No matched info.')
                return False
            
        return True

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            'Imengyu Ballance',
            'Auto grouping name standard for Imengyu/Ballance.',
            _ImengyuConvention.parse_from_object,
            _ImengyuConvention.set_to_object
        )

#endregion

#region Naming Convention Register

## All available naming conventions
#  Each naming convention should have a identifier for visiting them.
#  The identifier is its index in this tuple.
_g_NamingConventions: list[_NamingConventionProfile] = []
def _register_naming_convention_with_index(profile: _NamingConventionProfile) -> int:
    global _g_NamingConventions
    ret: int = len(_g_NamingConventions)
    _g_NamingConventions.append(profile)
    return ret

# register and assign to a enum
class NamingConvention(enum.IntEnum):
    VirtoolsGroup = _register_naming_convention_with_index(_VirtoolsGroupConvention.register())
    YYCToolchain = _register_naming_convention_with_index(_YYCToolchainConvention.register())
    Imengyu = _register_naming_convention_with_index(_ImengyuConvention.register())

class _EnumPropHelper():
    """
    Operate like UTIL_virtools_types.EnumPropHelper
    Return the identifier (index) of naming convention.
    """

    @staticmethod
    def generate_items() -> tuple[tuple, ...]:
        # create a function to filter Virtools Group profile 
        # and return index at the same time
        def naming_convention_iter() -> typing.Iterator[tuple[int, _NamingConventionProfile]]:
            for item in NamingConvention:
                if item != NamingConvention.VirtoolsGroup:
                    yield (item.value, _g_NamingConventions[item.value])

        # token, display name, descriptions, icon, index
        return tuple(
            (
                str(idx), 
                item.mName, 
                item.mDesc, 
                "", 
                idx
            ) for idx, item in naming_convention_iter()
        )
    
    @staticmethod
    def get_selection(prop: str) -> NamingConvention:
        return NamingConvention(int(prop))
    
    @staticmethod
    def to_selection(val: NamingConvention) -> str:
        return str(val.value)
    
    @staticmethod
    def get_virtools_group_identifier() -> NamingConvention:
        # The native naming convention is Virtools Group
        # We treat it as naming convention because we want use a universal interface to process naming converting.
        # So Virtools Group can no be seen as a naming convention, but we treat it like naming convention in code.
        return NamingConvention.VirtoolsGroup
    
    @staticmethod
    def get_default_naming_identifier() -> NamingConvention:
        # The default fallback naming convention is YYC toolchain
        return NamingConvention.YYCToolchain

#endregion

def name_setter_core(ident: NamingConvention, info: BallanceObjectInfo, obj: bpy.types.Object) -> None:
    # get profile
    profile: _NamingConventionProfile = _g_NamingConventions[ident.value]
    # set name. don't care whether success.
    profile.mSetFct(obj, info, None)

def name_converting_core(src_ident: NamingConvention, dst_ident: NamingConvention, objs: typing.Iterable[bpy.types.Object]) -> None:
    # no convert needed
    if src_ident == dst_ident: return

    # get convert profile
    src: _NamingConventionProfile = _g_NamingConventions[src_ident.value]
    dst: _NamingConventionProfile = _g_NamingConventions[dst_ident.value]

    # create reporter and success counter
    failed_obj_counter: int = 0
    all_obj_counter: int = 0
    err_reporter: _RenameErrorReporter = _RenameErrorReporter()

    # print console report header
    print('============')
    print('Rename Report')
    print('------------')

    # start converting
    for obj in objs:
        # inc counter all
        all_obj_counter += 1
        # begin object processing
        err_reporter.begin_object(obj)
        # parsing from src and set by dst
        # inc failed counter if failed
        obj_info: BallanceObjectInfo | None= src.mParseFct(obj, err_reporter)
        if obj_info is not None:
            ret: bool = dst.mSetFct(obj, obj_info, err_reporter)
            if not ret: failed_obj_counter += 1
        else:
            failed_obj_counter += 1
        # end object processing and output err list
        err_reporter.end_object(obj)

    # print console report tail
    print('------------')
    print(f'All / Failed - {all_obj_counter} / {failed_obj_counter}')
    print('============')

    # popup blender window to notice user
    UTIL_functions.message_box(
        (
            'View console to get more detail.',
            f'All: {all_obj_counter}',
            f'Failed: {failed_obj_counter}',
        ),
        "Rename Report", 
        UTIL_icons_manager.BlenderPresetIcons.Info.value
    )
