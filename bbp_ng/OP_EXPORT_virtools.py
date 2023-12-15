import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport
import tempfile, os, typing
from . import PROP_preferences, UTIL_ioport_shared
from . import UTIL_virtools_types, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_ballance_texture, UTIL_icons_manager
from . import PROP_virtools_group, PROP_virtools_material, PROP_virtools_mesh, PROP_virtools_texture
from .PyBMap import bmap_wrapper as bmap

# define global tex save opt blender enum prop helper
_g_EnumHelper_CK_TEXTURE_SAVEOPTIONS: UTIL_virtools_types.EnumPropHelper = UTIL_virtools_types.EnumPropHelper(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS)

class BBP_OT_export_virtools(bpy.types.Operator, UTIL_file_browser.ExportVirtoolsFile, UTIL_ioport_shared.ExportParams, UTIL_ioport_shared.VirtoolsParams):
    """Export Virtools File"""
    bl_idname = "bbp.export_virtools"
    bl_label = "Export Virtools File"
    bl_options = {'PRESET'}

    texture_save_opt: bpy.props.EnumProperty(
        name = "Global Texture Save Options",
        description = "Decide how texture saved if texture is specified as Use Global as its Save Options.",
        items = _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.generate_items(),
        default = _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.to_selection(UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL)
    )

    use_compress: bpy.props.BoolProperty(
        name="Use Compress",
        default = True,
    )

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
                _g_EnumHelper_CK_TEXTURE_SAVEOPTIONS.get_selection(self.texture_save_opt),
                self.use_compress,
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
        layout.label(text = 'Global Texture Save Option')
        layout.prop(self, 'texture_save_opt', text = '')
        layout.prop(self, 'use_compress')
        if self.use_compress:
            layout.prop(self, 'compress_level')

_TObj3dPair = tuple[bpy.types.Object, bmap.BM3dObject]
_TMeshPair = tuple[bpy.types.Object, bpy.types.Mesh, bmap.BMMesh]
_TMaterialPair = tuple[bpy.types.Material, bmap.BMMaterial]
_TTexturePair = tuple[bpy.types.Image, bmap.BMTexture]

def _export_virtools(
        file_name_: str, 
        encodings_: tuple[str], 
        texture_save_opt_: UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS,
        use_compress_: bool,
        compress_level_: int, 
        export_objects: tuple[bpy.types.Object, ...]
    ) -> None:

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
                obj3d_crets: tuple[_TObj3dPair, ...] = _prepare_virtools_3dobjects(
                    writer, progress, export_objects)
                # export group and 3dobject by prepared 3dobject
                _export_virtools_groups(writer, progress, obj3d_crets)
                mesh_crets: tuple[_TMeshPair, ...] = _export_virtools_3dobjects(
                    writer, progress, obj3d_crets)
                # export mesh
                material_crets: tuple[_TMaterialPair, ...] = _export_virtools_meshes(
                    writer, progress, mesh_crets)
                # export material
                texture_crets: tuple[_TTexturePair, ...] = _export_virtools_materials(
                    writer, progress, material_crets)
                # export texture
                _export_virtools_textures(writer, progress, vt_temp_folder, texture_crets)

                # save document
                _save_virtools_document(
                    writer, progress, file_name_, texture_save_opt_, use_compress_, compress_level_)

def _prepare_virtools_3dobjects(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        export_objects: tuple[bpy.types.Object]
        ) -> tuple[_TObj3dPair, ...]:
    # this function only create equvalent entries in virtools engine and do not export anything
    # because _export_virtools_3dobjects() and _export_virtools_groups() are need use the return value of this function

    # create 3dobject hashset and result
    obj3d_crets: list[_TObj3dPair] = []
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
        obj3d_crets: tuple[_TObj3dPair, ...]
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
        obj3d_crets: tuple[_TObj3dPair, ...]
        ) -> tuple[_TMeshPair, ...]:
    # create virtools mesh
    mesh_crets: list[_TMeshPair] = []
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
    return tuple(mesh_crets)

