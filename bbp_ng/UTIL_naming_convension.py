import bpy
import typing, enum, re
from . import UTIL_functions
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

class RenameErrorReporter():
    """
    A basic 'rename error report' using simple prints in console.

    This object can be used as a context manager.

    It supports multiple levels of 'substeps' - you shall always enter at least one substep (because level 0
    has only one single step, representing the whole 'area' of the progress stuff).

    You should give the object renaming of substeps each time you enter a new one.

    Leaving a substep automatically steps by one the parent level.

    ```
    with RenameErrorReporter() as reporter:
        progress.enter_object(obj)

        # process for object with reporter
        reporter.add_error('fork!')

        progress.leave_object()
    ```
    """
    mAllObjCounter: int
    mFailedObjCounter: int

    mErrList: list[_RenameErrorItem]
    mOldName: str
    mHasError: bool

    def __init__(self):
        self.mAllObjCounter = 0
        self.mFailedObjCounter = 0
        
        self.mErrList = []
        self.mOldName = ""
        self.mHasError = False

    def add_error(self, description: str):
        self.mHasError = True
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.ERROR, description))
    def add_warning(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.WARNING, description))
    def add_info(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.INFO, description))

    def get_all_objs_count(self) -> int: return self.mAllObjCounter
    def get_failed_objs_count(self) -> int: return self.mFailedObjCounter

    def __enter__(self):
        # print console report header
        print('============')
        print('Rename Report')
        print('------------')
        # return self as context
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # print console report tail
        print('------------')
        print(f'All / Failed - {self.mAllObjCounter} / {self.mFailedObjCounter}')
        print('============')
        # reset variables
        self.mAllObjCounter = 0
        self.mFailedObjCounter = 0
    
    def enter_object(self, obj: bpy.types.Object) -> None:
        # inc all counter
        self.mAllObjCounter += 1
        # assign old name
        self.mOldName = obj.name
    def leave_object(self, obj:bpy.types.Object) -> None:
        # if error list is empty, no need to report
        if len(self.mErrList) == 0: return

        # inc failed if necessary
        if self.mHasError:
            self.mFailedObjCounter += 1

        # output header
        # if new name is different with old name, output both of them
        new_name: str = obj.name
        if self.mOldName == new_name:
            print(f'For object "{new_name}"')
        else:
            print(f'For object "{new_name}" (Old name: "{self.mOldName}")')

        # output error list with indent
        for item in self.mErrList:
            print('\t' + RenameErrorReporter.__erritem_to_string(item))

        # clear error list for next object
        self.mErrList.clear()
        self.mHasError = False

    @staticmethod
    def __errtype_to_string(err_v: _RenameErrorType) -> str:
        match(err_v):
            case _RenameErrorType.ERROR: return 'ERROR'
            case _RenameErrorType.WARNING: return 'WARN'
            case _RenameErrorType.INFO: return 'INFO'
            case _: raise UTIL_functions.BBPException("Unknown error type.")
    @staticmethod
    def __erritem_to_string(item: _RenameErrorItem) -> str:
        return f'[{RenameErrorReporter.__errtype_to_string(item.mErrType)}]\t{item.mDescription}'

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

#endregion

#region Sector Extractor

_g_RegexBlcSectorGroup: re.Pattern = re.compile('^Sector_(0[1-8]|[1-9][0-9]{1,2}|9)$')

def extract_sector_from_name(group_name: str) -> int | None:
    """
    A convenient function to extract sector index from given group name.
    This function also supports 999 sector plugin.

    Not only in this module, but also in outside modules, this function is vary used to extract sector index info.

    Function return the index extracted, or None if given group name is not a valid sector group.
    The valid sector index is range from 1 to 999 (inclusive)
    """
    regex_result = _g_RegexBlcSectorGroup.match(group_name)
    if regex_result is not None:
        return int(regex_result.group(1))
    else:
        return None

def build_name_from_sector_index(sector_index: int) -> str:
    """
    A convenient function to build Ballance recognizable sector group name.
    This function also supports 999 sector plugin.

    This function also is used in this module or other modules outside.
    
    Function return a sector name string. It basically the reverse operation of `extract_sector_from_name`.
    """
    if sector_index == 9:
        return 'Sector_9'
    else:
        return f'Sector_{sector_index:0>2d}'

#endregion

#region Naming Convention Declaration

_g_BlcNormalComponents: set[str] = set((
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
    "P_Modul_41"
))
_g_BlcUniqueComponents: set[str] = set((
    "PS_Levelstart",
    "PE_Levelende",
    "PC_Checkpoints",
    "PR_Resetpoints"
))
_g_BlcFloor: set[str] = set((
    "Sound_HitID_01",
    "Sound_RollID_01"
))
_g_BlcWood: set[str] = set((
    "Sound_HitID_02",
    "Sound_RollID_02"
))

