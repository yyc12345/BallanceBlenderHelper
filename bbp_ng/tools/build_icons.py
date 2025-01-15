import os
import bme_utils
import common
import PIL, PIL.Image

# the config for thumbnail
g_ThumbnailSize: int = 16

class ThumbnailCreator():

    __mReporter: bme_utils.Reporter

    def __init__(self):
        self.__mReporter = bme_utils.Reporter()

    def run(self) -> None:
        self.__create_thumbnails()

    def __create_thumbnails(self) -> None:
        # get folder path
        root_folder: str = common.get_plugin_folder()

        # prepare handler
        def folder_handler(rel_name: str, src_folder: str, dst_folder: str) -> None:
            # just create folder
            self.__mReporter.info(f'Creating Folder: {src_folder} -> {dst_folder}')
            os.makedirs(dst_folder, exist_ok = True)
        def file_handler(rel_name: str, src_file: str, dst_file: str) -> None:
            # skip non-image
            if not src_file.endswith('.png'): return
            # call thumbnail func
            self.__mReporter.info(f'Processing Thumbnail: {src_file} -> {dst_file}')
            self.__resize_image(src_file, dst_file)

        # call common processor
        common.common_file_migrator(
            os.path.join(root_folder, 'raw_icons'),
            os.path.join(root_folder, 'icons'),
            folder_handler,
            file_handler
        )

        self.__mReporter.info('Building thumbnail done.')

    def __resize_image(self, src_file: str, dst_file: str) -> None:
        # open image
        src_image: PIL.Image.Image = PIL.Image.open(src_file)
        # create thumbnail
        src_image.thumbnail((g_ThumbnailSize, g_ThumbnailSize))
        # save to new file
        src_image.save(dst_file)

if __name__ == '__main__':
    thumbnail_creator = ThumbnailCreator()
    thumbnail_creator.run()
