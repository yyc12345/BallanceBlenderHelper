import bpy
import typing
from . import UTIL_naming_convension, UTIL_functions, UTIL_icons_manager

class BBP_OT_regulate_objects_name(bpy.types.Operator):
    """Regulate Objects Name by Virtools Group and Naming Convention"""
    bl_idname = "bbp.regulate_objects_name"
    bl_label = "Regulate Objects Name"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_regulate_objects_name'

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        _rename_core(
            UTIL_naming_convension.VirtoolsGroupConvention.parse_from_object,
            UTIL_naming_convension.YYCToolchainConvention.set_to_object
        )
        return {'FINISHED'}

class BBP_OT_auto_grouping(bpy.types.Operator):
    """Auto Grouping Objects by Its Name and Name Convention"""
    bl_idname = "bbp.auto_grouping"
    bl_label = "Auto Grouping"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_auto_grouping'

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        _rename_core(
            UTIL_naming_convension.YYCToolchainConvention.parse_from_object,
            UTIL_naming_convension.VirtoolsGroupConvention.set_to_object
        )
        return {'FINISHED'}

class BBP_OT_convert_to_imengyu(bpy.types.Operator):
    """Convert Objects Name from YYC Convention to Imengyu Convention."""
    bl_idname = "bbp.convert_to_imengyu"
    bl_label = "Convert to Imengyu"
    bl_options = {'UNDO'}
    bl_translation_context = 'BBP_OT_convert_to_imengyu'

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        _rename_core(
            UTIL_naming_convension.YYCToolchainConvention.parse_from_object,
            UTIL_naming_convension.ImengyuConvention.set_to_object
        )
        return {'FINISHED'}

def _rename_core(
    fct_get_info: typing.Callable[[bpy.types.Object, UTIL_naming_convension.RenameErrorReporter], UTIL_naming_convension.BallanceObjectInfo | None],
    ftc_set_info: typing.Callable[[bpy.types.Object, UTIL_naming_convension.BallanceObjectInfo, UTIL_naming_convension.RenameErrorReporter], bool]
    ) -> None:
    # get selected objects. allow nested collection
    selected_objects: typing.Iterable[bpy.types.Object] = bpy.context.view_layer.active_layer_collection.collection.all_objects
    
    # create reporter
    with UTIL_naming_convension.RenameErrorReporter() as reporter:
        # iterate objects
        for obj in selected_objects:
            reporter.enter_object(obj)
            
            # try get info
            info: UTIL_naming_convension.BallanceObjectInfo | None = fct_get_info(obj, reporter)
            if info is not None:
                # if info is valid, try assign it
                if not ftc_set_info(obj, info, reporter):
                    reporter.add_error('Fail to set info to object.')
            else:
                reporter.add_error('Fail to get info from object.')

            # end obj process
            reporter.leave_object(obj)

        # report data
        tr_text_1: str = bpy.app.translations.pgettext_rpt('View console to get more detail', 'BBP/OP_OBJECT_naming_convention._rename_core()')
        tr_text_2: str = bpy.app.translations.pgettext_rpt('All: {0}', 'BBP/OP_OBJECT_naming_convention._rename_core()')
        tr_text_3: str = bpy.app.translations.pgettext_rpt('Failed: {0}', 'BBP/OP_OBJECT_naming_convention._rename_core()')
        UTIL_functions.message_box(
            (
                tr_text_1,
                tr_text_2.format(reporter.get_all_objs_count()),
                tr_text_3.format(reporter.get_failed_objs_count())
            ),
            'Rename System Report',
            UTIL_icons_manager.BlenderPresetIcons.Info.value
        )

def register() -> None:
    bpy.utils.register_class(BBP_OT_regulate_objects_name)
    bpy.utils.register_class(BBP_OT_auto_grouping)
    bpy.utils.register_class(BBP_OT_convert_to_imengyu)

def unregister() -> None:
    bpy.utils.unregister_class(BBP_OT_convert_to_imengyu)
    bpy.utils.unregister_class(BBP_OT_auto_grouping)
    bpy.utils.unregister_class(BBP_OT_regulate_objects_name)
