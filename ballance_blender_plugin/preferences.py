import bpy

class BallanceBlenderPluginPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    external_folder: bpy.props.StringProperty(
        name="External texture folder",
        description="The Ballance texture folder which will be used buy this plugin to get external texture.",
        )

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column()

        col.prop(self, "external_folder")