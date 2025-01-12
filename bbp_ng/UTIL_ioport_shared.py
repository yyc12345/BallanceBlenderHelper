import bpy
import enum, typing
from . import UTIL_virtools_types, UTIL_functions
from . import PROP_ptrprop_resolver, PROP_ballance_map_info

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
    __mLightStrategy: ConflictStrategy
    __mMeshStrategy: ConflictStrategy
    __mMaterialStrategy: ConflictStrategy
    __mTextureStrategy: ConflictStrategy

    def __init__(self, 
            obj_strategy: ConflictStrategy, 
            light_strategy: ConflictStrategy, 
            mesh_strategy: ConflictStrategy, 
            mtl_strategy: ConflictStrategy, 
            tex_strategy: ConflictStrategy):
        self.__mObjectStrategy = obj_strategy
        self.__mLightStrategy = light_strategy
        self.__mMeshStrategy = mesh_strategy
        self.__mMaterialStrategy = mtl_strategy
        self.__mTextureStrategy = tex_strategy

    def create_object(self, name: str, data: bpy.types.Mesh | None) -> tuple[bpy.types.Object, bool]:
        """
        Create object according to conflict strategy.
        `data` will only be applied when creating new object (no existing instance or strategy order rename).

        Please note this function is only used to create mesh 3d object.
        If you want to create light object, please use other functions provided by this class.
        The 3d object and data block of light is created together.
        """
        if self.__mObjectStrategy == ConflictStrategy.Current:
            old: bpy.types.Object | None = bpy.data.objects.get(name, None)
            if old is not None:
                return (old, False)
        return (bpy.data.objects.new(name, data), True)
    
    def create_light(self, name: str) -> tuple[bpy.types.Object, bpy.types.Light, bool]:
        """
        Create light data block and associated 3d object.

        If conflict strategy is "Current", we try fetch 3d object with given name first,
        then check whether it is light.
        If no given name object or this object is not light, we create a new one,
        otherwise return old one.
        """
        if self.__mLightStrategy == ConflictStrategy.Current:
            old_obj: bpy.types.Object | None = bpy.data.objects.get(name, None)
            if old_obj is not None and old_obj.type == 'LIGHT':
                return (old_obj, typing.cast(bpy.types.Light, old_obj.data), False)
        # create new object.
        # if object or light name is conflict, rename it directly without considering conflict strategy.
        # create light with default point light type
        new_light: bpy.types.Light = bpy.data.lights.new(name, 'POINT')
        new_obj: bpy.types.Object = bpy.data.objects.new(name, new_light)
        return (new_obj, new_light, True)

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
        translation_context = 'BBP/UTIL_ioport_shared.ImportParams/property'
    ) # type: ignore

    material_conflict_strategy: bpy.props.EnumProperty(
        name = "Material Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process material name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
        translation_context = 'BBP/UTIL_ioport_shared.ImportParams/property'
    ) # type: ignore

    mesh_conflict_strategy: bpy.props.EnumProperty(
        name = "Mesh Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process mesh name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
        translation_context = 'BBP/UTIL_ioport_shared.ImportParams/property'
    ) # type: ignore

    light_conflict_strategy: bpy.props.EnumProperty(
        name = "Light Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process light name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
        translation_context = 'BBP/UTIL_ioport_shared.ImportParams/property'
    ) # type: ignore

    object_conflict_strategy: bpy.props.EnumProperty(
        name = "Object Name Conflict",
        items = _g_EnumHelper_ConflictStrategy.generate_items(),
        description = "Define how to process object name conflict",
        default = _g_EnumHelper_ConflictStrategy.to_selection(ConflictStrategy.Rename),
        translation_context = 'BBP/UTIL_ioport_shared.ImportParams/property'
    ) # type: ignore

    def draw_import_params(self, layout: bpy.types.UILayout) -> None:
        header: bpy.types.UILayout
        body: bpy.types.UILayout
        header, body = layout.panel("BBP_PT_ioport_shared_import_params", default_closed=False)
        header.label(text='Import Parameters', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        # NOTE: if panel is collapsed, body will be None. So we need check it.
        if body is None: return

        body.label(text='Name Conflict Strategy', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid = body.grid_flow(row_major=False, columns=2)
        grid.label(text='Object', icon='CUBE', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid.label(text='Light', icon='LIGHT', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid.label(text='Mesh', icon='MESH_DATA', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid.label(text='Material', icon='MATERIAL', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid.label(text='Texture', icon='TEXTURE', text_ctxt='BBP/UTIL_ioport_shared.ImportParams/draw')
        grid.prop(self, 'object_conflict_strategy', text='')
        grid.prop(self, 'light_conflict_strategy', text='')
        grid.prop(self, 'mesh_conflict_strategy', text='')
        grid.prop(self, 'material_conflict_strategy', text='')
        grid.prop(self, 'texture_conflict_strategy', text='')

    def general_get_texture_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.texture_conflict_strategy)

    def general_get_material_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.material_conflict_strategy)

    def general_get_mesh_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.mesh_conflict_strategy)

    def general_get_light_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.light_conflict_strategy)

    def general_get_object_conflict_strategy(self) -> ConflictStrategy:
        return _g_EnumHelper_ConflictStrategy.get_selection(self.object_conflict_strategy)

    def general_get_conflict_resolver(self) -> ConflictResolver:
        return ConflictResolver(
            self.general_get_object_conflict_strategy(),
            self.general_get_light_conflict_strategy(),
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
        translation_context = 'BBP/UTIL_ioport_shared.ExportParams/property'
    ) # type: ignore

    def draw_export_params(self, context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
        header: bpy.types.UILayout
        body: bpy.types.UILayout
        header, body = layout.panel("BBP_PT_ioport_shared_export_params", default_closed=False)
        header.label(text='Export Parameters', text_ctxt='BBP/UTIL_ioport_shared.ExportParams/draw')
        if body is None: return

        # make prop expand horizontaly, not vertical.
        horizon_body = body.row()
        # draw switch
        horizon_body.prop(self, "export_mode", expand=True)

        # draw picker
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        if self.export_mode == 'COLLECTION':
            ptrprops.draw_export_collection(body)
        elif self.export_mode == 'OBJECT':
            ptrprops.draw_export_object(body)

    def general_get_export_objects(self, context: bpy.types.Context) -> tuple[bpy.types.Object] | None:
        """
        Return resolved exported objects or None if no selection.
        """
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        if self.export_mode == 'COLLECTION':
            col: bpy.types.Collection = ptrprops.get_export_collection()
            if col is None: return None
            else:
                return tuple(col.all_objects)
        else:
            obj: bpy.types.Object = ptrprops.get_export_object()
            if obj is None: return None
            else: return (obj, )

# define global tex save opt blender enum prop helper
_g_EnumHelper_CK_TEXTURE_SAVEOPTIONS: UTIL_virtools_types.EnumPropHelper = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS)

class VirtoolsParams():
    texture_save_opt: bpy.props.EnumProperty(
        name = "Global Texture Save Options",
        description = "Decide how texture saved if texture is specified as Use Global as its Save Options.",
        items = _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.generate_items(),
        default = _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.to_selection(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL),
        translation_context = 'BBP/UTIL_ioport_shared.VirtoolsParams/property'
    ) # type: ignore

    use_compress: bpy.props.BoolProperty(
        name="Use Compress",
        description = "Whether use ZLib to compress result when saving composition.",
        default = True,
        translation_context = 'BBP/UTIL_ioport_shared.VirtoolsParams/property'
    ) # type: ignore

    compress_level: bpy.props.IntProperty(
        name = "Compress Level",
        description = "The ZLib compress level used by Virtools Engine when saving composition.",
        min = 1, max = 9,
        default = 5,
        translation_context = 'BBP/UTIL_ioport_shared.VirtoolsParams/property'
    ) # type: ignore

    def draw_virtools_params(self, context: bpy.types.Context, layout: bpy.types.UILayout, is_importer: bool) -> None:
        header: bpy.types.UILayout
        body: bpy.types.UILayout
        header, body = layout.panel("BBP_PT_ioport_shared_virtools_params", default_closed=False)
        header.label(text='Virtools Parameters', text_ctxt='BBP/UTIL_ioport_shared.VirtoolsParams/draw')
        if body is None: return

        # draw encodings
        body.label(text='Encodings', text_ctxt='BBP/UTIL_ioport_shared.VirtoolsParams/draw')
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        ptrprops.draw_ioport_encodings(body)

        # following field are only valid in exporter
        if not is_importer:
            body.separator()
            body.label(text='Global Texture Save Options', text_ctxt='BBP/UTIL_ioport_shared.VirtoolsParams/draw')
            body.prop(self, 'texture_save_opt', text='')

            body.separator()
            body.label(text='Compression', text_ctxt='BBP/UTIL_ioport_shared.VirtoolsParams/draw')
            body.prop(self, 'use_compress')
            if self.use_compress:
                body.prop(self, 'compress_level')


    def general_get_vt_encodings(self, context: bpy.types.Context) -> tuple[str, ...]:
        # get from ptrprop resolver then filter empty item
        ptrprops = PROP_ptrprop_resolver.PropsVisitor(context.scene)
        return tuple(filter(lambda encoding: len(encoding) != 0, ptrprops.get_ioport_encodings()))

    def general_get_texture_save_opt(self) -> UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS:
        return _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.get_selection(self.texture_save_opt)

    def general_get_use_compress(self) -> bool:
        return self.use_compress

    def general_get_compress_level(self) -> int:
        return self.compress_level
    
class BallanceParams():
    successive_sector: bpy.props.BoolProperty(
        name="Successive Sector",
        description = "Whether order exporter to use document specified sector count to make sure sector is successive.",
        default = True,
        translation_context = 'BBP/UTIL_ioport_shared.BallanceParams/property'
    ) # type: ignore

    def draw_ballance_params(self, layout: bpy.types.UILayout, is_importer: bool) -> None:
        # ballance params only presented in exporter.
        # so if we are in impoerter, we skip the whole function
        # because we don't want to create an empty panel.
        if is_importer: return

        header: bpy.types.UILayout
        body: bpy.types.UILayout
        header, body = layout.panel("BBP_PT_ioport_shared_ballance_params", default_closed=False)
        header.label(text='Ballance Parameters', text_ctxt='BBP/UTIL_ioport_shared.BallanceParams/draw')
        if body is None: return

        map_info: PROP_ballance_map_info.RawBallanceMapInfo = PROP_ballance_map_info.get_raw_ballance_map_info(bpy.context.scene)
        body.prop(self, 'successive_sector')
        tr_text: str = bpy.app.translations.pgettext_iface(
            'Map Sectors: {0}', 'BBP/UTIL_ioport_shared.BallanceParams/draw')
        body.label(text=tr_text.format(map_info.mSectorCount), translate=False)

    def general_get_successive_sector(self) -> bool:
        return self.successive_sector

    def general_get_successive_sector_count(self) -> int:
        # if user do not pick successive sector, return a random int directly.
        if not self.general_get_successive_sector():
            return 0
        
        # otherwise fetch user specified sector number
        map_info: PROP_ballance_map_info.RawBallanceMapInfo
        map_info = PROP_ballance_map_info.get_raw_ballance_map_info(bpy.context.scene)
        return map_info.mSectorCount
