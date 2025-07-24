import json, logging, ast, typing
import common, bme
from common import AssetKind
import pydantic

#region Assistant Checker

# TODO:
# If possible, following check should be done.
# They are not done now because they are so complex to implement.
# - The reference to variables and functions in programmable fields.
# - The return type of prorgammable fields.
# - Texture name referred in the programmable field in Face.
# - In instance, passed params to instance is fulfilled.


def _try_add(entries: set[str], entry: str) -> bool:
    if entry in entries:
        return False
    else:
        entries.add(entry)
        return True


def _check_programmable_field(probe: str) -> None:
    # TODO:
    # If possible, allow checking the reference to variables and function,
    # to make sure the statement must can be executed.
    try:
        ast.parse(probe)
    except SyntaxError:
        logging.error(f'String {probe} may not be a valid Python statement which is not suit for programmable field.')


def _check_showcase_icon(icon_name: str) -> None:
    icon_path = common.get_raw_assets_folder(AssetKind.Icons) / 'bme' / f'{icon_name}.png'
    if not icon_path.is_file():
        logging.error(f'Showcase icon value {icon_name} may be invalid.')


#endregion

#region Core Validator


def _pre_validate_prototype(prototype: bme.Prototype, identifiers: set[str]) -> None:
    identifier = prototype.identifier

    # Show status
    logging.info(f'Pre-checking prototype {identifier}')

    # Check identifier and add it.
    if not _try_add(identifiers, identifier):
        logging.error(f'Identifier {identifier} is already registered.')


def _validate_showcase(showcase: bme.Showcase, variables: set[str]) -> None:
    # I18N Module Req:
    # The title of showcase should not be empty
    if len(showcase.title) == 0:
        logging.error('The title of showcase should not be empty.')

    # Check icon name
    _check_showcase_icon(showcase.icon)

    # Check configuration list.
    for cfg in showcase.cfgs:
        # Check name
        field_name = cfg.field
        if not _try_add(variables, field_name):
            logging.error(f'Field {field_name} is already registered.')

        # I18N Module Req:
        # The title and desc of cfg should not be empty.
        # And they are should not be the same string.
        if len(cfg.title) == 0:
            logging.error('The title of showcase configuration entry should not be empty.')
        if len(cfg.desc) == 0:
            logging.error('The description of showcase configuration entry should not be empty.')
        if cfg.title == cfg.desc:
            logging.error('The title of showcase configuration entry and its description should not be same string.')

        # Check programmable field
        _check_programmable_field(cfg.default)


def _validate_params(params: list[bme.Param], variables: set[str]) -> None:
    for param in params:
        # Check name
        field_name = param.field
        if not _try_add(variables, field_name):
            logging.error(f'Field {field_name} is already registered.')

        # Check programmable fields
        _check_programmable_field(param.data)


def _validate_vars(vars: list[bme.Var], variables: set[str]) -> None:
    for var in vars:
        # Check name
        field_name = var.field
        if not _try_add(variables, field_name):
            logging.error(f'Field {field_name} is already registered.')

        # Check programmable fields
        _check_programmable_field(var.data)


def _validate_vertices(vertices: list[bme.Vertex]) -> None:
    for vertex in vertices:
        # Check programmable fields
        _check_programmable_field(vertex.skip)
        _check_programmable_field(vertex.data)


def _validate_faces(faces: list[bme.Face], vertices_count: int) -> None:
    for face in faces:
        # The index referred in indices should not be exceed the max value of vertices count.
        for index in face.indices:
            if index >= vertices_count:
                logging.error(f'Index {index} is out of vertices range.')

        # The size of uvs list and normals list (if existing)
        # should be equal to the size of indices list.
        edges = len(face.indices)
        if len(face.uvs) != edges:
            logging.error(f'The size of UVs list is not matched with indices.')
        if face.normals is not None and len(face.normals) != edges:
            logging.error(f'The size of Normals list is not matched with indices.')

        # Check programmable fields
        _check_programmable_field(face.skip)
        _check_programmable_field(face.texture)
        for uv in face.uvs:
            _check_programmable_field(uv)
        if face.normals is not None:
            for normal in face.normals:
                _check_programmable_field(normal)


def _validate_instances(instances: list[bme.Instance], identifiers: set[str]) -> None:
    for instance in instances:
        # The reference of identifier should be existing.
        referred_identifier = instance.identifier
        if referred_identifier not in identifiers:
            logging.error(f'The identifier {referred_identifier} referred in instance is not existing.')

        # Check programmable fields
        _check_programmable_field(instance.skip)
        for v in instance.params.values():
            _check_programmable_field(v)
        _check_programmable_field(instance.transform)


def _validate_prototype(prototype: bme.Prototype, identifiers: set[str]) -> None:
    # Show status
    logging.info(f'Checking prototype {prototype.identifier}')

    # A set of all variable names registered in this prototypes
    variables: set[str] = set()

    # Check fields
    if prototype.showcase is not None:
        _validate_showcase(prototype.showcase, variables)
    _validate_params(prototype.params, variables)
    _check_programmable_field(prototype.skip)
    _validate_vars(prototype.vars, identifiers)
    _validate_vertices(prototype.vertices)
    _validate_faces(prototype.faces, len(prototype.vertices))
    _validate_instances(prototype.instances, identifiers)


#endregion


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

    # Pre-validate first to collect identifier and check identifier first.
    # We need collect it first because "instances" field need it to check the validation of identifier.
    identifiers: set[str] = set()
    for prototype in prototypes:
        _pre_validate_prototype(prototype, identifiers)

    # Start custom validation
    for prototype in prototypes:
        _validate_prototype(prototype, identifiers)


if __name__ == '__main__':
    common.setup_logging()
    validate_jsons()
