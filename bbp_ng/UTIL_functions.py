import bpy, mathutils
import math, typing, enum, sys

class BBPException(Exception):
    """ The exception thrown by Ballance Blender Plugin"""
    pass

def clamp_float(v: float, min_val: float, max_val: float) -> float:
    """
    Clamp a float value

    :param v: The value need to be clamp.
    :param min_val: The allowed minium value (inclusive).
    :param max_val: The allowed maxium value (inclusive).
    :return: Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_float().")
    
    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v

def clamp_int(v: int, min_val: int, max_val: int) -> int:
    """
    Clamp a int value

    :param v: The value need to be clamp.
    :param min_val: The allowed minium value (inclusive).
    :param max_val: The allowed maxium value (inclusive).
    :return: Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_int().")
    
    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v

def message_box(message: tuple[str, ...], title: str, icon: str):
    """
    Show a message box in Blender. Non-block mode.

    :param message: The text this message box displayed. Each item in this param will show as a single line.
    :param title: Message box title text.
    :param icon: The icon this message box displayed.
    """
    def draw(self, context: bpy.types.Context):
        layout = self.layout
        for item in message:
            layout.label(text=item, translate=False)
    
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def add_into_scene(obj: bpy.types.Object):
    """
    Add given object into active scene.

    :param obj: The 3d object to be added.
    """
    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)

def move_to_cursor(obj: bpy.types.Object):
    """
    Move given object to the position of cursor.

    :param obj: The 3d object to be moved.
    """
    # YYC MARK:
    # Use `obj.matrix_world` to move, not `obj.location`, because this bug:
    # https://blender.stackexchange.com/questions/27667/incorrect-matrix-world-after-transformation
    # The update of `matrix_world` after setting `location` is not immediately.
    # And it is inviable that calling `update()` function for `view_layer` to update these fields,
    # because it involve too much objects and cost too much time.
    
    # obj.location = bpy.context.scene.cursor.location
    obj.matrix_world = obj.matrix_world @ mathutils.Matrix.Translation(bpy.context.scene.cursor.location - obj.location)

def add_into_scene_and_move_to_cursor(obj: bpy.types.Object):
    """
    Add given object into active scene and move it to cursor position.

    This function is just a simple combination of previous functions.

    :param obj: The 3d object to be processed.
    """
    add_into_scene(obj)
    move_to_cursor(obj)

def select_certain_objects(objs: tuple[bpy.types.Object, ...]) -> None:
    """
    Deselect all objects and then select given 3d objects.
    
    :param objs: The tuple of 3d objects to be selected.
    """
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
    """
    Check whether we are in Blender Object Mode.

    :return: True if we are in object mode which suit for exporting something.
    """
    # get active object from context
    obj = bpy.context.active_object
    
    # if there is no active object, we think it is in object mode
    if obj is None: return True
    
    # simply check active object mode
    return obj.mode == 'OBJECT'

#region Blender Enum Property Helper

_TRawEnum = typing.TypeVar('_TRawEnum')

_TFctToStr = typing.Callable[[_TRawEnum], str]
_TFctFromStr = typing.Callable[[str], _TRawEnum]
_TFctName = typing.Callable[[_TRawEnum], str]
_TFctDesc = typing.Callable[[_TRawEnum], str]
_TFctIcon = typing.Callable[[_TRawEnum], str | int]

class EnumPropHelper(typing.Generic[_TRawEnum]):
    """
    These class contain all functions related to EnumProperty, including generating `items`, 
    parsing data from EnumProperty string value and getting EnumProperty acceptable string format from data.
    """
    
    __mCollections: typing.Iterable[_TRawEnum]
    __mFctToStr: _TFctToStr
    __mFctFromStr: _TFctFromStr
    __mFctName: _TFctName
    __mFctDesc: _TFctDesc
    __mFctIcon: _TFctIcon
    
    def __init__(self, collections: typing.Iterable[typing.Any],
                 fct_to_str: _TFctToStr, fct_from_str: _TFctFromStr,
                 fct_name: _TFctName, fct_desc: _TFctDesc,
                 fct_icon: _TFctIcon):
        """
        Initialize an EnumProperty helper.

        :param collections: The collection containing all available enum property entries.
            It can be `enum.Enum` or a simple list/tuple.
        :param fct_to_str: A function pointer converting data collection member to its string format.
            You must make sure that each members built name is unique in collection!
            For `enum.IntEnum`, it can be simple `lambda x: str(x.value)`
        :param fct_from_str: A function pointer getting data collection member from its string format.
            This class promise that given string must can be parsed.
            For `enum.IntEnum`, it can be simple `lambda x: TEnum(int(x))`
        :param fct_name: A function pointer converting data collection member to its display name which shown in Blender.
        :param fct_desc: Same as `fct_name` but return description instead which shown in Blender
            If no description, return empty string, not None.
        :param fct_icon: Same as `fct_name` but return the used icon instead which shown in Blender.
            It can be a Blender builtin icon string, or any loaded icon integer ID.
            If no icon, return empty string.
        """
        # assign member
        self.__mCollections = collections
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
    
    def get_selection(self, prop: str) -> _TRawEnum:
        """
        Return collection member from given Blender EnumProp string data.
        """
        # call from_str fct ptr
        return self.__mFctFromStr(prop)
    
    def to_selection(self, val: _TRawEnum) -> str:
        """
        Parse collection member to Blender EnumProp acceptable string format.
        """
        # call to_str fct ptr
        return self.__mFctToStr(val)

