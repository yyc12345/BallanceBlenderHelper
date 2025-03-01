import bpy
import typing, enum, copy
from . import PROP_virtools_material, PROP_virtools_texture
from . import UTIL_ballance_texture, UTIL_functions, UTIL_icons_manager

#region BME Material Presets

class _BMEMaterialPreset():
    ## Associated Ballance texture file name, including file extension.
    mTexName: str
    ## Predefined mtl preset in virtools material module
    mRawMtl: PROP_virtools_material.RawVirtoolsMaterial

    def __init__(self, texname: str, rawmtl: PROP_virtools_material.RawVirtoolsMaterial):
        self.mTexName = texname
        self.mRawMtl = rawmtl

_g_BMEMaterialPresets: dict[str, _BMEMaterialPreset] = {
    'FloorSide': _BMEMaterialPreset(
        'Floor_Side.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorSide).mData
    ),
    'LightingFloorTopBorder': _BMEMaterialPreset(
        'Floor_Top_Border.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorSide).mData
    ),
    'LightingFloorTopBorderless': _BMEMaterialPreset(
        'Floor_Top_Borderless.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorSide).mData
    ),

    'FloorTopBorder': _BMEMaterialPreset(
        'Floor_Top_Border.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorTop).mData
    ),
    'FloorTopBorderless': _BMEMaterialPreset(
        'Floor_Top_Borderless.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorTop).mData
    ),
    'FloorTopFlat': _BMEMaterialPreset(
        'Floor_Top_Flat.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorTop).mData
    ),
    'FloorTopProfil': _BMEMaterialPreset(
        'Floor_Top_Profil.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorTop).mData
    ),
    'FloorTopProfilFlat': _BMEMaterialPreset(
        'Floor_Top_ProfilFlat.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.FloorTop).mData
    ),

    'BallPaper': _BMEMaterialPreset(
        'Ball_Paper.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.TrafoPaper).mData
    ),

    'BallStone': _BMEMaterialPreset(
        'Ball_Stone.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.TraforWoodStone).mData
    ),
    'BallWood': _BMEMaterialPreset(
        'Ball_Wood.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.TraforWoodStone).mData
    ),

    'Rail': _BMEMaterialPreset(
        'Rail_Environment.bmp', 
        PROP_virtools_material.get_virtools_material_preset(PROP_virtools_material.MaterialPresetType.Rail).mData
    ),
}

#endregion

#region BME Material Define & Visitor

class BBP_PG_bme_material(bpy.types.PropertyGroup):
    bme_material_name: bpy.props.StringProperty(
        name = "Name",
        default = "",
        translation_context = 'BBP_PG_bme_material/property'
    ) # type: ignore
    
    material_ptr: bpy.props.PointerProperty(
        name = "Material",
        type = bpy.types.Material,
        translation_context = 'BBP_PG_bme_material/property'
    ) # type: ignore

def get_bme_materials(scene: bpy.types.Scene) -> UTIL_functions.CollectionVisitor[BBP_PG_bme_material]:
    return UTIL_functions.CollectionVisitor(scene.bme_materials)

#endregion

#region Material Preset Loader

def _load_bme_material_preset(mtl: bpy.types.Material, preset_name: str) -> None:
    # get preset first
    preset: _BMEMaterialPreset = _g_BMEMaterialPresets[preset_name]

    # get raw mtl and do a shallow copy
    # because we will change something later. but do not want to affect preset self.
    raw_mtl: PROP_virtools_material.RawVirtoolsMaterial = copy.copy(preset.mRawMtl)

    # load ballance texture
    blctex: bpy.types.Image = UTIL_ballance_texture.load_ballance_texture(preset.mTexName)
    # apply texture props
    PROP_virtools_texture.set_raw_virtools_texture(blctex, PROP_virtools_texture.get_ballance_texture_preset(preset.mTexName))
    # set loaded texture to shallow copied raw mtl
    raw_mtl.mTexture = blctex

    # set raw mtl
    PROP_virtools_material.set_raw_virtools_material(mtl, raw_mtl)
    # apply vt mtl to blender mtl
    PROP_virtools_material.apply_to_blender_material(mtl)

#endregion

#region BME Material Operation Help Class & Functions

