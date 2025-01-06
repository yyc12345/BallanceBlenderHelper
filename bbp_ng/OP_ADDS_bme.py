import bpy, mathutils
import typing
from . import PROP_preferences
from . import UTIL_functions, UTIL_bme

#region BME Adder

_g_EnumHelper_BmeStructType: UTIL_bme.EnumPropHelper = UTIL_bme.EnumPropHelper()

class BBP_PG_bme_adder_cfgs(bpy.types.PropertyGroup):
    prop_int: bpy.props.IntProperty(
        name = 'Single Int', description = 'Single Int',
        min = 0, max = 64,
        soft_min = 0, soft_max = 32,
        step = 1,
        default = 1,
    ) # type: ignore
    prop_float: bpy.props.FloatProperty(
        name = 'Single Float', description = 'Single Float',
        min = 0.0, max = 1024.0,
        soft_min = 0.0, soft_max = 512.0,
        step = 50, # Step is in UI, in [1, 100] (WARNING: actual value is /100). So we choose 50, mean 0.5
        default = 5.0,
    ) # type: ignore
    prop_bool: bpy.props.BoolProperty(
        name = 'Single Bool', description = 'Single Bool',
        default = True
    ) # type: ignore

class BBP_OT_add_bme_struct(bpy.types.Operator):
    """Add BME Struct"""
    bl_idname = "bbp.add_bme_struct"
    bl_label = "Add BME Struct"
    bl_options = {'REGISTER', 'UNDO'}
    
    ## There is a compromise due to the shitty Blender design.
    #  
    #  The passed `self` of Blender Property update function is not the instance of operator,
    #  but a simple OperatorProperties.
    #  It mean that I can not visit the full operator, only what I can do is visit existing 
    #  Blender properties.
    #  
    #  So these is the solution about generating cache list according to the change of bme struct type.
    #  First, update function will only set a "outdated" flag for operator which is a pre-registered Blender property.
    #  The "outdated" flags is not showen and not saved.
    #  Then call a internal cache list update function at the begin of `invoke`, `execute` and `draw`.
    #  In this internal cache list updator, check "outdated" flag first, if cache is outdated, update and reset flag.
    #  Otherwise do nothing.
    #  
    #  Reference: https://docs.blender.org/api/current/bpy.props.html#update-example

    ## Compromise used "outdated" flag.
    outdated_flag: bpy.props.BoolProperty(
        name = "Outdated Type",
        description = "Internal flag.",
        options = {'HIDDEN', 'SKIP_SAVE'},
        default = False
    ) # type: ignore

    ## A BME struct cfgs descriptor cache list
    #  Not only the descriptor self, also the cfg associated index in bme_struct_cfgs
    bme_struct_cfg_index_cache: list[tuple[UTIL_bme.PrototypeShowcaseCfgDescriptor, int]]

    def __internal_update_bme_struct_type(self) -> None:
        # if not outdated, skip
        if not self.outdated_flag: return

        # get available cfg entires
        cfgs: typing.Iterator[UTIL_bme.PrototypeShowcaseCfgDescriptor]
        cfgs = _g_EnumHelper_BmeStructType.get_bme_showcase_cfgs(
            _g_EnumHelper_BmeStructType.get_selection(self.bme_struct_type)
        )

        # analyse cfgs. 
        # create counter first
        counter_int: int = 0
        counter_float: int = 0
        counter_bool: int = 0
        # create cache list
        self.bme_struct_cfg_index_cache.clear()
        # iterate cfgs and register them
        for cfg in cfgs:
            match(cfg.get_type()):
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Integer:
                    self.bme_struct_cfg_index_cache.append((cfg, counter_int))
                    counter_int += 1
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Float:
                    self.bme_struct_cfg_index_cache.append((cfg, counter_float))
                    counter_float += 1
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Boolean:
                    self.bme_struct_cfg_index_cache.append((cfg, counter_bool))
                    counter_bool += 1
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Face:
                    self.bme_struct_cfg_index_cache.append((cfg, counter_bool))
                    counter_bool += 6   # face will occupy 6 bool.


        # init data collection
        adder_cfgs_visitor: UTIL_functions.CollectionVisitor[BBP_PG_bme_adder_cfgs]
        adder_cfgs_visitor = UTIL_functions.CollectionVisitor(self.bme_struct_cfgs)
        # clear first
        adder_cfgs_visitor.clear()
        # create enough entries specified by gotten cfgs
        for _ in range(max(counter_int, counter_float, counter_bool)):
            adder_cfgs_visitor.add()

        # assign default value
        for (cfg, cfg_index) in self.bme_struct_cfg_index_cache:
            # show prop differently by cfg type
            match(cfg.get_type()):
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Integer:
                    adder_cfgs_visitor[cfg_index].prop_int = cfg.get_default()
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Float:
                    adder_cfgs_visitor[cfg_index].prop_float = cfg.get_default()
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Boolean:
                    adder_cfgs_visitor[cfg_index].prop_bool = cfg.get_default()
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Face:
                    # face is just 6 bool
                    default_values: tuple[bool, ...] = cfg.get_default()
                    for i in range(6):
                        adder_cfgs_visitor[cfg_index + i].prop_bool = default_values[i]

        # reset outdated flag
        self.outdated_flag = False

    # the updator for default side value
    def bme_struct_type_updated(self, context):
        # update outdated flag
        self.outdated_flag = True
        # blender required
        return None
    
    bme_struct_type: bpy.props.EnumProperty(
        name = "Type",
        description = "BME struct type",
        items = _g_EnumHelper_BmeStructType.generate_items(),
        update = bme_struct_type_updated
    ) # type: ignore
    
    bme_struct_cfgs : bpy.props.CollectionProperty(
        name = "Cfgs",
        description = "Cfg collection.",
        type = BBP_PG_bme_adder_cfgs,
    ) # type: ignore
    
    ## Extra transform for good "what you see is what you gotten".
    #  Extra transform will be added after moving this object to cursor.
    extra_translation: bpy.props.FloatVectorProperty(
        name = "Extra Translation",
        description = "The extra translation applied to object after moving to cursor.",
        size = 3,
        subtype = 'TRANSLATION',
        step = 50, # same step as the float entry of BBP_PG_bme_adder_cfgs
        default = (0.0, 0.0, 0.0)
    ) # type: ignore
    extra_rotation: bpy.props.FloatVectorProperty(
        name = "Extra Rotation",
        description = "The extra rotation applied to object after moving to cursor.",
        size = 3,
        subtype = 'EULER',
        step = 100, # We choosen 100, mean 1. Sync with property window.
        default = (0.0, 0.0, 0.0)
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        return PROP_preferences.get_raw_preferences().has_valid_blc_tex_folder()
    
    def invoke(self, context, event):
        # reset extra transform to identy
        self.extra_translation = (0.0, 0.0, 0.0)
        self.extra_rotation = (0.0, 0.0, 0.0)
        self.extra_scale = (1.0, 1.0, 1.0)
        # create internal list
        self.bme_struct_cfg_index_cache = []
        # trigger default bme struct type updator
        self.bme_struct_type_updated(context)
        # call internal updator
        self.__internal_update_bme_struct_type()
        # run execute() function
        return self.execute(context)
    
    def execute(self, context):
        # call internal updator
        self.__internal_update_bme_struct_type()

        # create cfg visitor
        adder_cfgs_visitor: UTIL_functions.CollectionVisitor[BBP_PG_bme_adder_cfgs]
        adder_cfgs_visitor = UTIL_functions.CollectionVisitor(self.bme_struct_cfgs)
        # collect cfgs data
        cfgs: dict[str, typing.Any] = {}
        for (cfg, cfg_index) in self.bme_struct_cfg_index_cache:
            match(cfg.get_type()):
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Integer:
                    cfgs[cfg.get_field()] = adder_cfgs_visitor[cfg_index].prop_int
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Float:
                    cfgs[cfg.get_field()] = adder_cfgs_visitor[cfg_index].prop_float
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Boolean:
                    cfgs[cfg.get_field()] = adder_cfgs_visitor[cfg_index].prop_bool
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Face:
                    # face is just 6 bool tuple
                    cfgs[cfg.get_field()] = tuple(
                        adder_cfgs_visitor[cfg_index + i].prop_bool for i in range(6)
                    )

        # call general creator
        obj: bpy.types.Object = UTIL_bme.create_bme_struct_wrapper(
            _g_EnumHelper_BmeStructType.get_selection(self.bme_struct_type),
            cfgs
        )

        # add into scene and move to cursor
        UTIL_functions.add_into_scene_and_move_to_cursor(obj)
        # add extra transform
        obj.matrix_world = obj.matrix_world @ mathutils.Matrix.LocRotScale(
            mathutils.Vector(self.extra_translation),
            mathutils.Euler(self.extra_rotation, 'XYZ'),
            mathutils.Vector((1.0, 1.0, 1.0)) # no scale
        )
        # select created object
        UTIL_functions.select_certain_objects((obj, ))
        return {'FINISHED'}
    
    def draw(self, context):
        # call internal updator
        self.__internal_update_bme_struct_type()

        # start drawing
        layout: bpy.types.UILayout = self.layout
        # show type
        layout.prop(self, 'bme_struct_type')

        # create cfg visitor
        adder_cfgs_visitor: UTIL_functions.CollectionVisitor[BBP_PG_bme_adder_cfgs]
        adder_cfgs_visitor = UTIL_functions.CollectionVisitor(self.bme_struct_cfgs)
        # visit cfgs cache list to show cfg
        layout.label(text = "Prototype Configurations:")
        for (cfg, cfg_index) in self.bme_struct_cfg_index_cache:
            # create box for cfgs
            box_layout: bpy.types.UILayout = layout.box()

            # draw title and description first
            box_layout.label(text = cfg.get_title())
            box_layout.label(text = cfg.get_desc())

            # show prop differently by cfg type
            match(cfg.get_type()):
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Integer:
                    box_layout.prop(adder_cfgs_visitor[cfg_index], 'prop_int', text = '')
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Float:
                    box_layout.prop(adder_cfgs_visitor[cfg_index], 'prop_float', text = '')
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Boolean:
                    box_layout.prop(adder_cfgs_visitor[cfg_index], 'prop_bool', text = '')
                case UTIL_bme.PrototypeShowcaseCfgsTypes.Face:
                    # face will show a special layout (grid view)
                    grids = box_layout.grid_flow(
                        row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
                    grids.alignment = 'CENTER'
                    grids.separator()
                    grids.prop(adder_cfgs_visitor[cfg_index + 0], 'prop_bool', text = 'Top') # top
                    grids.prop(adder_cfgs_visitor[cfg_index + 2], 'prop_bool', text = 'Front') # front
                    grids.prop(adder_cfgs_visitor[cfg_index + 4], 'prop_bool', text = 'Left') # left
                    grids.label(text = '', icon = 'CUBE')   # show a 3d cube as icon
                    grids.prop(adder_cfgs_visitor[cfg_index + 5], 'prop_bool', text = 'Right') # right
                    grids.prop(adder_cfgs_visitor[cfg_index + 3], 'prop_bool', text = 'Back') # back
                    grids.prop(adder_cfgs_visitor[cfg_index + 1], 'prop_bool', text = 'Bottom') # bottom
                    grids.separator()

        # show extra transform props
        # forcely order that each one are placed horizontally
        layout.label(text = "Extra Transform:")
        # translation
        layout.label(text = 'Translation')
        hbox_layout: bpy.types.UILayout = layout.row()
        hbox_layout.prop(self, 'extra_translation', text = '')
        # rotation
        layout.label(text = 'Rotation')
        hbox_layout = layout.row()
        hbox_layout.prop(self, 'extra_rotation', text = '')

    @classmethod
    def draw_blc_menu(cls, layout: bpy.types.UILayout):
        for ident in _g_EnumHelper_BmeStructType.get_bme_identifiers():
            # draw operator
            cop = layout.operator(
                cls.bl_idname,
                text = _g_EnumHelper_BmeStructType.get_bme_showcase_title(ident),
                icon_value = _g_EnumHelper_BmeStructType.get_bme_showcase_icon(ident)
            )
            # and assign its init type value
            cop.bme_struct_type = _g_EnumHelper_BmeStructType.to_selection(ident)

#endregion

def register() -> None:
    bpy.utils.register_class(BBP_PG_bme_adder_cfgs)
    bpy.utils.register_class(BBP_OT_add_bme_struct)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_add_bme_struct)
    bpy.utils.unregister_class(BBP_PG_bme_adder_cfgs)