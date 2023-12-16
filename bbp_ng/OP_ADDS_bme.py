import bpy
import typing
from . import PROP_preferences, PROP_virtools_mesh, PROP_virtools_group, PROP_bme_material
from . import UTIL_functions, UTIL_icons_manager, UTIL_bme

#region BME Adder

_g_EnumHelper_BmeStructType: UTIL_bme.EnumPropHelper = UTIL_bme.EnumPropHelper()

class BBP_PG_bme_adder_params(bpy.types.PropertyGroup):
    prop_int: bpy.props.IntProperty(
        name = 'Single Int', description = 'Single Int',
        min = 0, max = 64,
        soft_min = 0, soft_max = 32,
        default = 1,
    )
    prop_float: bpy.props.FloatProperty(
        name = 'Single Float', description = 'Single Float',
        min = 0.0, max = 1024.0,
        soft_min = 0.0, soft_max = 64.0,
        default = 5.0,
    )
    prop_str: bpy.props.StringProperty(
        name = 'Single Str', description = 'Single Str',
        default = ''
    )
    prop_bool: bpy.props.BoolProperty(
        name = 'Single Bool', description = 'Single Bool',
        default = True
    )

class BBP_OT_add_bme_struct(bpy.types.Operator):
    """Add BME Struct"""
    bl_idname = "bbp.dd_bme_struct"
    bl_label = "Add BME Struct"
    bl_options = {'REGISTER', 'UNDO'}

    # the updator for default side value
    def bme_struct_type_updated(self, context):
        # get floor prototype
        #floor_prototype = UTILS_constants.floor_blockDict[self.floor_type]

        # try sync default value
        #default_sides = floor_prototype['DefaultSideConfig']
        #self.use_2d_top = default_sides['UseTwoDTop']
        #self.use_2d_right = default_sides['UseTwoDRight']
        #self.use_2d_bottom = default_sides['UseTwoDBottom']
        #self.use_2d_left = default_sides['UseTwoDLeft']
        #self.use_3d_top = default_sides['UseThreeDTop']
        #self.use_3d_bottom = default_sides['UseThreeDBottom']

        # init data collection
        # todo: this state will add 32 items in each call.
        # please clear it or resize it.
        for i in range(32):
            item = self.data_floats.add()

        # blender required
        return None
    
    bme_struct_type: bpy.props.EnumProperty(
        name = "Type",
        description = "BME struct type",
        items = _g_EnumHelper_BmeStructType.generate_items(),
        update = bme_struct_type_updated
    )

    data_floats : bpy.props.CollectionProperty(
        name = "Floats",
        description = "Float collection.",
        type = BBP_PG_bme_adder_params,
    )

    @classmethod
    def poll(self, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()

    def invoke(self, context, event):
        # trigger default bme struct type updator
        self.bme_struct_type_updated(context)
        # run execute() function
        return self.execute(context)

    def execute(self, context):
        # todo: call general creator
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        # show type
        layout.prop(self, 'bme_struct_type')
        # show type
        for i in self.data_floats:
            layout.prop(i, 'prop_bool')

    @classmethod
    def draw_blc_menu(self, layout: bpy.types.UILayout):
        for ident in _g_EnumHelper_BmeStructType.get_bme_identifiers():
            # draw operator
            cop = layout.operator(
                self.bl_idname, 
                text = _g_EnumHelper_BmeStructType.get_bme_showcase_title(ident),
                icon_value = _g_EnumHelper_BmeStructType.get_bme_showcase_icon(ident)
            )
            # and assign its init type value
            cop.bme_struct_type = _g_EnumHelper_BmeStructType.to_selection(ident)
        """         
        for item in PROP_ballance_element.BallanceElementType:
            item_name: str = PROP_ballance_element.get_ballance_element_name(item)

            cop = layout.operator(
                self.bl_idname, text = item_name, 
                icon_value = UTIL_icons_manager.get_component_icon(item_name)
            )
            cop.component_type = EnumPropHelper.to_selection(item) 
        """

#endregion

def register():
    bpy.utils.register_class(BBP_PG_bme_adder_params)
    bpy.utils.register_class(BBP_OT_add_bme_struct)

def unregister():
    bpy.utils.unregister_class(BBP_OT_add_bme_struct)
    bpy.utils.unregister_class(BBP_PG_bme_adder_params)