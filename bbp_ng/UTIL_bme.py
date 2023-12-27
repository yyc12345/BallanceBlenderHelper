import bpy, mathutils
import os, json, enum, typing, math
from . import PROP_virtools_group, PROP_bme_material
from . import UTIL_functions, UTIL_icons_manager, UTIL_blender_mesh, UTIL_virtools_types, UTIL_naming_convension

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

TOKEN_SKIP: str = 'skip'

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
for walk_root, walk_dirs, walk_files in os.walk(os.path.join(os.path.dirname(__file__), 'jsons')):
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

def _eval_skip(strl: str, params_data: dict[str, typing.Any]) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, params_data)

def _eval_vars(strl: str, params_data: dict[str, typing.Any]) -> typing.Any:
    return eval(strl, _g_ProgFieldGlobals, params_data)

def _eval_others(strl: str, params_vars_data: dict[str, typing.Any]) -> typing.Any:
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

def create_bme_struct_wrapper(ident: str, cfgs: dict[str, typing.Any]) -> bpy.types.Object:
    # get prototype first
    proto: dict[str, typing.Any] = _get_prototype_by_identifier(ident)

    # analyse params by given cfgs
    params: dict[str, typing.Any] = {}
    for proto_param in proto[TOKEN_PARAMS]:
        params[proto_param[TOKEN_PARAMS_FIELD]] = _eval_params(proto_param[TOKEN_PARAMS_DATA], cfgs)

    # create used mesh
    mesh: bpy.types.Mesh = bpy.data.meshes.new('BMEStruct')

    # create mesh writer and bme mtl helper
    # recursively calling underlying creation function
    with UTIL_blender_mesh.MeshWriter(mesh) as writer:
        with PROP_bme_material.BMEMaterialsHelper(bpy.context.scene) as bmemtl:
            create_bme_struct(
                ident,
                writer,
                bmemtl,
                mathutils.Matrix.Identity(4),
                params
            )

    # create object and assign prop
    # get obj info first
    obj_info: UTIL_naming_convension.BallanceObjectInfo
    match(PrototypeShowcaseTypes(proto[TOKEN_SHOWCASE][TOKEN_SHOWCASE_TYPE])):
        case PrototypeShowcaseTypes.No:
            obj_info = UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.DECORATION)
        case PrototypeShowcaseTypes.Floor:
            obj_info = UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.FLOOR)
        case PrototypeShowcaseTypes.Rail:
            obj_info = UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.RAIL)
        case PrototypeShowcaseTypes.Wood:
            obj_info = UTIL_naming_convension.BallanceObjectInfo.create_from_others(UTIL_naming_convension.BallanceObjectType.WOOD)
    # then get object name
    obj_name: str | None = UTIL_naming_convension.YYCToolchainConvention.set_to_name(obj_info, None)
    if obj_name is None: raise UTIL_functions.BBPException('impossible null name')
    # create object by name
    obj: bpy.types.Object = bpy.data.objects.new(obj_name, mesh)
    # assign virtools groups
    UTIL_naming_convension.VirtoolsGroupConvention.set_to_object(obj, obj_info, None)

    # return object
    return obj

