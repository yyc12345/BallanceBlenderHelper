import bpy,bmesh,bpy_extras,mathutils
import pathlib,zipfile,time,os,tempfile,math
import struct,shutil
from bpy_extras import io_utils,node_shader_utils
from . import utils, config

class ImportBM(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Ballance Map File (BM file spec 1.0)"""
    bl_idname = "import_scene.bm"
    bl_label = "Import BM "
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".bm"

    def execute(self, context):
        import_bm(context, self.filepath)
        return {'FINISHED'}
        
class ExportBM(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a Ballance Map File (BM file spec 1.0)"""
    bl_idname = "export_scene.bm"
    bl_label = 'Export BM'
    bl_options = {'PRESET'}
    filename_ext = ".bm"
    
    export_mode: bpy.props.EnumProperty(
        name="Export mode",
        items=(('COLLECTION', "Selected collection", "Export the selected collection"),
               ('OBJECT', "Selected objects", "Export the selected objects"),
               ),
        )
    export_target: bpy.props.StringProperty(
        name="Export target",
        description="Which one will be exported",
        )
    no_component_suffix: bpy.props.StringProperty(
        name="No component suffix",
        description="The object which have this suffix will not be saved as component.",
        )
    
    def execute(self, context):
        export_bm(context, self.filepath, self.export_mode, self.export_target, self.no_component_suffix)
        return {'FINISHED'}


# ========================================== method

bm_current_version = 10

def import_bm(context,filepath):
    # todo: finish this
    pass
    
def export_bm(context,filepath,export_mode, export_target, no_component_suffix):
    # ============================================ alloc a temp folder
    tempFolderObj = tempfile.TemporaryDirectory()
    tempFolder = tempFolderObj.name
    # debug
    # tempFolder = "G:\\ziptest"
    tempTextureFolder = os.path.join(tempFolder, "Texture")
    os.makedirs(tempTextureFolder)
    
    # ============================================ find export target
    if export_mode== "COLLECTION":
        objectList = bpy.data.collections[export_target].objects
    else:
        objectList = [bpy.data.objects[export_target]]

    needSuffixChecker = no_component_suffix != ""
    componentObj = set()
    for obj in objectList:
        if needSuffixChecker and obj.name.endwith(no_component_suffix):
            pass # meshObjList.add(obj)
        else:
            if is_component(obj.name):
                componentObj.add(obj)
            else:
                pass # meshObjList.add(obj)
                    
    # ============================================ export
    finfo = open(os.path.join(tempFolder, "index.bm"), "wb")
    finfo.write(struct.pack("I", bm_current_version))
    
    # ====================== export object
    fobject = open(os.path.join(tempFolder, "object.bm"), "wb")
    meshSet = set()
    meshList = []
    meshCount = 0
    for obj in objectList:
        # only export mesh object
        if obj.type != 'MESH':
            continue
        
        varis_component = obj in componentObj

        # clean no mesh object
        currentMesh = obj.data
        if currentMesh == None:
            continue
        # triangle first and then group
        if not varis_component:
            if currentMesh not in meshSet:
                mesh_triangulate(currentMesh)
                meshSet.add(currentMesh)
                meshList.append(currentMesh)
                meshId = meshCount
                meshCount += 1
            else:
                meshId = meshList.index(currentMesh)

        # write finfo first
        write_string(finfo, obj.name)
        write_int(finfo, info_bm_type.OBJECT)
        write_long(finfo, fobject.tell())

        # write fobject
        write_int(fobject, 1 if varis_component else 0)
        write_worldMatrix(fobject, obj.matrix_world)
        if varis_component:
            write_int(fobject, get_component_id(obj.name))
        else:
            write_int(fobject, meshId)

    fobject.close()

    # ====================== export mesh
    fmesh = open(os.path.join(tempFolder, "mesh.bm"), "wb")
    materialSet = set()
    materialList = []
    for mesh in meshList:
        mesh.calc_normals_split()

        # write finfo first
        write_string(finfo, mesh.name)
        write_int(finfo, info_bm_type.MESH)
        write_long(finfo, fmesh.tell())

        # write fmesh
        # vertices
        vecList = mesh.vertices[:]
        write_int(fmesh, len(vecList))
        for vec in vecList:
            #swap yz
            write_3vector(fmesh,vec.co[0],vec.co[2],vec.co[1])

        # uv
        face_index_pairs = [(face, index) for index, face in enumerate(mesh.polygons)]
        uv_layer = mesh.uv_layers.active.data[:]
        write_int(fmesh, len(face_index_pairs) * 3)
        for f, f_index in face_index_pairs:
            # it should be triangle face, otherwise throw a error
            if (f.loop_total != 3):
                raise Exception("Not a triangle", f.poly.loop_total)

            for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                uv = uv_layer[loop_index].uv
                # reverse v
                write_2vector(fmesh, uv[0], -uv[1])

        # normals
        write_int(fmesh, len(face_index_pairs) * 3)
        for f, f_index in face_index_pairs:
            # no need to check triangle again
            for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                nml = mesh.loops[loop_index].normal
                # swap yz
                write_3vector(fmesh, nml[0], nml[2], nml[1])

        # face
        # get material first
        currentMat = mesh.materials[:]
        noMaterial = len(currentMat) == 0
        for mat in currentMat:
            if mat not in materialSet:
                materialSet.add(mat)
                materialList.append(mat)

        write_int(fmesh, len(face_index_pairs))
        vtIndex = []
        vnIndex = []
        vIndex = []
        for f, f_index in face_index_pairs:
            # confirm material use
            if noMaterial:
                usedMat = 0
            else:
                usedMat = materialList.index(currentMat[f.material_index])

            # export face
            vtIndex.clear()
            vnIndex.clear()
            vIndex.clear()

            counter = 0
            for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                vIndex.append(mesh.loops[loop_index].vertex_index)
                vnIndex.append(f_index * 3 + counter)
                vtIndex.append(f_index * 3 + counter)
                counter += 1
            # reverse vertices sort
            write_face(fmesh,
            vIndex[2], vtIndex[2], vnIndex[2],
            vIndex[1], vtIndex[1], vnIndex[1],
            vIndex[0], vtIndex[0], vnIndex[0])

            # set used material
            write_int(fmesh, 0 if noMaterial else 1)
            write_int(fmesh, usedMat)

        mesh.free_normals_split()

    fmesh.close()

    # ====================== export material
    fmaterial = open(os.path.join(tempFolder, "material.bm"), "wb")
    textureSet = set()
    textureList = []
    textureCount = 0

    for material in materialList:
        # write finfo first
        write_string(finfo, material.name)
        write_int(finfo, info_bm_type.MATERIAL)
        write_long(finfo, fmaterial.tell())

        # write basic color
        mat_wrap = node_shader_utils.PrincipledBSDFWrapper(material)
        if mat_wrap:
            use_mirror = mat_wrap.metallic != 0.0
            if use_mirror:
                write_3vector(fmaterial, mat_wrap.metallic, mat_wrap.metallic, mat_wrap.metallic)
            else:
                write_3vector(fmaterial, 1, 1, 1)
            write_3vector(fmaterial, mat_wrap.base_color[0], mat_wrap.base_color[1], mat_wrap.base_color[2])
            write_3vector(fmaterial, mat_wrap.specular, mat_wrap.specular, mat_wrap.specular)
        
            # confirm texture
            tex_wrap = getattr(mat_wrap, "base_color_texture", None)
            if tex_wrap:
                image = tex_wrap.image
                if image:
                    # add into texture list
                    if image not in textureSet:
                        textureSet.add(image)
                        textureList.append(image)
                        currentTexture = textureCount
                        textureCount += 1
                    else:
                        currentTexture = textureList.index(image)

                    write_int(fmaterial, 1)
                    write_int(fmaterial, currentTexture)
                else:
                    # no texture
                    write_int(fmaterial, 0)
                    write_int(fmaterial, 0)
            else:
                # no texture
                write_int(fmaterial, 0)
                write_int(fmaterial, 0)

        else:
            # no Principled BSDF. write garbage
            write_3vector(fmaterial, 0.8, 0.8, 0.8)
            write_3vector(fmaterial, 0.8, 0.8, 0.8)
            write_3vector(fmaterial, 0.8, 0.8, 0.8)
            write_int(fmaterial, 0)
            write_int(fmaterial, 0)
    
    fmaterial.close()

    # ====================== export texture
    ftexture = open(os.path.join(tempFolder, "texture.bm"), "wb")
    source_dir = os.path.dirname(bpy.data.filepath)
    existed_texture = set()
    
    for texture in textureList:
        # write finfo first
        write_string(finfo, texture.name)
        write_int(finfo, info_bm_type.TEXTURE)
        write_long(finfo, ftexture.tell())

        # confirm internal
        texture_filepath = io_utils.path_reference(texture.filepath, source_dir, tempTextureFolder,
                                                       'ABSOLUTE', "", None, texture.library)
        filename = os.path.basename(texture_filepath)
        write_string(ftexture, filename)
        if (is_external_texture(filename)):
            write_int(ftexture, 1)
        else:
            # copy internal texture, if this file is copied, do not copy it again
            write_int(ftexture, 0)
            if filename not in existed_texture:
                shutil.copy(texture_filepath, os.path.join(tempTextureFolder, filename))
                existed_texture.add(filename)

    ftexture.close()

    # close info fs
    finfo.close()

    # ============================================ save zip and clean up folder
    if os.path.isfile(filepath):
        os.remove(filepath)
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED, 9) as zipObj:
       for folderName, subfolders, filenames in os.walk(tempFolder):
           for filename in filenames:
               filePath = os.path.join(folderName, filename)
               arcname=os.path.relpath(filePath, tempFolder)
               zipObj.write(filePath, arcname)
    tempFolderObj.cleanup()

