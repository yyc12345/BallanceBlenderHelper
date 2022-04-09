import bpy,bmesh,bpy_extras,mathutils
import pathlib,zipfile,time,os,tempfile,math
import struct, shutil
from bpy_extras import io_utils,node_shader_utils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from . import UTILS_constants, UTILS_functions, UTILS_file_io, UTILS_zip_helper, UTILS_virtools_prop

class BALLANCE_OT_import_bm(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Ballance Map File (BM file spec 1.4)"""
    bl_idname = "ballance.import_bm"
    bl_label = "Import BM "
    bl_options = {'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".bmx"
    filter_glob: bpy.props.StringProperty(
        default="*.bmx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    texture_conflict_strategy: bpy.props.EnumProperty(
        name="Texture name conflict",
        items=(('NEW', "New instance", "Create a new instance"),
               ('CURRENT', "Use current", "Use current"),),
        description="Define how to process texture name conflict",
        default='CURRENT',
        )

    material_conflict_strategy: bpy.props.EnumProperty(
        name="Material name conflict",
        items=(('RENAME', "Rename", "Rename the new one"),
               ('CURRENT', "Use current", "Use current"),),
        description="Define how to process material name conflict",
        default='RENAME',
        )

    mesh_conflict_strategy: bpy.props.EnumProperty(
        name="Mesh name conflict",
        items=(('RENAME', "Rename", "Rename the new one"),
               ('CURRENT', "Use current", "Use current"),),
        description="Define how to process mesh name conflict",
        default='RENAME',
        )

    object_conflict_strategy: bpy.props.EnumProperty(
        name="Object name conflict",
        items=(('RENAME', "Rename", "Rename the new one"),
               ('CURRENT', "Use current", "Use current"),),
        description="Define how to process object name conflict",
        default='RENAME',
        )

    @classmethod
    def poll(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        return (os.path.isdir(prefs.temp_texture_folder) and os.path.isdir(prefs.external_folder))

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        import_bm(context, self.filepath, 
                prefs.no_component_collection, prefs.external_folder, prefs.temp_texture_folder,
                self.texture_conflict_strategy, self.material_conflict_strategy, 
                self.mesh_conflict_strategy, self.object_conflict_strategy)
        return {'FINISHED'}
        

def import_bm(context, bmx_filepath, prefs_fncg, prefs_externalTexture, prefs_tempTextureFolder, opts_texture, opts_material, opts_mesh, opts_object):
    # ============================================ 
    # alloc a temp folder for decompress
    utils_tempFolderObj = tempfile.TemporaryDirectory()
    utils_tempFolder = utils_tempFolderObj.name
    utils_tempTextureFolder = os.path.join(utils_tempFolder, "Texture")
    # decompress
    UTILS_zip_helper.decompress(utils_tempFolder, bmx_filepath)

    # ============================================ 
    # read bmx file officially
    # index.bm
    objectList = []
    meshList = []
    materialList = []
    textureList = []
    with open(os.path.join(utils_tempFolder, "index.bm"), "rb") as findex:
        # check version first
        index_gottenVersion = UTILS_file_io.read_uint32(findex)
        if (index_gottenVersion != UTILS_constants.bmfile_currentVersion):
            # clean temp folder, output error
            UTILS_functions.show_message_box(
                ("Unsupported BM spec. Expect: {} Gotten: {}".format(UTILS_constants.bmfile_currentVersion, index_gottenVersion), ), 
                "Unsupported BM spec", 'ERROR')
            findex.close()
            utils_tempFolderObj.cleanup()
            return

        # collect block header data
        while len(UTILS_file_io.peek_stream(findex)) != 0:
            # read
            index_name = UTILS_file_io.read_string(findex)
            index_type = UTILS_file_io.read_uint8(findex)
            index_offset = UTILS_file_io.read_uint64(findex)
            index_blockCache = _InfoBlockHelper(index_name, index_offset)

            # grouping into list
            if index_type == UTILS_constants.BmfileInfoType.OBJECT:
                objectList.append(index_blockCache)
            elif index_type == UTILS_constants.BmfileInfoType.MESH:
                meshList.append(index_blockCache)
            elif index_type == UTILS_constants.BmfileInfoType.MATERIAL:
                materialList.append(index_blockCache)
            elif index_type == UTILS_constants.BmfileInfoType.TEXTURE:
                textureList.append(index_blockCache)
            else:
                pass


    # texture.bm
    with open(os.path.join(utils_tempFolder, "texture.bm"), "rb") as ftexture:
        for item in textureList:
            # seek to block
            ftexture.seek(item.offset, os.SEEK_SET)

            # read data
            texture_filename = UTILS_file_io.read_string(ftexture)
            texture_isExternal = UTILS_file_io.read_bool(ftexture)
            if texture_isExternal:
                (texture_target, skip_init) = UTILS_functions.create_instance_with_option(
                    UTILS_constants.BmfileInfoType.TEXTURE, item.name, opts_texture,
                    extra_texture_filename= texture_filename, extra_texture_path= prefs_externalTexture)
            else:
                # not external. copy temp file into blender temp. then use it.
                # try copy. if fail, don't need to do more
                try:
                    shutil.copy(os.path.join(utils_tempTextureFolder, texture_filename), 
                        os.path.join(prefs_tempTextureFolder, texture_filename))
                except:
                    pass

                (texture_target, skip_init) = UTILS_functions.create_instance_with_option(
                    UTILS_constants.BmfileInfoType.TEXTURE, item.name, opts_texture,
                    extra_texture_filename= texture_filename, extra_texture_path= prefs_tempTextureFolder)
            
            # setup name and blender data for header
            item.blender_data = texture_target

    # material.bm
    # WARNING: this code is shared with add_floor - create_or_get_material()
    with open(os.path.join(utils_tempFolder, "material.bm"), "rb") as fmaterial:
        for item in materialList:
            # seek to block
            fmaterial.seek(item.offset, os.SEEK_SET)

            # read data
            material_colAmbient = UTILS_file_io.read_3vector(fmaterial)
            material_colDiffuse = UTILS_file_io.read_3vector(fmaterial)
            material_colSpecular = UTILS_file_io.read_3vector(fmaterial)
            material_colEmissive = UTILS_file_io.read_3vector(fmaterial)
            material_specularPower = UTILS_file_io.read_float(fmaterial)
            material_useTexture = UTILS_file_io.read_bool(fmaterial)
            material_texture = UTILS_file_io.read_uint32(fmaterial)

            # alloc basic material
            (material_target, skip_init) = UTILS_functions.create_instance_with_option(
                UTILS_constants.BmfileInfoType.MATERIAL, item.name, opts_material)
            item.blender_data = material_target
            if skip_init:
                continue
            
            # try create material nodes
            UTILS_functions.create_material_nodes(material_target,
                material_colAmbient, material_colDiffuse, material_colSpecular, material_colEmissive,
                material_specularPower,
                textureList[material_texture].blender_data if material_useTexture else None)

    # mesh.bm
    # WARNING: this code is shared with add_floor
    with open(os.path.join(utils_tempFolder, "mesh.bm"), "rb") as fmesh:
        mesh_vList=[]
        mesh_vtList=[]
        mesh_vnList=[]
        mesh_faceList=[]
        mesh_materialSolt = []
        for item in meshList:
            fmesh.seek(item.offset, os.SEEK_SET)

            # create real mesh
            (mesh_target, skip_init) = UTILS_functions.create_instance_with_option(
                UTILS_constants.BmfileInfoType.MESH, item.name, opts_mesh)
            item.blender_data = mesh_target
            if skip_init:
                continue

            mesh_vList.clear()
            mesh_vtList.clear()
            mesh_vnList.clear()
            mesh_faceList.clear()
            mesh_materialSolt.clear()
            # in first read, store all data into list
            mesh_listCount = UTILS_file_io.read_uint32(fmesh)
            for i in range(mesh_listCount):
                cache = UTILS_file_io.read_3vector(fmesh)
                # switch yz
                mesh_vList.append((cache[0], cache[2], cache[1]))
            mesh_listCount = UTILS_file_io.read_uint32(fmesh)
            for i in range(mesh_listCount):
                cache = UTILS_file_io.read_2vector(fmesh)
                # reverse v
                mesh_vtList.append((cache[0], -cache[1]))
            mesh_listCount = UTILS_file_io.read_uint32(fmesh)
            for i in range(mesh_listCount):
                cache = UTILS_file_io.read_3vector(fmesh)
                # switch yz
                mesh_vnList.append((cache[0], cache[2], cache[1]))
            
            mesh_listCount = UTILS_file_io.read_uint32(fmesh)
            for i in range(mesh_listCount):
                mesh_faceData = UTILS_file_io.read_face(fmesh)
                mesh_useMaterial = UTILS_file_io.read_bool(fmesh)
                mesh_materialIndex = UTILS_file_io.read_uint32(fmesh)

                if mesh_useMaterial:
                    mesh_neededMaterial = materialList[mesh_materialIndex].blender_data
                    if mesh_neededMaterial in mesh_materialSolt:
                        mesh_blenderMtlIndex = mesh_materialSolt.index(mesh_neededMaterial)
                    else:
                        mesh_blenderMtlIndex = len(mesh_materialSolt)
                        mesh_materialSolt.append(mesh_neededMaterial)
                else:
                    mesh_blenderMtlIndex = -1

                # we need invert triangle sort
                mesh_faceList.append((
                    mesh_faceData[6], mesh_faceData[7], mesh_faceData[8],
                    mesh_faceData[3], mesh_faceData[4], mesh_faceData[5],
                    mesh_faceData[0], mesh_faceData[1], mesh_faceData[2],
                    mesh_blenderMtlIndex
                ))

            # and then we need add material solt for this mesh
            for mat in mesh_materialSolt:
                mesh_target.materials.append(mat)

            # then, we need add correspond count for vertices
            mesh_target.vertices.add(len(mesh_vList))
            mesh_target.loops.add(len(mesh_faceList)*3)  # triangle face confirm
            mesh_target.polygons.add(len(mesh_faceList))
            mesh_target.uv_layers.new(do_init=False)
            mesh_target.create_normals_split()

            # add vertices data
            mesh_target.vertices.foreach_set("co", unpack_list(mesh_vList))
            mesh_target.loops.foreach_set("vertex_index", unpack_list(_flat_vertices_index(mesh_faceList)))
            mesh_target.loops.foreach_set("normal", unpack_list(_flat_vertices_normal(mesh_faceList, mesh_vnList)))
            mesh_target.uv_layers[0].data.foreach_set("uv", unpack_list(_flat_vertices_uv(mesh_faceList, mesh_vtList)))
            for i in range(len(mesh_faceList)):
                mesh_target.polygons[i].loop_start = i * 3
                mesh_target.polygons[i].loop_total = 3
                if mesh_faceList[i][9] != -1:
                    mesh_target.polygons[i].material_index = mesh_faceList[i][9]

                mesh_target.polygons[i].use_smooth = True
            
            mesh_target.validate(clean_customdata=False)
            mesh_target.update(calc_edges=False, calc_edges_loose=False)
            

    # object
    with open(os.path.join(utils_tempFolder, "object.bm"), "rb") as fobject:

        # we need get needed collection first
        blender_viewLayer = context.view_layer
        blender_collection = blender_viewLayer.active_layer_collection.collection
        if prefs_fncg == "":
            # fncg stands with Forced Non-Component Group
            object_fncgCollection = None
        else:
            try:
                # try get collection
                object_fncgCollection = bpy.data.collections[prefs_fncg]
            except:
                # fail to get, create new one under active collection instead
                object_fncgCollection = bpy.data.collections.new(prefs_fncg)
                blender_collection.children.link(object_fncgCollection)

        # start process it
        object_groupList = []
        for item in objectList:
            fobject.seek(item.offset, os.SEEK_SET)

            # read data
            object_isComponent = UTILS_file_io.read_bool(fobject)
            #object_isForcedNoComponent = UTILS_file_io.read_bool(fobject)
            object_isHidden = UTILS_file_io.read_bool(fobject)
            object_worldMatrix = UTILS_file_io.read_world_materix(fobject)
            object_groupListCount = UTILS_file_io.read_uint32(fobject)
            object_groupList.clear()
            for i in range(object_groupListCount):
                object_groupList.append(UTILS_file_io.read_string(fobject))
            object_meshIndex = UTILS_file_io.read_uint32(fobject)

            # got mesh first
            if object_isComponent:
                object_neededMesh = UTILS_functions.load_component(object_meshIndex)
            else:
                object_neededMesh = meshList[object_meshIndex].blender_data

            # create real object
            (object_target, skip_init) = UTILS_functions.create_instance_with_option(
                UTILS_constants.BmfileInfoType.OBJECT, item.name, opts_object, 
                extra_mesh=object_neededMesh)
            if skip_init:
                continue

            # link to correct collection
            if (object_fncgCollection is not None) and (not object_isComponent) and UTILS_functions.is_component(item.name):
                # a object should be grouped into fncg should check following requirements
                # fncg is not null
                # this object is a normal object
                # but its name match component format
                object_fncgCollection.objects.link(object_target)
            else:
                # otherwise, group it into normal collection
                blender_collection.objects.link(object_target)
            object_target.matrix_world = object_worldMatrix
            object_target.hide_set(object_isHidden)

            # write custom property
            if len(object_groupList) != 0:
                UTILS_virtools_prop.set_virtools_group_data(object_target, tuple(object_groupList))
            else:
                UTILS_virtools_prop.set_virtools_group_data(object_target, None)

        # update view layer after all objects has been imported
        blender_viewLayer.update()

    # release temp folder
    utils_tempFolderObj.cleanup()
    

# ========================================== 
# blender related functions

class _InfoBlockHelper():
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset
        self.blender_data = None

def _flat_vertices_index(faceList):
    for item in faceList:
        yield (item[0], )
        yield (item[3], )
        yield (item[6], )

def _flat_vertices_normal(faceList, vnList):
    for item in faceList:
        yield vnList[item[2]]
        yield vnList[item[5]]
        yield vnList[item[8]]

def _flat_vertices_uv(faceList, vtList):
    for item in faceList:
        yield vtList[item[1]]
        yield vtList[item[4]]
        yield vtList[item[7]]