#endregion

#region Blender Collection Visitor

_TPropertyGroup = typing.TypeVar('_TPropertyGroup', bound = bpy.types.PropertyGroup)

class CollectionVisitor(typing.Generic[_TPropertyGroup]):
    """
    This is a patch class for Blender collection property.
    Blender collcetion property lack essential type hint and document.
    So I create a wrapper for my personal use to reduce type hint errors raised by my linter.
    """
    
    __mSrcProp: bpy.types.CollectionProperty
    
    def __init__(self, src_prop: bpy.types.CollectionProperty):
        self.__mSrcProp = src_prop
    
    def add(self) -> _TPropertyGroup:
        """
        Adds a new item to the collection.

        :return: The instance of newly created item.
        """
        return self.__mSrcProp.add()
    
    def remove(self, index: int) -> None:
        """
        Removes the item at the specified index from the collection.

        :param index: The index of the item to remove.
        """
        self.__mSrcProp.remove(index)
    
    def move(self, from_index: int, to_index: int) -> None:
        """
        Moves an item from one index to another within the collection.

        :param from_index: The current index of the item to move.
        :param to_index: The target index where the item should be moved.
        """
        self.__mSrcProp.move(from_index, to_index)
    
    def clear(self) -> None:
        """
        Clears all items from the collection.
        """
        self.__mSrcProp.clear()
    
    def __len__(self) -> int:
        return self.__mSrcProp.__len__()
    def __getitem__(self, index: int | str) -> _TPropertyGroup:
        return self.__mSrcProp.__getitem__(index)
    def __setitem__(self, index: int | str, value: _TPropertyGroup) -> None:
        self.__mSrcProp.__setitem__(index, value)
    def __delitem__(self, index: int | str) -> None:
        self.__mSrcProp.__delitem__(index)
    def __iter__(self) -> typing.Iterator[_TPropertyGroup]:
        return self.__mSrcProp.__iter__()
    def __contains__(self, item: _TPropertyGroup) -> bool:
        return self.__mSrcProp.__contains__(item)

#endregion

#region Tiny Mutex for With Context

_TMutexObject = typing.TypeVar('_TMutexObject')

class TinyMutex(typing.Generic[_TMutexObject]):
    """
    In this plugin, some classes have "with" context feature.
    However, in some cases, it is essential to block any futher visiting if some "with" context are operating on some object.
    This is the reason why this tiny mutex is designed.

    Please note this class is not a real MUTEX.
    We just want to make sure the resources only can be visited by one "with" context.
    So it doesn't matter that we do not use lock before operating something.
    """
    
    __mProtectedObjects: set[_TMutexObject]
    
    def __init__(self):
        self.__mProtectedObjects = set()
    
    def lock(self, obj: _TMutexObject) -> None:
        """
        Lock given object.

        :raise BBPException: Raised if given object has been locked.
        :param obj: The resource to be locked.
        """
        if obj in self.__mProtectedObjects:
            raise BBPException('It is not allowed that operate multiple "with" contexts on a single object.')
        self.__mProtectedObjects.add(obj)
    
    def try_lock(self, obj: _TMutexObject) -> bool:
        """
        Try lock given object.

        :param obj: The resource to be locked.
        :return: True if we successfully lock it, otherwise false.
        """
        if obj in self.__mProtectedObjects:
            return False
        self.__mProtectedObjects.add(obj)
        return True
    
    def unlock(self, obj: _TMutexObject) -> None:
        """
        Unlock given object.

        :raise BBPException: Raised if given object is not locked.
        :param obj: The resource to be unlocked.
        """
        if obj not in self.__mProtectedObjects:
            raise BBPException('It is not allowed that unlock an non-existent object.')
        self.__mProtectedObjects.remove(obj)

#endregion
