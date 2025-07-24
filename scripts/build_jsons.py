import json, logging
from pathlib import Path
import common
from common import AssetKind


def _compress_json(src_file: Path, dst_file: Path) -> None:
    # load data first
    with open(src_file, 'r', encoding='utf-8') as f:
        loaded_prototypes = json.load(f)

    # save result with compress config
    with open(dst_file, 'w', encoding='utf-8') as f:
        json.dump(
            loaded_prototypes,  # loaded data
            f,
            indent=None,  # no indent. the most narrow style.
            separators=(',', ':'),  # also for narrow style.
            sort_keys=False,  # do not sort key
        )


def build_jsons() -> None:
    raw_jsons_dir = common.get_raw_assets_folder(AssetKind.Jsons)
    plg_jsons_dir = common.get_plugin_assets_folder(AssetKind.Jsons)

    for raw_json_file in raw_jsons_dir.glob('*.json'):
        # Skip non-file.
        if not raw_json_file.is_file():
            continue

        # Build final path
        plg_json_file = plg_jsons_dir / raw_json_file.relative_to(raw_jsons_dir)

        # Show message
        logging.info(f'Compressing {raw_json_file} -> {plg_json_file}')

        # Compress json
        _compress_json(raw_json_file, plg_json_file)


if __name__ == '__main__':
    common.setup_logging()
    build_jsons()
