import bpy
from . import UTIL_functions

class BBP_PG_virtools_group(bpy.types.PropertyGroup):
    group_name: bpy.props.StringProperty(
        name = "Group Name", 
        default = ""
    )
