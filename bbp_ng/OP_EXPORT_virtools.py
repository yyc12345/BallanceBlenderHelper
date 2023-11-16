import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport
import tempfile, os, typing
from . import PROP_preferences, PROP_ptrprop_resolver, UTIL_ioport_shared
from . import UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_icons_manager
from .PyBMap import bmap_wrapper as bmap

class BBP_OT_export_virtools(bpy.types.Operator, UTIL_file_browser.ExportVirtoolsFile, UTIL_ioport_shared.ExportParams, UTIL_ioport_shared.VirtoolsParams):
    """Export Virtools File"""
    bl_idname = "bbp.export_virtools"
    bl_label = "Export Virtools File"
    bl_options = {'PRESET'}

    @classmethod
    def poll(self, context):
        return (
            PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
            and bmap.is_bmap_available())
    
    def execute(self, context):
        # check selecting first
        objls: tuple[bpy.types.Object] | None = self.general_get_export_objects()
        if objls is None:
            UTIL_functions.message_box(
                ('No selected target!', ), 
                'Lost Parameters', 
                UTIL_icons_manager.BlenderPresetIcons.Error.value
            )
            return {'CANCELLED'}

        # start exporting
        with UTIL_ioport_shared.ExportEditModeBackup() as editmode_guard:
            _export_virtools(
                self.general_get_filename(),
                self.general_get_vt_encodings(),
                objls
            )

        self.report({'INFO'}, "Virtools File Exporting Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Export Target')
        self.draw_export_params(layout)
        layout.separator()
        layout.label(text = 'Virtools Params')
        self.draw_virtools_params(layout)

def _export_virtools(file_name_: str, encodings_: tuple[str], export_objects: tuple[bpy.types.Object]) -> None:
    # create temp folder
    with tempfile.TemporaryDirectory() as vt_temp_folder:
        print(f'Virtools Engine Temp: {vt_temp_folder}')

        # create virtools reader context
        with bmap.BMFileWriter(
            vt_temp_folder,
            PROP_preferences.get_raw_preferences().mBallanceTextureFolder,
            encodings_) as writer:

            # prepare progress reporter
            with ProgressReport(wm = bpy.context.window_manager) as progress:
                pass


def register() -> None:
    bpy.utils.register_class(BBP_OT_export_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_virtools)
