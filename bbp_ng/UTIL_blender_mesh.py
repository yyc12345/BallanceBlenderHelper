import bpy, bmesh
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

## Face used vertex index struct.
#  Data member is (PosIdx, NmlIdx, UVIdx)
FaceVertexIndex = tuple[int, int, int]
## Face used vertex indices struct.
#  A tuple with FaceVertexIndex member.
#  At least 3 member because face need at least 3 vertex to be constructed.
FaceVertexIndices = tuple[FaceVertexIndex, ...]
## Face data struct.
#  First is FaceVertexIndices struct to describe how the face constructed.
#  Second is used material index.
#  If you don't want to use material, you need pass None via material and point this index to it.
FaceData = tuple[FaceVertexIndices, int]

def flat_vxvector3(it: typing.Iterator[UTIL_virtools_types.ConstVxVector3]) -> typing.Iterator[float]:
    for entry in it:
        yield entry[0]
        yield entry[1]
        yield entry[2]

def flat_vxvector2(it: typing.Iterator[UTIL_virtools_types.ConstVxVector2]) -> typing.Iterator[float]:
    for entry in it:
        yield entry[0]
        yield entry[1]

def flat_vertex_indices(it: FaceVertexIndices, prev_pos: int, prev_nml: int, prev_uv: int) -> typing.Iterator[int]:
    for entry in it:
        yield entry[0] + prev_pos
        yield entry[1] + prev_nml
        yield entry[2] + prev_uv

#endregion

class MeshReader():
    """
    The passed mesh must be created by bpy.types.Object.to_mesh() and destroyed by bpy.types.Object.to_mesh_clear().
    Because this class must trianglate mesh. To prevent change original mesh, this operations is essential.
    """
    pass

class MeshWriter():
    """
    
    """
    
    class MeshWriterPartData():
        mVertexPosition: typing.Iterator[UTIL_virtools_types.ConstVxVector3] | None
        mVertexNormal: typing.Iterator[UTIL_virtools_types.ConstVxVector3] | None
        mVertexUV: typing.Iterator[UTIL_virtools_types.ConstVxVector2] | None
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
    
    __mAssocMesh: bpy.types.Mesh | None
    
    __mVertexPos: array.array ##< Array item is float(f). Length must be an integer multiple of 3.
    __mVertexNormal: array.array ##< Array item is float(f). Length must be an integer multiple of 3.
    __mVertexUV: array.array ##< Array item is float(f). Length must be an integer multiple of 2.
    
    ## Array item is int32(L).
    #  Length must be (the sum of each items in __mFaceVertexCount) * 3.
    #  Item is flatten FaceVertexIndex, it mean every 3 continuous items indicate one vertex property.
    __mFaceIndices: array.array
    ## Array item is int32(L). 
    #  Length is the face count.
    #  It indicate how much vertex need to be consumed in __mFaceIndices for one face.
    #  The real consumed number of items in __mFaceVertexCount for each face need be multipled by 3 because __mFaceVertexCount is flat structure.
    __mFaceVertexCount: array.array
    __mFaceMtlIdx: array.array  ##< Array item is int32(L). Length is equal to __mFaceVertexCount.
    
    __mMtlSlot: list[bpy.types.Material]
    __mMtlSlotMap: dict[bpy.types.Material, int]
    
    def __init__(self, assoc_mesh: bpy.types.Mesh):
        self.__mAssocMesh = assoc_mesh
        
        self.__mVertexPos = array.array('f')
        self.__mVertexNormal = array.array('f')
        self.__mVertexUV = array.array('f')
        
        self.__mFaceIndices = array.array('L')
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
    
    def add_part(self, data: MeshWriterPartData):
        if not data.is_valid():
            raise UTIL_functions.BBPException('invalid mesh part data.')
        
        # add vertex data
        prev_vertex_pos_count: int = len(self.__mVertexPos)
        self.__mVertexPos.extend(flat_vxvector3(data.mVertexPosition))
        prev_vertex_nml_count: int = len(self.__mVertexNormal)
        self.__mVertexNormal.extend(flat_vxvector3(data.mVertexNormal))
        prev_vertex_uv_count: int = len(self.__mVertexUV)
        self.__mVertexUV.extend(flat_vxvector2(data.mVertexUV))
        
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
            indices = face[0]
            if len(indices) < 3:
                raise UTIL_functions.BBPException('face must have at least 3 vertex.')
            
            # add indices
            self.__mFaceIndices.extend(
                flat_vertex_indices(indices, 
                    prev_vertex_pos_count,
                    prev_vertex_nml_count,
                    prev_vertex_uv_count
                )
            )
            self.__mFaceVertexCount.append(len(indices))
            
            # add face mtl with remap
            mtl_idx: int = face[1]
            self.__mFaceMtlIdx.append(mtl_remap[mtl_idx])
            
    def dispose(self):
        if self.is_valid():
            
            
            
            
            
            # reset mesh
            self.__mAssocMesh = None



class MeshUVModifier():
    pass

def register() -> None:
    pass # nothing to register

def unregister() -> None:
    pass
