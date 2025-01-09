import os, json, typing
import bme_relatives, simple_po
import common

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

class JsonCompressor():

    __mReporter: bme_relatives.Reporter
    __mPoWriter: simple_po.PoWriter
    __mValidator: bme_relatives.BMEValidator
    __mExtractor: bme_relatives.BMEExtractor

    def __init__(self):
        self.__mReporter = bme_relatives.Reporter()
        self.__mPoWriter = simple_po.PoWriter(
            os.path.join(common.get_plugin_folder(), 'i18n', 'bme.pot'), 
            'BME Prototypes'
        )
        self.__mValidator = bme_relatives.BMEValidator(self.__mReporter)
        self.__mExtractor = bme_relatives.BMEExtractor(self.__mPoWriter)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self) -> None:
        self.__mPoWriter.close()

    def run(self) -> None:
        self.__compress_jsons()

    def __compress_jsons(self) -> None:
        # get folder path
        root_folder: str = common.get_plugin_folder()

        # prepare handler
        def folder_handler(src_folder: str, dst_folder: str) -> None:
            # just create folder
            self.__mReporter.info(f'Creating Folder: {src_folder} -> {dst_folder}')
            os.makedirs(dst_folder, exist_ok = True)
        def file_handler(src_file: str, dst_file: str) -> None:
            # skip non-json
            if not src_file.endswith('.json'): return
            # call compress func
            self.__mReporter.info(f'Processing Json: {src_file} -> {dst_file}')
            self.__compress_json(src_file, dst_file)

        # call common processor
        common.common_file_migrator(
            os.path.join(root_folder, 'raw_jsons'),
            os.path.join(root_folder, 'jsons'),
            folder_handler,
            file_handler
        )

        self.__mReporter.info('Done.')

    def __compress_json(self, src_file: str, dst_file: str) -> None:
        # load data first
        loaded_prototypes: typing.Any
        with open(src_file, 'r', encoding = 'utf-8') as fr:
            loaded_prototypes = json.load(fr)

        # validate loaded data
        self.__mValidator.validate(os.path.basename(src_file), loaded_prototypes)

        # extract translation
        self.__mExtractor.extract(os.path.basename(src_file), loaded_prototypes)

        # save result
        with open(dst_file, 'w', encoding = 'utf-8') as fw:
            json.dump(
                loaded_prototypes,  # loaded data
                fw,
                indent = None,  # no indent. the most narrow style.
                separators = (',', ':'),    # also for narrow style.
                sort_keys = False,  # do not sort key
            )


if __name__ == '__main__':
    with JsonCompressor() as json_compressor:
        json_compressor.run()