def create_bme_struct(
        ident: str, 
        writer: UTIL_blender_mesh.MeshWriter, 
        bmemtl: PROP_bme_material.BMEMaterialsHelper,
        transform: mathutils.Matrix, 
        params: dict[str, typing.Any]) -> None:
    # get prototype first
    proto: dict[str, typing.Any] = _get_prototype_by_identifier(ident)

    # check whether skip the whole struct before cal vars
    if _eval_skip(proto[TOKEN_SKIP], params) == True:
        return

    # calc vars by given params
    # please note i will add entries directly into params dict
    # but the params dict will not used independently later,
    # all following use is the union of params and vars dict.
    # so it is safe.
    for proto_var in proto[TOKEN_VARS]:
        params[proto_var[TOKEN_VARS_FIELD]] = _eval_vars(proto_var[TOKEN_VARS_DATA], params)

    # collect valid face and vertices data for following using.
    # if NOT skip, add into valid list
    valid_vec_idx: list[int] = []
    for vec_idx, proto_vec in enumerate(proto[TOKEN_VERTICES]):
        if _eval_others(proto_vec[TOKEN_VERTICES_SKIP], params) == False:
            valid_vec_idx.append(vec_idx)
    valid_face_idx: list[int] = []
    for face_idx, proto_face in enumerate(proto[TOKEN_FACES]):
        if _eval_others(proto_face[TOKEN_FACES_SKIP], params) == False:
            valid_face_idx.append(face_idx)

    # create mtl slot remap to help following mesh adding
    # because mesh writer do not accept string format mtl slot visiting,
    # it only accept int based mtl slot index.
    # NOTE: since Python 3.6, the item of builtin dict is ordered by inserting order.
    # we rely on this to implement following features
    mtl_remap: dict[str, int] = {}
    for face_idx in valid_face_idx:
        # eval mtl name
        mtl_name: str = _eval_others(proto[TOKEN_FACES][face_idx][TOKEN_FACES_TEXTURE], params)
        # add into remap if not exist
        if mtl_name not in mtl_remap:
            mtl_remap[mtl_name] = len(mtl_remap)

    # prepare mesh part data
    mesh_part: UTIL_blender_mesh.MeshWriterIngredient = UTIL_blender_mesh.MeshWriterIngredient()
    def vpos_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        bv: mathutils.Vector = mathutils.Vector((0, 0, 0))
        v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for vec_idx in valid_vec_idx:
            # BME no need to convert co system
            # but it need mul with transform matrix
            bv.x, bv.y, bv.z = _eval_others(proto[TOKEN_VERTICES][vec_idx][TOKEN_VERTICES_DATA], params)
            bv = transform @ bv
            # yield result
            v.x, v.y, v.z = bv.x, bv.y, bv.z
            yield v
    mesh_part.mVertexPosition = vpos_iterator()
    def vnml_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        # calc normal used transform first
        # ref: https://zhuanlan.zhihu.com/p/96717729
        nml_transform: mathutils.Matrix = transform.inverted_safe().transposed()
        # prepare vars
        bv: mathutils.Vector = mathutils.Vector((0, 0, 0))
        v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for face_idx in valid_face_idx:
            face_data: dict[str, typing.Any] = proto[TOKEN_FACES][face_idx]
            for i in range(len(face_data[TOKEN_FACES_INDICES])):
                # BME normals need transform by matrix first,
                bv.x, bv.y, bv.z = _eval_others(face_data[TOKEN_FACES_NORMALS][i], params)
                bv = nml_transform @ bv
                # then normalize it
                bv.normalize()
                # yield result
                v.x, v.y, v.z = bv.x, bv.y, bv.z
                yield v
    mesh_part.mVertexNormal = vnml_iterator()
    def vuv_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector2]:
        v: UTIL_virtools_types.VxVector2 = UTIL_virtools_types.VxVector2()
        for face_idx in valid_face_idx:
            face_data: dict[str, typing.Any] = proto[TOKEN_FACES][face_idx]
            for i in range(len(face_data[TOKEN_FACES_INDICES])):
                # BME uv do not need any extra process
                v.x, v.y = _eval_others(face_data[TOKEN_FACES_UVS][i], params)
                yield v
    mesh_part.mVertexUV = vuv_iterator()
    def mtl_iterator() -> typing.Iterator[bpy.types.Material | None]:
        for mtl_name in mtl_remap.keys():
            yield bmemtl.get_material(mtl_name)
    mesh_part.mMaterial = mtl_iterator()
    def face_iterator() -> typing.Iterator[UTIL_blender_mesh.FaceData]:
        # create face data with 3 placeholder
        f: UTIL_blender_mesh.FaceData = UTIL_blender_mesh.FaceData(
            [UTIL_blender_mesh.FaceVertexData() for i in range(3)]
        )

        # create a internal counter to count how many indices has been processed
        # this counter will be used to calc uv and normal index
        # because these are based on face, not vertex position index.
        face_counter: int = 0

        # iterate valid face
        for face_idx in valid_face_idx:
            # get face data
            face_data: dict[str, typing.Any] = proto[TOKEN_FACES][face_idx]

            # calc indices count
            face_indices: list[int] = face_data[TOKEN_FACES_INDICES]
            indices_count: int = len(face_indices)
            # resize face data to fulfill req
            while len(f.mIndices) > indices_count:
                f.mIndices.pop()
            while len(f.mIndices) < indices_count:
                f.mIndices.append(UTIL_blender_mesh.FaceVertexData())

            # fill the data
            for i in range(indices_count):
                # fill vertex position data by indices
                f.mIndices[i].mPosIdx = face_indices[i]
                # fill nml and uv based on face index
                f.mIndices[i].mNmlIdx = face_counter + i
                f.mIndices[i].mUvIdx = face_counter + i

            # add current face indices count to internal counter
            face_counter += indices_count

            # fill texture data
            mtl_name: str = _eval_others(face_data[TOKEN_FACES_TEXTURE], params)
            f.mMtlIdx = mtl_remap[mtl_name]

            # return data once
            yield f
    mesh_part.mFace = face_iterator()
    # add part to writer
    writer.add_ingredient(mesh_part)

    # then we incursively process instance creation
    for proto_instance in proto[TOKEN_INSTANCES]:
        # check whether skip this instance
        if _eval_others(proto_instance[TOKEN_INSTANCES_SKIP], params) == True:
            continue

        # calc instance params
        instance_params: dict[str, typing.Any] = {}
        proto_instance_params: dict[str, str] = proto_instance[TOKEN_INSTANCES_PARAMS]
        for proto_inst_param_field, proto_inst_param_data in proto_instance_params.items():
            instance_params[proto_inst_param_field] = _eval_others(proto_inst_param_data, params)

        # call recursively
        create_bme_struct(
            proto_instance[TOKEN_INSTANCES_IDENTIFIER],
            writer,
            bmemtl,
            # left-mul transform, because self transform should be applied first, the apply parent's transform
            transform @ _eval_others(proto_instance[TOKEN_INSTANCES_TRANSFORM], params),
            instance_params
        )

#endregion
