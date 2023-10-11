import typing, enum
from . import UTIL_functions

class VxColor():
    """
    The Color struct support RGBA.
    """
    a: float
    r: float
    g: float
    b: float
    def __init__(self, _r: float, _g: float, _b: float, _a: float):
        self.a = _a
        self.r = _r
        self.g = _g
        self.b = _b
        self.regulate()

    def to_tuple_rgba(self) -> tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)
    
    def to_tuple_rgb(self) -> tuple[float, float, float]:
        return (self.r, self.g, self.b)

    def from_tuple_rgba(self, val: tuple[float, float, float, float]) -> None:
        (self.r, self.g, self.b, self.a) = val
        self.regulate()

    def from_tuple_rgb(self, val: tuple[float, float, float]) -> None:
        (self.r, self.g, self.b) = val
        self.a = 1.0
        self.regulate()

    def clone(self):
        return VxColor(self.r, self.g, self.b, self.a)

    def regulate(self):
        self.a = UTIL_functions.clamp_float(self.a, 0.0, 1.0)
        self.r = UTIL_functions.clamp_float(self.r, 0.0, 1.0)
        self.g = UTIL_functions.clamp_float(self.g, 0.0, 1.0)
        self.b = UTIL_functions.clamp_float(self.b, 0.0, 1.0)


class VXTEXTURE_BLENDMODE(enum.IntEnum):
    """!
    Blend Mode Flags   
    """
    VXTEXTUREBLEND_DECAL = 1  ##< Texture replace any material information
    VXTEXTUREBLEND_MODULATE = 2  ##< Texture and material are combine. Alpha information of the texture replace material alpha component.
    VXTEXTUREBLEND_DECALALPHA = 3  ##< Alpha information in the texture specify how material and texture are combined. Alpha information of the texture replace material alpha component.
    VXTEXTUREBLEND_MODULATEALPHA = 4  ##< Alpha information in the texture specify how material and texture are combined
    VXTEXTUREBLEND_DECALMASK = 5
    VXTEXTUREBLEND_MODULATEMASK = 6
    VXTEXTUREBLEND_COPY = 7  ##< Equivalent to DECAL
    VXTEXTUREBLEND_ADD = 8
    VXTEXTUREBLEND_DOTPRODUCT3 = 9  ##< Perform a Dot Product 3 between texture (normal map) and a referential vector given in VXRENDERSTATE_TEXTUREFACTOR.
    VXTEXTUREBLEND_MAX = 10

class VXTEXTURE_FILTERMODE(enum.IntEnum):
    """!
    Filter Mode Options
    """
    VXTEXTUREFILTER_NEAREST = 1  ##< No Filter
    VXTEXTUREFILTER_LINEAR = 2  ##< Bilinear Interpolation
    VXTEXTUREFILTER_MIPNEAREST = 3  ##< Mip mapping
    VXTEXTUREFILTER_MIPLINEAR = 4  ##< Mip Mapping with Bilinear interpolation
    VXTEXTUREFILTER_LINEARMIPNEAREST = 5  ##< Mip Mapping with Bilinear interpolation between mipmap levels.
    VXTEXTUREFILTER_LINEARMIPLINEAR = 6  ##< Trilinear Filtering
    VXTEXTUREFILTER_ANISOTROPIC = 7  ##< Anisotropic filtering

class VXTEXTURE_ADDRESSMODE(enum.IntEnum):
    """!
    Texture addressing modes.
    """
    VXTEXTURE_ADDRESSWRAP = 1  ##< Default mesh wrap mode is used (see CKMesh::SetWrapMode)
    VXTEXTURE_ADDRESSMIRROR = 2  ##< Texture coordinates outside the range [0..1] are flipped evenly.
    VXTEXTURE_ADDRESSCLAMP = 3  ##< Texture coordinates greater than 1.0 are set to 1.0, and values less than 0.0 are set to 0.0.
    VXTEXTURE_ADDRESSBORDER = 4  ##< When texture coordinates are greater than 1.0 or less than 0.0  texture is set to a color defined in CKMaterial::SetTextureBorderColor.
    VXTEXTURE_ADDRESSMIRRORONCE = 5  ##<
    VXTEXTURE_ADDRESSMASK = 0x7  ##< mask for all values

