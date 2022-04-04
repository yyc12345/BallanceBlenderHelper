import bpy,bmesh,bpy_extras,mathutils
import pathlib,zipfile,time,os,tempfile,math
import struct, shutil
from bpy_extras import io_utils, node_shader_utils
from . import UTILS_constants, UTILS_functions, UTILS_file_io, UTILS_zip_helper

class BALLANCE_OT_export_bm(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a Ballance Map File (BM file spec 1.4)"""
    bl_idname = "ballance.export_bm"
    bl_label = 'Export BM'
    bl_options = {'PRESET'}

    # ExportHelper mixin class uses this
    filename_ext = ".bmx"
    filter_glob: bpy.props.StringProperty(
        default="*.bmx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    export_mode: bpy.props.EnumProperty(
        name="Export mode",
        items=(('COLLECTION', "Collection", "Export a collection"),
               ('OBJECT', "Objects", "Export an objects"),
               ),
        )

    def execute(self, context):
        if ((self.export_mode == 'COLLECTION' and context.scene.BallanceBlenderPluginProperty.collection_picker is None) or 
            (self.export_mode == 'OBJECT' and context.scene.BallanceBlenderPluginProperty.object_picker is None)):
            UTILS_functions.show_message_box(("No specific target", ), "Lost parameter", 'ERROR')
        else:
            prefs = bpy.context.preferences.addons[__package__].preferences

            if self.export_mode == 'COLLECTION':
                export_bm(context, self.filepath, 
                prefs.no_component_collection,
                self.export_mode, context.scene.BallanceBlenderPluginProperty.collection_picker)
            elif self.export_mode == 'OBJECT':
                export_bm(context, self.filepath, 
                prefs.no_component_collection,
                self.export_mode, context.scene.BallanceBlenderPluginProperty.object_picker)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_mode")
        if self.export_mode == 'COLLECTION':
            layout.prop(context.scene.BallanceBlenderPluginProperty, "collection_picker")
        elif self.export_mode == 'OBJECT':
            layout.prop(context.scene.BallanceBlenderPluginProperty, "object_picker")


def export_bm(context, bmx_filepath, prefs_fncg, opts_exportMode, opts_exportTarget):
    # ============================================ alloc a temp folder
    utils_tempFolderObj = tempfile.TemporaryDirectory()
    utils_tempFolder = utils_tempFolderObj.name
    utils_tempTextureFolder = os.path.join(utils_tempFolder, "Texture")
    os.makedirs(utils_tempTextureFolder)
    
    # ============================================ 
    # find export target. 
    # do not need check them validation in there. 
    # just collect them.
    if opts_exportMode== "COLLECTION":
        objectList = opts_exportTarget.objects
    else:
        objectList = [opts_exportTarget, ]

    # try get fncg collection
    # fncg stands with forced non-component group
    try:
        object_fncgCollection = bpy.data.collections[prefs_fncg]
    except:
        object_fncgCollection = None
   
    # ============================================ export
    with open(os.path.join(utils_tempFolder, "index.bm"), "wb") as finfo:
        UTILS_file_io.write_uint32(finfo, UTILS_constants.bmfile_currentVersion)
        
        # ====================== export object
        meshSet = set()
        meshList = []
        meshCount = 0        
        with open(os.path.join(utils_tempFolder, "object.bm"), "wb") as fobject:
            for obj in objectList:
                # only export mesh object
                if obj.type != 'MESH':
                    continue

                # clean no mesh object
                object_blenderMesh = obj.data
                if object_blenderMesh is None:
                    continue

                # check component
                if (object_fncgCollection is not None) and (obj.name in object_fncgCollection.objects):
                    # it should be set as normal object forcely
                    object_isComponent = False
                else:
                    # check isComponent normally
                    object_isComponent = UTILS_functions.is_component(obj.name)

                # triangle first and then group
                if not object_isComponent:
                    if object_blenderMesh not in meshSet:
                        _mesh_triangulate(object_blenderMesh)
                        meshSet.add(object_blenderMesh)
                        meshList.append(object_blenderMesh)
                        object_meshIndex = meshCount
                        meshCount += 1
                    else:
                        object_meshIndex = meshList.index(object_blenderMesh)
                else:
                    object_meshIndex = UTILS_functions.get_component_id(obj.name)

                # get visibility
                object_isHidden = not obj.visible_get()

                # try get grouping data
                object_groupList = _try_get_custom_property(obj, 'virtools-group')
                object_groupList = _set_value_when_none(object_groupList, [])

                # =======================
                # write to files
                # write finfo first
                UTILS_file_io.write_string(finfo, obj.name)
                UTILS_file_io.write_uint8(finfo, UTILS_constants.BmfileInfoType.OBJECT)
                UTILS_file_io.write_uint64(finfo, fobject.tell())

                # write fobject
                UTILS_file_io.write_bool(fobject, object_isComponent)
                UTILS_file_io.write_bool(fobject, object_isHidden)
                UTILS_file_io.write_world_matrix(fobject, obj.matrix_world)
                UTILS_file_io.write_uint32(fobject, len(object_groupList))
                for item in object_groupList:
                    UTILS_file_io.write_string(fobject, item)
                UTILS_file_io.write_uint32(fobject, object_meshIndex)

        # ====================== export mesh
        materialSet = set()
        materialList = []
        with open(os.path.join(utils_tempFolder, "mesh.bm"), "wb") as fmesh:
            for mesh in meshList:
                # split normals
                mesh.calc_normals_split()

                # write finfo first
                UTILS_file_io.write_string(finfo, mesh.name)
                UTILS_file_io.write_uint8(finfo, UTILS_constants.BmfileInfoType.MESH)
                UTILS_file_io.write_uint64(finfo, fmesh.tell())

                # write fmesh
                # vertices
                mesh_vecList = mesh.vertices[:]
                UTILS_file_io.write_uint32(fmesh, len(mesh_vecList))
                for vec in mesh_vecList:
                    #swap yz
                    UTILS_file_io.write_3vector(fmesh,vec.co[0],vec.co[2],vec.co[1])

                # uv
                mesh_faceIndexPairs = [(face, index) for index, face in enumerate(mesh.polygons)]
                UTILS_file_io.write_uint32(fmesh, len(mesh_faceIndexPairs) * 3)
                if mesh.uv_layers.active is not None:
                    uv_layer = mesh.uv_layers.active.data[:]
                    for f, f_index in mesh_faceIndexPairs:
                        # it should be triangle face, otherwise throw a error
                        if (f.loop_total != 3):
                            raise Exception("Not a triangle", f.poly.loop_total)

                        for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                            uv = uv_layer[loop_index].uv
                            # reverse v
                            UTILS_file_io.write_2vector(fmesh, uv[0], -uv[1])
                else:
                    # no uv data. write garbage
                    for i in range(len(mesh_faceIndexPairs) * 3):
                        UTILS_file_io.write_2vector(fmesh, 0.0, 0.0)

                # normals
                UTILS_file_io.write_uint32(fmesh, len(mesh_faceIndexPairs) * 3)
                for f, f_index in mesh_faceIndexPairs:
                    # no need to check triangle again
                    for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                        nml = mesh.loops[loop_index].normal
                        # swap yz
                        UTILS_file_io.write_3vector(fmesh, nml[0], nml[2], nml[1])

                # face
                # get material first
                mesh_usedBlenderMtl = mesh.materials[:]
                mesh_noMaterial = len(mesh_usedBlenderMtl) == 0
                for mat in mesh_usedBlenderMtl:
                    if mat not in materialSet:
                        materialSet.add(mat)
                        materialList.append(mat)

                UTILS_file_io.write_uint32(fmesh, len(mesh_faceIndexPairs))
                mesh_vtIndex = []
                mesh_vnIndex = []
                mesh_vIndex = []
                for f, f_index in mesh_faceIndexPairs:
                    # confirm material use
                    if mesh_noMaterial:
                        mesh_materialIndex = 0
                    else:
                        mesh_materialIndex = materialList.index(mesh_usedBlenderMtl[f.material_index])

                    # export face
                    mesh_vtIndex.clear()
                    mesh_vnIndex.clear()
                    mesh_vIndex.clear()

                    counter = 0
                    for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                        mesh_vIndex.append(mesh.loops[loop_index].vertex_index)
                        mesh_vnIndex.append(f_index * 3 + counter)
                        mesh_vtIndex.append(f_index * 3 + counter)
                        counter += 1
                    # reverse vertices sort
                    UTILS_file_io.write_face(fmesh,
                    mesh_vIndex[2], mesh_vtIndex[2], mesh_vnIndex[2],
                    mesh_vIndex[1], mesh_vtIndex[1], mesh_vnIndex[1],
                    mesh_vIndex[0], mesh_vtIndex[0], mesh_vnIndex[0])

                    # set used material
                    UTILS_file_io.write_bool(fmesh, not mesh_noMaterial)
                    UTILS_file_io.write_uint32(fmesh, mesh_materialIndex)

                # free splited normals
                mesh.free_normals_split()

        # ====================== export material
        textureSet = set()
        textureList = []
        textureCount = 0        
        with open(os.path.join(utils_tempFolder, "material.bm"), "wb") as fmaterial:
            for material in materialList:
                # write finfo first
                UTILS_file_io.write_string(finfo, material.name)
                UTILS_file_io.write_uint8(finfo, UTILS_constants.BmfileInfoType.MATERIAL)
                UTILS_file_io.write_uint64(finfo, fmaterial.tell())

                # try get original written data
                material_colAmbient = _try_get_custom_property(material, 'virtools-ambient')
                material_colDiffuse = _try_get_custom_property(material, 'virtools-diffuse')
                material_colSpecular = _try_get_custom_property(material, 'virtools-specular')
                material_colEmissive = _try_get_custom_property(material, 'virtools-emissive')
                material_specularPower = _try_get_custom_property(material, 'virtools-power')

                # get basic color
                mat_wrap = node_shader_utils.PrincipledBSDFWrapper(material)
                if mat_wrap:
                    use_mirror = mat_wrap.metallic != 0.0
                    if use_mirror:
                        material_colAmbient = _set_value_when_none(material_colAmbient, (mat_wrap.metallic, mat_wrap.metallic, mat_wrap.metallic))
                    else:
                        material_colAmbient = _set_value_when_none(material_colAmbient, (1.0, 1.0, 1.0))
                    material_colDiffuse = _set_value_when_none(material_colDiffuse, (mat_wrap.base_color[0], mat_wrap.base_color[1], mat_wrap.base_color[2]))
                    material_colSpecular = _set_value_when_none(material_colSpecular, (mat_wrap.specular, mat_wrap.specular, mat_wrap.specular))
                    material_colEmissive = _set_value_when_none(material_colEmissive, mat_wrap.emission_color[:3])
                    material_specularPower = _set_value_when_none(material_specularPower, 0.0)

                    # confirm texture
                    tex_wrap = getattr(mat_wrap, "base_color_texture", None)
                    if tex_wrap:
                        image = tex_wrap.image
                        if image:
                            # add into texture list
                            if image not in textureSet:
                                textureSet.add(image)
                                textureList.append(image)
                                textureIndex = textureCount
                                textureCount += 1
                            else:
                                textureIndex = textureList.index(image)

                            material_useTexture = True
                            material_textureIndex = textureIndex
                        else:
                            # no texture
                            material_useTexture = False
                            material_textureIndex = 0
                    else:
                        # no texture
                        material_useTexture = False
                        material_textureIndex = 0

                else:
                    # no Principled BSDF. write garbage
                    material_colAmbient = _set_value_when_none(material_colAmbient, (0.8, 0.8, 0.8))
                    material_colDiffuse = _set_value_when_none(material_colDiffuse, (0.8, 0.8, 0.8))
                    material_colSpecular = _set_value_when_none(material_colSpecular, (0.8, 0.8, 0.8))
                    material_colEmissive = _set_value_when_none(material_colEmissive, (0.8, 0.8, 0.8))
                    material_specularPower = _set_value_when_none(material_specularPower, 0.0)

                    material_useTexture = False
                    material_textureIndex = 0

                UTILS_file_io.write_color(fmaterial, material_colAmbient)
                UTILS_file_io.write_color(fmaterial, material_colDiffuse)
                UTILS_file_io.write_color(fmaterial, material_colSpecular)
                UTILS_file_io.write_color(fmaterial, material_colEmissive)
                UTILS_file_io.write_float(fmaterial, material_specularPower)
                UTILS_file_io.write_bool(fmaterial, material_useTexture)
                UTILS_file_io.write_uint32(fmaterial, material_textureIndex)
            

        # ====================== export texture
        texture_blenderFilePath = os.path.dirname(bpy.data.filepath)
        texture_existedTextureFilepath = set()        
        with open(os.path.join(utils_tempFolder, "texture.bm"), "wb") as ftexture:
            for texture in textureList:
                # write finfo first
                UTILS_file_io.write_string(finfo, texture.name)
                UTILS_file_io.write_uint8(finfo, UTILS_constants.BmfileInfoType.TEXTURE)
                UTILS_file_io.write_uint64(finfo, ftexture.tell())

                # confirm whether it is internal texture
                # get absolute texture path
                texture_filepath = io_utils.path_reference(texture.filepath, texture_blenderFilePath, utils_tempTextureFolder,
                                                            'ABSOLUTE', "", None, texture.library)
                # get file name and write it
                texture_filename = os.path.basename(texture_filepath)
                UTILS_file_io.write_string(ftexture, texture_filename)

                if (_is_external_texture(texture_filename)):
                    # write directly, use Ballance texture
                    UTILS_file_io.write_bool(ftexture, True)
                else:
                    # copy internal texture, if this file is copied, do not copy it again
                    UTILS_file_io.write_bool(ftexture, False)
                    if texture_filename not in texture_existedTextureFilepath:
                        shutil.copy(texture_filepath, os.path.join(utils_tempTextureFolder, texture_filename))
                        texture_existedTextureFilepath.add(texture_filename)


    # ============================================ 
    # save zip and clean up folder
    UTILS_zip_helper.compress(utils_tempFolder, bmx_filepath)
    utils_tempFolderObj.cleanup()

# ========================================== 
# blender related functions

def _is_external_texture(name):
    if name in UTILS_constants.bmfile_externalTextureSet:
        return True
    else:
        return False

def _mesh_triangulate(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def _try_get_custom_property(obj, field):
    try:
        return obj[field]
    except:
        return None

def _set_value_when_none(obj, newValue):
    if obj is None:
        return newValue
    else:
        return obj

