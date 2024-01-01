import bpy
import enum
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
    Replace = enum.auto()
_g_ConflictStrategyDesc: dict[ConflictStrategy, tuple[str, str]] = {
    ConflictStrategy.Rename: ('Rename', 'Rename the new one'),
    ConflictStrategy.Current: ('Use Current', 'Use current one'),
    ConflictStrategy.Replace: ('Replace', 'Replace the old one with new one'),
}
_g_EnumHelper_ConflictStrategy: UTIL_functions.EnumPropHelper = UTIL_functions.EnumPropHelper(
    ConflictStrategy,
    lambda x: str(x.value),
    lambda x: ConflictStrategy(int(x)),
    lambda x: _g_ConflictStrategyDesc[x][0],
    lambda x: _g_ConflictStrategyDesc[x][1],
    lambda _: ''
)

class ImportParams():
    texture_conflict_strategy: bpy.props.EnumProperty(
        name = "Texture Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process texture name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Current),
    )

    material_conflict_strategy: bpy.props.EnumProperty(
        name = "Material Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process material name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    )

    mesh_conflict_strategy: bpy.props.EnumProperty(
        name = "Mesh Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process mesh name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    )

    object_conflict_strategy: bpy.props.EnumProperty(
        name = "Object Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process object name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
    )

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

class ExportParams():
    export_mode: bpy.props.EnumProperty(
        name = "Export Mode",
        items = (
            ('COLLECTION', "Collection", "Export a collection", 'OUTLINER_COLLECTION', 0),
            ('OBJECT', "Object", "Export an object", 'OBJECT_DATA', 1),
        ),
    )

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
    )

    def draw_virtools_params(self, layout: bpy.types.UILayout) -> None:
        layout.label(text = 'Encodings')
        layout.prop(self, 'vt_encodings', text = '')

    def general_get_vt_encodings(self) -> tuple[str]:
        # get encoding, split it by `;` and strip blank chars.
        encodings: str = self.vt_encodings
        return tuple(map(lambda x: x.strip(), encodings.split(';')))

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

    This class also provide 3 static common creation functions without considering conflict.
    They just a redirect calling to `bpy.data.xxx.new()`.
    No static texture (Image) creation function because texture is not created from `bpy.data.images`.
    """
    
    @staticmethod
    def create_object(name: str, data: bpy.types.Mesh) -> bpy.types.Object:
        return bpy.data.objects.new(name, data)
    
    @staticmethod
    def create_mesh(name: str) -> bpy.types.Mesh:
        return bpy.data.meshes.new(name)
    
    @staticmethod
    def create_material(name: str) -> bpy.types.Material:
        return bpy.data.materials.new(name)
    
    