class VXBLEND_MODE(enum.IntEnum):
    """!
    Blending Mode options
    """
    VXBLEND_ZERO = 1  ##< Blend factor is (0, 0, 0, 0).
    VXBLEND_ONE = 2  ##< Blend factor is (1, 1, 1, 1).
    VXBLEND_SRCCOLOR = 3  ##< Blend factor is (Rs, Gs, Bs, As).
    VXBLEND_INVSRCCOLOR = 4  ##< Blend factor is (1-Rs, 1-Gs, 1-Bs, 1-As).
    VXBLEND_SRCALPHA = 5  ##< Blend factor is (As, As, As, As).
    VXBLEND_INVSRCALPHA = 6  ##< Blend factor is (1-As, 1-As, 1-As, 1-As).
    VXBLEND_DESTALPHA = 7  ##< Blend factor is (Ad, Ad, Ad, Ad).
    VXBLEND_INVDESTALPHA = 8  ##< Blend factor is (1-Ad, 1-Ad, 1-Ad, 1-Ad).
    VXBLEND_DESTCOLOR = 9  ##< Blend factor is (Rd, Gd, Bd, Ad).
    VXBLEND_INVDESTCOLOR = 10  ##< Blend factor is (1-Rd, 1-Gd, 1-Bd, 1-Ad).
    VXBLEND_SRCALPHASAT = 11  ##< Blend factor is (f, f, f, 1); f = min(As, 1-Ad).
    VXBLEND_BOTHSRCALPHA = 12  ##< Source blend factor is (As, As, As, As) and destination blend factor is (1-As, 1-As, 1-As, 1-As)
    VXBLEND_BOTHINVSRCALPHA = 13  ##< Source blend factor is (1-As, 1-As, 1-As, 1-As) and destination blend factor is (As, As, As, As)

class VXFILL_MODE(enum.IntEnum):
    """!
    Fill Mode Options 
    """
    VXFILL_POINT = 1  ##< Vertices rendering
    VXFILL_WIREFRAME = 2  ##< Edges rendering
    VXFILL_SOLID = 3  ##< Face rendering

class VXSHADE_MODE(enum.IntEnum):
    """!
    Shade Mode Options
    """
    VXSHADE_FLAT = 1  ##< Flat Shading
    VXSHADE_GOURAUD = 2  ##< Gouraud Shading
    VXSHADE_PHONG = 3  ##< Phong Shading (Not yet supported by most implementation)

class VXCMPFUNC(enum.IntEnum):
    """!
    Comparison Function
    """
    VXCMP_NEVER = 1  ##< Always fail the test.
    VXCMP_LESS = 2  ##< Accept if value if less than current value.
    VXCMP_EQUAL = 3  ##< Accept if value if equal than current value.
    VXCMP_LESSEQUAL = 4  ##< Accept if value if less or equal than current value.
    VXCMP_GREATER = 5  ##< Accept if value if greater than current value.
    VXCMP_NOTEQUAL = 6  ##< Accept if value if different than current value.
    VXCMP_GREATEREQUAL = 7  ##< Accept if value if greater or equal current value.
    VXCMP_ALWAYS = 8  ##< Always accept the test.