def _export_virtools_meshes(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        mesh_crets: tuple[_TMeshPair, ...]
        ) -> tuple[_TMaterialPair, ...]:
    # create virtools mesh
    material_crets: list[_TMaterialPair] = []
    material_cret_map: dict[bpy.types.Material, bmap.BMMaterial] = {}
    # start saving
    progress.enter_substeps(len(mesh_crets), "Saving Meshes")

    # iterate meshes
    for obj3d, mesh, vtmesh in mesh_crets:
        # we need use temporary mesh function to visit triangulated meshes
        # so we ignore mesh factor and use obj3d to create temp mesh to get data
        # open temp mesh helper
        with UTIL_blender_mesh.TemporaryMesh(obj3d) as tempmesh:
            # sync mesh name, lit mode
            vtmesh.set_name(mesh.name)
            mesh_settings: PROP_virtools_mesh.RawVirtoolsMesh = PROP_virtools_mesh.get_raw_virtools_mesh(mesh)
            vtmesh.set_lit_mode(mesh_settings.mLitMode)

            # sync mesh main data
            # open mesh visitor
            with UTIL_blender_mesh.MeshReader(tempmesh.get_temp_mesh()) as mesh_visitor:
                # construct data provider
                def pos_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                    for v in mesh_visitor.get_vertex_position():
                        UTIL_virtools_types.vxvector3_conv_co(v)
                        yield v
                def nml_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                    for v in mesh_visitor.get_vertex_normal():
                        UTIL_virtools_types.vxvector3_conv_co(v)
                        yield v
                def uv_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector2]:
                    for v in mesh_visitor.get_vertex_uv():
                        UTIL_virtools_types.vxvector2_conv_co(v)
                        yield v

                # construct mtl slot
                def mtl_iterator() -> typing.Iterator[bmap.BMMaterial | None]:
                    for mtl in mesh_visitor.get_material_slot():
                        if mtl is None: yield None
                        else:
                            # get existing one or create new one
                            vtmaterial: bmap.BMMaterial | None = material_cret_map.get(mtl, None)
                            if vtmaterial is None:
                                vtmaterial = writer.create_material()
                                material_crets.append((mtl, vtmaterial))
                                material_cret_map[mtl] = vtmaterial
                            # yield data
                            yield vtmaterial

                def face_idx_iterator(idx_type: int) -> typing.Iterator[UTIL_virtools_types.CKFaceIndices]:
                    data: UTIL_virtools_types.CKFaceIndices = UTIL_virtools_types.CKFaceIndices()
                    for fidx in mesh_visitor.get_face():
                        # swap indices
                        fidx.conv_co()
                        # set data by specific index
                        match(idx_type):
                            case 0:  data.i1, data.i2, data.i3 = fidx.mIndices[0].mPosIdx, fidx.mIndices[1].mPosIdx, fidx.mIndices[2].mPosIdx
                            case 1:  data.i1, data.i2, data.i3 = fidx.mIndices[0].mNmlIdx, fidx.mIndices[1].mNmlIdx, fidx.mIndices[2].mNmlIdx
                            case 2:  data.i1, data.i2, data.i3 = fidx.mIndices[0].mUvIdx, fidx.mIndices[1].mUvIdx, fidx.mIndices[2].mUvIdx
                            case _: raise UTIL_functions.BBPException('invalid index type.')
                        # yield data
                        yield data
                def face_mtl_iterator() -> typing.Iterator[int]:
                    for fidx in mesh_visitor.get_face():
                        yield fidx.mMtlIdx
                
                # create virtools mesh transition
                # and write into mesh
                with bmap.BMMeshTrans() as mesh_trans:
                    # prepare vertices
                    mesh_trans.prepare_vertex(
                        mesh_visitor.get_vertex_position_count(),
                        pos_iterator()
                    )
                    mesh_trans.prepare_normal(
                        mesh_visitor.get_vertex_normal_count(),
                        nml_iterator()
                    )
                    mesh_trans.prepare_uv(
                        mesh_visitor.get_vertex_uv_count(),
                        uv_iterator()
                    )
                    # prepare mtl slots
                    mesh_trans.prepare_mtl_slot(
                        mesh_visitor.get_material_slot_count(),
                        mtl_iterator()
                    )
                    # prepare face
                    mesh_trans.prepare_face(
                        mesh_visitor.get_face_count(),
                        face_idx_iterator(0),
                        face_idx_iterator(1),
                        face_idx_iterator(2),
                        face_mtl_iterator()
                    )

                    # parse to vtmesh
                    mesh_trans.parse(writer, vtmesh)

                # end of mesh trans
            # end of mesh visitor
        # end of temp mesh

        # step
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return tuple(material_crets)

