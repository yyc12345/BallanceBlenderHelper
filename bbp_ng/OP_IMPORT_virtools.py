import bpy, mathutils
from bpy_extras.wm_utils.progress_report import ProgressReport
import tempfile, os, typing
from . import PROP_preferences, UTIL_ioport_shared
from . import UTIL_virtools_types, UTIL_functions, UTIL_file_browser, UTIL_blender_mesh, UTIL_ballance_texture, UTIL_naming_convension
from . import PROP_virtools_group, PROP_virtools_material, PROP_virtools_mesh, PROP_virtools_texture, PROP_virtools_light, PROP_ballance_map_info
from .PyBMap import bmap_wrapper as bmap

class BBP_OT_import_virtools(bpy.types.Operator, UTIL_file_browser.ImportVirtoolsFile, UTIL_ioport_shared.ImportParams, UTIL_ioport_shared.VirtoolsParams, UTIL_ioport_shared.BallanceParams):
    """Import Virtools File"""
    bl_idname = "bbp.import_virtools"
    bl_label = "Import Virtools File"
    bl_options = {'PRESET', 'UNDO'}
    bl_translation_context = 'BBP_OT_import_virtools'

    @classmethod
    def poll(cls, context):
        return (
            PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
            and bmap.is_bmap_available())
    
    def execute(self, context):
        # check whether encoding list is empty to avoid real stupid user.
        encodings = self.general_get_vt_encodings(context)
        if len(encodings) == 0:
            self.report({'ERROR'}, 'You must specify at least one encoding for file loading (e.g. cp1252, gbk)!')
            return {'CANCELLED'}

        _import_virtools(
            self.general_get_filename(),
            encodings,
            self.general_get_conflict_resolver()
        )
        self.report({'INFO'}, "Virtools File Importing Finished.")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        self.draw_import_params(layout)
        self.draw_virtools_params(context, layout, True)
        self.draw_ballance_params(layout, True)

def _import_virtools(file_name_: str, encodings_: tuple[str], resolver: UTIL_ioport_shared.ConflictResolver) -> None:
    # create temp folder
    with tempfile.TemporaryDirectory() as vt_temp_folder:
        tr_text: str = bpy.app.translations.pgettext_rpt(
            'Virtools Engine Temporary Directory: {0}', 'BBP_OT_import_virtools/execute')
        print(tr_text.format(vt_temp_folder))

        # create virtools reader context
        with bmap.BMFileReader(
            file_name_, 
            vt_temp_folder,
            PROP_preferences.get_raw_preferences().mBallanceTextureFolder,
            encodings_) as reader:

            # prepare progress reporter
            with ProgressReport(wm = bpy.context.window_manager) as progress:
                # import textures
                texture_cret_map: dict[bmap.BMTexture, bpy.types.Image] = _import_virtools_textures(
                    reader, progress, resolver)
                # import materials
                material_cret_map: dict[bmap.BMMaterial, bpy.types.Material] = _import_virtools_materials(
                    reader, progress, resolver, texture_cret_map)
                # import meshes
                mesh_cret_map: dict[bmap.BMMesh, bpy.types.Mesh] = _import_virtools_meshes(
                    reader, progress, resolver, material_cret_map)
                # import 3dobjects
                obj3d_cret_map: dict[bmap.BM3dObject, bpy.types.Object] = _import_virtools_3dobjects(
                    reader, progress, resolver, mesh_cret_map)
                # import light
                _import_virtools_lights(reader, progress, resolver)
                # import groups
                _import_virtools_groups(reader, progress, obj3d_cret_map)

