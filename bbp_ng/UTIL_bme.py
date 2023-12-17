import bpy, mathutils
import os, json, enum, typing, math
from . import PROP_virtools_group, PROP_bme_material
from . import UTIL_functions, UTIL_icons_manager, UTIL_blender_mesh

## NOTE: Outside caller should use BME struct's unique indetifier to visit each prototype
#  and drive this class' functions to work.

#region Prototype Visitor

class PrototypeShowcaseCfgsTypes(enum.Enum):
    Integer = 'int'
    Float = 'float'
    Boolean = 'bool'
    Face = 'face'

class PrototypeShowcaseTypes(enum.Enum):
    No = 'none'
    Floor = 'floor'
    Rail = 'rail'
    Wood = 'wood'

TOKEN_IDENTIFIER: str = 'identifier'

TOKEN_SHOWCASE: str = 'showcase'
TOKEN_SHOWCASE_TITLE: str = 'title'
TOKEN_SHOWCASE_ICON: str = 'icon'
TOKEN_SHOWCASE_TYPE: str = 'type'
TOKEN_SHOWCASE_CFGS: str = 'cfgs'
TOKEN_SHOWCASE_CFGS_FIELD: str = 'field'
TOKEN_SHOWCASE_CFGS_TYPE: str = 'type'
TOKEN_SHOWCASE_CFGS_TITLE: str = 'title'
TOKEN_SHOWCASE_CFGS_DESC: str = 'desc'
TOKEN_SHOWCASE_CFGS_DEFAULT: str = 'default'

TOKEN_PARAMS: str = 'params'
TOKEN_PARAMS_FIELD: str = 'field'
TOKEN_PARAMS_DATA: str = 'data'

TOKEN_VARS: str = 'vars'
TOKEN_VARS_FIELD: str = 'field'
TOKEN_VARS_DATA: str = 'data'

TOKEN_VERTICES: str = 'vertices'
TOKEN_VERTICES_SKIP: str = 'skip'
TOKEN_VERTICES_DATA: str = 'data'

TOKEN_FACES: str = 'faces'
TOKEN_FACES_SKIP: str = 'skip'
TOKEN_FACES_TEXTURE: str = 'texture'
TOKEN_FACES_INDICES: str = 'indices'
TOKEN_FACES_UVS: str = 'uvs'
TOKEN_FACES_NORMALS: str = 'normals'

TOKEN_INSTANCES: str = 'instances'
TOKEN_INSTANCES_IDENTIFIER: str = 'identifier'
TOKEN_INSTANCES_SKIP: str = 'skip'
TOKEN_INSTANCES_PARAMS: str = 'params'
TOKEN_INSTANCES_TRANSFORM: str = 'transform'

#endregion

#region Prototype Loader

## The list storing BME prototype.
_g_BMEPrototypes: list[dict[str, typing.Any]] = []
## The dict. Key is prototype identifier. value is the index of prototype in prototype list.
_g_BMEPrototypeIndexMap: dict[str, int] = {}

# the core loader
for walk_root, walk_dirs, walk_files in os.walk(os.path.join(os.path.dirname(__file__), 'json')):
    for relfile in walk_files:
        if not relfile.endswith('.json'): continue
        with open(os.path.join(walk_root, relfile), 'r', encoding = 'utf-8') as fp:
            proto: dict[str, typing.Any]
            for proto in json.load(fp):
                # insert index to map
                _g_BMEPrototypeIndexMap[proto[TOKEN_IDENTIFIER]] = len(_g_BMEPrototypes)
                # add into list
                _g_BMEPrototypes.append(proto)

def _get_prototype_by_identifier(ident: str) -> dict[str, typing.Any]:
    return _g_BMEPrototypes[_g_BMEPrototypeIndexMap[ident]]

#endregion

#region Programmable Field Calc

