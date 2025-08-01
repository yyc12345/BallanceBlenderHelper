import bpy
import os, typing
from . import UTIL_naming_convention

class RawPreferences():
    cBallanceTextureFolder: typing.ClassVar[str] = ""
    cNoComponentCollection: typing.ClassVar[str] = ""

    mBallanceTextureFolder: str
    mNoComponentCollection: str

    def __init__(self, **kwargs):
        self.mBallanceTextureFolder = kwargs.get("mBallanceTextureFolder", "")
        self.mNoComponentCollection = kwargs.get("mNoComponentCollection", "")

    def has_valid_blc_tex_folder(self) -> bool:
        return os.path.isdir(self.mBallanceTextureFolder)

class BBPPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    
    ballance_texture_folder: bpy.props.StringProperty(
        name = "Ballance Texture Folder",
        description = "The path to folder which will be used by this plugin to get external Ballance texture.",
        subtype = 'DIR_PATH',
        default = RawPreferences.cBallanceTextureFolder,
        translation_context = 'BBPPreferences/property'
    ) # type: ignore
    
    no_component_collection: bpy.props.StringProperty(
        name = "No Component Collection",
        description = "When importing, it is the name of collection where objects store will not be saved as component. When exporting, all forced no component objects will be stored in this name represented collection",
        default = RawPreferences.cNoComponentCollection,
        translation_context = 'BBPPreferences/property'
    ) # type: ignore
    
    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        
        row = layout.row()
        col = row.column()
        col.label(text="Ballance Texture Folder", text_ctxt='BBPPreferences/draw')
        col.prop(self, "ballance_texture_folder", text = "")
        col.label(text="No Component Collection", text_ctxt='BBPPreferences/draw')
        col.prop(self, "no_component_collection", text = "")

def get_preferences() -> BBPPreferences:
    return bpy.context.preferences.addons[__package__].preferences

def get_raw_preferences() -> RawPreferences:
    pref: BBPPreferences = get_preferences()
    rawdata: RawPreferences = RawPreferences()

    rawdata.mBallanceTextureFolder = pref.ballance_texture_folder
    rawdata.mNoComponentCollection = pref.no_component_collection

    return rawdata

def register() -> None:
    bpy.utils.register_class(BBPPreferences)

def unregister() -> None:
    bpy.utils.unregister_class(BBPPreferences)
