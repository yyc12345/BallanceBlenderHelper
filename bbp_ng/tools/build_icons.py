import os
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

def relative_to_folder(abs_path: str, src_parent: str, dst_parent: str) -> str:
    return os.path.join(dst_parent, os.path.relpath(abs_path, src_parent))

def create_thumbnails() -> None:
    # get folder path
    root_folder: str = os.path.dirname(os.path.dirname(__file__))
    raw_icons_folder: str = os.path.join(root_folder, 'raw_icons')
    icons_folder: str = os.path.join(root_folder, 'icons')

    # iterate raw icons folder
    for root, dirs, files in os.walk(raw_icons_folder, topdown = True):
        # iterate folder and create it in dest folder
        for name in dirs:
            src_folder: str = os.path.join(root, name)
            dst_folder: str = relative_to_folder(src_folder, raw_icons_folder, icons_folder)
            print(f'Creating Folder: {src_folder} -> {dst_folder}')
            os.makedirs(dst_folder, exist_ok = True)
        for name in files:
            if not name.endswith('.png'): continue  # skip non-image
            src_file: str = os.path.join(root, name)
            dst_file: str = relative_to_folder(src_file, raw_icons_folder, icons_folder)
            print(f'Processing Thumbnail: {src_file} -> {dst_file}')
            resize_image(src_file, dst_file)

    print('Done.')

if __name__ == '__main__':
    create_thumbnails()
