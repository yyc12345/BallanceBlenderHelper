import bpy, mathutils
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

def message_box(message: tuple[str, ...], title: str, icon: str):
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

def move_to_cursor(obj: bpy.types.Object):
    # use obj.matrix_world to move, not obj.location because this bug:
    # https://blender.stackexchange.com/questions/27667/incorrect-matrix-world-after-transformation
    # the update of matrix_world after setting location is not immediately.
    # and calling update() function for view_layer for the translation of each object is not suit for too much objects.

    # obj.location = bpy.context.scene.cursor.location
    obj.matrix_world = obj.matrix_world @ mathutils.Matrix.Translation(bpy.context.scene.cursor.location - obj.location)

def add_into_scene_and_move_to_cursor(obj: bpy.types.Object):
    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)

    move_to_cursor(obj)

class EnumPropHelper():
    """
    These class contain all functions related to EnumProperty creation for Python Enums
    """

    # define some type hint

    _TEnumVar = typing.TypeVar('_TEnumVar',  bound = enum.Enum) ##< Mean a variable of enum.Enum's children
    _TEnum = type[_TEnumVar] ##< Mean the type self which is enum.Enum's children.
    _TFctName = typing.Callable[[_TEnumVar], str]
    _TFctDesc = typing.Callable[[_TEnumVar], str]
    _TFctIcon = typing.Callable[[_TEnumVar], str | int]

    # define class member

    __mTy: _TEnum
    __mIsIntEnum: bool
    __mFctName: _TFctName
    __mFctDesc: _TFctDesc
    __mFctIcon: _TFctIcon

    def __init__(
            self, 
            ty: _TEnum, 
            fct_name: _TFctName,
            fct_desc: _TFctDesc,
            fct_icon: _TFctIcon):
        # check type
        if not issubclass(ty, enum.Enum):
            raise BBPException('invalid type for EnumPropHelper')
        # assign member
        self.__mTy = ty
        self.__mIsIntEnum = issubclass(ty, enum.IntEnum)
        self.__mFctName = fct_name
        self.__mFctDesc = fct_desc
        self.__mFctIcon = fct_icon

    def generate_items(self) -> tuple[tuple[str, str, str, int | str, int], ...]:
        """
        Generate a tuple which can be applied to Blender EnumProperty's "items".
        """
        # blender enum prop item format:
        # (token, display name, descriptions, icon, index)
        if self.__mIsIntEnum:
            # for intenum, we can use its value as index number directly.
            # and use the string format of index as blender prop token.
            return tuple(
                (
                    str(member.value), 
                    self.__mFctName(member), 
                    self.__mFctDesc(member), 
                    self.__mFctIcon(member), 
                    member.value
                ) for member in self.__mTy
            )
        else:
            # for non-intenum, we need create number index manually for it.
            # and directly use its value as blender prop token
            return tuple(
                (
                    member.value, 
                    self.__mFctName(member), 
                    self.__mFctDesc(member), 
                    self.__mFctIcon(member), 
                    idx
                ) for idx, member in enumerate(self.__mTy)
            )
    
    def get_selection(self, prop: str) -> _TEnumVar:
        """
        Return Python enum value from given Blender EnumProp.
        """
        # for intenum, param is its string format, we need use int() to convert it first
        # for non-intenum, param is just its value, we use it directly
        # then we parse it to python enum type
        if self.__mIsIntEnum:
            return self.__mTy(int(prop))
        else:
            return self.__mTy(prop)
    
    def to_selection(self, val: _TEnumVar) -> str:
        """
        Parse Python enum value to Blender EnumProp acceptable string.
        """
        # the inversed operation of get_selection().
        if self.__mIsIntEnum:
            return str(val.value)
        else:
            return val.value