# ======================================================================================= export / import assistant

class info_bm_type():
    OBJECT = 0
    MESH = 1
    MATERIAL = 2
    TEXTURE = 3

def is_component(name):
    return get_component_id(name) != -1

def get_component_id(name):
    return -1 # todo: finish this, -1 mean not a component

def is_external_texture(name):
    if name in config.external_texture_list:
        return True
    else:
        return False

def mesh_triangulate(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

# ======================================================================================= file io assistant

def write_string(fs,str):
    count=len(str)
    write_int(fs,count)
    fs.write(str.encode("utf_32_le"))

def write_int(fs,num):
    fs.write(struct.pack("I", num))

def write_long(fs,num):
    fs.write(struct.pack("Q", num))

def write_worldMatrix(fs, matt):
    mat = matt.transposed()
    fs.write(struct.pack("ffffffffffffffff",
    mat[0][0],mat[0][2], mat[0][1], mat[0][3],
    mat[2][0],mat[2][2], mat[2][1], mat[2][3],
    mat[1][0],mat[1][2], mat[1][1], mat[1][3],
    mat[3][0],mat[3][2], mat[3][1], mat[3][3]))

def write_3vector(fs, x, y ,z):
    fs.write(struct.pack("fff", x, y ,z))

def write_2vector(fs, u, v):
    fs.write(struct.pack("ff", u, v))

def write_face(fs, v1, vn1, vt1, v2, vn2, vt2, v3, vn3, vt3):
    fs.write(struct.pack("IIIIIIIII", v1, vn1, vt1, v2, vn2, vt2, v3, vn3, vt3))

