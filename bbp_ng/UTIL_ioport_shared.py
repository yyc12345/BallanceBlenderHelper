import bpy
import enum, typing
from . import UTIL_virtools_types, UTIL_functions
from . import PROP_ptrprop_resolver

## Intent
#  Some importer or exporter may share same properties.
#  So we create some shared class and user just need inherit them 
#  and call general getter to get user selected data.
#  Also provide draw function thus caller do not need draw the params themselves.

class ConflictStrategy(enum.IntEnum):
    Rename = enum.auto()
    Current = enum.auto()
_g_ConflictStrategyDesc: dict[ConflictStrategy, tuple[str, str]] = {
    ConflictStrategy.Rename: ('Rename', 'Rename the new one'),
    ConflictStrategy.Current: ('Use Current', 'Use current one'),
}
_g_EnumHelper_ConflictStrategy: UTIL_functions.EnumPropHelper = UTIL_functions.EnumPropHelper(
    ConflictStrategy,
    lambda x: str(x.value),
    lambda x: ConflictStrategy(int(x)),
    lambda x: _g_ConflictStrategyDesc[x][0],
    lambda x: _g_ConflictStrategyDesc[x][1],
    lambda _: ''
)

#region Assist Classes

class ExportEditModeBackup():
    """
    The class which save Edit Mode when exporting and restore it after exporting.
    Because edit mode is not allowed when exporting.
    Support `with` statement.

    ```
    with ExportEditModeBackup():
        # do some exporting work
        blabla()
    # restore automatically when exiting "with"
    ```
    """
    mInEditMode: bool

    def __init__(self):
        if bpy.context.object and bpy.context.object.mode == "EDIT":
            # set and toggle it. otherwise exporting will failed.
            self.mInEditMode = True
            bpy.ops.object.editmode_toggle()
        else:
            self.mInEditMode = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.mInEditMode:
            bpy.ops.object.editmode_toggle()
            self.mInEditMode = False
    
class ConflictResolver():
    """
    This class frequently used when importing objects.
    This class accept 4 conflict strategies for object, mesh, material and texture,
    and provide 4 general creation functions to handle these strategies.
    Each general creation functions will return an instance and a bool indicating whether this instance need be initialized.
    """
    
    __mObjectStrategy: ConflictStrategy
    __mMeshStrategy: ConflictStrategy
    __mMaterialStrategy: ConflictStrategy
    __mTextureStrategy: ConflictStrategy

    def __init__(self, obj_strategy: ConflictStrategy, mesh_strategy: ConflictStrategy, mtl_strategy: ConflictStrategy, tex_strategy: ConflictStrategy):
        self.__mObjectStrategy = obj_strategy
        self.__mMeshStrategy = mesh_strategy
        self.__mMaterialStrategy = mtl_strategy
        self.__mTextureStrategy = tex_strategy

    def create_object(self, name: str, data: bpy.types.Mesh) -> tuple[bpy.types.Object, bool]:
        """
        Create object according to conflict strategy.
        `data` will only be applied when creating new object (no existing instance or strategy order rename)
        """
        if self.__mObjectStrategy == ConflictStrategy.Current:
            old: bpy.types.Object | None = bpy.data.objects.get(name, None)
            if old is not None:
                return (old, False)
        return (bpy.data.objects.new(name, data), True)
    
    def create_mesh(self, name: str) -> tuple[bpy.types.Mesh, bool]:
        if self.__mMeshStrategy == ConflictStrategy.Current:
            old: bpy.types.Mesh | None = bpy.data.meshes.get(name, None)
            if old is not None:
                return (old, False)
        return (bpy.data.meshes.new(name), True)
    
    def create_material(self, name: str) -> tuple[bpy.types.Material, bool]:
        if self.__mMaterialStrategy == ConflictStrategy.Current:
            old: bpy.types.Material | None = bpy.data.materials.get(name, None)
            if old is not None:
                return (old, False)
        return (bpy.data.materials.new(name), True)
    
    def create_texture(self, name: str, fct_cret: typing.Callable[[], bpy.types.Image]) -> tuple[bpy.types.Image, bool]:
        """
        Create texture according to conflict strategy.
        If the strategy order current, it will return current existing instance.
        If no existing instance or strategy order rename, it will call `fct_cret` to create new texture.

        Because texture do not have a general creation function, we frequently create it by other modules provided texture functions.
        So `fct_cret` is the real creation function. And it will not be executed if no creation happended.
        """
        if self.__mTextureStrategy == ConflictStrategy.Current:
            old: bpy.types.Image | None = bpy.data.images.get(name, None)
            if old is not None:
                return (old, False)
        # create texture, set name, and return
        tex: bpy.types.Image = fct_cret()
        tex.name = name
        return (tex, True)

