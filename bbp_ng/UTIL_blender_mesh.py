import bpy, bmesh

## Blender Mesh Usage
#  This module create a universal mesh visitor, including MeshReader, MeshWriter and MeshUVModifier
#  for every other possible module using.
#  Obviously, MeshReader is served for 2 exporter, MeshWriter is served for 2 importer.
#  MeshWriter also served for BMERevenge module and Ballance element loading.
#  MeshUVModifier is used by Flatten UV and Rail UV.
#  

class MeshReader():
    pass


class MeshWriter():
    pass


class MeshUVModifier():
    pass


def register() -> None:
    pass # nothing to register

def unregister() -> None:
    pass
