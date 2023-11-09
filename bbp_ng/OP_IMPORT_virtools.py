import bpy
import tempfile
from . import PROP_preferences, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh
from .PyBMap import bmap_wrapper as bmap

class BBP_OT_import_virtools(bpy.types.Operator, UTIL_file_browser.ImportVirtoolsFile):
    """Import Virtools File"""
    bl_idname = "bbp.import_virtools"
    bl_label = "Import Virtools File"
    bl_options = {'PRESET', 'UNDO'}

    vt_encodings: bpy.props.StringProperty(
        name = "Encodings",
        description = "The encoding list used by Virtools engine to resolve object name. Use `;` to split multiple encodings",
        default = "1252"
    )

    @classmethod
    def poll(self, context):
        return (
            PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
            and bmap.is_bmap_available())
    
    def execute(self, context):
        # get encoding, split it by `;` and strip blank chars.
        encodings: str = self.vt_encodings
        _import_virtools(
            self.general_get_filename(),
            tuple(map(lambda x: x.strip(), encodings.split(';')))
        )
        self.report({'INFO'}, "Virtools File Importing Finished.")
        return {'FINISHED'}
    
def _import_virtools(file_name_: str, encodings_: tuple[str]) -> None:
    # create temp folder
    with tempfile.TemporaryDirectory() as vt_temp_folder:
        # create virtools reader context
        with bmap.BMFileReader(
                file_name_, vt_temp_folder,
                PROP_preferences.get_raw_preferences().mBallanceTextureFolder,
                encodings_) as reader:
            pass

def register() -> None:
    bpy.utils.register_class(BBP_OT_import_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_import_virtools)