def _import_virtools_textures(
        reader: bmap.BMFileReader, 
        progress: ProgressReport,
        resolver: UTIL_ioport_shared.ConflictResolver
        ) -> dict[bmap.BMTexture, bpy.types.Image]:
    # create map
    texture_cret_map: dict[bmap.BMTexture, bpy.types.Image] = {}
    # notify steps
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading Textures', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_texture_count(), tr_text)

    # create another temp folder for raw data virtools texture importing
    with tempfile.TemporaryDirectory() as rawdata_temp:
        tr_text = bpy.app.translations.pgettext_rpt(
            'Texture Raw Data Temporary Directory: {0}', 'BBP_OT_import_virtools/execute')
        print(tr_text.format(rawdata_temp))

        for vttexture in reader.get_textures():
            tex_cret: typing.Callable[[], bpy.types.Image]
            texpath_to_load: str | None = vttexture.get_file_name()

            # if no assoc file path (what? but it is real happended)
            # this is invalid image, create a blank image instead
            if texpath_to_load is None:
                tex_cret = lambda: bpy.data.images.new("", 1, 1)
            else:
                # if this image is raw data, save it in external folder before loading
                # the attribute of raw data saving is the file path is not absolute path
                if not os.path.isabs(texpath_to_load):
                    texpath_to_load = os.path.join(
                        rawdata_temp,
                        os.path.basename(texpath_to_load)
                    )
                    vttexture.save_image(texpath_to_load)

                # detect whether it is ballance texture and load
                try_blc_tex: str | None = UTIL_ballance_texture.get_ballance_texture_filename(texpath_to_load)
                
                if try_blc_tex is not None:
                    # load as ballance texture
                    tex_cret = lambda: UTIL_ballance_texture.load_ballance_texture(typing.cast(str, try_blc_tex))
                else:
                    # load as other textures
                    tex_cret = lambda: UTIL_ballance_texture.load_other_texture(typing.cast(str, texpath_to_load))

            # create real texture by tex cret fct
            (tex, init_tex) = resolver.create_texture(
                UTIL_virtools_types.virtools_name_regulator(vttexture.get_name()), 
                tex_cret
            )
            
            # init tex if needed
            if init_tex:
                # set texture cfg
                rawtex: PROP_virtools_texture.RawVirtoolsTexture = PROP_virtools_texture.RawVirtoolsTexture()
                rawtex.mSaveOptions = vttexture.get_save_options()
                rawtex.mVideoFormat = vttexture.get_video_format()
                PROP_virtools_texture.set_raw_virtools_texture(tex, rawtex)

            # insert it to map
            texture_cret_map[vttexture] = tex

            # inc steps
            progress.step()

    # leave progress and return map
    progress.leave_substeps()
    return texture_cret_map
    
def _import_virtools_materials(
        reader: bmap.BMFileReader, 
        progress: ProgressReport,
        resolver: UTIL_ioport_shared.ConflictResolver,
        texture_cret_map: dict[bmap.BMTexture, bpy.types.Image]
        ) -> dict[bmap.BMMaterial, bpy.types.Material]:
    # create map and prepare progress
    material_cret_map: dict[bmap.BMMaterial, bpy.types.Material] = {}
    # notify steps
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading Materials', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_material_count(), tr_text)

    for vtmaterial in reader.get_materials():
        # create mtl
        (mtl, init_mtl) = resolver.create_material(
            UTIL_virtools_types.virtools_name_regulator(vtmaterial.get_name())
        )

        # apply it if necessary
        if init_mtl:
            # create new raw material
            rawmtl: PROP_virtools_material.RawVirtoolsMaterial = PROP_virtools_material.RawVirtoolsMaterial()
            
            rawmtl.mDiffuse = vtmaterial.get_diffuse()
            rawmtl.mAmbient = vtmaterial.get_ambient()
            rawmtl.mSpecular = vtmaterial.get_specular()
            rawmtl.mEmissive = vtmaterial.get_emissive()
            rawmtl.mSpecularPower = vtmaterial.get_specular_power()

            mtltex: bmap.BMTexture | None = vtmaterial.get_texture()
            if mtltex:
                rawmtl.mTexture = texture_cret_map.get(mtltex, None)
            else:
                rawmtl.mTexture = None
            rawmtl.mTextureBorderColor = vtmaterial.get_texture_border_color()

            rawmtl.mTextureBlendMode = vtmaterial.get_texture_blend_mode()
            rawmtl.mTextureMinMode = vtmaterial.get_texture_min_mode()
            rawmtl.mTextureMagMode = vtmaterial.get_texture_mag_mode()
            rawmtl.mTextureAddressMode = vtmaterial.get_texture_address_mode()

            rawmtl.mSourceBlend = vtmaterial.get_source_blend()
            rawmtl.mDestBlend = vtmaterial.get_dest_blend()
            rawmtl.mFillMode = vtmaterial.get_fill_mode()
            rawmtl.mShadeMode = vtmaterial.get_shade_mode()

            rawmtl.mEnableAlphaTest = vtmaterial.get_alpha_test_enabled()
            rawmtl.mEnableAlphaBlend = vtmaterial.get_alpha_blend_enabled()
            rawmtl.mEnablePerspectiveCorrection = vtmaterial.get_perspective_correction_enabled()
            rawmtl.mEnableZWrite = vtmaterial.get_z_write_enabled()
            rawmtl.mEnableTwoSided = vtmaterial.get_two_sided_enabled()

            rawmtl.mAlphaRef = vtmaterial.get_alpha_ref()
            rawmtl.mAlphaFunc = vtmaterial.get_alpha_func()
            rawmtl.mZFunc = vtmaterial.get_z_func()

            PROP_virtools_material.set_raw_virtools_material(mtl, rawmtl)
            PROP_virtools_material.apply_to_blender_material(mtl)

        # add into map and step
        material_cret_map[vtmaterial] = mtl
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return material_cret_map

