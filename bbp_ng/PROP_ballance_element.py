import bpy
import os, typing, enum, array
from . import PROP_virtools_mesh
from . import UTIL_functions, UTIL_file_io, UTIL_blender_mesh, UTIL_virtools_types

#region Raw Elements Operations

class BallanceElementType(enum.IntEnum):
    P_Extra_Life = 0
    P_Extra_Point = 1
    P_Trafo_Paper = 2
    P_Trafo_Stone = 3
    P_Trafo_Wood = 4
    P_Ball_Paper = 5
    P_Ball_Stone = 6
    P_Ball_Wood = 7
    P_Box = 8
    P_Dome = 9
    P_Modul_01 = 10
    P_Modul_03 = 11
    P_Modul_08 = 12
    P_Modul_17 = 13
    P_Modul_18 = 14
    P_Modul_19 = 15
    P_Modul_25 = 16
    P_Modul_26 = 17
    P_Modul_29 = 18
    P_Modul_30 = 19
    P_Modul_34 = 20
    P_Modul_37 = 21
    P_Modul_41 = 22
    PC_TwoFlames = 23
    PE_Balloon = 24
    PR_Resetpoint = 25
    PS_FourFlames = 26

_g_ElementCount: int = len(BallanceElementType)

def get_ballance_element_type_from_id(id: int) -> BallanceElementType | None:
    """
    Get Ballance element type by its id.

    @param id[in] The id of element
    @return the type of this Ballance element name distributed by this plugin. or None if providing id is invalid.
    """
    try:
        return BallanceElementType(id)  # https://docs.python.org/zh-cn/3/library/enum.html#enum.EnumType.__call__
    except ValueError:
        return None

def get_ballance_element_type_from_name(name: str) -> BallanceElementType | None:
    """
    Get Ballance element type by its name.

    @param name[in] The name of element
    @return the type of this Ballance element name distributed by this plugin. or None if providing name is invalid.
    """
    try:
        return BallanceElementType[name]    # https://docs.python.org/zh-cn/3/library/enum.html#enum.EnumType.__getitem__
    except KeyError:
        return None

def get_ballance_element_id(ty: BallanceElementType) -> int:
    """
    Get Ballance element id by its type

    @param ty[in] The type of element
    @return the id of this Ballance element.
    """
    return ty.value

def get_ballance_element_name(ty: BallanceElementType) -> str:
    """
    Get Ballance element name by its type

    @param ty[in] The type of element
    @return the name of this Ballance element.
    """
    return ty.name

def is_ballance_element(name: str) -> bool:
    """
    Check whether providing name is Ballance element.

    Just a wrapper of get_ballance_element_id

    @param name[in] The name of element
    @return True if providing name is Ballance element name.
    """
    return get_ballance_element_type_from_name(name) is not None

#endregion

#region Ballance Elements Define & Visitor

class BBP_PG_ballance_element(bpy.types.PropertyGroup):
    element_id: bpy.props.IntProperty(
        name = "Element Id",
        default = 0
    )
    
    mesh_ptr: bpy.props.PointerProperty(
        name = "Mesh",
        type = bpy.types.Mesh
    )

def get_ballance_elements(scene: bpy.types.Scene) -> bpy.types.CollectionProperty:
    return scene.ballance_elements

#endregion

#region Element Loader

def _save_element(mesh: bpy.types.Mesh, filename: str) -> None:
    # todo: if we need add element placeholder save operator, 
    # write this function and call this function in operator.
    pass

