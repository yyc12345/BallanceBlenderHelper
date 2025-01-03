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

def add_into_scene(obj: bpy.types.Object):
    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)

def move_to_cursor(obj: bpy.types.Object):
    # use obj.matrix_world to move, not obj.location because this bug:
    # https://blender.stackexchange.com/questions/27667/incorrect-matrix-world-after-transformation
    # the update of matrix_world after setting location is not immediately.
    # and calling update() function for view_layer for the translation of each object is not suit for too much objects.

    # obj.location = bpy.context.scene.cursor.location
    obj.matrix_world = obj.matrix_world @ mathutils.Matrix.Translation(bpy.context.scene.cursor.location - obj.location)

def add_into_scene_and_move_to_cursor(obj: bpy.types.Object):
    add_into_scene(obj)
    move_to_cursor(obj)

def select_certain_objects(objs: tuple[bpy.types.Object, ...]) -> None:
    # deselect all objects first
    bpy.ops.object.select_all(action = 'DESELECT')
    # if no objects, return
    if len(objs) == 0: return

    # set selection for each object
    for obj in objs:
        obj.select_set(True)
    # select first object as active object
    bpy.context.view_layer.objects.active = objs[0]

def is_in_object_mode() -> bool:
    # get active object from context
    obj = bpy.context.active_object

    # if there is no active object, we think it is in object mode
    if obj is None: return True

    # simply check active object mode
    return obj.mode == 'OBJECT'

class EnumPropHelper():
    """
    These class contain all functions related to EnumProperty, including generating `items`, 
    parsing data from EnumProperty string value and getting EnumProperty acceptable string format from data.
    """

    # define some type hint
    _TFctToStr = typing.Callable[[typing.Any], str]
    _TFctFromStr = typing.Callable[[str], typing.Any]
    _TFctName = typing.Callable[[typing.Any], str]
    _TFctDesc = typing.Callable[[typing.Any], str]
    _TFctIcon = typing.Callable[[typing.Any], str | int]

    # define class member

    __mCollections: typing.Iterable[typing.Any]
    __mFctToStr: _TFctToStr
    __mFctFromStr: _TFctFromStr
    __mFctName: _TFctName
    __mFctDesc: _TFctDesc
    __mFctIcon: _TFctIcon

    def __init__(
            self, 
            collections_: typing.Iterable[typing.Any],
            fct_to_str: _TFctToStr,
            fct_from_str: _TFctFromStr,
            fct_name: _TFctName,
            fct_desc: _TFctDesc,
            fct_icon: _TFctIcon):
        """
        Initialize a EnumProperty helper.

        @param collections_ [in] The collection all available enum property entries contained.
        It can be enum.Enum or a simple list/tuple/dict.
        @param fct_to_str [in] A function pointer converting data collection member to its string format.
        For enum.IntEnum, it can be simply `lambda x: str(x.value)`
        @param fct_from_str [in] A function pointer getting data collection member from its string format.
        For enum.IntEnum, it can be simply `lambda x: TEnum(int(x))`
        @param fct_name [in] A function pointer converting data collection member to its display name.
        @param fct_desc [in] Same as `fct_name` but return description instead. Return empty string, not None if no description.
        @param fct_icon [in] Same as `fct_name` but return the used icon instead. Return empty string if no icon.
        """
        # assign member
        self.__mCollections = collections_
        self.__mFctToStr = fct_to_str
        self.__mFctFromStr = fct_from_str
        self.__mFctName = fct_name
        self.__mFctDesc = fct_desc
        self.__mFctIcon = fct_icon

    def generate_items(self) -> tuple[tuple[str, str, str, int | str, int], ...]:
        """
        Generate a tuple which can be applied to Blender EnumProperty's "items".
        """
        # blender enum prop item format:
        # (token, display name, descriptions, icon, index)
        return tuple(
            (
                self.__mFctToStr(member),   # call to_str as its token.
                self.__mFctName(member), 
                self.__mFctDesc(member), 
                self.__mFctIcon(member), 
                idx # use hardcode index, not the collection member self.
            ) for idx, member in enumerate(self.__mCollections)
        )
    
    def get_selection(self, prop: str) -> typing.Any:
        """
        Return collection member from given Blender EnumProp string data.
        """
        # call from_str fct ptr
        return self.__mFctFromStr(prop)
    
    def to_selection(self, val: typing.Any) -> str:
        """
        Parse collection member to Blender EnumProp acceptable string format.
        """
        # call to_str fct ptr
        return self.__mFctToStr(val)

