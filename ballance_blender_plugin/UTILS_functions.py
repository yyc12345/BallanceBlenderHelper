import bpy, bmesh, bpy_extras, mathutils
import struct, shutil, os
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from bpy_extras import io_utils, node_shader_utils
from . import UTILS_file_io, UTILS_constants, UTILS_virtools_prop

# =================================
# scene operation

def show_message_box(message, title, icon):

    def draw(self, context):
        layout = self.layout
        for item in message:
            layout.label(text=item, translate=False)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def add_into_scene_and_move_to_cursor(obj):
    move_to_cursor(obj)

    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)

def move_to_cursor(obj):
    obj.location = bpy.context.scene.cursor.location

# =================================
# is compoent

def is_component(name):
    return get_component_id(name) != -1

def get_component_id(name):
    for ind, comp in enumerate(UTILS_constants.bmfile_componentList):
        if name.startswith(comp):
            return ind
    return -1

# =================================
# create / parse material

def create_blender_material(input_mtl, packed_data):
    # adding material nodes
    create_material_nodes(input_mtl, packed_data)

    # write custom property
    UTILS_virtools_prop.set_virtools_material_data(input_mtl, packed_data)

def create_material_nodes(input_mtl, packed_data):
    (enable_virtools_material,
    ambient, diffuse, specular, emissive, specular_power, 
    alpha_test, alpha_blend, z_buffer, two_sided,
    texture) = packed_data

    # enable nodes mode
    input_mtl.use_nodes=True
    # delete all existed nodes
    for node in input_mtl.node_tree.nodes:
        input_mtl.node_tree.nodes.remove(node)

    # create ballance-style blender material
    bnode = input_mtl.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
    mnode = input_mtl.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    input_mtl.node_tree.links.new(bnode.outputs[0],mnode.inputs[0])

    input_mtl.metallic = sum(ambient) / 3
    input_mtl.diffuse_color = [i for i in diffuse] + [1]
    input_mtl.specular_color = specular
    input_mtl.specular_intensity = specular_power

    # adding a texture
    if texture is not None:
        inode = input_mtl.node_tree.nodes.new(type="ShaderNodeTexImage")
        inode.image = texture
        input_mtl.node_tree.links.new(inode.outputs[0], bnode.inputs[0])

# return None if fail to parse
def parse_material_nodes(mtl):
    # get node
    mat_wrap = node_shader_utils.PrincipledBSDFWrapper(mtl)
    # check existence of Principled BSDF
    if mat_wrap:
        # we trying get texture data from Principled BSDF
        use_mirror = mat_wrap.metallic != 0.0
        if use_mirror:
            mtl_ambient = (mat_wrap.metallic, mat_wrap.metallic, mat_wrap.metallic)
        else:
            mtl_ambient = (1.0, 1.0, 1.0)
        mtl_diffuse = (mat_wrap.base_color[0], mat_wrap.base_color[1], mat_wrap.base_color[2])
        mtl_specular = (mat_wrap.specular, mat_wrap.specular, mat_wrap.specular)
        mtl_emissive = mat_wrap.emission_color[:3]
        mtl_specularPower = 0.0

        # confirm texture
        mtl_texture = None
        tex_wrap = getattr(mat_wrap, "base_color_texture", None)
        if tex_wrap:
            image = tex_wrap.image
            if image:
                mtl_texture = image

        # return value
        return (True,
            mtl_ambient, mtl_diffuse, mtl_specular, mtl_emissive, mtl_specularPower,
            False, False, True, False,
            mtl_texture
        )

    else:
        return None

# =================================
# load component

