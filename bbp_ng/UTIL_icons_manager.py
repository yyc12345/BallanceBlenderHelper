import bpy, bpy.utils.previews
import os, enum, typing

class BlenderPresetIcons(enum.Enum):
    Info = 'INFO'
    Warning = 'ERROR'
    Error = 'CANCEL'

#region Custom Icons Helper

_g_SupportedImageExts: set[str] = (
    '.png',
)

_g_IconsManager: bpy.utils.previews.ImagePreviewCollection | None = None

_g_EmptyIcon: int = 0
_g_IconPrefix: str = "BlcBldPlg_"

_g_FloorIconsMap: dict[str, int] = {}
_g_FloorIconPrefix: str = _g_IconPrefix + 'Floor_'
_g_ElementIconsMap: dict[str, int] = {}
_g_ElementIconPrefix: str = _g_IconPrefix + 'Element_'
_g_GroupIconsMap: dict[str, int] = {}
_g_GroupIconPrefix: str = _g_IconPrefix + 'Group_'

def _iterate_folder_images(folder: str) -> typing.Iterator[tuple[str, str]]:
    for name in os.listdir(folder):
        # check whether it is file
        filepath: str = os.path.join(folder, name)
        if os.path.isfile(filepath):
            # check file exts
            (root, ext) = os.path.splitext(name)
            if ext.lower() in _g_SupportedImageExts:
                yield (filepath, root)

def _load_image_folder(
        folder: str, 
        loader: bpy.utils.previews.ImagePreviewCollection, 
        container: dict[str, int],
        name_prefix: str) -> None:
    # iterate folder
    for (filepath, filename_no_ext) in _iterate_folder_images(folder):
        # generate name for unique
        icon_name: str = name_prefix + filename_no_ext
        # load it
        loader.load(icon_name, filepath, 'IMAGE')
        # add into list. use plain name (not the unique name)
        container[filename_no_ext] = loader[icon_name].icon_id

#endregion

#region Custom Icons Visitors

def get_empty_icon() -> int:
    return _g_EmptyIcon

def get_floor_icon(name: str) -> int | None:
    return _g_FloorIconsMap.get(name, None)

def get_element_icon(name: str) -> int | None:
    return _g_ElementIconsMap.get(name, None)

def get_group_icon(name: str) -> int | None:
    return _g_GroupIconsMap.get(name, None)

#endregion

def register():
    global _g_IconsManager
    global _g_EmptyIcon
    global _g_FloorIconsMap, _g_ElementIconsMap, _g_GroupIconsMap

    # create preview collection and get icon folder
    icons_folder: str = os.path.join(os.path.dirname(__file__), "icons")
    _g_IconsManager = bpy.utils.previews.new()

    # load empty icon as default fallback
    empty_icon_name: str = _g_IconPrefix + 'EmptyIcon'
    _g_IconsManager.load(empty_icon_name, os.path.join(icons_folder, "Empty.png"), 'IMAGE')
    _g_EmptyIcon = _g_IconsManager[empty_icon_name].icon_id

    # load floor, element, group icon
    _load_image_folder(
        os.path.join(icons_folder, 'floor'),
        _g_IconsManager,
        _g_FloorIconsMap,
        _g_FloorIconPrefix
    )
    _load_image_folder(
        os.path.join(icons_folder, 'element'),
        _g_IconsManager,
        _g_ElementIconsMap,
        _g_ElementIconPrefix
    )
    _load_image_folder(
        os.path.join(icons_folder, 'group'),
        _g_IconsManager,
        _g_GroupIconsMap,
        _g_GroupIconPrefix
    )

def unregister():
    global _g_IconsManager
    global _g_EmptyIcon
    global _g_FloorIconsMap, _g_ElementIconsMap, _g_GroupIconsMap

    bpy.utils.previews.remove(_g_IconsManager)
    _g_IconsManager = None

    _g_FloorIconsMap.clear()
    _g_ElementIconsMap.clear()
    _g_GroupIconsMap.clear()
