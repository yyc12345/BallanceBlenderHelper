import shutil, logging
import common
from common import AssetKind


def build_meshes() -> None:
    raw_meshes_dir = common.get_raw_assets_folder(AssetKind.Meshes)
    plg_meshes_dir = common.get_plugin_assets_folder(AssetKind.Meshes)

    for raw_ph_file in raw_meshes_dir.glob('*.ph'):
        # Skip non-file.
        if not raw_ph_file.is_file():
            continue

        # Build final path
        plg_ph_file = plg_meshes_dir / raw_ph_file.relative_to(raw_meshes_dir)

        # Show message
        logging.info(f'Copying {raw_ph_file} -> {plg_ph_file}')

        # Copy placeholder
        shutil.copyfile(raw_ph_file, plg_ph_file)


if __name__ == '__main__':
    common.setup_logging()
    build_meshes()
