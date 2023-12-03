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

#region Enum Annotations

g_Annotation_VXTEXTURE_BLENDMODE: dict[int, EnumAnnotation] = {
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECAL.value: EnumAnnotation("Decal", "Texture replace any material information "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATE.value: EnumAnnotation("Modulate", "Texture and material are combine. Alpha information of the texture replace material alpha component. "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECALALPHA.value: EnumAnnotation("Decal Alpha", "Alpha information in the texture specify how material and texture are combined. Alpha information of the texture replace material alpha component. "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEALPHA.value: EnumAnnotation("Modulate Alpha", "Alpha information in the texture specify how material and texture are combined "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECALMASK.value: EnumAnnotation("Decal Mask", ""),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEMASK.value: EnumAnnotation("Modulate Mask", ""),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_COPY.value: EnumAnnotation("Copy", "Equivalent to DECAL "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_ADD.value: EnumAnnotation("Add", ""),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DOTPRODUCT3.value: EnumAnnotation("Dot Product 3", "Perform a Dot Product 3 between texture (normal map) and a referential vector given in VXRENDERSTATE_TEXTUREFACTOR. "),
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MAX.value: EnumAnnotation("Max", ""),
}
g_Annotation_VXTEXTURE_FILTERMODE: dict[int, EnumAnnotation] = {
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_NEAREST.value: EnumAnnotation("Nearest", "No Filter "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR.value: EnumAnnotation("Linear", "Bilinear Interpolation "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPNEAREST.value: EnumAnnotation("Mip Nearest", "Mip mapping "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPLINEAR.value: EnumAnnotation("Mip Linear", "Mip Mapping with Bilinear interpolation "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPNEAREST.value: EnumAnnotation("Linear Mip Nearest", "Mip Mapping with Bilinear interpolation between mipmap levels. "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPLINEAR.value: EnumAnnotation("Linear Mip Linear", "Trilinear Filtering "),
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_ANISOTROPIC.value: EnumAnnotation("Anisotropic", "Anisotropic filtering "),
}
g_Annotation_VXBLEND_MODE: dict[int, EnumAnnotation] = {
    VXBLEND_MODE.VXBLEND_ZERO.value: EnumAnnotation("Zero", "Blend factor is (0, 0, 0, 0). "),
    VXBLEND_MODE.VXBLEND_ONE.value: EnumAnnotation("One", "Blend factor is (1, 1, 1, 1). "),
    VXBLEND_MODE.VXBLEND_SRCCOLOR.value: EnumAnnotation("Src Color", "Blend factor is (Rs, Gs, Bs, As). "),
    VXBLEND_MODE.VXBLEND_INVSRCCOLOR.value: EnumAnnotation("Inv Src Color", "Blend factor is (1-Rs, 1-Gs, 1-Bs, 1-As). "),
    VXBLEND_MODE.VXBLEND_SRCALPHA.value: EnumAnnotation("Src Alpha", "Blend factor is (As, As, As, As). "),
    VXBLEND_MODE.VXBLEND_INVSRCALPHA.value: EnumAnnotation("Inv Src Alpha", "Blend factor is (1-As, 1-As, 1-As, 1-As). "),
    VXBLEND_MODE.VXBLEND_DESTALPHA.value: EnumAnnotation("Dest Alpha", "Blend factor is (Ad, Ad, Ad, Ad). "),
    VXBLEND_MODE.VXBLEND_INVDESTALPHA.value: EnumAnnotation("Inv Dest Alpha", "Blend factor is (1-Ad, 1-Ad, 1-Ad, 1-Ad). "),
    VXBLEND_MODE.VXBLEND_DESTCOLOR.value: EnumAnnotation("Dest Color", "Blend factor is (Rd, Gd, Bd, Ad). "),
    VXBLEND_MODE.VXBLEND_INVDESTCOLOR.value: EnumAnnotation("Inv Dest Color", "Blend factor is (1-Rd, 1-Gd, 1-Bd, 1-Ad). "),
    VXBLEND_MODE.VXBLEND_SRCALPHASAT.value: EnumAnnotation("Src Alpha Sat", "Blend factor is (f, f, f, 1); f = min(As, 1-Ad). "),
    #VXBLEND_MODE.VXBLEND_BOTHSRCALPHA.value: EnumAnnotation("Both Src Alpha", "Source blend factor is (As, As, As, As) and destination blend factor is (1-As, 1-As, 1-As, 1-As) "),
    #VXBLEND_MODE.VXBLEND_BOTHINVSRCALPHA.value: EnumAnnotation("Both Inv Src Alpha", "Source blend factor is (1-As, 1-As, 1-As, 1-As) and destination blend factor is (As, As, As, As) "),
}
g_Annotation_VXTEXTURE_ADDRESSMODE: dict[int, EnumAnnotation] = {
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSWRAP.value: EnumAnnotation("Wrap", "Default mesh wrap mode is used (see CKMesh::SetWrapMode) "),
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRROR.value: EnumAnnotation("Mirror", "Texture coordinates outside the range [0..1] are flipped evenly. "),
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSCLAMP.value: EnumAnnotation("Clamp", "Texture coordinates greater than 1.0 are set to 1.0, and values less than 0.0 are set to 0.0. "),
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSBORDER.value: EnumAnnotation("Border", "When texture coordinates are greater than 1.0 or less than 0.0  texture is set to a color defined in CKMaterial::SetTextureBorderColor. "),
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRRORONCE.value: EnumAnnotation("Mirror Once", " "),
}
g_Annotation_VXFILL_MODE: dict[int, EnumAnnotation] = {
    VXFILL_MODE.VXFILL_POINT.value: EnumAnnotation("Point", "Vertices rendering "),
    VXFILL_MODE.VXFILL_WIREFRAME.value: EnumAnnotation("Wireframe", "Edges rendering "),
    VXFILL_MODE.VXFILL_SOLID.value: EnumAnnotation("Solid", "Face rendering "),
}
g_Annotation_VXSHADE_MODE: dict[int, EnumAnnotation] = {
    VXSHADE_MODE.VXSHADE_FLAT.value: EnumAnnotation("Flat", "Flat Shading "),
    VXSHADE_MODE.VXSHADE_GOURAUD.value: EnumAnnotation("Gouraud", "Gouraud Shading "),
    VXSHADE_MODE.VXSHADE_PHONG.value: EnumAnnotation("Phong", "Phong Shading (Not yet supported by most implementation) "),
}
g_Annotation_VXCMPFUNC: dict[int, EnumAnnotation] = {
    VXCMPFUNC.VXCMP_NEVER.value: EnumAnnotation("Never", "Always fail the test. "),
    VXCMPFUNC.VXCMP_LESS.value: EnumAnnotation("Less", "Accept if value if less than current value. "),
    VXCMPFUNC.VXCMP_EQUAL.value: EnumAnnotation("Equal", "Accept if value if equal than current value. "),
    VXCMPFUNC.VXCMP_LESSEQUAL.value: EnumAnnotation("Less Equal", "Accept if value if less or equal than current value. "),
    VXCMPFUNC.VXCMP_GREATER.value: EnumAnnotation("Greater", "Accept if value if greater than current value. "),
    VXCMPFUNC.VXCMP_NOTEQUAL.value: EnumAnnotation("Not Equal", "Accept if value if different than current value. "),
    VXCMPFUNC.VXCMP_GREATEREQUAL.value: EnumAnnotation("Greater Equal", "Accept if value if greater or equal current value. "),
    VXCMPFUNC.VXCMP_ALWAYS.value: EnumAnnotation("Always", "Always accept the test. "),
}

g_Annotation_CK_TEXTURE_SAVEOPTIONS: dict[int, EnumAnnotation] = {
    CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA.value: EnumAnnotation("Raw Data", "Save raw data inside file. The bitmap is saved in a raw 32 bit per pixel format. "),
    CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL.value: EnumAnnotation("External", "Store only the file name for the texture. The bitmap file must be present in the bitmap paths when loading the composition. "),
    CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_IMAGEFORMAT.value: EnumAnnotation("Image Format", "Save using format specified. The bitmap data will be converted to the specified format by the correspondant bitmap plugin and saved inside file. "),
    CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_USEGLOBAL.value: EnumAnnotation("Use Global", "Use Global settings, that is the settings given with CKContext::SetGlobalImagesSaveOptions. (Not valid when using CKContext::SetImagesSaveOptions). "),
    CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_INCLUDEORIGINALFILE.value: EnumAnnotation("Include Original File", "Insert original image file inside CMO file. The bitmap file that was used originally for the texture or sprite will be append to the composition file and extracted when the file is loaded. "),
}
g_Annotation_VX_PIXELFORMAT: dict[int, EnumAnnotation] = {
    VX_PIXELFORMAT._32_ARGB8888.value: EnumAnnotation("32 Bits ARGB8888", "32-bit ARGB pixel format with alpha "),
    VX_PIXELFORMAT._32_RGB888.value: EnumAnnotation("32 Bits RGB888", "32-bit RGB pixel format without alpha "),
    VX_PIXELFORMAT._24_RGB888.value: EnumAnnotation("24 Bits RGB888", "24-bit RGB pixel format "),
    VX_PIXELFORMAT._16_RGB565.value: EnumAnnotation("16 Bits RGB565", "16-bit RGB pixel format "),
    VX_PIXELFORMAT._16_RGB555.value: EnumAnnotation("16 Bits RGB555", "16-bit RGB pixel format (5 bits per color) "),
    VX_PIXELFORMAT._16_ARGB1555.value: EnumAnnotation("16 Bits ARGB1555", "16-bit ARGB pixel format (5 bits per color + 1 bit for alpha) "),
    VX_PIXELFORMAT._16_ARGB4444.value: EnumAnnotation("16 Bits ARGB4444", "16-bit ARGB pixel format (4 bits per color) "),
    VX_PIXELFORMAT._8_RGB332.value: EnumAnnotation("8 Bits RGB332", "8-bit  RGB pixel format "),
    VX_PIXELFORMAT._8_ARGB2222.value: EnumAnnotation("8 Bits ARGB2222", "8-bit  ARGB pixel format "),
    VX_PIXELFORMAT._32_ABGR8888.value: EnumAnnotation("32 Bits ABGR8888", "32-bit ABGR pixel format "),
    VX_PIXELFORMAT._32_RGBA8888.value: EnumAnnotation("32 Bits RGBA8888", "32-bit RGBA pixel format "),
    VX_PIXELFORMAT._32_BGRA8888.value: EnumAnnotation("32 Bits BGRA8888", "32-bit BGRA pixel format "),
    VX_PIXELFORMAT._32_BGR888.value: EnumAnnotation("32 Bits BGR888", "32-bit BGR pixel format "),
    VX_PIXELFORMAT._24_BGR888.value: EnumAnnotation("24 Bits BGR888", "24-bit BGR pixel format "),
    VX_PIXELFORMAT._16_BGR565.value: EnumAnnotation("16 Bits BGR565", "16-bit BGR pixel format "),
    VX_PIXELFORMAT._16_BGR555.value: EnumAnnotation("16 Bits BGR555", "16-bit BGR pixel format (5 bits per color) "),
    VX_PIXELFORMAT._16_ABGR1555.value: EnumAnnotation("16 Bits ABGR1555", "16-bit ABGR pixel format (5 bits per color + 1 bit for alpha) "),
    VX_PIXELFORMAT._16_ABGR4444.value: EnumAnnotation("16 Bits ABGR4444", "16-bit ABGR pixel format (4 bits per color) "),
    VX_PIXELFORMAT._DXT1.value: EnumAnnotation("DXT1", "S3/DirectX Texture Compression 1 "),
    VX_PIXELFORMAT._DXT2.value: EnumAnnotation("DXT2", "S3/DirectX Texture Compression 2 "),
    VX_PIXELFORMAT._DXT3.value: EnumAnnotation("DXT3", "S3/DirectX Texture Compression 3 "),
    VX_PIXELFORMAT._DXT4.value: EnumAnnotation("DXT4", "S3/DirectX Texture Compression 4 "),
    VX_PIXELFORMAT._DXT5.value: EnumAnnotation("DXT5", "S3/DirectX Texture Compression 5 "),
    VX_PIXELFORMAT._16_V8U8.value: EnumAnnotation("16 Bits V8U8", "16-bit Bump Map format format (8 bits per color) "),
    VX_PIXELFORMAT._32_V16U16.value: EnumAnnotation("32 Bits V16U16", "32-bit Bump Map format format (16 bits per color) "),
    VX_PIXELFORMAT._16_L6V5U5.value: EnumAnnotation("16 Bits L6V5U5", "16-bit Bump Map format format with luminance "),
    VX_PIXELFORMAT._32_X8L8V8U8.value: EnumAnnotation("32 Bits X8L8V8U8", "32-bit Bump Map format format with luminance "),
    VX_PIXELFORMAT._8_ABGR8888_CLUT.value: EnumAnnotation("8 Bits ABGR8888 CLUT", "8 bits indexed CLUT (ABGR) "),
    VX_PIXELFORMAT._8_ARGB8888_CLUT.value: EnumAnnotation("8 Bits ARGB8888 CLUT", "8 bits indexed CLUT (ARGB) "),
    VX_PIXELFORMAT._4_ABGR8888_CLUT.value: EnumAnnotation("4 Bits ABGR8888 CLUT", "4 bits indexed CLUT (ABGR) "),
    VX_PIXELFORMAT._4_ARGB8888_CLUT.value: EnumAnnotation("4 Bits ARGB8888 CLUT", "4 bits indexed CLUT (ARGB) "),
}

g_Annotation_VXMESH_LITMODE: dict[int, EnumAnnotation] = {
    VXMESH_LITMODE.VX_PRELITMESH.value: EnumAnnotation("Prelit", "Lighting use color information store with vertices "),
    VXMESH_LITMODE.VX_LITMESH.value: EnumAnnotation("Lit", "Lighting is done by renderer using normals and face material information. "),
}

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
