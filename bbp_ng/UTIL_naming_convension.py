import bpy
import typing, enum
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

    def get_presentation(self):
        return "[{}]\t{}".format(_RenameErrorType.cvt_err_from_int_to_str(self.err_type), self.description)

class _RenameErrorReporter():
    mErrList: list[_RenameErrorItem]

    def __init__(self):
        self.mErrList = []

    def add_error(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.ERROR, description))
    def add_warning(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.WARNING, description))
    def add_info(self, description: str):
        self.mErrList.append(_RenameErrorItem(_RenameErrorType.INFO, description))

    def need_report(self):
        return len(self.mErrList) != 0
    def report(self, header: str):
        print(header)
        for item in self.mErrList:
            print('\t' + _RenameErrorReporter.__erritem_to_string(item))
    def clear(self):
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

class _BallanceObjectType(enum.IntEnum):
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

class _BallanceObjectInfo():
    mBasicType: _BallanceObjectType

    ## Only available for COMPONENT basic type
    mComponentType: str | None
    ## Only available for COMPONENT, CHECKPOINT, RESETPOINT basic type
    #  For COMPONENT, it indicate which sector this component belong to.
    #  For CHECKPOINT, RESETPOINT, it indicate the index of this object.
    #  In CHECKPOINT, RESETPOINT mode, the sector actually is the suffix number of these objects' name. So checkpoint starts with 1, not 0.
    mSector: int | None

    def __init__(self, basic_type: _BallanceObjectType):
        self.mBasicType = basic_type

    @classmethod
    def create_from_component(cls, comp_type: str, sector: int):
        inst = cls(_BallanceObjectType.COMPONENT)
        inst.mComponentType = comp_type
        inst.mSector = sector
        return inst
    
    @classmethod
    def create_from_checkpoint(cls, sector: int):
        inst = cls(_BallanceObjectType.CHECKPOINT)
        inst.mSector = sector
        return inst
    @classmethod
    def create_from_resetpoint(cls, sector: int):
        inst = cls(_BallanceObjectType.RESETPOINT)
        inst.mSector = sector
        return inst

    @classmethod
    def create_from_others(cls, basic_type: _BallanceObjectType):
        return cls(basic_type)

class _NamingConventionProfile():
    _TNameFct = typing.Callable[[], str]
    _TDescFct = typing.Callable[[], str]
    _TParseFct = typing.Callable[[bpy.types.Object, _RenameErrorReporter], _BallanceObjectInfo]
    _TSetFct = typing.Callable[[bpy.types.Object,_BallanceObjectInfo, _RenameErrorReporter], None]

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
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter) -> _BallanceObjectInfo:
        pass

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: _BallanceObjectInfo, reporter: _RenameErrorReporter) -> None:
        pass

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
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter) -> _BallanceObjectInfo:
        pass

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: _BallanceObjectInfo, reporter: _RenameErrorReporter) -> None:
        pass

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
    def parse_from_object(obj: bpy.types.Object, reporter: _RenameErrorReporter) -> _BallanceObjectInfo:
        pass

    @staticmethod
    def set_to_object(obj: bpy.types.Object, info: _BallanceObjectInfo, reporter: _RenameErrorReporter) -> None:
        pass

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

## The native naming convention is Virtools Group
#  We treat it as naming convention because we want use a universal interface to process naming converting.
#  So Virtools Group can no be seen as a naming convention, but we treat it like naming convention in code.
#  The "native" mean this is 
_g_NativeNamingConvention: _NamingConventionProfile = _VirtoolsGroupConvention.register()

## All available naming conventions
#  Each naming convention should have a identifier for visiting them.
#  The identifier is its index in this tuple.
_g_NamingConventions: tuple[_NamingConventionProfile, ...] = (
    _VirtoolsGroupConvention.register(),
    _YYCToolchainConvention.register(),
    _ImengyuConvention.register(),
)

#endregion








