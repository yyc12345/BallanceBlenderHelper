import json, logging, ast, typing
import common, bme
from common import AssetKind
import pydantic

#region Assistant Validator

def _validate_programmable_field(probe: str) -> None:
    try:
        ast.parse(probe)
    except SyntaxError:
        logging.error(f'String {probe} may not be a valid Python statement which is not suit for programmable field.')


def _validate_showcase_icon(icon_name: str) -> None:
    icon_path = common.get_raw_assets_folder(AssetKind.Icons) / 'bme' / f'{icon_name}.png'
    if not icon_path.is_file():
        logging.error(f'Icon value {icon_name} may not be valid because it do not existing.')

#endregion

#region Core Validator

def _validate_prototype(prototype: bme.Prototype) -> None:
    pass


#endregion

# 把提取JSON翻译的要求写入到验证中：
# - Showcase::Cfgs::Title或Desc不能为空。
# - Showcase::Cfgs::Title和Showcase::Cfgs::Desc不能重复


def validate_jsons() -> None:
    raw_jsons_dir = common.get_raw_assets_folder(AssetKind.Jsons)

    # Load all prototypes and check their basic format
    prototypes: list[bme.Prototype] = []
    for raw_json_file in raw_jsons_dir.glob('*.json'):
        # Skip non-file
        if not raw_json_file.is_file():
            continue

        # Show info
        logging.info(f'Loading {raw_json_file}')

        # Load prototypes
        try:
            with open(raw_json_file, 'r', encoding='utf-8') as f:
                docuement = json.load(f)
                file_prototypes = bme.Prototypes.model_validate(docuement)
        except json.JSONDecodeError as e:
            logging.error(f'File {raw_json_file} is not a valid JSON file. Reason: {e}')
        except pydantic.ValidationError as e:
            logging.error(f'JSON file {raw_json_file} lose essential fields. Detail: {e}')

        # Append all prototypes into list
        prototypes += file_prototypes.root

    # Collect identifier and check identifier first.
    identifiers: set[str] = set()
    for prototype in prototypes:
        identifier = prototype.identifier
        if prototype.identifier in identifiers:
            logging.error(f'Identifier {identifier} is registered more than once.')
        else:
            identifiers.add(identifier)

    # Start custom validation
    for protype in prototypes:
        _validate_prototype(prototype)

if __name__ == '__main__':
    common.setup_logging()
    validate_jsons()
