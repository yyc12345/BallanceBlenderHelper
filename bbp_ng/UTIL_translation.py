import bpy

#region Translation Contexts

## NOTE: Translation Priniciple
#  Due to the shitty design of Blender I18N tools (I can't specify context for every translation entries and its static analyse is so bad),
#  I will specify all context but I can't do anything if Blender throw my translation context away.
#  
#  BME module has its own context naming convention which make sure all configuration fields of prototypes are properly translated.
#  This module also provide a corresponding function to compute these context string from given BME prototype name and the index of configuration fields.
#  
#  For BBP plugin self, there is a list containing multiple priniciples which you should follow when providing translation context.
#  - For operator, menu, panel and etc.
#      * For themselves, fill `bl_translation_context` to their name, such as `BBP_OT_some_operator`.
#      * For properties located inside, add `/property` suffix, such as `BBP_OT_some_operator/property`.
#      * For draw function (any function callings requiring translation context inside it), add `/draw` suffix, such as `BBP_OT_some_operator/draw`.
#      * For execute function, or any functions mainly called by this execution function, add `/execute` suffix, such as `BBP_OT_some_operator/execute`.
#  - For shared class (usually shared by multiple operators).
#      * For themselves (usually not used because they don't have `bl_translation_context`), the default context is `BME/<MODULE_NAME>.<CLASS_NAME>`, such as `BBP/some_module.some_class`.
#      * For properties located inside, add `/property` suffix, such as `BBP/some_module.some_class/property`.
#      * For draw function (any function callings requiring translation context inside it), add `/draw` suffix, such as `BBP/some_module.some_class/draw`.
#  - For menu draw function (usually defined in __init__ module).
#      * For themselves (any calling inside them), the context is `BME/<MODULE_NAME>.<METHOD_NAME>()`, such as `BBP/some_module.some_method()`.
#  
#  Due to the shitty design, I can't find a way to add translation context for descrption field and report function used string.
#  So these description may collide with Blender official translation, thus they may not be put in result translation file.
#  I have no idea about this.
#  
#  Due to the shitty static analyse ability of Blender I18N plugin, all context should be written in literal,
#  not the reference to other fields or the return value of some function.
#  However for those strings, which originally should not be extracted by Blender I18N plugin, the way to get their context string is free.
#  
#  
#  For the string given to Python `print()` which will be output in console,
#  please use `bpy.app.translations.pgettext_rpt()` to get translation message because they are report.
#  For the string given to `UTIL_functions.message_box()`, please use `bpy.app.translations.pgettext_iface` because they are UI elements.
#  
#  `bpy.app.translations.pgettext` function family has fatal error when extracting message with context
#  (it will produce a correct one and a wrong one which just simply concat the message and its context. I don't know why).
#  This will happen if you put `bpy.app.translations.pgettext` calling inside `UILayout.label` or any UILayout functions like it.
#  `bpy.app.translations.pgettext` will produce the correct entry but Blender used "magic of `UILayout.label` will produce the wrong one.
#  It seems that Blender's magic just join the string provided in `text` argument as much as possible.
#  So the solution is simple:
#  - If we use `bpy.app.translations.pgettext` and `UILayout.label` together
#      * Create a variable holding the result of `bpy.app.translations.pgettext`.
#      * Format this gotten string if necessary.
#      * Call `UILayout.label` and use this variable as its `text` argument. Then set `translated` to False.
#  - If we use `bpy.app.translations.pgettext` with other non-Blender functions, such as `print`.
#      * Use it as a normal function.
#  
#  All translation annotation are started with `TR:`
#  

# The universal translation context prefix for BBP_NG plugin.
CTX_BBP: str = 'BBP'

# The universal translation context prefix for BME module in BBP_NG plugin.
CTX_BBP_BME: str = f'{CTX_BBP}/BME'
CTX_BBP_BME_CATEGORY: str = f'{CTX_BBP_BME}/Category'
CTX_BBP_BME_PROTOTYPE: str = f'{CTX_BBP_BME}/Proto'
def build_prototype_showcase_category_context() -> str:
    """
    Build the context for getting the translation for BME prototype showcase category.
    @return The context for getting translation.
    """
    return CTX_BBP_BME_CATEGORY
def build_prototype_showcase_title_context(identifier: str) -> str:
    """
    Build the context for getting the translation for BME prototype showcase title.
    @param[in] identifier The identifier of this prototype.
    @return The context for getting translation.
    """
    return f'{CTX_BBP_BME_PROTOTYPE}/{identifier}'
def build_prototype_showcase_cfg_context(identifier: str, cfg_index: int) -> str:
    """
    Build the context for getting the translation for BME prototype showcase configuration title or description.
    @param[in] identifier The identifier of this prototype.
    @param[in] cfg_index The index of this configuration in this prototype showcase.
    @return The context for getting translation.
    """
    return f'{CTX_BBP_BME_PROTOTYPE}/{identifier}/[{cfg_index}]'

#endregion

# ##### BEGIN AUTOGENERATED I18N SECTION #####
# NOTE: You can safely move around this auto-generated block (with the begin/end markers!),
#       and edit the translations by hand.
#       Just carefully respect the format of the tuple!

# Tuple of tuples:
# ((msgctxt, msgid), (sources, gen_comments), (lang, translation, (is_fuzzy, comments)), ...)
translations_tuple = ()

translations_dict = {}
for msg in translations_tuple:
    key = msg[0]
    for lang, trans, (is_fuzzy, comments) in msg[2:]:
        if trans and not is_fuzzy:
            translations_dict.setdefault(lang, {})[key] = trans

# ##### END AUTOGENERATED I18N SECTION #####

def register() -> None:
    bpy.app.translations.register(__package__, translations_dict)

def unregister() -> None:
    bpy.app.translations.unregister(__package__)
