import logging
from pathlib import Path
import common
import PIL, PIL.Image

# the config for thumbnail
THUMBNAIL_SIZE: int = 16

class ThumbnailBuilder():

    def __init__(self):
        pass

    def build_thumbnails(self) -> None:
        # get folder path
        root_folder = common.get_root_folder()

        # prepare handler
        def folder_handler(rel_name: str, src_folder: Path, dst_folder: Path) -> None:
            # just create folder
            logging.info(f'Creating Folder: {src_folder} -> {dst_folder}')
            dst_folder.mkdir(parents=False, exist_ok=True)
        def file_handler(rel_name: str, src_file: Path, dst_file: Path) -> None:
            # skip non-image
            if src_file.suffix != '.png': return
            # call thumbnail func
            logging.info(f'Building Thumbnail: {src_file} -> {dst_file}')
            self.__resize_image(src_file, dst_file)

        # call common processor
        common.common_file_migrator(
            root_folder / 'raw_icons',
            root_folder / 'icons',
            folder_handler,
            file_handler
        )

        logging.info('Building thumbnail done.')

    def __resize_image(self, src_file: Path, dst_file: Path) -> None:
        # open image
        src_image: PIL.Image.Image = PIL.Image.open(src_file)
        # create thumbnail
        src_image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        # save to new file
        src_image.save(dst_file)

if __name__ == '__main__':
    common.setup_logging()
    thumbnail_builder = ThumbnailBuilder()
    thumbnail_builder.build_thumbnails()
