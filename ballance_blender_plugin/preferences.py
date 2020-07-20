import bpy

class BallanceBlenderPluginPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    external_folder: bpy.props.StringProperty(
        name="External texture folder",
        description="The Ballance texture folder which will be used buy this plugin to get external texture.",
        )

    no_component_collection: bpy.props.StringProperty(
        name="No component collection",
        description="(Import) The object which stored in this collectiion will not be saved as component. (Export) All forced no component objects will be stored in this collection",
        )

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column()

        col.prop(self, "external_folder")
        col.prop(self, "no_component_collection")