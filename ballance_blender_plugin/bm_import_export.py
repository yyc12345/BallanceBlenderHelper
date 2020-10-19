import bpy,bmesh,bpy_extras,mathutils
import pathlib,zipfile,time,os,tempfile,math
import struct,shutil
from bpy_extras import io_utils,node_shader_utils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from . import utils, config

class BALLANCE_OT_import_bm(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Ballance Map File (BM file spec 1.2)"""
    bl_idname = "ballance.import_bm"
    bl_label = "Import BM "
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".bmx"

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
        import_bm(context, self.filepath, prefs.external_folder, prefs.temp_texture_folder,
        self.texture_conflict_strategy, self.material_conflict_strategy, self.mesh_conflict_strategy, self.object_conflict_strategy)
        return {'FINISHED'}
        
class BALLANCE_OT_export_bm(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Save a Ballance Map File (BM file spec 1.2)"""
    bl_idname = "ballance.export_bm"
    bl_label = 'Export BM'
    bl_options = {'PRESET'}
    filename_ext = ".bmx"
    
    export_mode: bpy.props.EnumProperty(
        name="Export mode",
        items=(('COLLECTION', "Collection", "Export a collection"),
               ('OBJECT', "Objects", "Export an objects"),
               ),
        )

    def execute(self, context):
        if (self.export_mode == 'COLLECTION' and context.scene.BallanceBlenderPluginProperty.collection_picker is None) or (self.export_mode == 'OBJECT' and context.scene.BallanceBlenderPluginProperty.object_picker is None):
            utils.ShowMessageBox(("No specific target", ), "Lost parameter", 'ERROR')
        else:
            if self.export_mode == 'COLLECTION':
                export_bm(context, self.filepath, self.export_mode, context.scene.BallanceBlenderPluginProperty.collection_picker)
            elif self.export_mode == 'OBJECT':
                export_bm(context, self.filepath, self.export_mode, context.scene.BallanceBlenderPluginProperty.object_picker)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_mode")
        if self.export_mode == 'COLLECTION':
            layout.prop(context.scene.BallanceBlenderPluginProperty, "collection_picker")
        elif self.export_mode == 'OBJECT':
            layout.prop(context.scene.BallanceBlenderPluginProperty, "object_picker")

# ========================================== method

bm_current_version = 12

def import_bm(context,filepath,externalTexture,blenderTempFolder, textureOpt, materialOpt, meshOpt, objectOpt):
    # ============================================ alloc a temp folder
    tempFolderObj = tempfile.TemporaryDirectory()
    tempFolder = tempFolderObj.name
    # debug
    # print(tempFolder)
    tempTextureFolder = os.path.join(tempFolder, "Texture")
    prefs = bpy.context.preferences.addons[__package__].preferences
    blenderTempTextureFolder = prefs.temp_texture_folder
    externalTextureFolder = prefs.external_folder

    with zipfile.ZipFile(filepath, 'r', zipfile.ZIP_DEFLATED, 9) as zipObj:
        zipObj.extractall(tempFolder)

    # index.bm
    objectList = []
    meshList = []
    materialList = []
    textureList = []
    with open(os.path.join(tempFolder, "index.bm"), "rb") as findex:
        # judge version first
        gotten_version = read_uint32(findex)
        if (gotten_version != bm_current_version):
            utils.ShowMessageBox(("Unsupported BM spec. Expect: {} Gotten: {}".format(bm_current_version, gotten_version), ), "Unsupported BM spec", 'ERROR')
            findex.close()
            tempFolderObj.cleanup()
            return

        while len(peek_stream(findex)) != 0:
            index_name = read_string(findex)
            index_type = read_uint8(findex)
            index_offset = read_uint64(findex)
            blockCache = info_block_helper(index_name, index_offset)
            if index_type == info_bm_type.OBJECT:
                objectList.append(blockCache)
            elif index_type == info_bm_type.MESH:
                meshList.append(blockCache)
            elif index_type == info_bm_type.MATERIAL:
                materialList.append(blockCache)
            elif index_type == info_bm_type.TEXTURE:
                textureList.append(blockCache)
            else:
                pass


    # texture.bm
    with open(os.path.join(tempFolder, "texture.bm"), "rb") as ftexture:
        for item in textureList:
            ftexture.seek(item.offset, os.SEEK_SET)
            texture_filename = read_string(ftexture)
            texture_isExternal = read_bool(ftexture)
            if texture_isExternal:
                txur = load_image(texture_filename, externalTextureFolder, check_existing=(textureOpt == 'CURRENT'))
                item.blenderData = txur
            else:
                # not external. copy temp file into blender temp. then use it.
                # try copy. if fail, don't need to do more
                try:
                    shutil.copy(os.path.join(tempTextureFolder, texture_filename), os.path.join(blenderTempTextureFolder, texture_filename))
                except:
                    pass
                txur = load_image(texture_filename, blenderTempTextureFolder, check_existing=(textureOpt == 'CURRENT'))
                item.blenderData = txur
            txur.name = item.name

    # material.bm
    # WARNING: this code is shared with add_floor - create_or_get_material()
    with open(os.path.join(tempFolder, "material.bm"), "rb") as fmaterial:
        for item in materialList:
            fmaterial.seek(item.offset, os.SEEK_SET)

            # read data
            material_colAmbient = read_3vector(fmaterial)
            material_colDiffuse = read_3vector(fmaterial)
            material_colSpecular = read_3vector(fmaterial)
            material_colEmissive = read_3vector(fmaterial)
            material_specularPower = read_float(fmaterial)
            material_useTexture = read_bool(fmaterial)
            material_texture = read_uint32(fmaterial)

            # create basic material
            (m, needSkip) = createInstanceWithOption(info_bm_type.MATERIAL, item.name, materialOpt)
            item.blenderData = m
            if needSkip:
                continue
                
            m.use_nodes=True
            for node in m.node_tree.nodes:
                m.node_tree.nodes.remove(node)
            bnode=m.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
            mnode=m.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
            m.node_tree.links.new(bnode.outputs[0],mnode.inputs[0])

            m.metallic = sum(material_colAmbient) / 3
            m.diffuse_color = [i for i in material_colDiffuse] + [1]
            m.specular_color = material_colSpecular
            m.specular_intensity = material_specularPower

            # create a texture
            if material_useTexture:
                inode=m.node_tree.nodes.new(type="ShaderNodeTexImage")
                inode.image=textureList[material_texture].blenderData
                m.node_tree.links.new(inode.outputs[0],bnode.inputs[0])

            # write custom property
            m['virtools-ambient'] = material_colAmbient
            m['virtools-diffuse'] = material_colDiffuse
            m['virtools-specular'] = material_colSpecular
            m['virtools-emissive'] = material_colEmissive
            m['virtools-power'] = material_specularPower


    # mesh.bm
    # WARNING: this code is shared with add_floor
    with open(os.path.join(tempFolder, "mesh.bm"), "rb") as fmesh:
        vList=[]
        vtList=[]
        vnList=[]
        faceList=[]
        materialSolt = []
        for item in meshList:
            fmesh.seek(item.offset, os.SEEK_SET)

            # create real mesh
            (mesh, needSkip) = createInstanceWithOption(info_bm_type.MESH, item.name, meshOpt)
            item.blenderData = mesh
            if needSkip:
                continue

            vList.clear()
            vtList.clear()
            vnList.clear()
            faceList.clear()
            materialSolt.clear()
            # in first read, store all data into list
            listCount = read_uint32(fmesh)
            for i in range(listCount):
                cache = read_3vector(fmesh)
                # switch yz
                vList.append((cache[0], cache[2], cache[1]))
            listCount = read_uint32(fmesh)
            for i in range(listCount):
                cache = read_2vector(fmesh)
                # reverse v
                vtList.append((cache[0], -cache[1]))
            listCount = read_uint32(fmesh)
            for i in range(listCount):
                cache = read_3vector(fmesh)
                # switch yz
                vnList.append((cache[0], cache[2], cache[1]))
            
            listCount = read_uint32(fmesh)
            for i in range(listCount):
                faceData = read_face(fmesh)
                mesh_useMaterial = read_bool(fmesh)
                mesh_materialIndex = read_uint32(fmesh)

                if mesh_useMaterial:
                    neededMaterial = materialList[mesh_materialIndex].blenderData
                    if neededMaterial in materialSolt:
                        neededIndex = materialSolt.index(neededMaterial)
                    else:
                        neededIndex = len(materialSolt)
                        materialSolt.append(neededMaterial)
                else:
                    neededIndex = -1

                # we need invert triangle sort
                faceList.append((
                    faceData[6], faceData[7], faceData[8],
                    faceData[3], faceData[4], faceData[5],
                    faceData[0], faceData[1], faceData[2],
                    neededIndex
                ))

            # and then we need add material solt for this mesh
            for mat in materialSolt:
                mesh.materials.append(mat)

            # then, we need add correspond count for vertices
            mesh.vertices.add(len(vList))
            mesh.loops.add(len(faceList)*3)  # triangle face confirm
            mesh.polygons.add(len(faceList))
            mesh.uv_layers.new(do_init=False)
            mesh.create_normals_split()

            # add vertices data
            mesh.vertices.foreach_set("co", unpack_list(vList))
            mesh.loops.foreach_set("vertex_index", unpack_list(flat_vertices_index(faceList)))
            mesh.loops.foreach_set("normal", unpack_list(flat_vertices_normal(faceList, vnList)))
            mesh.uv_layers[0].data.foreach_set("uv", unpack_list(flat_vertices_uv(faceList, vtList)))
            for i in range(len(faceList)):
                mesh.polygons[i].loop_start = i * 3
                mesh.polygons[i].loop_total = 3
                if faceList[i][9] != -1:
                    mesh.polygons[i].material_index = faceList[i][9]

                mesh.polygons[i].use_smooth = True
            
            mesh.validate(clean_customdata=False)
            mesh.update(calc_edges=False, calc_edges_loose=False)
            

    # object
    with open(os.path.join(tempFolder, "object.bm"), "rb") as fobject:

        # we need get needed collection first
        view_layer = context.view_layer
        collection = view_layer.active_layer_collection.collection
        if prefs.no_component_collection == "":
            forcedCollection = None
        else:
            try:
                forcedCollection = bpy.data.collections[prefs.no_component_collection]
            except:
                forcedCollection = bpy.data.collections.new(prefs.no_component_collection)
                view_layer.active_layer_collection.collection.children.link(forcedCollection)

        # start process it
        for item in objectList:
            fobject.seek(item.offset, os.SEEK_SET)

            # read data
            object_isComponent = read_bool(fobject)
            object_isForcedNoComponent = read_bool(fobject)
            object_isHidden = read_bool(fobject)
            object_worldMatrix = read_worldMaterix(fobject)
            object_meshIndex = read_uint32(fobject)

            # got mesh first
            if object_isComponent:
                neededMesh = load_component(object_meshIndex)
            else:
                neededMesh = meshList[object_meshIndex].blenderData

            # create real object
            (obj, needSkip) = createInstanceWithOption(info_bm_type.OBJECT, item.name, objectOpt, extraMesh=neededMesh)
            if needSkip:
                continue
            if (not object_isComponent) and object_isForcedNoComponent and (forcedCollection is not None):
                forcedCollection.objects.link(obj)
            else:
                collection.objects.link(obj)
            obj.matrix_world = object_worldMatrix
            obj.hide_set(object_isHidden)

    view_layer.update()

    tempFolderObj.cleanup()
    
def export_bm(context, filepath, export_mode, export_target):
    # ============================================ alloc a temp folder
    tempFolderObj = tempfile.TemporaryDirectory()
    tempFolder = tempFolderObj.name
    # debug
    # tempFolder = "G:\\ziptest"
    tempTextureFolder = os.path.join(tempFolder, "Texture")
    os.makedirs(tempTextureFolder)
    prefs = bpy.context.preferences.addons[__package__].preferences
    
    # ============================================ find export target. don't need judge them in there. just collect them
    if export_mode== "COLLECTION":
        objectList = export_target.objects
    else:
        objectList = [export_target]

    # try get forcedCollection
    try:
        forcedCollection = bpy.data.collections[prefs.no_component_collection]
    except:
        forcedCollection = None
   
    # ============================================ export
    with open(os.path.join(tempFolder, "index.bm"), "wb") as finfo:
        write_uint32(finfo, bm_current_version)
        
        # ====================== export object
        meshSet = set()
        meshList = []
        meshCount = 0        
        with open(os.path.join(tempFolder, "object.bm"), "wb") as fobject:
            for obj in objectList:
                # only export mesh object
                if obj.type != 'MESH':
                    continue

                # clean no mesh object
                currentMesh = obj.data
                if currentMesh is None:
                    continue

                # judge component
                object_isComponent = is_component(obj.name)
                object_isForcedNoComponent = False
                if (forcedCollection is not None) and (obj.name in forcedCollection.objects):
                    # change it to forced no component
                    object_isComponent = False
                    object_isForcedNoComponent = True

                # triangle first and then group
                if not object_isComponent:
                    if currentMesh not in meshSet:
                        mesh_triangulate(currentMesh)
                        meshSet.add(currentMesh)
                        meshList.append(currentMesh)
                        meshId = meshCount
                        meshCount += 1
                    else:
                        meshId = meshList.index(currentMesh)
                else:
                    meshId = get_component_id(obj.name)

                # get visibility
                object_isHidden = not obj.visible_get()

                # write finfo first
                write_string(finfo, obj.name)
                write_uint8(finfo, info_bm_type.OBJECT)
                write_uint64(finfo, fobject.tell())

                # write fobject
                write_bool(fobject, object_isComponent)
                write_bool(fobject, object_isForcedNoComponent)
                write_bool(fobject, object_isHidden)
                write_worldMatrix(fobject, obj.matrix_world)
                write_uint32(fobject, meshId)

        # ====================== export mesh
        materialSet = set()
        materialList = []        
        with open(os.path.join(tempFolder, "mesh.bm"), "wb") as fmesh:
            for mesh in meshList:
                mesh.calc_normals_split()

                # write finfo first
                write_string(finfo, mesh.name)
                write_uint8(finfo, info_bm_type.MESH)
                write_uint64(finfo, fmesh.tell())

                # write fmesh
                # vertices
                vecList = mesh.vertices[:]
                write_uint32(fmesh, len(vecList))
                for vec in vecList:
                    #swap yz
                    write_3vector(fmesh,vec.co[0],vec.co[2],vec.co[1])

                # uv
                face_index_pairs = [(face, index) for index, face in enumerate(mesh.polygons)]
                write_uint32(fmesh, len(face_index_pairs) * 3)
                if mesh.uv_layers.active is not None:
                    uv_layer = mesh.uv_layers.active.data[:]
                    for f, f_index in face_index_pairs:
                        # it should be triangle face, otherwise throw a error
                        if (f.loop_total != 3):
                            raise Exception("Not a triangle", f.poly.loop_total)

                        for loop_index in range(f.loop_start, f.loop_start + f.loop_total):
                            uv = uv_layer[loop_index].uv
                            # reverse v
                            write_2vector(fmesh, uv[0], -uv[1])
                else:
                    # no uv data. write garbage
                    for i in range(len(face_index_pairs) * 3):
                        write_2vector(fmesh, 0.0, 0.0)

                # normals
                write_uint32(fmesh, len(face_index_pairs) * 3)
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

                write_uint32(fmesh, len(face_index_pairs))
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
                    write_bool(fmesh, not noMaterial)
                    write_uint32(fmesh, usedMat)

                mesh.free_normals_split()

        # ====================== export material
        textureSet = set()
        textureList = []
        textureCount = 0        
        with open(os.path.join(tempFolder, "material.bm"), "wb") as fmaterial:
            for material in materialList:
                # write finfo first
                write_string(finfo, material.name)
                write_uint8(finfo, info_bm_type.MATERIAL)
                write_uint64(finfo, fmaterial.tell())

                # try get original written data
                material_colAmbient = try_get_custom_property(material, 'virtools-ambient')
                material_colDiffuse = try_get_custom_property(material, 'virtools-diffuse')
                material_colSpecular = try_get_custom_property(material, 'virtools-specular')
                material_colEmissive = try_get_custom_property(material, 'virtools-emissive')
                material_specularPower = try_get_custom_property(material, 'virtools-power')

                # get basic color
                mat_wrap = node_shader_utils.PrincipledBSDFWrapper(material)
                if mat_wrap:
                    use_mirror = mat_wrap.metallic != 0.0
                    if use_mirror:
                        material_colAmbient = set_value_when_none(material_colAmbient, (mat_wrap.metallic, mat_wrap.metallic, mat_wrap.metallic))
                    else:
                        material_colAmbient = set_value_when_none(material_colAmbient, (1.0, 1.0, 1.0))
                    material_colDiffuse = set_value_when_none(material_colDiffuse, (mat_wrap.base_color[0], mat_wrap.base_color[1], mat_wrap.base_color[2]))
                    material_colSpecular = set_value_when_none(material_colSpecular, (mat_wrap.specular, mat_wrap.specular, mat_wrap.specular))
                    material_colEmissive = set_value_when_none(material_colEmissive, mat_wrap.emission_color[:3])
                    material_specularPower = set_value_when_none(material_specularPower, 0.0)

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

                            material_useTexture = True
                            material_texture = currentTexture
                        else:
                            # no texture
                            material_useTexture = False
                            material_texture = 0
                    else:
                        # no texture
                        material_useTexture = False
                        material_texture = 0

                else:
                    # no Principled BSDF. write garbage
                    material_colAmbient = set_value_when_none(material_colAmbient, (0.8, 0.8, 0.8))
                    material_colDiffuse = set_value_when_none(material_colDiffuse, (0.8, 0.8, 0.8))
                    material_colSpecular = set_value_when_none(material_colSpecular, (0.8, 0.8, 0.8))
                    material_colEmissive = set_value_when_none(material_colEmissive, (0.8, 0.8, 0.8))
                    material_specularPower = set_value_when_none(material_specularPower, 0.0)

                    material_useTexture = False
                    material_texture = 0

                write_color(fmaterial, material_colAmbient)
                write_color(fmaterial, material_colDiffuse)
                write_color(fmaterial, material_colSpecular)
                write_color(fmaterial, material_colEmissive)
                write_float(fmaterial, material_specularPower)
                write_bool(fmaterial, material_useTexture)
                write_uint32(fmaterial, material_texture)
            

        # ====================== export texture
        source_dir = os.path.dirname(bpy.data.filepath)
        existed_texture = set()        
        with open(os.path.join(tempFolder, "texture.bm"), "wb") as ftexture:
            for texture in textureList:
                # write finfo first
                write_string(finfo, texture.name)
                write_uint8(finfo, info_bm_type.TEXTURE)
                write_uint64(finfo, ftexture.tell())

                # confirm internal
                texture_filepath = io_utils.path_reference(texture.filepath, source_dir, tempTextureFolder,
                                                            'ABSOLUTE', "", None, texture.library)
                filename = os.path.basename(texture_filepath)
                write_string(ftexture, filename)
                if (is_external_texture(filename)):
                    write_bool(ftexture, True)
                else:
                    # copy internal texture, if this file is copied, do not copy it again
                    write_bool(ftexture, False)
                    if filename not in existed_texture:
                        shutil.copy(texture_filepath, os.path.join(tempTextureFolder, filename))
                        existed_texture.add(filename)


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

# shared

class info_bm_type():
    OBJECT = 0
    MESH = 1
    MATERIAL = 2
    TEXTURE = 3

# import

class info_block_helper():
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset
        self.blenderData = None

def createInstanceWithOption(instType, instName, instOpt, extraMesh = None):
    if instType == info_bm_type.OBJECT:
        target = bpy.data.objects
        args = (instName, extraMesh)
    elif instType == info_bm_type.MESH:
        target = bpy.data.meshes
        args = (instName, )
    elif instType == info_bm_type.MATERIAL:
        target = bpy.data.materials
        args = (instName, )

    if instOpt == 'RENAME':
        tempInst = target.new(*args)
        tempSkip = False
    elif instOpt == 'CURRENT':
        try:
            tempInst = target[instName]
            tempSkip = True
        except:
            tempInst = target.new(*args)
            tempSkip = False

    return (tempInst, tempSkip)

# NOTE: this function also used by add_elements.py
def load_component(component_id):
    # get file first
    compName = config.component_list[component_id]
    selectedFile = os.path.join(
        os.path.dirname(__file__),
        'meshes',
        compName + '.bin'
    )

    # read file. please note this sector is sync with import_bm's mesh's code. when something change, please change each other.
    fmesh = open(selectedFile, 'rb')

    # create real mesh, we don't need to consider name. blender will solve duplicated name
    mesh = bpy.data.meshes.new('mesh_' + compName)

    vList = []
    vnList = []
    faceList = []
    # in first read, store all data into list
    listCount = read_uint32(fmesh)
    for i in range(listCount):
        cache = read_3vector(fmesh)
        # switch yz
        vList.append((cache[0], cache[2], cache[1]))
    listCount = read_uint32(fmesh)
    for i in range(listCount):
        cache = read_3vector(fmesh)
        # switch yz
        vnList.append((cache[0], cache[2], cache[1]))
    
    listCount = read_uint32(fmesh)
    for i in range(listCount):
        faceData = read_component_face(fmesh)

        # we need invert triangle sort
        faceList.append((
            faceData[4], faceData[5],
            faceData[2], faceData[3],
            faceData[0], faceData[1]
        ))

    # then, we need add correspond count for vertices
    mesh.vertices.add(len(vList))
    mesh.loops.add(len(faceList)*3)  # triangle face confirm
    mesh.polygons.add(len(faceList))
    mesh.create_normals_split()

    # add vertices data
    mesh.vertices.foreach_set("co", unpack_list(vList))
    mesh.loops.foreach_set("vertex_index", unpack_list(flat_component_vertices_index(faceList)))
    mesh.loops.foreach_set("normal", unpack_list(flat_component_vertices_normal(faceList, vnList)))
    for i in range(len(faceList)):
        mesh.polygons[i].loop_start = i * 3
        mesh.polygons[i].loop_total = 3

        mesh.polygons[i].use_smooth = True
    
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=False, calc_edges_loose=False)

    fmesh.close()

    return mesh

