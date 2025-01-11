import bpy
import typing
from . import PROP_virtools_group

class BBP_OT_snoop_group_then_to_mesh(bpy.types.Operator):
    """Convert selected objects into mesh objects and try to copy the Virtools Group infos of their associated curve bevel object if they have. """
    bl_idname = "bbp.snoop_group_then_to_mesh"
    bl_label = "Snoop Group then to Mesh"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_snoop_group_then_to_mesh'

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def execute(self, context):
        for obj in context.selected_objects:
            # skip all non-curve object
            if obj.type != 'CURVE': continue
            
            # fetch curve data block
            curve: bpy.types.Curve = typing.cast(bpy.types.Curve, obj.data)

            # if bevel mode is not object, skip
            if curve.bevel_mode != 'OBJECT': continue
            # if bevel object is None, skip
            bevel_obj: bpy.types.Object | None = curve.bevel_object
            if bevel_obj is None: continue

            # copy bevel object group info into current object
            with PROP_virtools_group.VirtoolsGroupsHelper(obj) as this_gp:
                this_gp.clear_groups()
                with PROP_virtools_group.VirtoolsGroupsHelper(bevel_obj) as bevel_gp:
                    this_gp.add_groups(bevel_gp.iterate_groups())

        # convert all selected object to mesh 
        # no matter the success of copying virtools group infos and whether selected object is curve
        bpy.ops.object.convert(target = 'MESH')
        
        return {'FINISHED'}

def register() -> None:
    bpy.utils.register_class(BBP_OT_snoop_group_then_to_mesh)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_snoop_group_then_to_mesh)