g_Annotation_VXTEXTURE_BLENDMODE: dict[int, str] = {
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECAL.value: "Texture replace any material information ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATE.value: "Texture and material are combine. Alpha information of the texture replace material alpha component. ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECALALPHA.value: "Alpha information in the texture specify how material and texture are combined. Alpha information of the texture replace material alpha component. ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEALPHA.value: "Alpha information in the texture specify how material and texture are combined ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DECALMASK.value: "",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MODULATEMASK.value: "",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_COPY.value: "Equivalent to DECAL ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_ADD.value: "",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_DOTPRODUCT3.value: "Perform a Dot Product 3 between texture (normal map) and a referential vector given in VXRENDERSTATE_TEXTUREFACTOR. ",
    VXTEXTURE_BLENDMODE.VXTEXTUREBLEND_MAX.value: "",
}
g_Annotation_VXTEXTURE_FILTERMODE: dict[int, str] = {
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_NEAREST.value: "No Filter ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEAR.value: "Bilinear Interpolation ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPNEAREST.value: "Mip mapping ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_MIPLINEAR.value: "Mip Mapping with Bilinear interpolation ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPNEAREST.value: "Mip Mapping with Bilinear interpolation between mipmap levels. ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_LINEARMIPLINEAR.value: "Trilinear Filtering ",
    VXTEXTURE_FILTERMODE.VXTEXTUREFILTER_ANISOTROPIC.value: "Anisotropic filtering ",
}
g_Annotation_VXBLEND_MODE: dict[int, str] = {
    VXBLEND_MODE.VXBLEND_ZERO.value: "Blend factor is (0, 0, 0, 0). ",
    VXBLEND_MODE.VXBLEND_ONE.value: "Blend factor is (1, 1, 1, 1). ",
    VXBLEND_MODE.VXBLEND_SRCCOLOR.value: "Blend factor is (Rs, Gs, Bs, As). ",
    VXBLEND_MODE.VXBLEND_INVSRCCOLOR.value: "Blend factor is (1-Rs, 1-Gs, 1-Bs, 1-As). ",
    VXBLEND_MODE.VXBLEND_SRCALPHA.value: "Blend factor is (As, As, As, As). ",
    VXBLEND_MODE.VXBLEND_INVSRCALPHA.value: "Blend factor is (1-As, 1-As, 1-As, 1-As). ",
    VXBLEND_MODE.VXBLEND_DESTALPHA.value: "Blend factor is (Ad, Ad, Ad, Ad). ",
    VXBLEND_MODE.VXBLEND_INVDESTALPHA.value: "Blend factor is (1-Ad, 1-Ad, 1-Ad, 1-Ad). ",
    VXBLEND_MODE.VXBLEND_DESTCOLOR.value: "Blend factor is (Rd, Gd, Bd, Ad). ",
    VXBLEND_MODE.VXBLEND_INVDESTCOLOR.value: "Blend factor is (1-Rd, 1-Gd, 1-Bd, 1-Ad). ",
    VXBLEND_MODE.VXBLEND_SRCALPHASAT.value: "Blend factor is (f, f, f, 1); f = min(As, 1-Ad). ",
    VXBLEND_MODE.VXBLEND_BOTHSRCALPHA.value: "Source blend factor is (As, As, As, As) and destination blend factor is (1-As, 1-As, 1-As, 1-As) ",
    VXBLEND_MODE.VXBLEND_BOTHINVSRCALPHA.value: "Source blend factor is (1-As, 1-As, 1-As, 1-As) and destination blend factor is (As, As, As, As) ",
}
g_Annotation_VXTEXTURE_ADDRESSMODE: dict[int, str] = {
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSWRAP.value: "Default mesh wrap mode is used (see CKMesh::SetWrapMode) ",
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRROR.value: "Texture coordinates outside the range [0..1] are flipped evenly. ",
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSCLAMP.value: "Texture coordinates greater than 1.0 are set to 1.0, and values less than 0.0 are set to 0.0. ",
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSBORDER.value: "When texture coordinates are greater than 1.0 or less than 0.0  texture is set to a color defined in CKMaterial::SetTextureBorderColor. ",
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMIRRORONCE.value: " ",
    VXTEXTURE_ADDRESSMODE.VXTEXTURE_ADDRESSMASK.value: "mask for all values ",
}
g_Annotation_VXFILL_MODE: dict[int, str] = {
    VXFILL_MODE.VXFILL_POINT.value: "Vertices rendering ",
    VXFILL_MODE.VXFILL_WIREFRAME.value: "Edges rendering ",
    VXFILL_MODE.VXFILL_SOLID.value: "Face rendering ",
}
g_Annotation_VXSHADE_MODE: dict[int, str] = {
    VXSHADE_MODE.VXSHADE_FLAT.value: "Flat Shading ",
    VXSHADE_MODE.VXSHADE_GOURAUD.value: "Gouraud Shading ",
    VXSHADE_MODE.VXSHADE_PHONG.value: "Phong Shading (Not yet supported by most implementation) ",
}
g_Annotation_VXCMPFUNC: dict[int, str] = {
    VXCMPFUNC.VXCMP_NEVER.value: "Always fail the test. ",
    VXCMPFUNC.VXCMP_LESS.value: "Accept if value if less than current value. ",
    VXCMPFUNC.VXCMP_EQUAL.value: "Accept if value if equal than current value. ",
    VXCMPFUNC.VXCMP_LESSEQUAL.value: "Accept if value if less or equal than current value. ",
    VXCMPFUNC.VXCMP_GREATER.value: "Accept if value if greater than current value. ",
    VXCMPFUNC.VXCMP_NOTEQUAL.value: "Accept if value if different than current value. ",
    VXCMPFUNC.VXCMP_GREATEREQUAL.value: "Accept if value if greater or equal current value. ",
    VXCMPFUNC.VXCMP_ALWAYS.value: "Always accept the test. ",
}

InheritingIntEnum_t = typing.TypeVar('InheritingIntEnum_t',  bound = enum.IntEnum)
BlenderEnumPropEntry_t = tuple[str, str, str, str | int, int]
def generate_blender_enum_prop_entries(enum_data: InheritingIntEnum_t, anno: dict[int, str]) -> tuple[BlenderEnumPropEntry_t, ...]:
    # token, display name, descriptions, icon, index
    return tuple(
        (str(member.value), member.name, anno.get(member.value, ""), "", member.value) for member in enum_data
    )
