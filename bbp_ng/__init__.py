bl_info = {
    "name": "Ballance Blender Plugin",
    "description": "Ballance mapping tools for Blender",
    "author": "yyc12345",
    "version": (4, 0),
    "blender": (3, 6, 0),
    "category": "Object",
    "support": "COMMUNITY",
    "warning": "Please read document before using this plugin.",
    "doc_url": "https://github.com/yyc12345/BallanceBlenderHelper",
    "tracker_url": "https://github.com/yyc12345/BallanceBlenderHelper/issues"
}

#region Reload and Import

# import core lib
import bpy
import typing

# reload if needed
if "bpy" in locals():
    import importlib

#endregion

#region Register and Unregister.

def register() -> None:
    pass

def unregister() -> None:
    pass

if __name__ == "__main__":
    register()

#endregion