def flat_vertices_index(faceList):
    for item in faceList:
        yield (item[0], )
        yield (item[3], )
        yield (item[6], )

def flat_vertices_normal(faceList, vnList):
    for item in faceList:
        yield vnList[item[2]]
        yield vnList[item[5]]
        yield vnList[item[8]]

def flat_vertices_uv(faceList, vtList):
    for item in faceList:
        yield vtList[item[1]]
        yield vtList[item[4]]
        yield vtList[item[7]]

def flat_component_vertices_index(faceList):
    for item in faceList:
        yield (item[0], )
        yield (item[2], )
        yield (item[4], )

def flat_component_vertices_normal(faceList, vnList):
    for item in faceList:
        yield vnList[item[1]]
        yield vnList[item[3]]
        yield vnList[item[5]]

# export

def is_component(name):
    return get_component_id(name) != -1

def get_component_id(name):
    for ind, comp in enumerate(config.component_list):
        if name.startswith(comp):
            return ind
    return -1

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

def try_get_custom_property(obj, field):
    try:
        return obj[field]
    except:
        return None

def set_value_when_none(obj, newValue):
    if obj is None:
        return newValue
    else:
        return obj

# ======================================================================================= file io assistant

# import

def peek_stream(fs):
    res = fs.read(1)
    fs.seek(-1, os.SEEK_CUR)
    return res

