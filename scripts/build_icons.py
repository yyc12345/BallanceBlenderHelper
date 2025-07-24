import logging, os
from pathlib import Path
import common
from common import AssetKind
import PIL, PIL.Image

# The HW size of thumbnail
THUMBNAIL_SIZE: int = 16


def _create_thumbnail(src_file: Path, dst_file: Path) -> None:
    # open image
    src_image: PIL.Image.Image = PIL.Image.open(src_file)
    # create thumbnail
    src_image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
    # save to new file
    src_image.save(dst_file)


def build_icons() -> None:
    raw_icons_dir = common.get_raw_assets_folder(AssetKind.Icons)
    plg_icons_dir = common.get_plugin_assets_folder(AssetKind.Icons)

    # TODO: If we have Python 3.12, use Path.walk instead of current polyfill.

    # Icon assets has subdirectory, so we need use another way to process.
    for root, dirs, files in os.walk(raw_icons_dir):
        root = Path(root)

        # Iterate folders
        for name in dirs:
            # Fetch directory path
            raw_icon_subdir = root / name
            plg_icon_subdir = plg_icons_dir / raw_icon_subdir.relative_to(raw_icons_dir)
            # Show message
            logging.info(f'Creating Folder: {raw_icon_subdir} -> {plg_icon_subdir}')
            # Create directory
            plg_icon_subdir.mkdir(parents=True, exist_ok=True)

        # Iterate files
        for name in files:
            # Fetch file path
            raw_icon_file = root / name
            plg_icon_file = plg_icons_dir / raw_icon_file.relative_to(raw_icons_dir)
            # Show message
            logging.info(f'Building Thumbnail: {raw_icon_file} -> {plg_icon_file}')
            # Create thumbnail
            _create_thumbnail(raw_icon_file, plg_icon_file)


if __name__ == '__main__':
    common.setup_logging()
    build_icons()
