import bpy
import bpy.types

class MyPropertyGroup(bpy.types.PropertyGroup):
    material_picker : bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Material",
        description="The material used for rail"
    )

    collection_picker : bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Collection",
        description="The collection which will be exported"
    )

    object_picker : bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Object",
        description="The object which will be exported"
    )

class BallanceBlenderPluginPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    external_folder: bpy.props.StringProperty(
        name="External texture folder",
        description="The Ballance texture folder which will be used by this plugin to get external texture.",
        )

    no_component_collection: bpy.props.StringProperty(
        name="No component collection",
        description="(Import) The object which stored in this collectiion will not be saved as component. (Export) All forced no component objects will be stored in this collection",
        )

    temp_texture_folder: bpy.props.StringProperty(
        name="Temp texture folder",
        description="The folder which will temporarily store the textures which are extracted from bm. Due to system temp folder will be deleted after decoding of bm, so this path should not be blank.",
        )

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        col = row.column()

        col.prop(self, "external_folder")
        col.prop(self, "no_component_collection")
        col.prop(self, "temp_texture_folder")