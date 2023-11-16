import bpy
import math, typing, enum, sys

class BBPException(Exception):
    """
    The exception thrown by Ballance Blender Plugin
    """
    pass

def clamp_float(v: float, min_val: float, max_val: float) -> float:
    """!
    @brief Clamp a float value

    @param v[in] The value need to be clamp.
    @param min_val[in] The allowed minium value, including self.
    @param max_val[in] The allowed maxium value, including self.
    @return Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_float().")

    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v

def clamp_int(v: int, min_val: int, max_val: int) -> int:
    """!
    @brief Clamp a int value

    @param v[in] The value need to be clamp.
    @param min_val[in] The allowed minium value, including self.
    @param max_val[in] The allowed maxium value, including self.
    @return Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_int().")

    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v

def virtools_name_regulator(name: str | None) -> str:
    if name: return name
    else: return 'annoymous'

def message_box(message: tuple[str], title: str, icon: str):
    """
    Show a message box in Blender. Non-block mode.

    @param message[in] The text this message box displayed. Each item in this param will show as a single line.
    @param title[in] Message box title text.
    @param icon[in] The icon this message box displayed.
    """
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        for item in message:
            layout.label(text=item, translate=False)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#region Virtools Enums Annotation Help

class AnnotationData():
    mDisplayName: str
    mDescription: str
    def __init__(self, display_name: str, description: str):
        self.mDisplayName = display_name
        self.mDescription = description

InheritingIntEnum_t = typing.TypeVar('InheritingIntEnum_t',  bound = enum.IntEnum)
BlenderEnumPropEntry_t = tuple[str, str, str, str | int, int]
def generate_vt_enums_for_bl_enumprop(enum_data: type[InheritingIntEnum_t], anno: dict[int, AnnotationData]) -> tuple[BlenderEnumPropEntry_t, ...]:
    # define 2 assist functions
    def get_display_name(v: int, fallback: str):
        entry: AnnotationData | None = anno.get(v, None)
        if entry: return entry.mDisplayName
        else: return fallback
    
    def get_description(v: int, fallback: str):
        entry: AnnotationData | None = anno.get(v, None)
        if entry: return entry.mDescription
        else: return fallback
    
    # token, display name, descriptions, icon, index
    return tuple(
        (str(member.value), get_display_name(member.value, member.name), get_description(member.value, ""), "", member.value) for member in enum_data
    )

#endregion

#region Default Encoding of BMap

# Use semicolon split each encodings. Support Western European and Simplified Chinese in default.

g_PyBMapDefaultEncoding: str
if sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    # See: https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers
    g_PyBMapDefaultEncoding = "1252;936"
else:
    # See: https://www.gnu.org/software/libiconv/
    g_PyBMapDefaultEncoding = "CP1252;CP936"

#endregion
