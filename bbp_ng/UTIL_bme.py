import bpy, mathutils
import os, json, enum, typing, math
from . import PROP_virtools_group, PROP_bme_material, UTIL_naming_convention
from . import UTIL_functions, UTIL_icons_manager, UTIL_blender_mesh, UTIL_virtools_types

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

def _env_fct_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    diff = mathutils.Vector((x2, y2)) - mathutils.Vector((x1, y1))
    return diff.length

def _env_fct_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    # compute blender angle first
    # computed blender angle has some issues:
    # first, it is range from -180 to 180 (0 is +X axis).
    # second, its direction (clockwise is positive) is opposite with blender rotation direction (counter-clockwise is positive).
    diff = mathutils.Vector((x2, y2)) - mathutils.Vector((x1, y1))
    bld_angle = math.degrees(mathutils.Vector((1,0)).angle_signed(diff, 0))

    # flip it first
    bld_angle = -bld_angle
    # process positove number and negative number respectively
    # to let it range change from -180~180 to 0~360
    if bld_angle > 0: return bld_angle
    else: return 360 + bld_angle

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
    'scale': lambda x, y, z: mathutils.Matrix.LocRotScale(None, None, (x, y, z)),
    'ident': lambda: mathutils.Matrix.Identity(4),

    # my misc custom functions
    'distance': _env_fct_distance,
    'angle': _env_fct_angle,
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

class EnumPropHelper(UTIL_functions.EnumPropHelper[str]):
    """
    The BME specialized Blender EnumProperty helper.
    """
    
    def __init__(self):
        # init parent class
        super().__init__(
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
    obj_info: UTIL_naming_convention.BallanceObjectInfo
    match(PrototypeShowcaseTypes(proto[TOKEN_SHOWCASE][TOKEN_SHOWCASE_TYPE])):
        case PrototypeShowcaseTypes.No:
            obj_info = UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.DECORATION)
        case PrototypeShowcaseTypes.Floor:
            obj_info = UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.FLOOR)
        case PrototypeShowcaseTypes.Rail:
            obj_info = UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.RAIL)
        case PrototypeShowcaseTypes.Wood:
            obj_info = UTIL_naming_convention.BallanceObjectInfo.create_from_others(UTIL_naming_convention.BallanceObjectType.WOOD)
    # then get object name
    obj_name: str | None = UTIL_naming_convention.YYCToolchainConvention.set_to_name(obj_info, None)
    if obj_name is None: raise UTIL_functions.BBPException('impossible null name')
    # create object by name
    obj: bpy.types.Object = bpy.data.objects.new(obj_name, mesh)
    # assign virtools groups
    UTIL_naming_convention.VirtoolsGroupConvention.set_to_object(obj, obj_info, None)
    
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
    # 
    # Also we build face used mtl slot index at the same time.
    # So we do not analyse texture field again when providing face data.
    # The result is in `prebuild_face_mtl_idx` and please note it will store all face's mtl index.
    # For example: if face 0 is skipped and face 1 is used, the first entry in `prebuild_face_mtl_idx`
    # will be the mtl slot index used by face 0, not 1. And its length is equal to the face count.
    # However, because face 0 is skipped, so the entry is not used and default set to 0.
    # 
    # NOTE: since Python 3.6, the item of builtin dict is ordered by inserting order.
    # we rely on this to implement following features.
    mtl_remap: dict[str, int] = {}
    prebuild_face_mtl_idx: list[int] = [0] * len(proto[TOKEN_FACES])
    for face_idx in valid_face_idx:
        # eval mtl name
        mtl_name: str = _eval_others(proto[TOKEN_FACES][face_idx][TOKEN_FACES_TEXTURE], params)
        # try insert into remap and record to face mtl idx
        if mtl_name not in mtl_remap:
            # record index
            prebuild_face_mtl_idx[face_idx] = len(mtl_remap)
            # add into remap if not exist
            mtl_remap[mtl_name] = len(mtl_remap)
        else:
            # if existing, no need to add into remap
            # but we need get its index from remap
            prebuild_face_mtl_idx[face_idx] = mtl_remap.get(mtl_name, 0)

    # pre-compute vertices data because we may need used later.
    # Because if face normal data is null, it mean that we need to compute it
    # by given vertices.
    # The computed vertices is stored in `prebuild_vec_data` and is NOT like `prebuild_face_mtl_idx`,
    # we only store valid one in `prebuild_vec_data`.
    prebuild_vec_data: list[UTIL_virtools_types.ConstVxVector3 | None] = []
    cache_bv: mathutils.Vector = mathutils.Vector((0, 0, 0))
    for vec_idx in valid_vec_idx:
        # but it need mul with transform matrix
        cache_bv.x, cache_bv.y, cache_bv.z = _eval_others(proto[TOKEN_VERTICES][vec_idx][TOKEN_VERTICES_DATA], params)
        # mul with transform matrix
        cache_bv = typing.cast(mathutils.Vector, transform @ cache_bv)
        # get result
        prebuild_vec_data.append((cache_bv.x, cache_bv.y, cache_bv.z))

    # Check whether given transform is mirror matrix
    # because mirror matrix will reverse triangle indice order.
    # If matrix is mirror matrix, we need reverse it again in following procession,
    # including getting uv, calculating normal and providing face data.
    mirror_matrix: bool = _is_mirror_matrix(transform)
    
    # prepare mesh part data
    mesh_part: UTIL_blender_mesh.MeshWriterIngredient = UTIL_blender_mesh.MeshWriterIngredient()
    def vpos_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        # simply get data from prebuild vec data
        v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for vec_data in prebuild_vec_data:
            # skip skipped vertices
            if vec_data is None: continue
            # yield result
            v.x, v.y, v.z = vec_data
            yield v
    mesh_part.mVertexPosition = vpos_iterator()
    def vnml_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        # prepare normal used transform first
        # ref: https://zhuanlan.zhihu.com/p/96717729
        nml_transform: mathutils.Matrix = transform.inverted_safe().transposed()
        # prepare vars
        bv: mathutils.Vector = mathutils.Vector((0, 0, 0))
        v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for face_idx in valid_face_idx:
            face_data: dict[str, typing.Any] = proto[TOKEN_FACES][face_idx]
            face_nml_data: list[str] | None = face_data[TOKEN_FACES_NORMALS]
            if face_nml_data is None:
                # nml is null, we need compute by ourselves
                # get first 3 entries in indices list as the compution ref
                # please note that we may need reverse it
                face_indices_data: list[int]
                if mirror_matrix:
                    face_indices_data = face_data[TOKEN_FACES_INDICES][::-1]
                else:
                    face_indices_data = face_data[TOKEN_FACES_INDICES][:]
                # compute it by getting vertices info from prebuild vertices data
                # because the normals is computed from transformed vertices
                # so no need to correct its by normal transform.
                bv.x, bv.y, bv.z = _compute_normals(
                    typing.cast(UTIL_virtools_types.ConstVxVector3, prebuild_vec_data[face_indices_data[0]]),
                    typing.cast(UTIL_virtools_types.ConstVxVector3, prebuild_vec_data[face_indices_data[1]]),
                    typing.cast(UTIL_virtools_types.ConstVxVector3, prebuild_vec_data[face_indices_data[2]])
                )
                # yield result with N times (N = indices count)
                v.x, v.y, v.z = bv.x, bv.y, bv.z
                for _ in range(len(face_indices_data)):
                    yield v
            else:
                # nml is given, analyse programable fields
                for mtl_data in face_nml_data:
                    # BME normals need transform by matrix first,
                    bv.x, bv.y, bv.z = _eval_others(mtl_data, params)
                    bv = typing.cast(mathutils.Vector, nml_transform @ bv)
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
            # iterate uv list considering mirror matrix
            indices_count: int = len(face_data[TOKEN_FACES_INDICES])
            for i in (range(indices_count)[::-1] if mirror_matrix else range(indices_count)):
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
            
            # get face indices considering the mirror matrix
            face_indices: list[int]
            if mirror_matrix:
                face_indices = face_data[TOKEN_FACES_INDICES][::-1]
            else:
                face_indices = face_data[TOKEN_FACES_INDICES][:]
            # calc indices count
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
            f.mMtlIdx = prebuild_face_mtl_idx[face_idx]
            
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

