import bpy
import typing, enum
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
    _TNameFct = typing.Callable[[], str]
    _TDescFct = typing.Callable[[], str]
    _TParseFct = typing.Callable[[bpy.types.Object, _RenameErrorReporter | None], BallanceObjectInfo | None]
    _TSetFct = typing.Callable[[bpy.types.Object,BallanceObjectInfo, _RenameErrorReporter | None], bool]

    mNameFct: _TNameFct
    mDescFct: _TDescFct
    mParseFct: _TParseFct
    mSetFct: _TSetFct

    def __init__(self, name_fct: _TNameFct, desc_fct: _TDescFct, parse_fct: _TParseFct, set_fct: _TSetFct):
        self.mNameFct = name_fct
        self.mDescFct = desc_fct
        self.mParseFct = parse_fct
        self.mSetFct = set_fct

#endregion

#region Naming Convention Declaration

class _VirtoolsGroupConvention():
    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        return False

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            lambda: 'Virtools Group',
            lambda: 'Virtools Group',
            _VirtoolsGroupConvention.parse_from_object,
            _VirtoolsGroupConvention.set_to_object
        )

class _YYCToolchainConvention():
    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        return False

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            lambda: 'YYC Toolchain',
            lambda: 'YYC Toolchain name standard.',
            _YYCToolchainConvention.parse_from_object,
            _YYCToolchainConvention.set_to_object
        )

class _ImengyuConvention():
    @staticmethod
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter | None) -> BallanceObjectInfo | None:
        return None

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: BallanceObjectInfo, reporter: _RenameErrorReporter | None) -> bool:
        return False

    @staticmethod
    def register() -> _NamingConventionProfile:
        return _NamingConventionProfile(
            lambda: 'Imengyu Ballance',
            lambda: 'Auto grouping name standard for Imengyu/Ballance.',
            _ImengyuConvention.parse_from_object,
            _ImengyuConvention.set_to_object
        )

#endregion

#region Nameing Convention Register

## All available naming conventions
#  Each naming convention should have a identifier for visiting them.
#  The identifier is its index in this tuple.
_g_NamingConventions: list[_NamingConventionProfile] = []
def _register_naming_convention_with_index(profile: _NamingConventionProfile) -> int:
    global _g_NamingConventions
    ret: int = len(_g_NamingConventions)
    _g_NamingConventions.append(profile)
    return ret

# register native and default one and others
# but only native one and default one need keep its index
# 
# The native naming convention is Virtools Group
# We treat it as naming convention because we want use a universal interface to process naming converting.
# So Virtools Group can no be seen as a naming convention, but we treat it like naming convention in code.
# The "native" mean this is 
# 
# The default fallback naming convention is YYC toolchain
# 
_g_NativeNamingConventionIndex: int = _register_naming_convention_with_index(_VirtoolsGroupConvention.register())
_g_DefaultNamingConventionIndex: int = _register_naming_convention_with_index(_YYCToolchainConvention.register())
_register_naming_convention_with_index(_ImengyuConvention.register())

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
            for idx, item in enumerate(_g_NamingConventions):
                if idx != _g_NativeNamingConventionIndex:
                    yield (idx, item)

        # token, display name, descriptions, icon, index
        return tuple(
            (
                str(idx), 
                item.mNameFct(), 
                item.mDescFct(), 
                "", 
                idx
            ) for idx, item in naming_convention_iter()
        )
    
    @staticmethod
    def get_selection(prop: str) -> int:
        return int(prop)
    
    @staticmethod
    def to_selection(val: int) -> str:
        return str(val)
    
    @staticmethod
    def get_virtools_group_identifier() -> int:
        return _g_NativeNamingConventionIndex
    
    @staticmethod
    def get_default_naming_identifier() -> int:
        return _g_DefaultNamingConventionIndex

#endregion

def name_setter_core(ident: int, info: BallanceObjectInfo, obj: bpy.types.Object) -> None:
    # get profile
    profile: _NamingConventionProfile = _g_NamingConventions[ident]
    # set name. don't care whether success.
    profile.mSetFct(obj, info, None)

def name_converting_core(src_ident: int, dst_ident: int, objs: typing.Iterable[bpy.types.Object]) -> None:
    # no convert needed
    if src_ident == dst_ident: return

    # get convert profile
    src: _NamingConventionProfile = _g_NamingConventions[src_ident]
    dst: _NamingConventionProfile = _g_NamingConventions[dst_ident]

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