def _load_element(mesh: bpy.types.Mesh, element_type: BallanceElementType) -> None:
    # resolve mesh path
    element_name: str = get_ballance_element_name(element_type)
    element_filename: str = os.path.join(
        os.path.dirname(__file__),
        "meshes",
        element_name + '.bin'
    )

    # open file and read
    with open(element_filename, 'rb') as fmesh:
        # prepare container
        vpos: array.array = array.array('f')
        vnml: array.array = array.array('f')
        face: array.array = array.array('L')

        # read data
        # position is vector3
        vpos_count = UTIL_file_io.read_uint32(fmesh)
        vpos.extend(UTIL_file_io.read_float_array(fmesh, vpos_count * 3))
        # normal is vector3
        vnml_count = UTIL_file_io.read_uint32(fmesh)
        vnml.extend(UTIL_file_io.read_float_array(fmesh, vnml_count * 3))
        # each face use 6 uint32 to describe, 
        # they are: pos1, nml1, pos2, nml2, pos3, nml3. 
        # each item is a 0 based index refering to corresponding list
        face_count = UTIL_file_io.read_uint32(fmesh)
        face.extend(UTIL_file_io.read_uint32_array(fmesh, face_count * 6))

        # open mesh writer and write data
        with UTIL_blender_mesh.MeshWriter(mesh) as writer:
            # prepare writer essential function
            mesh_part: UTIL_blender_mesh.MeshWriterIngredient = UTIL_blender_mesh.MeshWriterIngredient()
            def vpos_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
                for i in range(vpos_count):
                    idx: int = i * 3
                    v.x = vpos[idx]
                    v.y = vpos[idx + 1]
                    v.z = vpos[idx + 2]
                    # conv co
                    UTIL_virtools_types.vxvector3_conv_co(v)
                    yield v
            mesh_part.mVertexPosition = vpos_iterator()
            def vnml_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                v: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
                for i in range(vnml_count):
                    idx: int = i * 3
                    v.x = vnml[idx]
                    v.y = vnml[idx + 1]
                    v.z = vnml[idx + 2]
                    # conv co
                    UTIL_virtools_types.vxvector3_conv_co(v)
                    yield v
            mesh_part.mVertexNormal = vnml_iterator()
            def vuv_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector2]:
                # no uv, no need to conv co
                v: UTIL_virtools_types.VxVector2 = UTIL_virtools_types.VxVector2()
                yield v
            mesh_part.mVertexUV = vuv_iterator()
            mesh_part.mMaterial = iter(tuple())
            def face_iterator() -> typing.Iterator[UTIL_blender_mesh.FaceData]:
                # create face data with 3 placeholder
                f: UTIL_blender_mesh.FaceData = UTIL_blender_mesh.FaceData(
                    [UTIL_blender_mesh.FaceVertexData() for i in range(3)]
                )
                for i in range(face_count):
                    idx: int = i * 6
                    f.mIndices[0].mPosIdx = face[idx]
                    f.mIndices[0].mNmlIdx = face[idx + 1]
                    f.mIndices[1].mPosIdx = face[idx + 2]
                    f.mIndices[1].mNmlIdx = face[idx + 3]
                    f.mIndices[2].mPosIdx = face[idx + 4]
                    f.mIndices[2].mNmlIdx = face[idx + 5]
                    # conv co
                    f.conv_co()
                    yield f
            mesh_part.mFace = face_iterator()

            writer.add_ingredient(mesh_part)

        # end of with writer
        # write mesh data

        # set other mesh settings
        # generated mesh always use lit mode.
        mesh_settings: PROP_virtools_mesh.RawVirtoolsMesh = PROP_virtools_mesh.RawVirtoolsMesh()
        mesh_settings.mLitMode = UTIL_virtools_types.VXMESH_LITMODE.VX_LITMESH
        PROP_virtools_mesh.set_raw_virtools_mesh(mesh, mesh_settings)

    # end of with fmesh
    # close file


#endregion

#region Ballance Elements Operation Help Class & Functions

class BallanceElementsHelper():
    """
    The helper of Ballance elements processing.

    All element operations, including getting or setting, must be manipulated by this class. 
    You should NOT operate Ballance Elements property (in Scene) directly.

    This class should only have 1 instance at the same time. This class support `with` syntax to achieve this.
    This class frequently used in importing stage to create element placeholder.
    """
    __mSingletonMutex: typing.ClassVar[bool] = False
    __mIsValid: bool
    __mAssocScene: bpy.types.Scene
    __mElementMap: dict[BallanceElementType, bpy.types.Mesh]

    def __init__(self, assoc: bpy.types.Scene):
        self.__mElementMap = {}
        self.__mAssocScene = assoc

        # check singleton
        if BallanceElementsHelper.__mSingletonMutex:
            self.__mIsValid = False
            raise UTIL_functions.BBPException('BallanceElementsHelper is mutex.')
        
        # set validation and read ballance elements property
        BallanceElementsHelper.__mSingletonMutex = True
        self.__mIsValid = True
        self.__read_from_ballance_element()

    def is_valid(self) -> bool:
        return self.__mIsValid
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self) -> None:
        if self.is_valid():
            # write to ballance elements property and reset validation
            self.__write_to_ballance_elements()
            self.__mIsValid = False
            BallanceElementsHelper.__mSingletonMutex = False
    
    def get_element(self, element_type: BallanceElementType) -> bpy.types.Mesh:
        if not self.is_valid():
            raise UTIL_functions.BBPException('calling invalid BallanceElementsHelper')
        
        # get exist one
        mesh: bpy.types.Mesh | None = self.__mElementMap.get(element_type, None)
        if mesh is not None: 
            return mesh

        # if no existing one, create new one
        new_mesh_name: str = get_ballance_element_name(element_type)
        new_mesh: bpy.types.Mesh = bpy.data.meshes.new(new_mesh_name)

        _load_element(new_mesh, element_type)
        self.__mElementMap[element_type] = new_mesh
        return new_mesh

    def __write_to_ballance_elements(self) -> None:
        elements: bpy.types.CollectionProperty = get_ballance_elements(self.__mAssocScene)
        elements.clear()

        for elety, elemesh in self.__mElementMap.items():
            item: BBP_PG_ballance_element = elements.add()
            item.element_id = get_ballance_element_id(elety)
            item.mesh_ptr = elemesh

    def __read_from_ballance_element(self) -> None:
        elements: bpy.types.CollectionProperty = get_ballance_elements(self.__mAssocScene)
        self.__mElementMap.clear()

        item: BBP_PG_ballance_element
        for item in elements:
            # check requirements
            if item.mesh_ptr is None: continue
            element_type: BallanceElementType | None = get_ballance_element_type_from_id(item.element_id)
            if element_type is None: continue

            # add into map
            self.__mElementMap[element_type] = item.mesh_ptr