#region Creation Assist Functions

def _compute_normals(
    point1: UTIL_virtools_types.ConstVxVector3,
    point2: UTIL_virtools_types.ConstVxVector3,
    point3: UTIL_virtools_types.ConstVxVector3) -> UTIL_virtools_types.ConstVxVector3:
    # build vector
    p1: mathutils.Vector = mathutils.Vector(point1)
    p2: mathutils.Vector = mathutils.Vector(point2)
    p3: mathutils.Vector = mathutils.Vector(point3)
    
    vector1: mathutils.Vector = p2 - p1
    vector2: mathutils.Vector = p3 - p2
    
    # do vector x mutiply
    # vector1 x vector2
    corss_mul: mathutils.Vector = vector1.cross(vector2)
    
    # do a normalization
    corss_mul.normalize()
    return (corss_mul.x, corss_mul.y, corss_mul.z)

def _is_mirror_matrix(mat: mathutils.Matrix) -> bool:
    """
    Reflection matrix (aka. mirror matrix) is a special scaling matrix.
    In this matrix, 1 or 3 scaling factor is minus number.

    Mirror matrix will cause the inverse of triangle indice order.
    So we need detect it and re-reverse when creating bm struct.
    This function can detect whether given matrix is mirror matrix.

    Reference: https://zhuanlan.zhihu.com/p/96717729
    """
    return mat.is_negative
    #return mat.to_3x3().determinant() < 0

#endregion
