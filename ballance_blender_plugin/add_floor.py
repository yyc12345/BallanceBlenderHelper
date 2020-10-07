import bpy,mathutils
import os, math
from bpy_extras import io_utils,node_shader_utils
from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from . import utils, config

class BALLANCE_OT_add_floor(bpy.types.Operator):
    """Add Ballance floor"""
    bl_idname = "ballance.add_floor"
    bl_label = "Add floor"
    bl_options = {'UNDO'}

    floor_type: bpy.props.EnumProperty(
        name="Type",
        description="Floor type",
        items=tuple((x, x, "") for x in config.floor_block_dict.keys()),
    )

    expand_length_1 : bpy.props.IntProperty(
        name="D1 length",
        description="The length of expand direction 1",
        min=0,
        default=0,
    )

    expand_length_2 : bpy.props.IntProperty(
        name="D2 length",
        description="The length of expand direction 2",
        min=0,
        default=0,
    )

    height_multiplier : bpy.props.FloatProperty(
        name="Height",
        description="The multiplier for height. Default height is 5",
        min=0.0,
        default=1.0,
    )

    rotation_inside_mesh: bpy.props.EnumProperty(
        name="Rotation",
        description="Rotation inside mesh",
        items=(
            ("R0", "0 degree", ""),
            ("R90", "90 degree", ""),
            ("R180", "180 degree", ""),
            ("R270", "270 degree", "")
        ),
        default="R0"
    )

    use_2d_top : bpy.props.BoolProperty(
        name="Top side"
    )
    use_2d_right : bpy.props.BoolProperty(
        name="Right side"
    )
    use_2d_bottom : bpy.props.BoolProperty(
        name="Bottom side"
    )
    use_2d_left : bpy.props.BoolProperty(
        name="Left side"
    )
    use_3d_top : bpy.props.BoolProperty(
        name="Top face"
    )
    use_3d_bottom : bpy.props.BoolProperty(
        name="Bottom face"
    )

    previous_floor_type = ''

    @classmethod
    def poll(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        return os.path.isdir(prefs.external_folder)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        # get floor prototype
        floor_prototype = config.floor_block_dict[self.floor_type]

        # try sync default value
        if self.previous_floor_type != self.floor_type:
            self.previous_floor_type = self.floor_type

            default_sides = floor_prototype['DefaultSideConfig']
            self.use_2d_top = default_sides['UseTwoDTop']
            self.use_2d_right = default_sides['UseTwoDRight']
            self.use_2d_bottom = default_sides['UseTwoDBottom']
            self.use_2d_left = default_sides['UseTwoDLeft']
            self.use_3d_top = default_sides['UseThreeDTop']
            self.use_3d_bottom = default_sides['UseThreeDBottom']

        # show property
        layout = self.layout
        col = layout.column()
        col.label(text="Basic param")
        col.prop(self, "floor_type")
        col.prop(self, "rotation_inside_mesh")
        col.prop(self, "height_multiplier")

        col.separator()
        col.label(text="Expand")
        if floor_prototype['ExpandType'] == 'Column' or floor_prototype['ExpandType'] == 'Freedom':
            col.prop(self, "expand_length_1")
        if floor_prototype['ExpandType'] == 'Freedom':
            col.prop(self, "expand_length_2")
        col.label(text="Unit size: " + floor_prototype['UnitSize'])
        col.label(text="Expand mode: " + floor_prototype['ExpandType'])
        grids = col.grid_flow(row_major=True, columns=3)
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][0])
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][3])
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][1])
        grids.separator()
        grids.label(text=config.floor_expand_direction_map[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][2])
        grids.separator()

        col.separator()
        col.label(text="Faces")
        row = col.row()
        row.prop(self, "use_3d_top")
        row.prop(self, "use_3d_bottom")

        col.separator()
        col.label(text="Sides")
        grids = col.grid_flow(row_major=True, columns=3)
        grids.separator()
        grids.prop(self, "use_2d_top")
        grids.separator()
        grids.prop(self, "use_2d_left")
        grids.template_icon(icon_value = config.blenderIcon_floor_dict[self.floor_type])
        grids.prop(self, "use_2d_right")
        grids.separator()
        grids.prop(self, "use_2d_bottom")
        grids.separator()

def face_fallback(normal_face, expand_face, height):
    if expand_face == None:
        return normal_face
    
    if height <= 1.0:
        return normal_face
    else:
        return expand_face