#endregion

class ImportParams():
    texture_conflict_strategy: bpy.props.EnumProperty(
        name = "Texture Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process texture name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Current),
    ) # type: ignore

    material_conflict_strategy: bpy.props.EnumProperty(
        name = "Material Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process material name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    ) # type: ignore

    mesh_conflict_strategy: bpy.props.EnumProperty(
        name = "Mesh Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process mesh name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    ) # type: ignore

    object_conflict_strategy: bpy.props.EnumProperty(
        name = "Object Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process object name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    ) # type: ignore

    def draw_import_params(self, layout: bpy.types.UILayout) -> None:
        layout.label(text = 'Object Name Conflict')
        layout.prop(self, 'object_conflict_strategy', text = '')
        layout.label(text = 'Mesh Name Conflict')
        layout.prop(self, 'mesh_conflict_strategy', text = '')
        layout.label(text = 'Material Name Conflict')
        layout.prop(self, 'material_conflict_strategy', text = '')
        layout.label(text = 'Texture Name Conflict')
        layout.prop(self, 'texture_conflict_strategy', text = '')

    def general_get_texture_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.texture_conflict_strategy)

    def general_get_material_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.material_conflict_strategy)

    def general_get_mesh_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.mesh_conflict_strategy)

    def general_get_object_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.object_conflict_strategy)

    def general_get_conflict_resolver(self) -> ConflictResolver:
        return ConflictResolver(
            self.general_get_object_conflict_strategy(),
            self.general_get_mesh_conflict_strategy(),
            self.general_get_material_conflict_strategy(),
            self.general_get_texture_conflict_strategy()
        )

class ExportParams():
    export_mode: bpy.props.EnumProperty(
        name = "Export Mode",
        items = (
            ('COLLECTION', "Collection", "Export a collection", 'OUTLINER_COLLECTION', 0),
            ('OBJECT', "Object", "Export an object", 'OBJECT_DATA', 1),
        ),
    ) # type: ignore

    def draw_export_params(self, layout: bpy.types.UILayout) -> None:
        # make prop expand horizontaly, not vertical.
        sublayout = layout.row()
        # draw switch
        sublayout.prop(self, "export_mode", expand = True)

        # draw picker
        if self.export_mode == 'COLLECTION':
            PROP_ptrprop_resolver.draw_export_collection(layout)
        elif self.export_mode == 'OBJECT':
            PROP_ptrprop_resolver.draw_export_object(layout)

    def general_get_export_objects(self) -> tuple[bpy.types.Object] | None:
        """
        Return resolved exported objects or None if no selection.
        """
        if self.export_mode == 'COLLECTION':
            col: bpy.types.Collection = PROP_ptrprop_resolver.get_export_collection()
            if col is None: return None
            else:
                return tuple(col.all_objects)
        else:
            obj: bpy.types.Object = PROP_ptrprop_resolver.get_export_object()
            if obj is None: return None
            else: return (obj, )

class VirtoolsParams():
    vt_encodings: bpy.props.StringProperty(
        name = "Encodings",
        description = "The encoding list used by Virtools engine to resolve object name. Use `;` to split multiple encodings",
        default = UTIL_virtools_types.g_PyBMapDefaultEncoding
    ) # type: ignore

    def draw_virtools_params(self, layout: bpy.types.UILayout) -> None:
        layout.label(text = 'Encodings')
        layout.prop(self, 'vt_encodings', text = '')

    def general_get_vt_encodings(self) -> tuple[str]:
        # get encoding, split it by `;` and strip blank chars.
        encodings: str = self.vt_encodings
        return tuple(map(lambda x: x.strip(), encodings.split(';')))
