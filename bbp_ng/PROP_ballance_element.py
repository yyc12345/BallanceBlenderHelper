import bpy
import os, typing
from . import UTIL_functions, UTIL_blender_mesh

#region Raw Elements Operations

_g_AllElementsName: tuple[str] = (
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
    "P_Modul_41",
    "PC_TwoFlames",
    "PE_Balloon",
    "PR_Resetpoint",
    "PS_FourFlames",
)

_g_ElementIndexMap: dict[str, int] = dict((val, idx) for idx, val in enumerate(_g_AllElementsName))

def get_ballance_element_index(name: str) -> int | None:
    """
    Get Ballance element index by its name.

    @param name[in] The name of element
    @return the index of this Ballance element name distributed by this plugin. or None if providing name is invalid.
    """
    return _g_ElementIndexMap.get(name, None)

def is_ballance_element(name: str) -> bool:
    """
    Check whether providing name is Ballance element.

    Just a wrapper of get_ballance_element_index

    @param name[in] The name of element
    @return True if providing name is Ballance element name.
    """
    return get_ballance_element_index(name) is not None

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

#region Ballance Elements Operation Help Class

class BallanceElementsHelper():
    __mSingletonOccupation: typing.ClassVar[bool] = False
    __mIsValid: bool
    __mElementMap: dict[int, bpy.types.Mesh]

    def __init__():
        pass

    def is_valid(self) -> bool:
        return self.__mIsValid
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self) -> None:
        if self.is_valid():
            pass
    
    def load_element(self, element_idx: int) -> bpy.types.Mesh:
        pass

    def __write_to_ballance_elements(self) -> None:
        pass

    def __read_from_ballance_element(self) -> None:
        pass

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
        scene: bpy.types.Scene = context.scene
        
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
            rows = len(_g_AllElementsName) // 2,
            maxrows = len(_g_AllElementsName),
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
