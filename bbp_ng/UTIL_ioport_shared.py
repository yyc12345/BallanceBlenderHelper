import bpy
import enum
from . import UTIL_functions
from . import PROP_ptrprop_resolver

## Intent
#  Some importer or exporter may share same properties.
#  So we create some shared class and user just need inherit them 
#  and call general getter to get user selected data.
#  Also provide draw function thus caller do not need draw the params themselves.

class ImportParams():
    texture_conflict_strategy: bpy.props.EnumProperty(
        name = "Texture name conflict",
        items = (
            ('NEW', "New Instance", "Create a new instance"),
            ('CURRENT', "Use Current", "Use current one"),
        ),
        description = "Define how to process texture name conflict",
        default = 'CURRENT',
        )

    material_conflict_strategy: bpy.props.EnumProperty(
        name = "Material name conflict",
        items = (
            ('RENAME', "Rename", "Rename the new one"),
            ('CURRENT', "Use Current", "Use current one"),
        ),
        description = "Define how to process material name conflict",
        default = 'RENAME',
        )

    mesh_conflict_strategy: bpy.props.EnumProperty(
        name = "Mesh name conflict",
        items = (
            ('RENAME', "Rename", "Rename the new one"),
            ('CURRENT', "Use Current", "Use current one"),
        ),
        description = "Define how to process mesh name conflict",
        default = 'RENAME',
        )

    object_conflict_strategy: bpy.props.EnumProperty(
        name = "Object name conflict",
        items = (
            ('RENAME', "Rename", "Rename the new one"),
            ('CURRENT', "Use Current", "Use current one"),
        ),
        description = "Define how to process object name conflict",
        default = 'RENAME',
        )

    def draw_import_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'object_conflict_strategy')
        layout.prop(self, 'mesh_conflict_strategy')
        layout.prop(self, 'material_conflict_strategy')
        layout.prop(self, 'texture_conflict_strategy')

class ExportParams():
    export_mode: bpy.props.EnumProperty(
        name = "Export Mode",
        items = (
            ('COLLECTION', "Collection", "Export a collection"),
            ('OBJECT', "Object", "Export an object"),
        ),
    )

    def draw_export_params(self, layout: bpy.types.UILayout) -> None:
        # draw switch
        layout.prop(self, "export_mode", expand = True)
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
        default = UTIL_functions.g_PyBMapDefaultEncoding
    )

    def draw_virtools_params(self, layout: bpy.types.UILayout) -> None:
        layout.prop(self, 'vt_encodings')

    def general_get_vt_encodings(self) -> tuple[str]:
        # get encoding, split it by `;` and strip blank chars.
        encodings: str = self.vt_encodings
        return tuple(map(lambda x: x.strip(), encodings.split(';')))

class ExportEditModeBackup():
    """
    The class which save Edit Mode when exporting and restore it after exporting.
    Because edit mode is not allowed when exporting.
    Support `with` statement.
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
    
    
