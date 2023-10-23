import bpy, bmesh, mathutils
import typing, array, collections
from . import UTIL_functions, UTIL_virtools_types

## Blender Mesh Usage
#  This module create a universal mesh visitor, including MeshReader, MeshWriter and MeshUVModifier
#  for every other possible module using.
#  Obviously, MeshReader is served for 2 exporter, MeshWriter is served for 2 importer.
#  MeshWriter also served for BMERevenge module and Ballance element loading.
#  MeshUVModifier is used by Flatten UV and Rail UV.
#

#region Assist Functions

class FaceVertexData():
    mPosIdx: int
    mNmlIdx: int
    mUvIdx: int
    
    def __init__(self, pos: int = 0, nml: int = 0, uv: int = 0):
        self.mPosIdx = pos
        self.mNmlIdx = nml
        self.mUvIdx = uv

class FaceData():
    ## @remark List or tuple. List is convenient for adding and removing
    mIndices: tuple[FaceVertexData] | list[FaceVertexData]
    ## Face used material slot index
    #  @remark If material slot is empty, or this face do not use material, set this value to 0.
    mMtlIdx: int
    
    def __init__(self, indices: tuple[FaceVertexData] | list[FaceVertexData] = tuple(), mtlidx: int = 0):
        self.mIndices = indices
        self.mMtlIdx = mtlidx
    
    def is_indices_legal(self) -> bool:
        return len(self.mIndices) >= 3

def _flat_vxvector3(it: typing.Iterator[UTIL_virtools_types.VxVector3]) -> typing.Iterator[float]:
    for entry in it:
        yield entry.x
        yield entry.y
        yield entry.z

def _flat_vxvector2(it: typing.Iterator[UTIL_virtools_types.VxVector2]) -> typing.Iterator[float]:
    for entry in it:
        yield entry.x
        yield entry.y

def _flat_face_nml_index(nml_idx: array.array, nml_array: array.array) -> typing.Iterator[float]:
    for idx in nml_idx:
        pos: int = idx * 3
        yield nml_array[pos]
        yield nml_array[pos + 1]
        yield nml_array[pos + 2]

def _flat_face_uv_index(uv_idx: array.array, uv_array: array.array) -> typing.Iterator[float]:
    for idx in uv_idx:
        pos: int = idx * 2
        yield uv_array[pos]
        yield uv_array[pos + 1]

def _nest_custom_split_normal(nml_idx: array.array, nml_array: array.array) -> typing.Iterator[UTIL_virtools_types.ConstVxVector3]:
    for idx in nml_idx:
        pos: int = idx * 3
        yield (nml_array[pos], nml_array[pos + 1], nml_array[pos + 2])

class TemporaryMesh():
    """
    
    """
    
    __mBindingObject: bpy.types.Object | None
    __mTempMesh: bpy.types.Mesh | None
    
    def __init__(self, binding_obj: bpy.types.Object):
        self.__mBindingObject = binding_obj
        self.__mTempMesh = None
        
        if self.__mBindingObject.data is None:
            raise UTIL_functions.BBPException('try getting mesh from an object without mesh.')
        self.__mTempMesh = self.__mBindingObject.to_mesh()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def is_valid(self) -> bool:
        if self.__mBindingObject is None: return False
        if self.__mTempMesh is None: return False
        return True
    
    def dispose(self) -> None:
        if self.is_valid():
            self.__mTempMesh = None
            self.__mBindingObject.to_mesh_clear()
            self.__mBindingObject = None
    
    def get_temp_mesh(self) -> bpy.types.Mesh:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try calling invalid TemporaryMesh.')
        return self.__mTempMesh

#endregion

