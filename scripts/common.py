import os, typing, logging, enum
from pathlib import Path


def get_root_folder() -> Path:
    """
    Get the path to the root folder of this repository.

    :return: The absolute path to the root folder of this repository.
    """
    return Path(__file__).resolve().parent.parent


class AssetKind(enum.StrEnum):
    Icons = 'icons'
    Jsons = 'jsons'
    Meshes = 'meshes'


def get_raw_assets_folder(kind: AssetKind) -> Path:
    """
    Get the path to the raw assets folder of given kind.

    :return: The absolute path to the raw assets folder of given kind.
    """
    return get_root_folder() / 'assets' / str(kind)


def get_plugin_assets_folder(kind: AssetKind) -> Path:
    """
    Get the path to the plugin assets folder of given kind.

    :return: The absolute path to the plugin assets folder of given kind.
    """
    return get_root_folder() / 'bbp_ng' / str(kind)


def setup_logging() -> None:
    """
    Setup uniform style for logging module.
    """
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