def _import_virtools_meshes(
        reader: bmap.BMFileReader, 
        progress: ProgressReport,
        resolver: UTIL_ioport_shared.ConflictResolver, 
        material_cret_map: dict[bmap.BMMaterial, bpy.types.Material]
        ) -> dict[bmap.BMMesh, bpy.types.Mesh]:
    # create map and prepare progress
    mesh_cret_map: dict[bmap.BMMesh, bpy.types.Mesh] = {}
    # notify steps
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading Meshes', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_mesh_count(), tr_text)

    for vtmesh in reader.get_meshs():
        # create mesh
        (mesh, init_mesh) = resolver.create_mesh(
            UTIL_virtools_types.virtools_name_regulator(vtmesh.get_name())
        )

        # set mesh data if necessary
        if init_mesh:
            # open mesh writer
            with UTIL_blender_mesh.MeshWriter(mesh) as meshoper:
                # construct data provider
                data_prov: UTIL_blender_mesh.MeshWriterIngredient = UTIL_blender_mesh.MeshWriterIngredient()

                # constructor data itor
                def pos_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                    for v in vtmesh.get_vertex_positions():
                        UTIL_virtools_types.vxvector3_conv_co(v)
                        yield v
                def nml_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector3]:
                    for v in vtmesh.get_vertex_normals():
                        UTIL_virtools_types.vxvector3_conv_co(v)
                        yield v
                def uv_iterator() -> typing.Iterator[UTIL_virtools_types.VxVector2]:
                    for v in vtmesh.get_vertex_uvs():
                        UTIL_virtools_types.vxvector2_conv_co(v)
                        yield v
                def face_iterator() -> typing.Iterator[UTIL_blender_mesh.FaceData]:
                    face: UTIL_blender_mesh.FaceData = UTIL_blender_mesh.FaceData(
                        [UTIL_blender_mesh.FaceVertexData() for i in range(3)]
                    )

                    findices_itor = vtmesh.get_face_indices()
                    fmtl_itor = vtmesh.get_face_material_slot_indexs()
                    for _ in range(vtmesh.get_face_count()):
                        # set indices data
                        vtindices = next(findices_itor)
                        face.mIndices[0].mPosIdx = vtindices.i1
                        face.mIndices[0].mNmlIdx = vtindices.i1
                        face.mIndices[0].mUvIdx = vtindices.i1
                        face.mIndices[1].mPosIdx = vtindices.i2
                        face.mIndices[1].mNmlIdx = vtindices.i2
                        face.mIndices[1].mUvIdx = vtindices.i2
                        face.mIndices[2].mPosIdx = vtindices.i3
                        face.mIndices[2].mNmlIdx = vtindices.i3
                        face.mIndices[2].mUvIdx = vtindices.i3
                        # swap indices
                        face.conv_co()

                        # set mtl data
                        vtmtl = next(fmtl_itor)
                        face.mMtlIdx = vtmtl

                        # return
                        yield face
                def mtl_iterator() -> typing.Iterator[bpy.types.Material | None]:
                    for vtmtl in vtmesh.get_material_slots():
                        if vtmtl:
                            yield material_cret_map.get(vtmtl, None)
                        else:
                            yield None

                # assign to data provider
                data_prov.mVertexPosition = pos_iterator()
                data_prov.mVertexNormal = nml_iterator()
                data_prov.mVertexUV = uv_iterator()
                data_prov.mFace = face_iterator()
                data_prov.mMaterial = mtl_iterator()

                # add part
                meshoper.add_ingredient(data_prov)

            # end of mesh writer

            # set other mesh settings
            mesh_settings: PROP_virtools_mesh.RawVirtoolsMesh = PROP_virtools_mesh.RawVirtoolsMesh()
            mesh_settings.mLitMode = vtmesh.get_lit_mode()
            PROP_virtools_mesh.set_raw_virtools_mesh(mesh, mesh_settings)

        # add into map and step
        mesh_cret_map[vtmesh] = mesh
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return mesh_cret_map

