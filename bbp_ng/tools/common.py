import os, typing

def relative_to_folder(abs_path: str, src_parent: str, dst_parent: str) -> str:
    """
    Rebase one path to another path.

    Give a absolute file path and folder path, and compute the relative path of given file to given folder.
    Then applied the computed relative path to another given folder path.
    Thus it seems like the file was rebased to from a folder to another folder with keeping the folder hierarchy.

    For example, given `/path/to/file` and `/path`, it will compute relative path `to/file`.
    Then it was applied to another folder path `/new` and got `/new/to/file`.

    @param abs_path[in] The absolute path to a folder or file.
    @param src_parent[in] The absolute path to folder which the `abs_path` will have relative path to.
    @param dst_parent[in] The absolute path to folder which the relative path will be applied to.
    """
    return os.path.join(dst_parent, os.path.relpath(abs_path, src_parent))

def common_file_migrator(
        from_folder: str, to_folder: str,
        fct_proc_folder: typing.Callable[[str, str], None],
        fct_proc_file: typing.Callable[[str, str], None]) -> None:
    """
    Common file migrator used by some build script.

    This function receive 2 absolute folder path. `from_folder` indicate the file migrated out,
    and `to_folder` indicate the file migrated in.
    `fct_proc_folder` is a function pointer from caller which handle folder migration in detail.
    `fct_proc_file` is same but handle file migration.

    `fct_proc_folder` will receive 2 args. First is the source folder. Second is expected dest folder.
    `fct_proc_file` is same, but receive the file path instead.
    Both of these function pointer should do the migration in detail. This function will only just iterate
    folder and give essential args and will not do any migration operations such as copying or moving.

    @param from_folder[in] The folder need to be migrated.
    @param to_folder[in] The folder will be migrated to.
    @param fct_proc_folder[in] Folder migration detail handler.
    @param fct_proc_file[in] File migration detail handler.
    """
    # iterate from_folder folder
    for root, dirs, files in os.walk(from_folder, topdown = True):
        # iterate folders
        for name in dirs:
            # prepare handler args
            src_folder: str = os.path.join(root, name)
            dst_folder: str = relative_to_folder(src_folder, from_folder, to_folder)
            # call handler
            fct_proc_folder(src_folder, dst_folder)
        # iterate files
        for name in files:
            # prepare handler args
            src_file: str = os.path.join(root, name)
            dst_file: str = relative_to_folder(src_file, from_folder, to_folder)
            # call handler
            fct_proc_file(src_file, dst_file)