def create_or_get_material(material_name):
    # WARNING: this code is shared with bm_import_export
    deconflict_name = "BMERevenge_" + material_name
    try:
        m = bpy.data.materials[deconflict_name]
    except:
        # it is not existed, we need create a new one
        m = bpy.data.materials.new(deconflict_name)
        # we need init it.
        # load texture first
        externalTextureFolder = bpy.context.preferences.addons[__package__].preferences.external_folder
        txur = load_image(config.floor_texture_corresponding_map[material_name], externalTextureFolder, check_existing=False)    # force reload, we don't want it is shared with normal material
        # create material and link texture
        m.use_nodes=True
        for node in m.node_tree.nodes:
            m.node_tree.nodes.remove(node)
        bnode=m.node_tree.nodes.new(type="ShaderNodeBsdfPrincipled")
        mnode=m.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
        m.node_tree.links.new(bnode.outputs[0],mnode.inputs[0])

        inode=m.node_tree.nodes.new(type="ShaderNodeTexImage")
        inode.image=txur
        m.node_tree.links.new(inode.outputs[0],bnode.inputs[0])

        # write custom property
        # WARNING: this data is shared with BallanceVirtoolsPlugin - mapping_BM.cpp - fix_blender_texture
        m['virtools-ambient'] = (0.0, 0.0, 0.0)
        m['virtools-diffuse'] = (122 / 255.0, 122 / 255.0, 122 / 255.0) if material_name == 'FloorSide' else (1.0, 1.0, 1.0)
        m['virtools-specular'] = (0.0, 0.0, 0.0) if material_name == 'FloorSide' else (80 / 255.0, 80 / 255.0, 80 / 255.0)
        m['virtools-emissive'] = (104 / 255.0, 104 / 255.0, 104 / 255.0) if material_name == 'FloorSide' else (0.0, 0.0, 0.0)
        m['virtools-power'] = 0.0

    return m

def solve_vec_data(str_data, d1, d2, d3, unit, unit_height):
    sp = str_data.splite(';')
    sp_point = sp[0].splite(',')
    vec = [float(sp_point[0]), float(sp_point[1]), float(sp_point[2])]

    for i in range(3):
        symbol = sp[i+1]
        if symbol == '':
            continue

        factor = 1.0 if symbol[0] == '+' else -1.0
        p = symbol[1:]
        if p == 'd1':
            vec[i] += d1 * unit * factor
        elif p == 'd2':
            vec[i] += d2 * unit * factor
        elif p == 'd3':
            vec[i] += (d3 - 1) * unit_height * factor

    return vec

def rotate_vec(vec, rotation, unit):
    vec[0] -= unit / 2
    vec[1] -= unit / 2

    if rotation == 'R0':
        coso=1
        sino=0
    elif rotation == 'R90':
        coso=0
        sino=1
    elif rotation == 'R180':
        coso=-1
        sino=0
    elif rotation == 'R270':
        coso=0
        sino=-1

    return (
        coso * vec[0] - sino * vec[1] + unit / 2,
        sino * vec[0] + coso * vec[1] + unit / 2,
        vec[2]
    )


def solve_uv_data(str_data, d1, d2, d3, unit):
    sp = str_data.splite(';')
    sp_point = sp[0].splite(',')
    vec = [float(sp_point[0]), float(sp_point[1])]

    for i in range(2):
        symbol = sp[i+1]
        if symbol == '':
            continue

        factor = 1.0 if symbol[0] == '+' else -1.0
        p = symbol[1:]
        if p == 'd1':
            vec[i] += d1 * unit * factor
        elif p == 'd2':
            vec[i] += d2 * unit * factor
        elif p == 'd3':
            vec[i] += (d3 - 1) * unit * factor

    return tuple(vec)

def solve_normal_data(point1, point2, point3):
    vector1 = (
        point2[0] - point1[0],
        point2[1] - point1[1],
        point2[2] - point1[2]
    )
    vector2 = (
        point3[0] - point2[0],
        point3[1] - point2[1],
        point3[2] - point2[2]
    )

    # do vector x mutiply
    # vector1 x vector2
    nor = [
        vector1[1] * vector2[2] - vector1[2] * vector2[1],
        vector1[2] * vector2[0] - vector1[0] * vector2[2],
        vector1[0] * vector2[1] - vector1[1] * vector2[0]
    ]

    # do a normalization
    length = math.sqrt(nor[0] ** 2 + nor[1] ** 2 + nor[2] ** 2)
    nor[0] /= length
    nor[1] /= length
    nor[2] /= length

    return tuple(nor)