def _import_virtools_3dobjects(
        reader: bmap.BMFileReader, 
        progress: ProgressReport,
        resolver: UTIL_ioport_shared.ConflictResolver, 
        mesh_cret_map: dict[bmap.BMMesh, bpy.types.Mesh]
        ) -> dict[bmap.BM3dObject, bpy.types.Object]:
    # create map and prepare progress
    obj3d_cret_map: dict[bmap.BM3dObject, bpy.types.Object] = {}
    # notify steps
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading 3dObjects', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_3dobject_count(), tr_text)

    for vt3dobj in reader.get_3dobjects():
        # get virtools binding mesh data first
        vt3dobj_data: bmap.BMMesh | None = vt3dobj.get_current_mesh()

        # create 3d object with mesh
        (obj3d, init_obj3d) = resolver.create_object(
            UTIL_virtools_types.virtools_name_regulator(vt3dobj.get_name()),
            None if vt3dobj_data is None else mesh_cret_map.get(vt3dobj_data, None)
        )

        # setup if necessary
        if init_obj3d:
            # add into scene
            UTIL_functions.add_into_scene(obj3d)

            # set world matrix
            vtmat: UTIL_virtools_types.VxMatrix = vt3dobj.get_world_matrix()
            UTIL_virtools_types.vxmatrix_conv_co(vtmat)
            obj3d.matrix_world = UTIL_virtools_types.vxmatrix_to_blender(vtmat)

            # set visibility
            obj3d.hide_set(not vt3dobj.get_visibility())

            # add into map
            # NOTE: the return value only provided to group setter
            # and group setter should only set group data to new created 3d objects
            # thus we only insert pair when this 3d obj is new created.
            obj3d_cret_map[vt3dobj] = obj3d

        # step forward
        progress.step()

    # leave progress and return
    progress.leave_substeps()
    return obj3d_cret_map

