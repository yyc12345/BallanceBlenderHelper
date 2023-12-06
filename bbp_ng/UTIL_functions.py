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
    obj.location = bpy.context.scene.cursor.location

def add_into_scene_and_move_to_cursor(obj: bpy.types.Object):
    move_to_cursor(obj)

    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)
