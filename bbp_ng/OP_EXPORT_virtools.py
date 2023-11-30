import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport
import tempfile, os, typing
from . import PROP_preferences, UTIL_ioport_shared
from . import UTIL_virtools_types, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_ballance_texture, UTIL_icons_manager
from . import PROP_virtools_group, PROP_virtools_material, PROP_virtools_mesh
from .PyBMap import bmap_wrapper as bmap

class BBP_OT_export_virtools(bpy.types.Operator, UTIL_file_browser.ExportVirtoolsFile, UTIL_ioport_shared.ExportParams, UTIL_ioport_shared.VirtoolsParams):
    """Export Virtools File"""
    bl_idname = "bbp.export_virtools"
    bl_label = "Export Virtools File"
    bl_options = {'PRESET'}

    compress_level: bpy.props.IntProperty(
        name = "Compress Level",
        description = "The ZLib compress level used by Virtools Engine when saving composition.",
        min = 1, max = 9,
        default = 5,
    )

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
                self.compress_level,
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
        layout.prop(self, 'compress_level')

def _export_virtools(file_name_: str, encodings_: tuple[str], compress_level_: int, export_objects: tuple[bpy.types.Object, ...]) -> None:
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
                # prepare 3dobject
                obj3d_crets: tuple[tuple[bpy.types.Object, bmap.BM3dObject], ...] = _prepare_virtools_3dobjects(
                    writer, progress, export_objects)
                # export group and 3dobject by prepared 3dobject
                _export_virtools_groups(writer, progress, obj3d_crets)
                mesh_crets: tuple[tuple[bpy.types.Object, bpy.types.Mesh, bmap.BMMesh], ...] = _export_virtools_3dobjects(
                    writer, progress, obj3d_crets)
                

                # save document
                _save_virtools_document(
                    writer, progress, file_name_, compress_level_)

def _prepare_virtools_3dobjects(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        export_objects: tuple[bpy.types.Object]
        ) -> tuple[tuple[bpy.types.Object, bmap.BM3dObject], ...]:
    # this function only create equvalent entries in virtools engine and do not export anything
    # because _export_virtools_3dobjects() and _export_virtools_groups() are need use the return value of this function

    # create 3dobject hashset and result
    obj3d_crets: list[tuple[bpy.types.Object, bmap.BM3dObject]] = []
    obj3d_cret_set: set[bpy.types.Object] = set()
    # start saving
    progress.enter_substeps(len(export_objects), "Creating 3dObjects")

    for obj3d in export_objects:
        if obj3d not in obj3d_cret_set:
            # add into set
            obj3d_cret_set.add(obj3d)
            # create virtools instance
            vtobj3d: bmap.BM3dObject = writer.create_3dobject()
            # add into result list
            obj3d_crets.append((obj3d, vtobj3d))
        
        # step progress no matter whether create new one
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return tuple(obj3d_crets)

def _export_virtools_groups(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        obj3d_crets: tuple[tuple[bpy.types.Object, bmap.BM3dObject], ...]
        ) -> None:
    # create virtools group
    group_cret_map: dict[str, bmap.BMGroup] = {}
    # start saving
    progress.enter_substeps(len(obj3d_crets), "Saving Groups")

    for obj3d, vtobj3d in obj3d_crets:
        # open group visitor
        with PROP_virtools_group.VirtoolsGroupsHelper(obj3d) as gp_visitor:
            for gp_name in gp_visitor.iterate_groups():
                # get group or create new group
                vtgroup: bmap.BMGroup | None = group_cret_map.get(gp_name, None)
                if vtgroup is None:
                    vtgroup = writer.create_group()
                    vtgroup.set_name(gp_name)
                    group_cret_map[gp_name] = vtgroup
                
                # group this object
                vtgroup.add_object(vtobj3d)

        # leave group visitor and step
        progress.step()

    # leave progress and return
    progress.leave_substeps()

def _export_virtools_3dobjects(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        obj3d_crets: tuple[tuple[bpy.types.Object, bmap.BM3dObject], ...]
        ) -> tuple[tuple[bpy.types.Object, bpy.types.Mesh, bmap.BMMesh], ...]:
    # create virtools mesh
    mesh_crets: list[tuple[bpy.types.Object, bpy.types.Mesh, bmap.BMMesh]] = []
    mesh_cret_map: dict[bpy.types.Mesh, bmap.BMMesh] = {}
    # start saving
    progress.enter_substeps(len(obj3d_crets), "Saving 3dObjects")

    for obj3d, vtobj3d in obj3d_crets:
        # set name
        vtobj3d.set_name(obj3d.name)

        # check mesh
        mesh: bpy.types.Mesh | None = obj3d.data
        if mesh is not None:
            # get existing vt mesh or create new one
            vtmesh: bmap.BMMesh | None = mesh_cret_map.get(mesh, None)
            if vtmesh is None:
                vtmesh = writer.create_mesh()
                mesh_crets.append((obj3d, mesh, vtmesh))
                mesh_cret_map[mesh] = vtmesh

            # assign mesh
            vtobj3d.set_current_mesh(vtmesh)
        else:
            vtobj3d.set_current_mesh(None)

        # set world matrix
        vtmat: UTIL_virtools_types.VxMatrix = UTIL_virtools_types.VxMatrix()
        UTIL_virtools_types.vxmatrix_from_blender(vtmat, obj3d.matrix_world)
        UTIL_virtools_types.vxmatrix_conv_co(vtmat)
        vtobj3d.set_world_matrix(vtmat)

        # set visibility
        vtobj3d.set_visibility(not obj3d.hide_get())

        # step
        progress.step()

    # leave progress and return
    progress.leave_substeps()


def _save_virtools_document(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        file_name: str,
        compress_level: int
        ) -> None:
    
    progress.enter_substeps(1, "Saving Document")
    writer.save(file_name, compress_level)
    progress.step()
    progress.leave_substeps()
    

def register() -> None:
    bpy.utils.register_class(BBP_OT_export_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_virtools)
