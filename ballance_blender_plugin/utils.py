import bpy
from bpy_extras.io_utils import unpack_list

def ShowMessageBox(message, title, icon):

    def draw(self, context):
        layout = self.layout
        for item in message:
            layout.label(text=item, translate=False)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def AddSceneAndMove2Cursor(obj):
    Move2Cursor(obj)

    view_layer = bpy.context.view_layer
    collection = view_layer.active_layer_collection.collection
    collection.objects.link(obj)

def Move2Cursor(obj):
    obj.location = bpy.context.scene.cursor.location
