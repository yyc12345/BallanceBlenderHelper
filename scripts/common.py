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


# def relative_to_folder(abs_path: Path, src_parent: Path, dst_parent: Path) -> Path:
#     """
#     Rebase one path to another path.

#     Give a absolute file path and folder path, and compute the relative path of given file to given folder.
#     Then applied the computed relative path to another given folder path.
#     Thus it seems like the file was rebased to from a folder to another folder with keeping the folder hierarchy.

#     For example, given `/path/to/file` and `/path`, it will compute relative path `to/file`.
#     Then it was applied to another folder path `/new` and got `/new/to/file`.

#     :param abs_path: The absolute path to a folder or file.
#     :param src_parent: The absolute path to folder which the `abs_path` will have relative path to.
#     :param dst_parent: The absolute path to folder which the relative path will be applied to.
#     """
#     return dst_parent / (abs_path.relative_to(src_parent))


# def common_file_migrator(from_folder: Path, to_folder: Path, fct_proc_folder: typing.Callable[[str, Path, Path], None],
#                          fct_proc_file: typing.Callable[[str, Path, Path], None]) -> None:
#     """
#     Common file migrator used by some build script.

#     This function receive 2 absolute folder path. `from_folder` indicate the file migrated out,
#     and `to_folder` indicate the file migrated in.
#     `fct_proc_folder` is a function pointer from caller which handle folder migration in detail.
#     `fct_proc_file` is same but handle file migration.

#     `fct_proc_folder` will receive 3 args.
#     First is the name of this folder which can be shown for end user.
#     Second is the source folder and third is expected dest folder.
#     `fct_proc_file` is same, but receive the file path instead.
#     Both of these function pointer should do the migration in detail. This function will only just iterate
#     folder and give essential args and will not do any migration operations such as copying or moving.

#     :param from_folder: The folder need to be migrated.
#     :param to_folder: The folder will be migrated to.
#     :param fct_proc_folder: Folder migration detail handler.
#     :param fct_proc_file: File migration detail handler.
#     """
#     # TODO: If we have Python 3.12, use Path.walk instead of current polyfill.

#     # iterate from_folder folder
#     for root, dirs, files in os.walk(from_folder, topdown=True):
#         root = Path(root)

#         # iterate folders
#         for name in dirs:
#             # prepare handler args
#             src_folder = root / name
#             dst_folder = relative_to_folder(src_folder, from_folder, to_folder)
#             # call handler
#             fct_proc_folder(name, src_folder, dst_folder)

#         # iterate files
#         for name in files:
#             # prepare handler args
#             src_file = root / name
#             dst_file = relative_to_folder(src_file, from_folder, to_folder)
#             # call handler
#             fct_proc_file(name, src_file, dst_file)


def setup_logging() -> None:
    """
    Setup uniform style for logging module.
    """
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