'''
sides_struct should be a tuple and it always have 6 bool items

(use_2d_top, use_2d_right, use_2d_bottom, use_2d_left, use_3d_top, use_3d_bottom)

WARNING: this code is shared with bm import export

'''
def load_basic_floor(mesh, floor_type, rotation, height_multiplier, d1, d2, sides_struct):
    floor_prototype = config.floor_block_dict[floor_type]

    # set some unit
    height_unit = 5.0
    if floor_prototype['UnitSize'] == 'Small':
        block_3dworld_unit = 2.5
        block_uvworld_unit = 0.5
    elif floor_prototype['UnitSize'] == 'Large':
        block_3dworld_unit = 5.0
        block_uvworld_unit = 1.0

    # got all needed faces
    needCreatedFaces = []
    if sides_struct[0]:
        needCreatedFaces.append(face_fallback(floor_prototype['TwoDTopSide'], floor_prototype['TwoDTopSideExpand'], height_multiplier))
    if sides_struct[1]:
        needCreatedFaces.append(face_fallback(floor_prototype['TwoDRightSide'], floor_prototype['TwoDRightSideExpand'], height_multiplier))
    if sides_struct[2]:
        needCreatedFaces.append(face_fallback(floor_prototype['TwoDBottomSide'], floor_prototype['TwoDBottomSideExpand'], height_multiplier))
    if sides_struct[3]:
        needCreatedFaces.append(face_fallback(floor_prototype['TwoDLeftSide'], floor_prototype['TwoDLeftSideExpand'], height_multiplier))
    if sides_struct[4]:
        needCreatedFaces.append(floor_prototype['ThreeDTopFace'])
    if sides_struct[5]:
        needCreatedFaces.append(floor_prototype['ThreeDBottomFace'])

    # resolve face
    # solve material first
    materialDict = {}
    counter = 0
    mesh.materials.clear()
    for face_define in needCreatedFaces:
        for face in face_define['Faces']:
            new_texture = face['Textures']
            if new_texture not in materialDict.keys():
                mesh.materials.append(create_or_get_material(new_texture))
                materialDict[new_texture] = counter
                counter += 1

    # now, we can process real mesh
    vecList = []
    uvList = []
    normalList = []
    faceList = []
    faceMatList = []
    for face_define in needCreatedFaces:
        base_indices = len(vecList)
        for vec in face_define['Vertices']:
            vecList.append(rotate_vec(
                    solve_vec_data(vec, d1, d2, height_multiplier, block_3dworld_unit, height_unit), 
                    rotation, block_3dworld_unit))

        for uv in face_define['UVs']:
            uvList.append(solve_uv_data(uv, d1, d2, height_multiplier, block_uvworld_unit))

        for face in face_define['Faces']:
            vec_indices = (
                face['P1'] + base_indices, 
                face['P2'] + base_indices,
                face['P3'] + base_indices,
                face['P4'] + base_indices)

            # we need calc normal and push it into list
            four_point_normal = solve_normal_data(vecList[vec_indices[0]]), vecList[vec_indices[1]], vecList[vec_indices[2]])
            for i in range(4):
                normalList.append(four_point_normal)
            
            # push indices into list
            for i in range(4):
                faceList.append((vec_indices[i], ))

            # push material into list
            faceMatList.append(materialDict[face['Textures']])

    # push data into blender struct
    mesh.vertices.add(len(vecList))
    mesh.loops.add(len(faceMatList)*4)  # 4 vec face confirm
    mesh.polygons.add(len(faceMatList))
    mesh.uv_layers.new(do_init=False)
    mesh.create_normals_split()

    mesh.vertices.foreach_set("co", unpack_list(vecList))
    mesh.loops.foreach_set("vertex_index", unpack_list(faceList))
    mesh.loops.foreach_set("normal", unpack_list(normalList))
    mesh.uv_layers[0].data.foreach_set("uv", unpack_list(uvList))

    for i in range(len(faceMatList)):
        mesh.polygons[i].loop_start = i * 4
        mesh.polygons[i].loop_total = 4
        mesh.polygons[i].material_index = faceMatList[i]
        mesh.polygons[i].use_smooth = True
    
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=False, calc_edges_loose=False)

def load_derived_floor(mesh, floor_type, rotation, height_multiplier, d1, d2, sides_struct):
    pass
