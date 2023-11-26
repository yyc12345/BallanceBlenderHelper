import mathutils
import typing, sys

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

#region Blender EnumProperty Creation

class EnumAnnotation():
    mDisplayName: str
    mDescription: str
    def __init__(self, display_name: str, description: str):
        self.mDisplayName = display_name
        self.mDescription = description

class EnumPropHelper():
    """
    These class contain all functions related to EnumProperty creation for Virtools Enums
    """

    _TIntEnumChildrenVar = typing.TypeVar('_TIntEnumChildrenVar',  bound = enum.IntEnum) ##< Mean a variable of IntEnum's children
    _TIntEnumChildren = type[_TIntEnumChildrenVar] ##< Mean the type self which is IntEnum's children.
    _TAnnoDict = dict[int, EnumAnnotation]

    @staticmethod
    def __get_name(v: _TIntEnumChildrenVar, anno: _TAnnoDict):
        entry: EnumAnnotation | None = anno.get(v, None)
        if entry is not None: return entry.mDisplayName
        else: return v.name

    @staticmethod
    def __get_desc(v: _TIntEnumChildrenVar, anno: _TAnnoDict):
        entry: EnumAnnotation | None = anno.get(v, None)
        if entry is not None: return entry.mDescription
        else: return ""

    @staticmethod
    def generate_items(enum_data: _TIntEnumChildren, anno: _TAnnoDict) -> tuple[tuple, ...]:
        """
        Generate a tuple which can be applied to Blender EnumProperty's "items".
        """
        # token, display name, descriptions, icon, index
        return tuple(
            (
                str(member.value), 
                EnumPropHelper.__get_name(member, anno), 
                EnumPropHelper.__get_desc(member, anno), 
                "", 
                member.value
            ) for member in enum_data
        )
    
    @staticmethod
    def get_selection(enum_define: _TIntEnumChildren, prop: str) -> _TIntEnumChildrenVar:
        # prop will return identifier which is defined as the string type of int value.
        # so we parse it to int and then parse it to enum type.
        return enum_define(int(prop))
    
    @staticmethod
    def to_selection(val: _TIntEnumChildrenVar) -> str:
        # like get_selection, we need get it int value, then convert it to string as the indetifier of enum props
        # them enum property will accept it.
        return str(val.value)

#endregion

#region Virtools Blender Bridge Funcs & Vars

def virtools_name_regulator(name: str | None) -> str:
    if name: return name
    else: return 'annoymous'

## Default Encoding for PyBMap
#  Use semicolon split each encodings. Support Western European and Simplified Chinese in default.
g_PyBMapDefaultEncoding: str
if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    # See: https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
    g_PyBMapDefaultEncoding = "1252;936"
else:
    # See: https://www.gnu.org/software/libiconv/
    g_PyBMapDefaultEncoding = "CP1252;CP936"

#endregion
