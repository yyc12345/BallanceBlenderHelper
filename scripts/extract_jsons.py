import json, logging, typing, itertools
from pathlib import Path
import common, bme
from common import AssetKind
import pydantic, polib

## YYC MARK:
#  This translation context string prefix is cpoied from UTIL_translation.py.
#  If the context string of translation changed, please synchronize it.

CTX_TRANSLATION: str = 'BBP/BME'


def _extract_prototype(prototype: bme.Prototype) -> typing.Iterator[polib.POEntry]:
    identifier = prototype.identifier
    showcase = prototype.showcase

    # Show message
    logging.info(f'Extracting prototype {identifier}')

    # Extract showcase
    if showcase is None:
        return

    # Extract showcase title
    yield polib.POEntry(msgid=showcase.title, msgstr='', msgctxt=f'{CTX_TRANSLATION}/{identifier}')
    # Extract showcase entries
    for i, cfg in enumerate(showcase.cfgs):
        # extract title and description
        yield polib.POEntry(msgid=cfg.title, msgstr='', msgctxt=f'{CTX_TRANSLATION}/{identifier}/[{i}]')
        yield polib.POEntry(msgid=cfg.desc, msgstr='', msgctxt=f'{CTX_TRANSLATION}/{identifier}/[{i}]')


def _extract_json(json_file: Path) -> typing.Iterator[polib.POEntry]:
    # Show message
    logging.info(f'Extracting file {json_file}')

    try:
        # Read file and convert it into BME struct.
        with open(json_file, 'r', encoding='utf-8') as f:
            document = json.load(f)
        prototypes = bme.Prototypes.model_validate(document)
        # Extract translation
        return itertools.chain.from_iterable(_extract_prototype(prototype) for prototype in prototypes.root)
    except json.JSONDecodeError:
        logging.error(f'Can not extract translation from {json_file} due to JSON error. Please validate it first.')
    except pydantic.ValidationError:
        logging.error(f'Can not extract translation from {json_file} due to struct error. Please validate it first.')

    # Output nothing
    return itertools.chain.from_iterable(())


def extract_jsons() -> None:
    raw_jsons_dir = common.get_raw_assets_folder(AssetKind.Jsons)

    # Create POT content
    po = polib.POFile()
    po.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'you@example.com',
        'POT-Creation-Date': 'YEAR-MO-DA HO:MI+ZONE',
        'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
        'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
        'Language-Team': 'LANGUAGE <LL@li.org>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'X-Generator': 'polib',
    }

    # Iterate all prototypes and add into POT
    for raw_json_file in raw_jsons_dir.glob('*.json'):
        # Skip non-file.
        if not raw_json_file.is_file():
            continue
        # Extract json and append it.
        po.extend(_extract_json(raw_json_file))

    # Write into POT file
    pot_file = common.get_root_folder() / 'i18n' / 'bme.pot'
    logging.info(f'Saving POT into {pot_file}')
    po.save(str(pot_file))


if __name__ == '__main__':
    common.setup_logging()
    extract_jsons()
