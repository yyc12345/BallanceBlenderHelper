import bpy
import os, typing
from . import UTIL_naming_convension

class RawPreferences():
    cBallanceTextureFolder: typing.ClassVar[str] = ""
    cNoComponentCollection: typing.ClassVar[str] = ""
    cDefaultNamingConvention: typing.ClassVar[UTIL_naming_convension.NamingConvention] = UTIL_naming_convension._EnumPropHelper.get_default_naming_identifier()

    mBallanceTextureFolder: str
    mNoComponentCollection: str
    mDefaultNamingConvention: UTIL_naming_convension.NamingConvention

    def __init__(self, **kwargs):
        self.mBallanceTextureFolder = kwargs.get("mBallanceTextureFolder", "")
        self.mNoComponentCollection = kwargs.get("mNoComponentCollection", "")
        self.mDefaultNamingConvention = kwargs.get('mDefaultNamingConvention', UTIL_naming_convension._EnumPropHelper.get_default_naming_identifier())

    def has_valid_blc_tex_folder(self) -> bool:
        return os.path.isdir(self.mBallanceTextureFolder)

class BBPPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    ballance_texture_folder: bpy.props.StringProperty(
        name = "Ballance Texture Folder",
        description = "The path to folder which will be used by this plugin to get external Ballance texture.",
        subtype='DIR_PATH',
        default = RawPreferences.cBallanceTextureFolder,
    )
    
    no_component_collection: bpy.props.StringProperty(
        name = "No Component Collection",
        description = "(Import) The object which stored in this collectiion will not be saved as component. (Export) All forced no component objects will be stored in this collection",
        default = RawPreferences.cNoComponentCollection,
    )

    default_naming_convention: bpy.props.EnumProperty(
        name = "Default Naming Convention",
        description = "The default naming convention when creating objects, import and export BM files.",
        items = UTIL_naming_convension._EnumPropHelper.generate_items(),
        default = UTIL_naming_convension._EnumPropHelper.to_selection(RawPreferences.cDefaultNamingConvention),
    )
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column()
        col.label(text = "Ballance Texture Folder")
        col.prop(self, "ballance_texture_folder", text = "")
        col.label(text = "No Component Collection")
        col.prop(self, "no_component_collection", text = "")
        col.label(text = "Default Naming Convention")
        col.prop(self, "default_naming_convention", text = "")

def get_preferences() -> BBPPreferences:
    return bpy.context.preferences.addons[__package__].preferences

def get_raw_preferences() -> RawPreferences:
    pref: BBPPreferences = get_preferences()
    rawdata: RawPreferences = RawPreferences()

    rawdata.mBallanceTextureFolder = pref.ballance_texture_folder
    rawdata.mNoComponentCollection = pref.no_component_collection
    rawdata.mDefaultNamingConvention = UTIL_naming_convension._EnumPropHelper.get_selection(pref.default_naming_convention)

    return rawdata

def register() -> None:
    bpy.utils.register_class(BBPPreferences)

def unregister() -> None:
    bpy.utils.unregister_class(BBPPreferences)