def load_component(component_id):
    # get file first
    component_name = UTILS_constants.bmfile_componentList[component_id]
    selected_file = os.path.join(
        os.path.dirname(__file__),
        'meshes',
        component_name + '.bin'
    )

    # read file. please note this sector is sync with import_bm's mesh's code. when something change, please change each other.
    fmesh = open(selected_file, 'rb')

    # create real mesh, we don't need to consider name. blender will solve duplicated name
    mesh = bpy.data.meshes.new('mesh_' + component_name)
    
    vList = []
    vnList = []
    faceList = []
    # in first read, store all data into list
    listCount = UTILS_file_io.read_uint32(fmesh)
    for i in range(listCount):
        cache = UTILS_file_io.read_3vector(fmesh)
        # switch yz
        vList.append((cache[0], cache[2], cache[1]))
    listCount = UTILS_file_io.read_uint32(fmesh)
    for i in range(listCount):
        cache = UTILS_file_io.read_3vector(fmesh)
        # switch yz
        vnList.append((cache[0], cache[2], cache[1]))
    
    listCount = UTILS_file_io.read_uint32(fmesh)
    for i in range(listCount):
        faceData = UTILS_file_io.read_component_face(fmesh)

        # we need invert triangle sort
        faceList.append((
            faceData[4], faceData[5],
            faceData[2], faceData[3],
            faceData[0], faceData[1]
        ))
    
    # then, we need add correspond count for vertices
    mesh.vertices.add(len(vList))
    mesh.loops.add(len(faceList)*3)  # triangle face confirmed
    mesh.polygons.add(len(faceList))
    mesh.create_normals_split()

    # add vertices data
    mesh.vertices.foreach_set("co", unpack_list(vList))
    mesh.loops.foreach_set("vertex_index", unpack_list(_flat_component_vertices_index(faceList)))
    mesh.loops.foreach_set("normal", unpack_list(_flat_component_vertices_normal(faceList, vnList)))
    for i in range(len(faceList)):
        mesh.polygons[i].loop_start = i * 3
        mesh.polygons[i].loop_total = 3

        mesh.polygons[i].use_smooth = True
    
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=False, calc_edges_loose=False)

    fmesh.close()

    return mesh


def _flat_component_vertices_index(faceList):
    for item in faceList:
        yield (item[0], )
        yield (item[2], )
        yield (item[4], )

def _flat_component_vertices_normal(faceList, vnList):
    for item in faceList:
        yield vnList[item[1]]
        yield vnList[item[3]]
        yield vnList[item[5]]

# =================================
# create instance with option

def create_instance_with_option(instance_type, instance_name, instance_opt, 
        extra_mesh = None, extra_texture_path = None, extra_texture_filename = None):
    """
    Create instance with opetions

    `instance_type`, `instance_name`, `instance_opt` are essential for each type instances.  
    For object, you should provide `extra_mesh`.    
    For texture, you should provide `extra_texture_path` and `extra_texture_filename`.  

    """

    def get_instance():
        try:
            if instance_type == UTILS_constants.BmfileInfoType.OBJECT:
                temp_instance = bpy.data.objects[instance_name]
            elif instance_type == UTILS_constants.BmfileInfoType.MESH:
                temp_instance = bpy.data.meshes[instance_name]
            elif instance_type == UTILS_constants.BmfileInfoType.MATERIAL:
                temp_instance = bpy.data.materials[instance_name]
            elif instance_type == UTILS_constants.BmfileInfoType.TEXTURE:
                temp_instance = bpy.data.images[instance_name]

            temp_is_existed = True
        except:
            temp_instance = None
            temp_is_existed = False

        return (temp_instance, temp_is_existed)

    def create_instance():
        if instance_type == UTILS_constants.BmfileInfoType.OBJECT:
            instance_obj = bpy.data.objects.new(instance_name, extra_mesh)
            #instance_obj.name = instance_name
        elif instance_type == UTILS_constants.BmfileInfoType.MESH:
            instance_obj = bpy.data.meshes.new(instance_name)
            #instance_obj.name = instance_name
        elif instance_type == UTILS_constants.BmfileInfoType.MATERIAL:
            instance_obj = bpy.data.materials.new(instance_name)
            #instance_obj.name = instance_name
        elif instance_type == UTILS_constants.BmfileInfoType.TEXTURE:
            # this command will also check current available texture
            # because `get_instance()` only check texture name
            # but this strategy is not based on texture filepath, so this create method will 
            # correct this problem
            instance_obj = load_image(extra_texture_filename, extra_texture_path, check_existing=(instance_opt == 'CURRENT'))
            instance_obj.name = instance_name

        return instance_obj

    # analyze options
    if (not isinstance(instance_opt, str)) or instance_opt == 'RENAME':
        # create new instance
        # or always create new instance if opts is not string
        temp_instance = create_instance()
        temp_skip_init = False
    elif instance_opt == 'CURRENT':
        # try get instance
        (temp_instance, temp_is_existed) = get_instance()
        # if got instance successfully, we do not create new one, otherwise, we should 
        # create new instance
        if not temp_is_existed:
            temp_instance = create_instance()
            temp_skip_init = False
        else:
            temp_skip_init = True

    return (temp_instance, temp_skip_init)