class VirtoolsGroupConvention():
    cRegexComponent: typing.ClassVar[re.Pattern] = re.compile('^(' + '|'.join(_g_BlcNormalComponents) + ')_(0[1-9]|[1-9][0-9])_.*$')
    cRegexPC: typing.ClassVar[re.Pattern] = re.compile('^PC_TwoFlames_(0[1-7])$')
    cRegexPR: typing.ClassVar[re.Pattern] = re.compile('^PR_Resetpoint_(0[1-8])$')

    @staticmethod
    def __get_pcpr_from_name(name: str, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
        regex_result = VirtoolsGroupConvention.cRegexPC.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = VirtoolsGroupConvention.cRegexPR.match(name)
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
            regex_result: int | None = extract_sector_from_name(i)
            if regex_result is not None:
                last_matched_sector = regex_result
                counter += 1
                
        if counter != 1: return None
        else: return last_matched_sector

    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
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
                    case 'PS_Levelstart':
                        return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
                    case 'PE_Levelende':
                        return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)
                    case 'PC_Checkpoints' | 'PR_Resetpoints':
                        # these type's data should be gotten from its name
                        return VirtoolsGroupConvention.__get_pcpr_from_name(obj.name, reporter)
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
                gotten_sector: int | None = VirtoolsGroupConvention.__get_sector_from_groups(gp.iterate_groups())
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
            if gp.contain_group('Phys_FloorRails'):
                # rail
                return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
            elif gp.contain_group('Phys_Floors'):
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
            elif gp.contain_group('Phys_FloorStopper'):
                return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)
            elif gp.contain_group('DepthTestCubes'):
                return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)

            # no matched
            if reporter: reporter.add_error("Group match lost.")
            return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: RenameErrorReporter | None) -> bool:
        # create visitor
        with PROP_virtools_group.VirtoolsGroupsHelper(obj) as gp:
            # match by basic type
            match(info.mBasicType):
                case BallanceObjectType.DECORATION: pass    # decoration do not need group
                case BallanceObjectType.SKYLAYER: pass  # sky layer do not need group
                
                case BallanceObjectType.LEVEL_START:
                    gp.add_group('PS_Levelstart')
                case BallanceObjectType.LEVEL_END:
                    gp.add_group('PE_Levelende')
                case BallanceObjectType.CHECKPOINT:
                    gp.add_group('PC_Checkpoints')
                case BallanceObjectType.RESETPOINT:
                    gp.add_group('PR_Resetpoints')

                case BallanceObjectType.DEPTH_CUBE:
                    gp.add_group('PE_Levelende')

                case BallanceObjectType.FLOOR:
                    gp.add_group('Phys_Floors')
                    gp.add_group('Sound_HitID_01')
                    gp.add_group('Sound_RollID_01')
                    # floor type also need group into shadow group.
                    gp.add_group('Shadow')
                case BallanceObjectType.RAIL:
                    gp.add_group('Phys_FloorRails')
                    gp.add_group('Sound_HitID_03')
                    gp.add_group('Sound_RollID_03')
                case BallanceObjectType.WOOD:
                    gp.add_group('Phys_Floors')
                    gp.add_group('Sound_HitID_02')
                    gp.add_group('Sound_RollID_02')
                case BallanceObjectType.STOPPER:
                    gp.add_group('Phys_FloorStopper')

                case BallanceObjectType.COMPONENT:
                    # group into component type
                    # use typing.cast() to force linter accept it because None is impossible
                    gp.add_group(typing.cast(str, info.mComponentType))
                    # group to sector
                    gp.add_group(build_name_from_sector_index(typing.cast(int, info.mSector)))

                case _:
                    if reporter is not None:
                        reporter.add_error('No matched info.')
                    return False
                
        return True

