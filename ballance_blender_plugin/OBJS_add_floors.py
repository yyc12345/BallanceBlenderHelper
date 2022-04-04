import bpy,mathutils
import os, math
from bpy_extras import io_utils,node_shader_utils
# from bpy_extras.io_utils import unpack_list
from bpy_extras.image_utils import load_image
from . import UTILS_constants, UTILS_functions

class BALLANCE_OT_add_floors(bpy.types.Operator):
    """Add Ballance floor"""
    bl_idname = "ballance.add_floors"
    bl_label = "Add floor"
    bl_options = {'UNDO'}

    floor_type: bpy.props.EnumProperty(
        name="Type",
        description="Floor type",
        items=tuple((x, x, "") for x in UTILS_constants.floor_blockDict.keys()),
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

    use_2d_top : bpy.props.BoolProperty(
        name="Top edge"
    )
    use_2d_right : bpy.props.BoolProperty(
        name="Right edge"
    )
    use_2d_bottom : bpy.props.BoolProperty(
        name="Bottom edge"
    )
    use_2d_left : bpy.props.BoolProperty(
        name="Left edge"
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
        # get prefs
        prefs = bpy.context.preferences.addons[__package__].preferences
        prefs_externalTexture = prefs.external_folder

        # load mesh
        objmesh = bpy.data.meshes.new('done_')
        if self.floor_type in UTILS_constants.floor_basicBlockList:
            _load_basic_floor(
                objmesh, 
                self.floor_type, 
                'R0', 
                self.height_multiplier, 
                self.expand_length_1,
                self.expand_length_2,
                (self.use_2d_top,
                self.use_2d_right,
                self.use_2d_bottom,
                self.use_2d_left,
                self.use_3d_top,
                self.use_3d_bottom),
                (0.0, 0.0),
                prefs_externalTexture)
        elif self.floor_type in UTILS_constants.floor_derivedBlockList:
            _load_derived_floor(
                objmesh, 
                self.floor_type,
                self.height_multiplier, 
                self.expand_length_1,
                self.expand_length_2,
                (self.use_2d_top,
                self.use_2d_right,
                self.use_2d_bottom,
                self.use_2d_left,
                self.use_3d_top,
                self.use_3d_bottom),
                prefs_externalTexture)
        else:
            raise Exception("Fatal error: unknow floor type.")

        # normalization mesh
        objmesh.validate(clean_customdata=False)
        objmesh.update(calc_edges=False, calc_edges_loose=False)
        
        # create object and link it
        obj=bpy.data.objects.new('A_Floor_BMERevenge_', objmesh)
        UTILS_functions.add_into_scene_and_move_to_cursor(obj)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        # get floor prototype
        floor_prototype = UTILS_constants.floor_blockDict[self.floor_type]

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
        grids.label(text=UTILS_constants.floor_expandDirectionMap[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][0])
        grids.separator()
        grids.label(text=UTILS_constants.floor_expandDirectionMap[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][3])
        grids.template_icon(icon_value = UTILS_constants.icons_floorDict[self.floor_type])
        grids.label(text=UTILS_constants.floor_expandDirectionMap[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][1])
        grids.separator()
        grids.label(text=UTILS_constants.floor_expandDirectionMap[floor_prototype['InitColumnDirection']][floor_prototype['ExpandType']][2])
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
        grids.template_icon(icon_value = UTILS_constants.icons_floorDict[self.floor_type])
        grids.prop(self, "use_2d_right")
        grids.separator()
        grids.prop(self, "use_2d_bottom")
        grids.separator()

def _face_fallback(normal_face, expand_face, height):
    if expand_face == None:
        return normal_face
    
    if height <= 1.0:
        return normal_face
    else:
        return expand_face

def _create_or_get_material(material_name, prefs_externalTexture):
    # WARNING: this code is shared with bm_import_export
    deconflict_mtl_name = "BMERevenge_" + material_name

    # create or get material
    (mtl, skip_init) = UTILS_functions.create_instance_with_option(
        UTILS_constants.BmfileInfoType.MATERIAL,
        deconflict_mtl_name, 'CURRENT'
    )
    if skip_init:
        return mtl

    # initialize material parameter
    # load texture first
    texture_filename = UTILS_constants.floor_textureReflactionMap[material_name]
    deconflict_texture_name = "BMERevenge_" + texture_filename
    (texture, skip_init) = UTILS_functions.create_instance_with_option(
        UTILS_constants.BmfileInfoType.TEXTURE,
        deconflict_texture_name, 'CURRENT',
        extra_texture_path = prefs_externalTexture, extra_texture_filename = texture_filename
    )

    # iterate material statistic to get corresponding mtl data
    for try_item in UTILS_constants.floor_materialStatistic:
        if material_name in try_item['member']:
            # got it
            # set material data
            UTILS_functions.create_material_nodes(mtl,
                try_item['data']['ambient'], try_item['data']['diffuse'], 
                try_item['data']['specular'], try_item['data']['emissive'],
                try_item['data']['power'],
                texture)
            break
    
    # return mtl
    return mtl

def _solve_vec_data(str_data, d1, d2, d3, unit, unit_height):
    sp = str_data.split(';')
    sp_point = sp[0].split(',')
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

def _rotate_translate_vec(vec, rotation, unit, extra_translate):
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
        coso * vec[0] - sino * vec[1] + unit / 2 + extra_translate[0],
        sino * vec[0] + coso * vec[1] + unit / 2 + extra_translate[1],
        vec[2]
    )


def _solve_uv_data(str_data, d1, d2, d3, unit):
    sp = str_data.split(';')
    sp_point = sp[0].split(',')
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

def _solve_normal_data(point1, point2, point3):
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

def _solve_smashed_position(str_data, d1, d2):
    sp=str_data.split(';')
    sp_pos = sp[0].split(',')
    sp_sync = sp[1].split(',')

    vec = [int(sp_pos[0]), int(sp_pos[1])]

    for i in range(2):
        offset = 0 if sp_sync[i * 2] == '' else int(sp_sync[i * 2])
        if sp_sync[i*2+1] == 'd1':
            vec[i] += d1 + offset
        elif sp_sync[i*2+1] == 'd2':
            vec[i] += d2 + offset

    return tuple(vec)

def _virtual_foreach_set(collection, field, base_num, data):
    counter = 0
    for i in data:
        exec("a[j]." + field + "=q", {}, {
            'a': collection,
            'j': counter + base_num,
            'q': i
        })
        counter+=1



'''
sides_struct should be a tuple and it always have 6 bool items

(use_2d_top, use_2d_right, use_2d_bottom, use_2d_left, use_3d_top, use_3d_bottom)

WARNING: this code is shared with bm import export

'''
def _load_basic_floor(mesh, floor_type, rotation, height_multiplier, d1, d2, sides_struct, extra_translate, prefs_externalTexture):
    floor_prototype = UTILS_constants.floor_blockDict[floor_type]

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
        needCreatedFaces.append(_face_fallback(floor_prototype['TwoDTopSide'], floor_prototype['TwoDTopSideExpand'], height_multiplier))
    if sides_struct[1]:
        needCreatedFaces.append(_face_fallback(floor_prototype['TwoDRightSide'], floor_prototype['TwoDRightSideExpand'], height_multiplier))
    if sides_struct[2]:
        needCreatedFaces.append(_face_fallback(floor_prototype['TwoDBottomSide'], floor_prototype['TwoDBottomSideExpand'], height_multiplier))
    if sides_struct[3]:
        needCreatedFaces.append(_face_fallback(floor_prototype['TwoDLeftSide'], floor_prototype['TwoDLeftSideExpand'], height_multiplier))
    if sides_struct[4]:
        needCreatedFaces.append(floor_prototype['ThreeDTopFace'])
    if sides_struct[5]:
        needCreatedFaces.append(floor_prototype['ThreeDBottomFace'])

    # resolve face
    # solve material first
    materialDict = {}
    allmat = mesh.materials[:]
    counter = len(allmat)
    for face_define in needCreatedFaces:
        for face in face_define['Faces']:
            new_texture = face['Textures']
            if new_texture not in materialDict.keys():
                # try get from existed solt
                pending_material = _create_or_get_material(new_texture, prefs_externalTexture)
                if pending_material not in allmat:
                    # no matched. add it
                    mesh.materials.append(pending_material)
                    materialDict[new_texture] = counter
                    counter += 1
                else:
                    # use existed index
                    materialDict[new_texture] = allmat.index(pending_material)

    # now, we can process real mesh
    # load existed base count
    global_offset_vec = len(mesh.vertices)
    global_offset_polygons = len(mesh.polygons)
    global_offset_loops = len(mesh.loops)
    vecList = []
    uvList = []
    normalList = []
    faceList = []
    faceIndList = []
    faceMatList = []
    for face_define in needCreatedFaces:
        base_indices = len(vecList)
        for vec in face_define['Vertices']:
            vecList.append(_rotate_translate_vec(
                    _solve_vec_data(vec, d1, d2, height_multiplier, block_3dworld_unit, height_unit), 
                    rotation, block_3dworld_unit, extra_translate))

        for uv in face_define['UVs']:
            uvList.append(_solve_uv_data(uv, d1, d2, height_multiplier, block_uvworld_unit))

        for face in face_define['Faces']:
            if face['Type'] == 'RECTANGLE':
                # rectangle
                vec_indices = (
                    face['P1'] + base_indices, 
                    face['P2'] + base_indices,
                    face['P3'] + base_indices,
                    face['P4'] + base_indices)
                indCount = 4
            elif face['Type'] == 'TRIANGLE':
                # triangle
                vec_indices = (
                    face['P1'] + base_indices, 
                    face['P2'] + base_indices,
                    face['P3'] + base_indices)
                indCount = 3

            # we need calc normal and push it into list
            point_normal = _solve_normal_data(vecList[vec_indices[0]], vecList[vec_indices[1]], vecList[vec_indices[2]])
            for i in range(indCount):
                normalList.append(point_normal)
            
            # push indices into list
            for i in range(indCount):
                faceList.append(vec_indices[i] + global_offset_vec)

            # push material into list
            faceMatList.append(materialDict[face['Textures']])

            # push face vec count into list
            faceIndList.append(indCount)

    # push data into blender struct
    mesh.vertices.add(len(vecList))
    mesh.loops.add(len(faceList))
    mesh.polygons.add(len(faceMatList))
    mesh.create_normals_split()
    if mesh.uv_layers.active is None:
        # if no uv, create it
        mesh.uv_layers.new(do_init=False)

    _virtual_foreach_set(mesh.vertices, "co", global_offset_vec, vecList)
    _virtual_foreach_set(mesh.loops, "vertex_index", global_offset_loops, faceList)
    _virtual_foreach_set(mesh.loops, "normal", global_offset_loops, normalList)
    _virtual_foreach_set(mesh.uv_layers[0].data, "uv", global_offset_loops, uvList)

    cache_counter = 0
    for i in range(len(faceMatList)):
        indCount = faceIndList[i]
        mesh.polygons[i + global_offset_polygons].loop_start = global_offset_loops + cache_counter
        mesh.polygons[i + global_offset_polygons].loop_total = indCount
        mesh.polygons[i + global_offset_polygons].material_index = faceMatList[i]
        mesh.polygons[i + global_offset_polygons].use_smooth = True
        cache_counter += indCount
    

def _load_derived_floor(mesh, floor_type, height_multiplier, d1, d2, sides_struct, prefs_externalTexture):
    floor_prototype = UTILS_constants.floor_blockDict[floor_type]

    # set some unit
    if floor_prototype['UnitSize'] == 'Small':
        block_3dworld_unit = 2.5
    elif floor_prototype['UnitSize'] == 'Large':
        block_3dworld_unit = 5.0

    # construct face dict
    sides_dict = {
        'True': True,
        'False': False,
        '2dTop': sides_struct[0],
        '2dRight': sides_struct[1],
        '2dBottom': sides_struct[2],
        '2dLeft': sides_struct[3],
        '3dTop': sides_struct[4],
        '3dBottom': sides_struct[5]
    }

    # iterate smahsed blocks
    for blk in floor_prototype['SmashedBlocks']:
        start_pos = _solve_smashed_position(blk['StartPosition'], d1, d2)
        expand_pos = _solve_smashed_position(blk['ExpandPosition'], d1, d2)

        sides_data = tuple(sides_dict[x] for x in blk['SideSync'].split(';'))

        # call basic floor creator
        _load_basic_floor(
            mesh,
            blk['Type'],
            blk['Rotation'],
            height_multiplier,
            expand_pos[0],
            expand_pos[1],
            sides_data,
            (start_pos[0] * block_3dworld_unit, start_pos[1] * block_3dworld_unit),
            prefs_externalTexture
        )