_g_ProgFieldGlobals: dict[str, typing.Any] = {
    # constant
    'pi': math.pi,
    'tau': math.tau,

    # math functions
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,

    'pow': math.pow,
    'sqrt': math.sqrt,

    'fabs': math.fabs,

    'degrees': math.degrees,
    'radians': math.radians,

    # builtin functions
    'abs': abs,
    
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,

    # my custom matrix functions
    'move': lambda x, y, z: mathutils.Matrix.Translation((x, y, z)),
    'rot': lambda x, y, z: mathutils.Matrix.LocRotScale(None, mathutils.Euler((math.radians(x), math.radians(y), math.radians(z)), 'XYZ'), None),
    'ident': lambda: mathutils.Matrix.Identity(4),
}

def _eval_showcase_cfgs_default(strl: str) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, None)

def _eval_params(strl: str, cfgs_data: dict[str, typing.Any]) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, cfgs_data)

def _eval_vars(strl: str, params_data: dict[str, typing.Any]) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, params_data)

def _eval_others(strl, str, params_vars_data: dict[str, typing.Any]) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, params_vars_data)

#endregion

#region Prototype Helper

class PrototypeShowcaseCfgDescriptor():
    __mRawCfg:  dict[str, str]

    def __init__(self, raw_cfg: dict[str, str]):
        self.__mRawCfg = raw_cfg

    def get_field(self) -> str: 
        return self.__mRawCfg[TOKEN_SHOWCASE_CFGS_FIELD]

    def get_type(self) -> PrototypeShowcaseCfgsTypes:
        return PrototypeShowcaseCfgsTypes(self.__mRawCfg[TOKEN_SHOWCASE_CFGS_TYPE])

    def get_title(self) -> str: 
        return self.__mRawCfg[TOKEN_SHOWCASE_CFGS_TITLE]

    def get_desc(self) -> str: 
        return self.__mRawCfg[TOKEN_SHOWCASE_CFGS_DESC]

    def get_default(self) -> typing.Any:
        return _eval_showcase_cfgs_default(self.__mRawCfg[TOKEN_SHOWCASE_CFGS_DEFAULT])

class EnumPropHelper(UTIL_functions.EnumPropHelper):
    """
    The BME specialized Blender EnumProperty helper.
    """

    def __init__(self):
        # init parent class
        UTIL_functions.EnumPropHelper.__init__(
            self,
            self.get_bme_identifiers(),
            lambda x: x,
            lambda x: x,
            lambda x: self.get_bme_showcase_title(x),
            lambda _: '',
            lambda x: self.get_bme_showcase_icon(x)
        )

    def get_bme_identifiers(self) -> tuple[str, ...]:
        """
        Get the identifier of prototype which need to be exposed to user.
        Template prototype is not included.
        """
        return tuple(
            x[TOKEN_IDENTIFIER] # get identifier
            for x in filter(lambda x: x[TOKEN_SHOWCASE] is not None, _g_BMEPrototypes)  # filter() to filter no showcase template.
        )
    
    def get_bme_showcase_title(self, ident: str) -> str:
        """
        Get BME display title by prototype identifier.
        """
        # get prototype first
        proto: dict[str, typing.Any] = _get_prototype_by_identifier(ident)
        # visit title field
        return proto[TOKEN_SHOWCASE][TOKEN_SHOWCASE_TITLE]

    def get_bme_showcase_icon(self, ident: str) -> int:
        """
        Get BME icon by prototype's identifier
        """
        # get prototype specified icon name
        proto: dict[str, typing.Any] = _get_prototype_by_identifier(ident)
        icon_name: str = proto[TOKEN_SHOWCASE][TOKEN_SHOWCASE_ICON]
        # get icon from icon manager
        cache: int | None = UTIL_icons_manager.get_bme_icon(icon_name)
        if cache is None: return UTIL_icons_manager.get_empty_icon()
        else: return cache

    def get_bme_showcase_cfgs(self, ident: str) -> typing.Iterator[PrototypeShowcaseCfgDescriptor]:
        # get prototype first
        proto: dict[str, typing.Any] = _get_prototype_by_identifier(ident)
        # use map to batch create descriptor
        return map(lambda x: PrototypeShowcaseCfgDescriptor(x), proto[TOKEN_SHOWCASE][TOKEN_SHOWCASE_CFGS])

#endregion

#region Core Creator

def get_bme_struct_cfgs():
    pass

def create_bme_struct_wrapper():
    pass

def create_bme_struct():
    pass

#endregion