def read_float(fs):
    return struct.unpack("f", fs.read(4))[0]

def read_uint8(fs):
    return struct.unpack("B", fs.read(1))[0]

def read_uint32(fs):
    return struct.unpack("I", fs.read(4))[0]

def read_uint64(fs):
    return struct.unpack("Q", fs.read(8))[0]

def read_string(fs):
    count  = read_uint32(fs)
    return fs.read(count*4).decode("utf_32_le")

def read_bool(fs):
    return read_uint8(fs) != 0

def read_worldMaterix(fs):
    p = struct.unpack("ffffffffffffffff", fs.read(4*4*4))
    res = mathutils.Matrix((
    (p[0], p[2], p[1], p[3]),
    (p[8], p[10], p[9], p[11]),
    (p[4], p[6], p[5], p[7]),
    (p[12], p[14], p[13], p[15])))
    return res.transposed()

def read_3vector(fs):
    return struct.unpack("fff", fs.read(3*4))

def read_2vector(fs):
    return struct.unpack("ff", fs.read(2*4))

def read_face(fs):
    return struct.unpack("IIIIIIIII", fs.read(4*9))

def read_component_face(fs):
    return struct.unpack("IIIIII", fs.read(4*6))

# export

def write_string(fs,str):
    count=len(str)
    write_uint32(fs,count)
    fs.write(str.encode("utf_32_le"))