def _export_virtools_materials(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        material_crets: tuple[_TMaterialPair, ...]
        ) -> tuple[_TTexturePair, ...]:
    # create virtools mesh
    texture_crets: list[_TTexturePair] = []
    texture_cret_map: dict[bpy.types.Image, bmap.BMTexture] = {}
    # start saving
    progress.enter_substeps(len(material_crets), "Saving Materials")

    for mtl, vtmaterial in material_crets:
        # set name
        vtmaterial.set_name(mtl.name)

        # get raw mtl
        rawmtl: PROP_virtools_material.RawVirtoolsMaterial = PROP_virtools_material.get_raw_virtools_material(mtl)

        # apply vt material
        vtmaterial.set_diffuse(rawmtl.mDiffuse)
        vtmaterial.set_ambient(rawmtl.mAmbient)
        vtmaterial.set_specular(rawmtl.mSpecular)
        vtmaterial.set_emissive(rawmtl.mEmissive)
        vtmaterial.set_specular_power(rawmtl.mSpecularPower)

        # apply assoc texture
        if rawmtl.mTexture is not None:
            # create or get new one vt texture
            vttexture: bmap.BMTexture | None = texture_cret_map.get(rawmtl.mTexture, None)
            if vttexture is None:
                vttexture = writer.create_texture()
                texture_cret_map[rawmtl.mTexture] = vttexture
                texture_crets.append((rawmtl.mTexture, vttexture))
            # assign texture
            vtmaterial.set_texture(vttexture)
        else:
            vtmaterial.set_texture(None)
        
        vtmaterial.set_texture_border_color(rawmtl.mTextureBorderColor)

        vtmaterial.set_texture_blend_mode(rawmtl.mTextureBlendMode)
        vtmaterial.set_texture_min_mode(rawmtl.mTextureMinMode)
        vtmaterial.set_texture_mag_mode(rawmtl.mTextureMagMode)
        vtmaterial.set_texture_address_mode(rawmtl.mTextureAddressMode)

        vtmaterial.set_source_blend(rawmtl.mSourceBlend)
        vtmaterial.set_dest_blend(rawmtl.mDestBlend)
        vtmaterial.set_fill_mode(rawmtl.mFillMode)
        vtmaterial.set_shade_mode(rawmtl.mShadeMode)

        vtmaterial.set_alpha_test_enabled(rawmtl.mEnableAlphaTest)
        vtmaterial.set_alpha_blend_enabled(rawmtl.mEnableAlphaBlend)
        vtmaterial.set_perspective_correction_enabled(rawmtl.mEnablePerspectiveCorrection)
        vtmaterial.set_z_write_enabled(rawmtl.mEnableZWrite)
        vtmaterial.set_two_sided_enabled(rawmtl.mEnableTwoSided)

        vtmaterial.set_alpha_ref(rawmtl.mAlphaRef)
        vtmaterial.set_alpha_func(rawmtl.mAlphaFunc)
        vtmaterial.set_z_func(rawmtl.mZFunc)

        # step
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return tuple(texture_crets)

def _export_virtools_textures(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        vt_temp_folder: str,
        texture_crets: tuple[_TTexturePair, ...]
        ) -> None:
    # start saving
    progress.enter_substeps(len(texture_crets), "Saving Textures")

    for tex, vttexture in texture_crets:
        # set name
        vttexture.set_name(tex.name)

        # set texture cfg
        rawtex: PROP_virtools_texture.RawVirtoolsTexture = PROP_virtools_texture.get_raw_virtools_texture(tex)
        vttexture.set_save_options(rawtex.mSaveOptions)
        vttexture.set_video_format(rawtex.mVideoFormat)

        # save core texture
        # load ballance textures to vt engine from external ref path
        # load other textures to vt engine from temp folder.
        # no need to distinguish save options
        try_filepath: str | None = UTIL_ballance_texture.get_ballance_texture_filename(
            UTIL_ballance_texture.get_texture_filepath(tex))
        if try_filepath is None:
            # non-ballance file, save in temp and change file path to point to it.
            try_filepath = UTIL_ballance_texture.generate_other_texture_save_path(tex, vt_temp_folder)
            UTIL_ballance_texture.save_other_texture(tex, try_filepath)
        # load into vt engine
        vttexture.load_image(try_filepath)

        # step
        progress.step()

    # leave progress and return
    progress.leave_substeps()

def _save_virtools_document(
        writer: bmap.BMFileWriter,
        progress: ProgressReport,
        file_name: str,
        texture_save_opt: UTIL_virtools_types.CK_TEXTURE_SAVEOPTIONS,
        use_compress: bool,
        compress_level: int
        ) -> None:
    
    progress.enter_substeps(1, "Saving Document")
    writer.save(file_name, texture_save_opt, use_compress, compress_level)
    progress.step()
    progress.leave_substeps()
    

def register() -> None:
    bpy.utils.register_class(BBP_OT_export_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_export_virtools)
