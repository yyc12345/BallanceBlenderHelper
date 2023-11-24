import os, pkgutil, importlib, typing, enum, types

#region Ballance Object Types

class BallanceObjectType(enum.IntEnum):
    COMPONENT = enum.auto()

    FLOOR = enum.auto()
    RAIL = enum.auto()
    WOOD = enum.auto()
    STOPPER = enum.auto()

    DEPTH_CUBE = enum.auto()

    DECORATION = enum.auto()

    LEVEL_START = enum.auto()
    LEVEL_END = enum.auto()
    CHECKPOINT = enum.auto()
    RESETPOINT = enum.auto()

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

#region Init Plugins

## Because Blender will only add the parent folder of BBP_NG into sys.path.
#  So we need use full name: bbp_ng.name_convention_plugin.xxx_module to import modules.
#  Considering any possible folder name changes, we dynamically compute these folder's name
#  And use importlib to import them.
#  A legal naming convention should provide its basic profile, parsing from name, and setting to name.

class NamingConventionProfile():
    mName: str
    mDescription: str

    def __init__(self, name: str, desc: str):
        self.mName = name
        self.mDescription = desc

_GetProfileFct = typing.Callable[[], NamingConventionProfile]
_ParseFromNameFct = typing.Callable[[str], BallanceObjectInfo]
_SetToNameFct = typing.Callable[[str, BallanceObjectInfo], None]

class _NamingConventionRegisterEntry():
    mIdentifier: int
    mName: str
    mDescription: str
    mParseNameFct: _ParseFromNameFct
    mSetNameFct: _SetToNameFct

    def __init__(self, ident: int, profile: NamingConventionProfile, parse_fct: _ParseFromNameFct, set_fct: _SetToNameFct):
        self.mIdentifier = ident
        self.mName = profile.mName
        self.mDescription = profile.mDescription
        self.mParseNameFct = parse_fct
        self.mSetNameFct = set_fct

_g_PkgPath: str = os.path.dirname(__file__)
_g_PkgName: str = os.path.basename(_g_PkgPath)
_g_BBPNGPath: str = os.path.dirname(_g_PkgPath)
_g_BBPNGName: str = os.path.basename(_g_BBPNGPath)

def _check_plugin_legality(module_: types.ModuleType) -> _NamingConventionRegisterEntry | None:
    pass

# iterate modules and load
for _, filename, _ in pkgutil.iter_modules((_g_PkgPath, )):
    module = importlib.import_module(f'{_g_BBPNGName}.{_g_PkgName}.{filename}')

#endregion

#region Naming Covension Visitors


#endregion