class MeshReader():
    """
    The passed mesh must be created by bpy.types.Object.to_mesh() and destroyed by bpy.types.Object.to_mesh_clear().
    Because this class must trianglate mesh. To prevent change original mesh, this operations is essential.
    A helper class TemporaryMesh can help you do this.
    """
    
    __mAssocMesh: bpy.types.Mesh | None ##< The binding mesh for this reader. None if this reader is invalid.
    
    def __init__(self, assoc_mesh: bpy.types.Mesh):
        self.__mAssocMesh = assoc_mesh
        
        # triangulate temp mesh
        if self.is_valid():
            self.__triangulate_mesh()
            self.__mAssocMesh.calc_normals_split()
    
    def is_valid(self) -> bool:
        return self.__mAssocMesh is not None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self) -> None:
        if self.is_valid():
            # reset mesh
            self.__mAssocMesh.free_normals_split()
            self.__mAssocMesh = None
    
    def get_vertex_position_count(self) -> int:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        return len(self.__mAssocMesh.vertices)
    
    def get_vertex_position(self) -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')

        cache: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for vec in self.__mAssocMesh.vertices:
            cache.x = vec.co.x
            cache.y = vec.co.y
            cache.z = vec.co.z
            yield cache
    
    def get_vertex_normal_count(self) -> int:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        # return loops count, equaling with face count * 3 in theory.
        return len(self.__mAssocMesh.loops)
    
    def get_vertex_normal(self) -> typing.Iterator[UTIL_virtools_types.VxVector3]:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')

        cache: UTIL_virtools_types.VxVector3 = UTIL_virtools_types.VxVector3()
        for nml in self.__mAssocMesh.loops:
            cache.x = nml.normal.x
            cache.y = nml.normal.y
            cache.z = nml.normal.z
            yield cache

    def get_vertex_uv_count(self) -> int:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        if self.__mAssocMesh.uv_layers.active is None:
            # if no uv layer, we need make a fake one
            # return the same value with normals.
            # it also mean create uv for each face vertex
            return len(self.__mAssocMesh.loops)
        else:
            # otherwise return its size, also equaling with face count * 3 in theory
            return len(self.__mAssocMesh.uv_layers.active.uv)

    def get_vertex_uv(self) -> typing.Iterator[UTIL_virtools_types.VxVector2]:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')

        cache: UTIL_virtools_types.VxVector2 = UTIL_virtools_types.VxVector2()
        if self.__mAssocMesh.uv_layers.active is None:
            # create a fake one
            cache.x = 0.0
            cache.y = 0.0
            for _ in range(self.get_vertex_uv_count()):
                yield cache
        else:
            for uv in self.__mAssocMesh.uv_layers.active.uv:
                cache.x = uv.vector.x
                cache.y = uv.vector.y
                yield cache

    def get_material_slot_count(self) -> int:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        return len(self.__mAssocMesh.materials)

    def get_material_slot(self) -> typing.Iterator[bpy.types.Material]:
        """
        @remark This generator may return None if this slot do not link to may material.
        """
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        for mtl in self.__mAssocMesh.materials:
            yield mtl

    def get_face_count(self) -> int:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        return len(self.__mAssocMesh.polygons)

    def get_face(self) -> typing.Iterator[FaceData]:
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshReader.')
        
        # detect whether we have material
        no_mtl: bool = self.get_material_slot_count() == 0

        # use list as indices container for convenient adding and deleting.
        cache: FaceData = FaceData([], 0)
        for face in self.__mAssocMesh.polygons:
            # confirm material use
            # a face without mtl have 2 situations. first is the whole object do not have mtl
            # another is this face use an empty mtl slot.
            if no_mtl:
                cache.mMtlIdx = 0
            else:
                cache.mMtlIdx = face.material_index

            # resize indices
            self.__resize_face_data_indices(cache.mIndices, face.loop_total)
            # set indices
            for i in range(face.loop_total):
                cache.mIndices[i].mPosIdx = self.__mAssocMesh.loops[face.loop_start + i].vertex_index
                cache.mIndices[i].mNmlIdx = face.loop_start + i
                cache.mIndices[i].mUvIdx = face.loop_start + i

            # return value
            yield cache

    def __resize_face_data_indices(self, ls: list[FaceVertexData], expected_size: int) -> None:
        diff: int = expected_size - len(ls)
        if diff > 0:
            # add entry
            for _ in range(diff):
                ls.append(FaceVertexData())
        elif diff < 0:
            # remove entry
            for _ in range(diff):
                ls.pop()
        else:
            # no count diff, pass
            pass
        
    def __triangulate_mesh(self) -> None:
        bm = bmesh.new()
        bm.from_mesh(self.__mAssocMesh)
        bmesh.ops.triangulate(bm, faces = bm.faces)
        bm.to_mesh(self.__mAssocMesh)
        bm.free()

