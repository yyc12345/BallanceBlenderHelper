import bpy
import os, typing, enum
from . import UTIL_functions, UTIL_blender_mesh

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
_g_ElementNameIdMap: dict[str, int] = dict((entry.name, entry.value) for entry in BallanceElementType)
_g_ElementIdNameMap: dict[str, int] = dict((entry.value, entry.name) for entry in BallanceElementType)

def get_ballance_element_id(name: str) -> int | None:
    """
    Get Ballance element ID by its name.

    @param name[in] The name of element
    @return the ID of this Ballance element name distributed by this plugin. or None if providing name is invalid.
    """
    return _g_ElementNameIdMap.get(name, None)

def get_ballance_element_name(id: int) -> int | None:
    """
    Get Ballance element name by its ID

    @param id[in] The ID of element
    @return the name of this Ballance element, or None if ID is invalid.
    """
    return _g_ElementIdNameMap.get(id, None)

def is_ballance_element(name: str) -> bool:
    """
    Check whether providing name is Ballance element.

    Just a wrapper of get_ballance_element_id

    @param name[in] The name of element
    @return True if providing name is Ballance element name.
    """
    return get_ballance_element_id(name) is not None

#endregion

#region Ballance Elements Define & Visitor

class BBP_PG_ballance_element(bpy.types.PropertyGroup):
    element_name: bpy.props.StringProperty(
        name = "Element Name",
        default = ""
    )
    
    mesh_ptr: bpy.props.PointerProperty(
        name = "Mesh",
        type = bpy.types.Mesh
    )

def get_ballance_elements() -> bpy.types.CollectionProperty:
    return bpy.context.scene.ballance_elements

#endregion

#region

def load_element(mesh: bpy.types.Mesh, element_id: int) -> None:
    pass

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
    __mElementMap: dict[int, bpy.types.Mesh]

    def __init__(self):
        self.__mElementMap = {}

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
            self.__mSingletonMutex = False
    
    def get_element(self, element_id: int) -> bpy.types.Mesh:
        if not self.is_valid():
            raise UTIL_functions.BBPException('calling invalid BallanceElementsHelper')
        
        # get exist one
        mesh: bpy.types.Mesh | None = self.__mElementMap.get(element_id, None)
        if mesh is not None: 
            return mesh

        # if no existing one, create new one
        new_mesh_name: str | None = get_ballance_element_id(element_id)
        if new_mesh_name is None: 
            raise UTIL_functions.BBPException('invalid element id')
        new_mesh: bpy.types.Mesh = bpy.data.meshes.new(get_ballance_element_name(element_id))

        load_element(new_mesh, element_id)
        self.__mElementMap[element_id] = new_mesh
        return new_mesh

    def __write_to_ballance_elements(self) -> None:
        elements: bpy.types.CollectionProperty = get_ballance_elements()
        elements.clear()

        for eleid, elemesh in self.__mElementMap.items():
            name: str | None = get_ballance_element_name(eleid)
            if name is None:
                continue

            item: BBP_PG_ballance_element = elements.add()
            item.element_name = name
            item.mesh_ptr = elemesh

    def __read_from_ballance_element(self) -> None:
        elements: bpy.types.CollectionProperty = get_ballance_elements()
        self.__mElementMap.clear()

        item: BBP_PG_ballance_element
        for item in elements:
            # check requirements
            if item.mesh_ptr is None: continue
            mesh_id: int | None = get_ballance_element_id(item.element_name)
            if mesh_id is None: continue

            # add into map
            self.__mElementMap[mesh_id] = item.mesh_ptr

def reset_ballance_elements() -> None:
    invalid_idx: list[int] = []
    elements: bpy.types.CollectionProperty = get_ballance_elements()

    # re-load all elements
    index: int = 0
    item: BBP_PG_ballance_element
    for item in elements:
        eleid: int | None = get_ballance_element_id(item.element_name)

        # load or record invalid entry
        if eleid is None or item.mesh_ptr is None:
            invalid_idx.append(index)
        else:
            load_element(item.mesh_ptr, eleid)

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
        if item.element_name != "" and item.mesh_ptr is not None:
            layout.label(text = item.element_name)
            layout.label(text = item.mesh_ptr, icon = 'MESH_DATA')

class BBP_OT_reset_ballance_elements(bpy.types.Operator):
    """Reset all Meshes of Loaded Ballance Elements to Original Geometry."""
    bl_idname = "bbp.reset_ballance_elements"
    bl_label = "Reset Ballance Elements"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def execute(self, context):
        reset_ballance_elements()
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