def _import_virtools_lights(
        reader: bmap.BMFileReader, 
        progress: ProgressReport,
        resolver: UTIL_ioport_shared.ConflictResolver
        ) -> None:
    # prepare progress
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading Lights', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_target_light_count(), tr_text)

    # please note light is slightly different between virtools and blender.
    # in virtools, light is the sub class of 3d entity.
    # it means that virtools use class inheritance to implement light.
    # however, in blender, light is the data property of object.
    # comparing with normal mesh object, it just replace the data property of object to a light.
    # so in blender, light is implemented as a data struct attached to object.
    # thus we can reuse light data for multiple objects but virtools can not.
    # in virtools, every light are individual objects.
    for vtlight in reader.get_target_lights():
        # create light data block and 3d object together
        (light_3dobj, light, init_light) = resolver.create_light(
            UTIL_virtools_types.virtools_name_regulator(vtlight.get_name())
        )

        if init_light:
            # setup light data block
            rawlight: PROP_virtools_light.RawVirtoolsLight = PROP_virtools_light.RawVirtoolsLight()
            rawlight.mType = vtlight.get_type()
            rawlight.mColor = vtlight.get_color()

            rawlight.mConstantAttenuation = vtlight.get_constant_attenuation()
            rawlight.mLinearAttenuation = vtlight.get_linear_attenuation()
            rawlight.mQuadraticAttenuation = vtlight.get_quadratic_attenuation()

            rawlight.mRange = vtlight.get_range()

            rawlight.mHotSpot = vtlight.get_hot_spot()
            rawlight.mFalloff = vtlight.get_falloff()
            rawlight.mFalloffShape = vtlight.get_falloff_shape()

            PROP_virtools_light.set_raw_virtools_light(light, rawlight)
            PROP_virtools_light.apply_to_blender_light(light)

            # setup light associated 3d object
            # add into scene
            UTIL_functions.add_into_scene(light_3dobj)
            # set world matrix
            vtmat: UTIL_virtools_types.VxMatrix = vtlight.get_world_matrix()
            UTIL_virtools_types.vxmatrix_conv_co(vtmat)
            bldmat: mathutils.Matrix = UTIL_virtools_types.vxmatrix_to_blender(vtmat)
            light_3dobj.matrix_world = UTIL_virtools_types.bldmatrix_patch_light_obj(bldmat)
            # set visibility
            light_3dobj.hide_set(not vtlight.get_visibility())

    # leave progress
    progress.leave_substeps()

def _import_virtools_groups(
        reader: bmap.BMFileReader, 
        progress: ProgressReport, 
        obj3d_cret_map: dict[bmap.BM3dObject, bpy.types.Object]
        ) -> None:
    # we need iterate all groups to construct a reversed map
    # to indicate which groups should this 3dobject be grouped into.
    reverse_map: dict[bmap.BM3dObject, set[str]] = {}
    # sector counter to record the maximum sector we have processed.
    sector_count: int = 1

    # prepare progress
    tr_text: str = bpy.app.translations.pgettext_rpt('Loading Groups', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(reader.get_group_count(), tr_text)

    for vtgroup in reader.get_groups():
        # if this group do not have name, skip it
        group_name: str | None = vtgroup.get_name()
        if group_name is None: continue

        # try extracting sector info
        potential_sector_count: int | None = UTIL_naming_convension.extract_sector_from_name(group_name)
        if potential_sector_count is not None:
            sector_count = max(sector_count, potential_sector_count)

        # creating map
        for item in vtgroup.get_objects():
            # get or create set
            objgroups: set[str] | None = reverse_map.get(item, None)
            if objgroups is None:
                objgroups = set()
                reverse_map[item] = objgroups

            # add into list
            objgroups.add(group_name)
            
        # step
        progress.step()

    # assign to ballance map info according to gotten sector count
    map_info: PROP_ballance_map_info.RawBallanceMapInfo = PROP_ballance_map_info.get_raw_ballance_map_info(bpy.context.scene)
    map_info.mSectorCount = max(map_info.mSectorCount, sector_count)
    PROP_ballance_map_info.set_raw_ballance_map_info(bpy.context.scene, map_info)

    # leave progress
    progress.leave_substeps()

    # now we can assign 3dobject group data by reverse map
    tr_text: str = bpy.app.translations.pgettext_rpt('Applying Groups', 'BBP_OT_import_virtools/execute')
    progress.enter_substeps(len(reverse_map), tr_text)
    for mapk, mapv in reverse_map.items():
        # check object
        assoc_obj = obj3d_cret_map.get(mapk, None)
        if assoc_obj is None: continue

        # assign group
        with PROP_virtools_group.VirtoolsGroupsHelper(assoc_obj) as gpoper:
            gpoper.clear_groups()
            gpoper.add_groups(mapv)

        # step
        progress.step()

    # leave progress
    progress.leave_substeps()


def register() -> None:
    bpy.utils.register_class(BBP_OT_import_virtools)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_import_virtools)
