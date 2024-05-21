import os, typing, fnmatch, shutil

def get_plugin_folder() -> str:
    """
    Get the absolute path to plugin root folder.

    @return The absolute path to plugin root folder.
    """
    return os.path.dirname(os.path.dirname(__file__))

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

def conditional_file_copy(
        from_folder: str, to_folder: str,
        only_copy: tuple[str, ...] | None = None,
        ignore_copy: tuple[str, ...] | None = None,
        recursively: bool = False) -> None:
    """
    The enhanced file tree copy function used in redist script.

    The name of file or folder will be checked by `only_copy` first,
    it it decide this file or folder should be copied, we then check whether
    it is in `ignore_copy`.

    @param from_folder[in] The folder need to be redist.
    @param to_folder[in] The folder will be placed redist files.
    @param only_copy[in] An Unix style pathname pattern tuple to instruct which files or folders should be copied, 
    or None if we want to copy every files and folders.
    @param ignore_copy[in] An Unix style pathname pattern tuple to instruct which files or folders should not be copied,
    or None if we want to copy every files and folders.
    @param recursively[in] Whether recursively copy sub-folders and their files.
    """
    # build a helper functions
    def is_need_copy(checked_filename: str) -> bool:
        # if only_copy enabled, check it.
        # if no only_copy, pass the check because file should be copied in default.
        if only_copy is not None:
            for only_copy_item in only_copy:
                # matched, should copy it, break this for syntax
                if fnmatch.fnmatch(checked_filename, only_copy_item):
                    break
            else:
                # no matched item, this entry should not be copied.
                return False
            
        if ignore_copy is not None:
            # check whether given name is in ignore_copy
            for ignore_copy_item in ignore_copy:
                # matched, should not be copied
                if fnmatch.fnmatch(checked_filename, only_copy_item):
                    return False
            # no matched, copy it
            return True
        else:
            # no ignore_copy, directly copy it
            return True

    # iterate from_folder folder
    for root, dirs, files in os.walk(from_folder, topdown = True):
        # create self
        src_self: str = root
        dst_self: str = relative_to_folder(src_self, from_folder, to_folder)
        print(f'Creating: {src_self} -> {dst_self}')
        os.makedirs(dst_self, exist_ok=True)

        # iterate files
        for name in files:
            # get source file path
            src_file: str = os.path.join(root, name)
            # check whether copy it
            if not is_need_copy(src_file):
                continue
            # build dst path and copy it
            dst_file: str = relative_to_folder(src_file, from_folder, to_folder)
            print(f'Copying: {src_file} -> {dst_file}')
            shutil.copy(src_file, dst_file)
            
        # iterate folders when recursively flag enabled
        # if recursively:
        #     for name in dirs:
        #         # get source folder path
        #         src_folder: str = os.path.join(root, name)
        #         # build dst path and create it
        #         dst_folder: str = relative_to_folder(src_folder, from_folder, to_folder)
        #         print(f'Copying: {src_folder} -> {dst_folder}')
        #         os.makedirs(dst_folder, exist_ok=True)

        # if we don't have recursively flag, 
        # we should exit at the end of first loop
        if not recursively:
            break

