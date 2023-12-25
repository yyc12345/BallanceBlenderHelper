import os
import common
import PIL, PIL.Image

# the config for thumbnail
g_ThumbnailSize: int = 16

def resize_image(src_file: str, dst_file: str) -> None:
    # open image
    src_image: PIL.Image.Image = PIL.Image.open(src_file)
    # create thumbnail
    src_image.thumbnail((g_ThumbnailSize, g_ThumbnailSize))
    # save to new file
    src_image.save(dst_file)

def create_thumbnails() -> None:
    # get folder path
    root_folder: str = os.path.dirname(os.path.dirname(__file__))

    # prepare handler
    def folder_handler(src_folder: str, dst_folder: str) -> None:
        # just create folder
        print(f'Creating Folder: {src_folder} -> {dst_folder}')
        os.makedirs(dst_folder, exist_ok = True)
    def file_handler(src_file: str, dst_file: str) -> None:
        # skip non-image
        if not src_file.endswith('.png'): return
        # call thumbnail func
        print(f'Processing Thumbnail: {src_file} -> {dst_file}')
        resize_image(src_file, dst_file)

    # call common processor
    common.common_file_migrator(
        os.path.join(root_folder, 'raw_icons'),
        os.path.join(root_folder, 'icons'),
        folder_handler,
        file_handler
    )

    print('Done.')

if __name__ == '__main__':
    create_thumbnails()
