import mathutils
import typing

# extract all declarations in PyBMap
from .PyBMap.virtools_types import *
# and add some patches for them
# mainly patch them with functions exchanging data with blender
# and the convertion between differnet coordinate system.
# hint: `co` mean coordinate system in blender.

#region VxVector2 Patch

def vxvector2_conv_co(self: VxVector2) -> None:
    """
    Convert UV coordinate system between Virtools and Blender.
    """
    self.y = -self.y

#endregion

#region VxVector3 Patch

def vxvector3_conv_co(self: VxVector3) -> None:
    """
    Convert Position or Normal coordinate system between Virtools and Blender.
    """
    self.y, self.z = self.z, self.y

#endregion

#region VxMatrix Patch

def vxmatrix_conv_co(self: VxMatrix) -> None:
    """
    Convert World Matrix coordinate system between Virtools and Blender.
    """
    # swap column 1 and 2
    for i in range(4):
        self.data[i][1], self.data[i][2] = self.data[i][2], self.data[i][1]
    # swap row 1 and 2
    for i in range(4):
        self.data[1][i], self.data[2][i] = self.data[2][i], self.data[1][i]

def vxmatrix_from_blender(self: VxMatrix, data_: mathutils.Matrix) -> None:
    """
    Set matrix by blender matrix.
    """
    # transposed first
    data: mathutils.Matrix = data_.transposed()
    (
        self.data[0][0], self.data[0][1], self.data[0][2], self.data[0][3],
        self.data[1][0], self.data[1][1], self.data[1][2], self.data[1][3],
        self.data[2][0], self.data[2][1], self.data[2][2], self.data[2][3],
        self.data[3][0], self.data[3][1], self.data[3][2], self.data[3][3]
    ) = (
        data[0][0], data[0][1], data[0][2], data[0][3],
        data[1][0], data[1][1], data[1][2], data[1][3],
        data[2][0], data[2][1], data[2][2], data[2][3],
        data[3][0], data[3][1], data[3][2], data[3][3]
    )

def vxmatrix_to_blender(self: VxMatrix) -> mathutils.Matrix:
    """
    Get blender matrix from this matrix
    """
    data: mathutils.Matrix = mathutils.Matrix((
        (self.data[0][0], self.data[0][1], self.data[0][2], self.data[0][3]),
        (self.data[1][0], self.data[1][1], self.data[1][2], self.data[1][3]),
        (self.data[2][0], self.data[2][1], self.data[2][2], self.data[2][3]),
        (self.data[3][0], self.data[3][1], self.data[3][2], self.data[3][3]),
    ))
    # transpose self
    data.transpose()
    return data

#endregion

