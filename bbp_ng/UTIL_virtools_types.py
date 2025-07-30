import bpy, mathutils
import typing, math
from . import UTIL_functions

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
    Please note there is no corrdinate system convertion between 
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

## Hints about Light Matrix
#  There is a slight difference between Virtools and Blender.
#  In blender, the default direction of all directional light (spot and sun) are Down (-Z).
#  Hoewver, in Virtools, the default direction of all directional light (spot and directional) are Forward (+Z).
#  
#  As brief view, in Blender coordinate system, you can see that we got Blender default light direction
#  from Virtools default light direction by rotating it around X-axis with -90 degree
#  (the positive rotation direction is decided by right hand priniciple).
#  
#  So, if the object we importing is a light, we need add a special transform matrix ahead of world matrix
#  to correct the light default direction first.
#  When exporting, just do a reverse operation.

def bldmatrix_patch_light_obj(data: mathutils.Matrix) -> mathutils.Matrix:
    """
    Add patch for light world matrix to correct its direction.
    This function is usually used when importing light.
    """
    # we multiple a matrix which represent a 90 degree roration in X-axis.
    # right multiple means that it will apply to light first, before apply the matrix gotten from virtools.
    return data @ mathutils.Matrix.Rotation(math.radians(90), 4, 'X')

def bldmatrix_restore_light_obj(data: mathutils.Matrix) -> mathutils.Matrix:
    """
    The reverse operation of bldmatrix_patch_light_mat().
    This function is usually used when exporting light.
    """
    # as the reverse operation, we need right mutiple a reversed matrix of the matrix
    # which represent a 90 degree roration in X-axis to remove the matrix we added in patch step.
    # however, the reverse matrix of 90 degree X-axis rotation is just NEGATUIVE 90 degree X-axis rotation.
    # so we simply right multiple it.
    return data @ mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')

#endregion

#region Blender EnumProperty Creation

class EnumAnnotation():
    mDisplayName: str
    mDescription: str
    def __init__(self, display_name: str, description: str):
        self.mDisplayName = display_name
        self.mDescription = description