class MeshWriter():
    """
    If face do not use material, pass 0 as its material index.
    If face do not have UV becuase it doesn't have material, you at least create 1 UV vector, eg. (0, 0),
    then refer it to all face uv.
    """
    
    class MeshWriterPartData():
        mVertexPosition: typing.Iterator[UTIL_virtools_types.VxVector3] | None
        mVertexNormal: typing.Iterator[UTIL_virtools_types.VxVector3] | None
        mVertexUV: typing.Iterator[UTIL_virtools_types.VxVector2] | None
        mFace: typing.Iterator[FaceData] | None
        mMaterial: typing.Iterator[bpy.types.Material] | None
        
        def __init__(self):
            self.mVertexPosition = None
            self.mVertexNormal = None
            self.mVertexUV = None
            self.mFace = None
            self.mMaterial = None
        
        def is_valid(self) -> bool:
            if self.mVertexPosition is None: return False
            if self.mVertexNormal is None: return False
            if self.mVertexUV is None: return False
            if self.mFace is None: return False
            if self.mMaterial is None: return False
            return True
    
    __mAssocMesh: bpy.types.Mesh | None ##< The binding mesh for this writer. None if this writer is invalid.
    
    __mVertexPos: array.array ##< Array item is float(f). Length must be an integer multiple of 3.
    __mVertexNormal: array.array ##< Array item is float(f). Length must be an integer multiple of 3.
    __mVertexUV: array.array ##< Array item is float(f). Length must be an integer multiple of 2.
    
    ## Array item is int32(L).
    #  Length must be the sum of each items in __mFaceVertexCount.
    #  Item is face vertex position index, based on 0, pointing to __mVertexPos (visiting need multiple it with 3 because __mVertexPos is flat struct).
    __mFacePosIndices: array.array
    ## Same as __mFacePosIndices, but store face vertex normal index.
    #  Array item is int32(L). Length is equal to __mFacePosIndices
    __mFaceNmlIndices: array.array
    ## Same as __mFacePosIndices, but store face vertex uv index.
    #  Array item is int32(L). Length is equal to __mFacePosIndices
    __mFaceUvIndices: array.array
    ## Array item is int32(L).
    #  Length is the face count.
    #  It indicate how much vertex need to be consumed in __mFacePosIndices, __mFaceNmlIndices and __mFaceUvIndices for one face.
    __mFaceVertexCount: array.array
    __mFaceMtlIdx: array.array  ##< Array item is int32(L). Length is equal to __mFaceVertexCount.
    
    ## Material Slot.
    #  Each item is unique make sure by __mMtlSlotMap
    __mMtlSlot: list[bpy.types.Material]
    ## The map to make sure every item in __mMtlSlot is unique.
    #  Key is bpy.types.Material
    #  Value is key's index in __mMtlSlot.
    __mMtlSlotMap: dict[bpy.types.Material, int]
    
    def __init__(self, assoc_mesh: bpy.types.Mesh):
        self.__mAssocMesh = assoc_mesh
        
        self.__mVertexPos = array.array('f')
        self.__mVertexNormal = array.array('f')
        self.__mVertexUV = array.array('f')
        
        self.__mFacePosIndices = array.array('L')
        self.__mFaceNmlIndices = array.array('L')
        self.__mFaceUvIndices = array.array('L')
        self.__mFaceVertexCount = array.array('L')
        self.__mFaceMtlIdx = array.array('L')
        
        self.__mMtlSlot = []
        self.__mMtlSlotMap = {}
    
    def is_valid(self) -> bool:
        return self.__mAssocMesh is not None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.dispose()
    
    def dispose(self):
        if self.is_valid():
            # write mesh
            self.__write_mesh()
            # reset mesh
            self.__mAssocMesh = None
    
    def add_part(self, data: MeshWriterPartData):
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshWriter.')
        if not data.is_valid():
            raise UTIL_functions.BBPException('invalid mesh part data.')
        
        # add vertex data
        prev_vertex_pos_count: int = len(self.__mVertexPos)
        self.__mVertexPos.extend(_flat_vxvector3(data.mVertexPosition))
        prev_vertex_nml_count: int = len(self.__mVertexNormal)
        self.__mVertexNormal.extend(_flat_vxvector3(data.mVertexNormal))
        prev_vertex_uv_count: int = len(self.__mVertexUV)
        self.__mVertexUV.extend(_flat_vxvector2(data.mVertexUV))
        
        # add material slot data and create mtl remap
        mtl_remap: list[int] = []
        for mtl in data.mMaterial:
            idx: int | None = self.__mMtlSlotMap.get(mtl, None)
            if idx:
                mtl_remap.append(idx)
            else:
                self.__mMtlSlotMap[mtl] = len(self.__mMtlSlot)
                mtl_remap.append(len(self.__mMtlSlot))
                self.__mMtlSlot.append(mtl)
        
        # add face data
        for face in data.mFace:
            # check indices count
            if not face.is_indices_legal():
                raise UTIL_functions.BBPException('face must have at least 3 vertex.')
            
            # add indices
            for vec_index in face.mIndices:
                self.__mFacePosIndices.append(vec_index.mPosIdx + prev_vertex_pos_count)
                self.__mFaceNmlIndices.append(vec_index.mNmlIdx + prev_vertex_nml_count)
                self.__mFaceUvIndices.append(vec_index.mUvIdx + prev_vertex_uv_count)
            self.__mFaceVertexCount.append(len(face.mIndices))
            
            # add face mtl with remap
            mtl_idx: int = face.mMtlIdx
            if mtl_idx < 0 or mtl_idx > len(mtl_remap):
                # fall back. add 0
                self.__mFaceMtlIdx.append(0)
            else:
                self.__mFaceMtlIdx.append(mtl_remap[mtl_idx])
    
    def __write_mesh(self):
        # detect status
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshWriter.')
        # and clear mesh
        self.__clear_mesh()
        
        # push material data
        for mtl in self.__mMtlSlot:
            self.__mAssocMesh.materials.append(mtl)
        
        # add corresponding count for vertex position
        self.__mAssocMesh.vertices.add(len(self.__mVertexPos))
        # add loops data, it is the sum count of indices
        # we use face pos indices size to get it
        self.__mAssocMesh.loops.add(len(self.__mFacePosIndices))
        # set face count
        self.__mAssocMesh.polygons.add(len(self.__mFaceVertexCount))
        # create uv layer
        self.__mAssocMesh.uv_layers.new(do_init = False)
        # split normals, it is IMPORTANT
        self.__mAssocMesh.create_normals_split()
        
        # add vertex position data
        self.__mAssocMesh.vertices.foreach_set('co', self.__mVertexPos)
        # add face vertex pos index data
        self.__mAssocMesh.loops.foreach_set('vertex_index', self.__mFacePosIndices)
        # add face vertex nml by function
        self.__mAssocMesh.loops.foreach_set('normal',
            list(_flat_face_nml_index(self.__mFaceNmlIndices, self.__mVertexNormal))
        )
        # add face vertex uv by function
        self.__mAssocMesh.uv_layers.active.uv.foreach_set('vector',
            list(_flat_face_uv_index(self.__mFaceUvIndices, self.__mVertexUV))
        )   # NOTE: blender 3.5 changed. UV must be visited by .uv, not the .data
        
        # iterate face to set face data
        fVertexIdx: int = 0
        for fi in range(len(self.__mFaceVertexCount)):
            # set start loop
            # NOTE: blender 3.6 changed. Loop setting in polygon do not need set loop_total any more.
            # the loop_total will be auto calculated by the next loop_start.
            # loop_total become read-only
            self.__mAssocMesh.polygons[fi].loop_start = fVertexIdx
            
            # set material index
            self.__mAssocMesh.polygons[fi].material_index = self.__mFaceMtlIdx[fi]
            
            # set auto smooth. it is IMPORTANT
            # because it related to whether custom split normal can work
            self.__mAssocMesh.polygons[fi].use_smooth = True
            
            # inc vertex idx
            fVertexIdx += self.__mFaceVertexCount[fi]
        
        # validate mesh.
        # it is IMPORTANT that do NOT delete custom data
        # because we need use these data to set custom split normal later
        self.__mAssocMesh.validate(clean_customdata = False)
        # update mesh without mesh calc
        self.__mAssocMesh.update(calc_edges = False, calc_edges_loose = False)
        
        # set custom split normal data
        self.__mAssocMesh.normals_split_custom_set(
            tuple(_nest_custom_split_normal(self.__mFaceNmlIndices, self.__mVertexNormal))
        )
        # enable auto smooth. it is IMPORTANT
        self.__mAssocMesh.use_auto_smooth = True
    
    def __clear_mesh(self):
        if not self.is_valid():
            raise UTIL_functions.BBPException('try to call an invalid MeshWriter.')
        
        # clear geometry
        self.__mAssocMesh.clear_geometry()
        # clear mtl slot because clear_geometry will not do this.
        self.__mAssocMesh.materials.clear()
