import os, json
import common

def compress_json(src_file: str, dst_file: str) -> None:
    with open(src_file, 'r', encoding = 'utf-8') as fr:
        with open(dst_file, 'w', encoding = 'utf-8') as fw:
            json.dump(
                json.load(fr),  # load from src file
                fw,
                indent = None,  # no indent. the most narrow style.
                separators = (',', ':'),    # also for narrow style.
                sort_keys = False,  # do not sort key
            )

def create_compressed_jsons() -> None:
    # get folder path
    root_folder: str = common.get_plugin_folder()

    # prepare handler
    def folder_handler(src_folder: str, dst_folder: str) -> None:
        # just create folder
        print(f'Creating Folder: {src_folder} -> {dst_folder}')
        os.makedirs(dst_folder, exist_ok = True)
    def file_handler(src_file: str, dst_file: str) -> None:
        # skip non-json
        if not src_file.endswith('.json'): return
        # call compress func
        print(f'Processing Json: {src_file} -> {dst_file}')
        compress_json(src_file, dst_file)

    # call common processor
    common.common_file_migrator(
        os.path.join(root_folder, 'raw_jsons'),
        os.path.join(root_folder, 'jsons'),
        folder_handler,
        file_handler
    )

    print('Done.')

if __name__ == '__main__':
    create_compressed_jsons()