class BMEMaterialsHelper():
    """
    The helper of BME materials processing.

    All BME materials operations, including getting or setting, must be manipulated by this class. 
    You should NOT operate BME Materials property (in Scene) directly.

    This class should only have 1 instance at the same time. This class support `with` syntax to achieve this.
    This class frequently used in creating BME meshes.
    """
    __mSingletonMutex: typing.ClassVar[UTIL_functions.TinyMutex[bpy.types.Scene]] = UTIL_functions.TinyMutex()
    __mIsValid: bool
    __mAssocScene: bpy.types.Scene
    __mMaterialMap: dict[str, bpy.types.Material]

    def __init__(self, assoc: bpy.types.Scene):
        self.__mMaterialMap = {}
        self.__mAssocScene = assoc
        self.__mIsValid = False

        # check singleton
        BMEMaterialsHelper.__mSingletonMutex.lock(self.__mAssocScene)
        # set validation and read ballance elements property
        self.__mIsValid = True
        self.__read_from_bme_materials()

    def is_valid(self) -> bool:
        return self.__mIsValid
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self) -> None:
        if self.is_valid():
            # write to ballance elements property and reset validation
            self.__write_to_bme_materials()
            self.__mIsValid = False
            BMEMaterialsHelper.__mSingletonMutex.unlock(self.__mAssocScene)
    
    def get_material(self, preset_name: str) -> bpy.types.Material:
        if not self.is_valid():
            raise UTIL_functions.BBPException('calling invalid BMEMaterialsHelper')
        
        # get exist one
        mtl: bpy.types.Material | None = self.__mMaterialMap.get(preset_name, None)
        if mtl is not None: 
            return mtl

        # if no existing one, create new one
        new_mtl_name: str = 'BME' + preset_name
        new_mtl: bpy.types.Material = bpy.data.materials.new(new_mtl_name)

        _load_bme_material_preset(new_mtl, preset_name)
        self.__mMaterialMap[preset_name] = new_mtl
        return new_mtl

    def reset_materials(self) -> None:
        if not self.is_valid():
            raise UTIL_functions.BBPException('calling invalid BMEMaterialsHelper')
        
        # load all items
        for preset_name, mtl in self.__mMaterialMap.items():
            _load_bme_material_preset(mtl, preset_name)

    def __write_to_bme_materials(self) -> None:
        mtls = get_bme_materials(self.__mAssocScene)
        mtls.clear()

        for preset_name, mtl in self.__mMaterialMap.items():
            item: BBP_PG_bme_material = mtls.add()
            item.bme_material_name = preset_name
            item.material_ptr = mtl

    def __read_from_bme_materials(self) -> None:
        mtls = get_bme_materials(self.__mAssocScene)
        self.__mMaterialMap.clear()

        for item in mtls:
            # check requirements
            if item.material_ptr is None: continue
            # add into map
            self.__mMaterialMap[item.bme_material_name] = item.material_ptr

#endregion

#region BME Materials Representation

class BBP_UL_bme_materials(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item: BBP_PG_bme_material, icon, active_data, active_propname):
        # check requirements
        if item.material_ptr is None: return
        # draw list item
        layout.label(text = item.bme_material_name, translate = False)
        layout.label(text = item.material_ptr.name, translate = False, icon = 'MATERIAL')

class BBP_OT_reset_bme_materials(bpy.types.Operator):
    """Reset all BME Materials to Default Settings."""
    bl_idname = "bbp.reset_bme_materials"
    bl_label = "Reset BME Materials"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_reset_bme_materials'
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def execute(self, context):
        with BMEMaterialsHelper(context.scene) as helper:
            helper.reset_materials()
        # show a window to let user know, not silence
        self.report({'INFO'}, 'Reset BME materials successfully.')
        return {'FINISHED'}

class BBP_PT_bme_materials(bpy.types.Panel):
    """Show BME Materials Properties."""
    bl_label = "BME Materials"
    bl_idname = "BBP_PT_bme_materials"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_translation_context = 'BBP_PT_bme_materials'

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        target: bpy.types.Scene = context.scene
        col = layout.column()

        # show restore operator
        opercol = col.column()
        opercol.operator(BBP_OT_reset_bme_materials.bl_idname, icon='LOOP_BACK')

        # show list but not allowed to edit
        listcol = col.column()
        listcol.enabled = False
        listcol.template_list(
            "BBP_UL_bme_materials", "", 
            target, "bme_materials", 
            target, "active_bme_materials",
            # default row height is a half of the count of all presets
            # limit the max row height to the the count of all presets
            rows = len(_g_BMEMaterialPresets) // 2,
            maxrows = len(_g_BMEMaterialPresets),
        )

#endregion

def register() -> None:
    # register all classes
    bpy.utils.register_class(BBP_PG_bme_material)
    bpy.utils.register_class(BBP_UL_bme_materials)
    bpy.utils.register_class(BBP_OT_reset_bme_materials)
    bpy.utils.register_class(BBP_PT_bme_materials)
    
    # add into scene metadata
    bpy.types.Scene.bme_materials = bpy.props.CollectionProperty(type = BBP_PG_bme_material)
    bpy.types.Scene.active_bme_materials = bpy.props.IntProperty()

def unregister() -> None:
    # del from scene metadata
    del bpy.types.Scene.active_bme_materials
    del bpy.types.Scene.bme_materials

    bpy.utils.unregister_class(BBP_PT_bme_materials)
    bpy.utils.unregister_class(BBP_OT_reset_bme_materials)
    bpy.utils.unregister_class(BBP_UL_bme_materials)
    bpy.utils.unregister_class(BBP_PG_bme_material)