def write_uint8(fs,num):
    fs.write(struct.pack("B", num))

def write_uint32(fs,num):
    fs.write(struct.pack("I", num))

def write_uint64(fs,num):
    fs.write(struct.pack("Q", num))

def write_bool(fs,boolean):
    if boolean:
        write_uint8(fs, 1)
    else:
        write_uint8(fs, 0)

def write_float(fs,fl):
    fs.write(struct.pack("f", fl))

def write_worldMatrix(fs, matt):
    mat = matt.transposed()
    fs.write(struct.pack("ffffffffffffffff",
    mat[0][0],mat[0][2], mat[0][1], mat[0][3],
    mat[2][0],mat[2][2], mat[2][1], mat[2][3],
    mat[1][0],mat[1][2], mat[1][1], mat[1][3],
    mat[3][0],mat[3][2], mat[3][1], mat[3][3]))

def write_3vector(fs, x, y ,z):
    fs.write(struct.pack("fff", x, y ,z))

def write_color(fs, colors):
    write_3vector(fs, colors[0], colors[1], colors[2])

def write_2vector(fs, u, v):
    fs.write(struct.pack("ff", u, v))

def write_face(fs, v1, vt1, vn1, v2, vt2, vn2, v3, vt3, vn3):
    fs.write(struct.pack("IIIIIIIII", v1, vt1, vn1, v2, vt2, vn2, v3, vt3, vn3))