class YYCToolchainConvention():
    @staticmethod
    def parse_from_name(name: str, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
        # check component first
        regex_result = VirtoolsGroupConvention.cRegexComponent.match(name)  # use vt one because they are same
        if regex_result is not None:
            return BallanceObjectInfo.create_from_component(
                regex_result.group(1),
                int(regex_result.group(2))
            )

        # check PC PR elements
        regex_result = VirtoolsGroupConvention.cRegexPC.match(name) # use vt one because they are same
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = VirtoolsGroupConvention.cRegexPR.match(name) # use vt one because they are same
        if regex_result is not None:
            return BallanceObjectInfo.create_from_resetpoint(
                int(regex_result.group(1))
            )

        # check other unique elements
        if name == "PS_FourFlames_01":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
        if name == "PE_Balloon_01":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)

        # process floors
        if name.startswith("A_Floor"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
        if name.startswith("A_Rail"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
        if name.startswith("A_Wood"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.WOOD)
        if name.startswith("A_Stopper"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)

        # process others
        if name.startswith("DepthCubes"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)
        if name.startswith("D_"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DECORATION)
        if name == 'SkyLayer':
            return BallanceObjectInfo.create_from_others(BallanceObjectType.SKYLAYER)

        if reporter is not None:
            reporter.add_error("Name match lost.")
        return None


    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
        return YYCToolchainConvention.parse_from_name(obj.name, reporter)
        
    @staticmethod
    def set_to_name(info: BallanceObjectInfo, reporter: RenameErrorReporter | None) -> str | None:
        match(info.mBasicType):
            case BallanceObjectType.DECORATION:
                return 'D_'
            case BallanceObjectType.SKYLAYER:
                return 'SkyLayer'
            
            case BallanceObjectType.LEVEL_START:
                return 'PS_FourFlames_01'
            case BallanceObjectType.LEVEL_END:
                return 'PE_Balloon_01'
            case BallanceObjectType.CHECKPOINT:
                return f'PC_TwoFlames_{info.mSector:0>2d}'
            case BallanceObjectType.RESETPOINT:
                return f'PR_Resetpoint_{info.mSector:0>2d}'

            case BallanceObjectType.DEPTH_CUBE:
                return 'DepthCubes_'

            case BallanceObjectType.FLOOR:
                return 'A_Floor_'
            case BallanceObjectType.RAIL:
                return 'A_Rail_'
            case BallanceObjectType.WOOD:
                return 'A_Wood_'
            case BallanceObjectType.STOPPER:
                return 'A_Stopper_'

            case BallanceObjectType.COMPONENT:
                return '{}_{:0>2d}_'.format(
                    info.mComponentType, info.mSector)
                
            case _:
                if reporter is not None:
                    reporter.add_error('No matched info.')
                return None
            
    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: RenameErrorReporter | None) -> bool:
        expect_name: str | None = YYCToolchainConvention.set_to_name(info, reporter)
        if expect_name is None: return False

        obj.name = expect_name
        return True

class ImengyuConvention():
    cRegexComponent: typing.ClassVar[re.Pattern] = re.compile('^(' + '|'.join(_g_BlcNormalComponents) + '):[^:]*:([1-9]|[1-9][0-9])$')
    cRegexPC: typing.ClassVar[re.Pattern] = re.compile('^PC_CheckPoint:([0-9]+)$')
    cRegexPR: typing.ClassVar[re.Pattern] = re.compile('^PR_ResetPoint:([0-9]+)$')

    @staticmethod
    def parse_from_name(name: str, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
        # check component first
        regex_result = ImengyuConvention.cRegexComponent.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_component(
                regex_result.group(1),
                int(regex_result.group(2))
            )

        # check PC PR elements
        regex_result = ImengyuConvention.cRegexPC.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_checkpoint(
                int(regex_result.group(1))
            )
        regex_result = ImengyuConvention.cRegexPR.match(name)
        if regex_result is not None:
            return BallanceObjectInfo.create_from_resetpoint(
                int(regex_result.group(1))
            )

        # check other unique elements
        if name == "PS_LevelStart":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_START)
        if name == "PE_LevelEnd":
            return BallanceObjectInfo.create_from_others(BallanceObjectType.LEVEL_END)

        # process floors
        if name.startswith("S_Floors"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.FLOOR)
        if name.startswith("S_FloorRails"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.RAIL)
        if name.startswith("S_FloorWoods"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.WOOD)
        if name.startswith("S_FloorStopper"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.STOPPER)

        # process others
        if name.startswith("DepthTestCubes"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DEPTH_CUBE)
        if name.startswith("O_"):
            return BallanceObjectInfo.create_from_others(BallanceObjectType.DECORATION)
        if name == 'SkyLayer':
            return BallanceObjectInfo.create_from_others(BallanceObjectType.SKYLAYER)

        if reporter is not None:
            reporter.add_error("Name match lost.")
        return None

    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: RenameErrorReporter | None) -> BallanceObjectInfo | None:
        return ImengyuConvention.parse_from_name(obj.name, reporter)

    @staticmethod
    def set_to_name(info: BallanceObjectInfo, oldname: str | None, reporter: RenameErrorReporter | None) -> str | None:
        match(info.mBasicType):
            case BallanceObjectType.DECORATION:
                return 'O_'
            case BallanceObjectType.SKYLAYER:
                return 'SkyLayer'
            
            case BallanceObjectType.LEVEL_START:
                return 'PS_LevelStart'
            case BallanceObjectType.LEVEL_END:
                return 'PE_LevelEnd'
            case BallanceObjectType.CHECKPOINT:
                return f'PR_ResetPoint:{info.mSector:d}'
            case BallanceObjectType.RESETPOINT:
                return f'PC_CheckPoint:{info.mSector:d}'

            case BallanceObjectType.DEPTH_CUBE:
                return 'DepthTestCubes'

            case BallanceObjectType.FLOOR:
                return 'S_Floors'
            case BallanceObjectType.RAIL:
                return 'S_FloorWoods'
            case BallanceObjectType.WOOD:
                return 'S_FloorRails'
            case BallanceObjectType.STOPPER:
                return 'S_FloorStopper'

            case BallanceObjectType.COMPONENT:
                return '{}:{}:{:d}'.format(
                    info.mComponentType, 
                    oldname.replace(':', '_') if oldname is not None else '', 
                    info.mSector
                )
                
            case _:
                if reporter is not None:
                    reporter.add_error('No matched info.')
                return None
            
    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: RenameErrorReporter | None) -> bool:
        expect_name: str | None = ImengyuConvention.set_to_name(info, obj.name, reporter)
        if expect_name is None: return False

        obj.name = expect_name
        return True


#endregion