_g_Annotation: dict[type, dict[int, EnumAnnotation]] = {
    VXTEXTURE_BLENDMODE: {
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
    },
    VXTEXTURE_FILTERMODE: {
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_NEAREST.value: EnumAnnotation("Nearest", "No Filter "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR.value: EnumAnnotation("Linear", "Bilinear Interpolation "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPNEAREST.value: EnumAnnotation("Mip Nearest", "Mip mapping "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPLINEAR.value: EnumAnnotation("Mip Linear", "Mip Mapping with Bilinear interpolation "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPNEAREST.value: EnumAnnotation("Linear Mip Nearest", "Mip Mapping with Bilinear interpolation between mipmap levels. "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPLINEAR.value: EnumAnnotation("Linear Mip Linear", "Trilinear Filtering "),
        VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_ANISOTROPIC.value: EnumAnnotation("Anisotropic", "Anisotropic filtering "),
    },
    VXBLEND_MODE: {
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
    },
    VXTEXTURE_ADDRESSMODE: {
        VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSWRAP.value: EnumAnnotation("Wrap", "Default mesh wrap mode is used (see CKMesh::SetWrapMode) "),
        VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRROR.value: EnumAnnotation("Mirror", "Texture coordinates outside the range [0..1] are flipped evenly. "),
        VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSCLAMP.value: EnumAnnotation("Clamp", "Texture coordinates greater than 1.0 are set to 1.0, and values less than 0.0 are set to 0.0. "),
        VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSBORDER.value: EnumAnnotation("Border", "When texture coordinates are greater than 1.0 or less than 0.0  texture is set to a color defined in CKMaterial::SetTextureBorderColor. "),
        VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRRORONCE.value: EnumAnnotation("Mirror Once", " "),
    },
    VXFILL_MODE: {
        VXFILL_MODE.VXFILL_POINT.value: EnumAnnotation("Point", "Vertices rendering "),
        VXFILL_MODE.VXFILL_WIREFRAME.value: EnumAnnotation("Wireframe", "Edges rendering "),
        VXFILL_MODE.VXFILL_SOLID.value: EnumAnnotation("Solid", "Face rendering "),
    },
    VXSHADE_MODE: {
        VXSHADE_MODE.VXSHADE_FLAT.value: EnumAnnotation("Flat", "Flat Shading "),
        VXSHADE_MODE.VXSHADE_GOURAUD.value: EnumAnnotation("Gouraud", "Gouraud Shading "),
        VXSHADE_MODE.VXSHADE_PHONG.value: EnumAnnotation("Phong", "Phong Shading (Not yet supported by most implementation) "),
    },
    VXCMPFUNC: {
        VXCMPFUNC.VXCMP_NEVER.value: EnumAnnotation("Never", "Always fail the test. "),
        VXCMPFUNC.VXCMP_LESS.value: EnumAnnotation("Less", "Accept if value if less than current value. "),
        VXCMPFUNC.VXCMP_EQUAL.value: EnumAnnotation("Equal", "Accept if value if equal than current value. "),
        VXCMPFUNC.VXCMP_LESSEQUAL.value: EnumAnnotation("Less Equal", "Accept if value if less or equal than current value. "),
        VXCMPFUNC.VXCMP_GREATER.value: EnumAnnotation("Greater", "Accept if value if greater than current value. "),
        VXCMPFUNC.VXCMP_NOTEQUAL.value: EnumAnnotation("Not Equal", "Accept if value if different than current value. "),
        VXCMPFUNC.VXCMP_GREATEREQUAL.value: EnumAnnotation("Greater Equal", "Accept if value if greater or equal current value. "),
        VXCMPFUNC.VXCMP_ALWAYS.value: EnumAnnotation("Always", "Always accept the test. "),
    },
    CK_TEXTURE_SAVEOPTIONS: {
        CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_RAWDATA.value: EnumAnnotation("Raw Data", "Save raw data inside file. The bitmap is saved in a raw 32 bit per pixel format. "),
        CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_EXTERNAL.value: EnumAnnotation("External", "Store only the file name for the texture. The bitmap file must be present in the bitmap paths when loading the composition. "),
        CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_IMAGEFORMAT.value: EnumAnnotation("Image Format", "Save using format specified. The bitmap data will be converted to the specified format by the correspondant bitmap plugin and saved inside file. "),
        CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_USEGLOBAL.value: EnumAnnotation("Use Global", "Use Global settings, that is the settings given with CKContext::SetGlobalImagesSaveOptions. (Not valid when using CKContext::SetImagesSaveOptions). "),
        CK_TEXTURE_SAVEOPTIONS.CKTEXTURE_INCLUDEORIGINALFILE.value: EnumAnnotation("Include Original File", "Insert original image file inside CMO file. The bitmap file that was used originally for the texture or sprite will be append to the composition file and extracted when the file is loaded. "),
    },
    VX_PIXELFORMAT: {
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
    },
    VXLIGHT_TYPE: {
        VXLIGHT_TYPE.VX_LIGHTPOINT.value: EnumAnnotation("Point", "The Light is a point of light "),
        VXLIGHT_TYPE.VX_LIGHTSPOT.value: EnumAnnotation("Spot", "The light is a spotlight "),
        VXLIGHT_TYPE.VX_LIGHTDIREC.value: EnumAnnotation("Directional", "The light is directional light : Lights comes from an infinite point so only direction of light can be given "),
        #VXLIGHT_TYPE.VX_LIGHTPARA.value: EnumAnnotation("Lightpara", "Obsolete, do not use "),
    },
    VXMESH_LITMODE: {
        VXMESH_LITMODE.VX_PRELITMESH.value: EnumAnnotation("Prelit", "Lighting use color information store with vertices "),
        VXMESH_LITMODE.VX_LITMESH.value: EnumAnnotation("Lit", "Lighting is done by renderer using normals and face material information. "),
    }
}

_TRawEnum = typing.TypeVar('_TRawEnum', bound = enum.Enum)

class EnumPropHelper(UTIL_functions.EnumPropHelper[_TRawEnum]):
    """
    Virtools type specified Blender EnumProp helper.
    """
    __mAnnotationDict: dict[int, EnumAnnotation]
    __mEnumTy: type[_TRawEnum]

    def __init__(self, ty: type[_TRawEnum]):
        # set enum type and annotation ref first
        self.__mEnumTy = ty
        self.__mAnnotationDict = _g_Annotation[ty]

        # YYC MARK:
        # It seems that Pylance has bad generic analyse ability in there.
        # It can not deduce the correct generic type in lambda.
        # I gave up.

        # Init parent data
        super().__init__(
            self.__mEnumTy, # enum.Enum its self is iterable
            lambda x: str(x.value), # convert enum.Enum's value to string
            lambda x: self.__mEnumTy(int(x)),   # use stored enum type and int() to get enum member
            lambda x: self.__mAnnotationDict[x.value].mDisplayName,
            lambda x: self.__mAnnotationDict[x.value].mDescription,
            lambda _: ''
        )

#endregion

#region Virtools Blender Bridge Funcs & Vars

def virtools_name_regulator(name: str | None) -> str:
    if name: return name
    else: return bpy.app.translations.pgettext_data('annoymous', 'BME/UTIL_virtools_types.virtools_name_regulator()')

# YYC MARK:
# There are default encodings for PyBMap. We support Western European and Simplified Chinese in default.
# Since LibCmo 0.2, the encoding name of LibCmo become universal encoding which is platfoorm independent.
# So no need set it according to different platform.
# Use universal encoding name (like Python).
g_PyBMapDefaultEncodings: tuple[str, ...] = (
    'cp1252',
    'gbk'
)

#endregion