def reset_ballance_elements(scene: bpy.types.Scene) -> None:
    invalid_idx: list[int] = []
    elements: bpy.types.CollectionProperty = get_ballance_elements(scene)

    # re-load all elements
    index: int = 0
    item: BBP_PG_ballance_element
    for item in elements:
        elety: BallanceElementType | None = get_ballance_element_type_from_id(item.element_id)

        # load or record invalid entry
        if elety is None or item.mesh_ptr is None:
            invalid_idx.append(index)
        else:
            _load_element(item.mesh_ptr, elety)

        # inc counter
        index += 1

    # remove invalid one with reversed order
    invalid_idx.reverse()
    for idx in invalid_idx:
        elements.remove(idx)

#endregion

#region Ballance Elements Representation

class BBP_UL_ballance_elements(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item: BBP_PG_ballance_element, icon, active_data, active_propname):
        # check requirements
        elety: BallanceElementType | None = get_ballance_element_type_from_id(item.element_id)
        if elety is None or item.mesh_ptr is None: return

        # draw list item
        layout.label(text = get_ballance_element_name(elety), translate = False)
        layout.label(text = item.mesh_ptr.name, translate = False, icon = 'MESH_DATA')

class BBP_OT_reset_ballance_elements(bpy.types.Operator):
    """Reset all Meshes of Loaded Ballance Elements to Original Geometry."""
    bl_idname = "bbp.reset_ballance_elements"
    bl_label = "Reset Ballance Elements"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def execute(self, context):
        reset_ballance_elements(context.scene)
        return {'FINISHED'}

class BBP_PT_ballance_elements(bpy.types.Panel):
    """Show Ballance Elements Properties."""
    bl_label = "Ballance Elements"
    bl_idname = "BBP_PT_ballance_elements"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        target: bpy.types.Scene = context.scene
        col = layout.column()

        # show restore operator
        opercol = col.column()
        opercol.operator(BBP_OT_reset_ballance_elements.bl_idname, icon='LOOP_BACK')

        # show list but not allowed to edit
        listcol = col.column()
        listcol.enabled = False
        listcol.template_list(
            "BBP_UL_ballance_elements", "", 
            target, "ballance_elements", 
            target, "active_ballance_elements",
            # default row height is a half of the count of all elements
            # limit the max row height to the the count of all elements
            rows = _g_ElementCount // 2,
            maxrows = _g_ElementCount,
        )

#endregion

def register():
    # register all classes
    bpy.utils.register_class(BBP_PG_ballance_element)
    bpy.utils.register_class(BBP_UL_ballance_elements)
    bpy.utils.register_class(BBP_OT_reset_ballance_elements)
    bpy.utils.register_class(BBP_PT_ballance_elements)
    
    # add into scene metadata
    bpy.types.Scene.ballance_elements = bpy.props.CollectionProperty(type = BBP_PG_ballance_element)
    bpy.types.Scene.active_ballance_elements = bpy.props.IntProperty()

def unregister():
    # del from scene metadata
    del bpy.types.Scene.active_ballance_elements
    del bpy.types.Scene.ballance_elements

    bpy.utils.unregister_class(BBP_PT_ballance_elements)
    bpy.utils.unregister_class(BBP_OT_reset_ballance_elements)
    bpy.utils.unregister_class(BBP_UL_ballance_elements)
    bpy.utils.unregister_class(BBP_PG_ballance_element)
