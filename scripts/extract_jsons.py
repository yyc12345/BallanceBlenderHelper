import logging, typing, itertools
from pathlib import Path
import common, bme
from common import AssetKind
import pydantic, polib, json5

## YYC MARK:
#  This translation context string prefix is cpoied from UTIL_translation.py.
#  If the context string of translation changed, please synchronize it.

CTX_TRANSLATION: str = 'BBP/BME'
CTX_PROTOTYPE: str = f'{CTX_TRANSLATION}/Proto'
CTX_CATEGORY: str = f'{CTX_TRANSLATION}/Category'


class JsonsExtractor:

    po: polib.POFile
    """Extracted PO file"""
    categories: set[str]
    """Set for removing duplicated category names"""

    def __init__(self) -> None:
        # create po file
        self.po = polib.POFile()
        self.po.metadata = {
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
        # create category set
        self.categories = set()

    def __extract_prototype(self, prototype: bme.Prototype) -> None:
        identifier = prototype.identifier
        showcase = prototype.showcase

        # Show message
        logging.info(f'Extracting prototype {identifier}')

        # Extract showcase
        if showcase is None:
            return

        # Extract showcase title
        self.po.append(polib.POEntry(msgid=showcase.title, msgstr='', msgctxt=f'{CTX_PROTOTYPE}/{identifier}'))
        # extract showcase category
        if showcase.category not in self.categories:
            self.po.append(polib.POEntry(msgid=showcase.category, msgstr='', msgctxt=CTX_CATEGORY))
            self.categories.add(showcase.category)
        # Extract showcase entries
        for i, cfg in enumerate(showcase.cfgs):
            # extract title and description
            self.po.append(polib.POEntry(msgid=cfg.title, msgstr='', msgctxt=f'{CTX_PROTOTYPE}/{identifier}/[{i}]'))
            self.po.append(polib.POEntry(msgid=cfg.desc, msgstr='', msgctxt=f'{CTX_PROTOTYPE}/{identifier}/[{i}]'))

    def __extract_json(self, json_file: Path) -> None:
        # Show message
        logging.info(f'Extracting file {json_file}')

        try:
            # Read file and convert it into BME struct.
            with open(json_file, 'r', encoding='utf-8') as f:
                document = json5.load(f)
            prototypes = bme.Prototypes.model_validate(document)
            # Extract translation
            for prototype in prototypes.root:
                self.__extract_prototype(prototype)
        except pydantic.ValidationError:
            logging.error(
                f'Can not extract translation from {json_file} due to struct error. Please validate it first.')
        except (ValueError, UnicodeDecodeError):
            logging.error(f'Can not extract translation from {json_file} due to JSON5 error. Please validate it first.')

    def extract_jsons(self) -> None:
        raw_jsons_dir = common.get_raw_assets_folder(AssetKind.Jsons)

        # Iterate all prototypes and add into POT
        for raw_json_file in raw_jsons_dir.glob('*.json5'):
            # Skip non-file.
            if not raw_json_file.is_file():
                continue
            # Extract json
            self.__extract_json(raw_json_file)

    def save(self) -> None:
        """Save extracted POT file into correct path"""
        pot_file = common.get_root_folder() / 'i18n' / 'bme.pot'
        logging.info(f'Saving POT into {pot_file}')
        self.po.save(str(pot_file))


if __name__ == '__main__':
    common.setup_logging()
    extractor = JsonsExtractor()
    extractor.extract_jsons()
    extractor.save()
