import enum
import json
import logging
import ast
from typing import Optional, Self
from pydantic import BaseModel, RootModel, Field, model_validator, ValidationError
import common


def validate_programmable_str(probe: str) -> None:
    try:
        ast.parse(probe)
    except SyntaxError:
        raise ValueError(
            f'String {probe} may not be a valid Python statement which is not suit for programmable field.')


class ShowcaseType(enum.StrEnum):
    Nothing = 'none'
    Floor = 'floor'
    Rail = 'Rail'
    Wood = 'wood'


class ShowcaseCfgType(enum.StrEnum):
    Float = 'float'
    Int = 'int'
    Bool = 'bool'
    Face = 'face'


class ShowcaseCfg(BaseModel):
    field: str = Field(frozen=True, strict=True)
    type: ShowcaseCfgType = Field(frozen=True)
    title: str = Field(frozen=True, strict=True)
    desc: str = Field(frozen=True, strict=True)
    default: str = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.default)
        return self


class Showcase(BaseModel):
    title: str = Field(frozen=True, strict=True)
    icon: str = Field(frozen=True, strict=True)
    type: ShowcaseType = Field(frozen=True)
    cfgs: list[ShowcaseCfg] = Field(frozen=True, strict=True)


class Param(BaseModel):
    field: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.data)
        return self


class Var(BaseModel):
    field: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.data)
        return self


class Vertex(BaseModel):
    skip: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.skip)
        validate_programmable_str(self.data)
        return self


class Face(BaseModel):
    skip: str = Field(frozen=True, strict=True)
    texture: str = Field(frozen=True, strict=True)
    indices: list[int] = Field(frozen=True, strict=True)
    uvs: list[str] = Field(frozen=True, strict=True)
    normals: Optional[list[str]] = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_count(self) -> Self:
        expected_count = len(self.indices)
        if len(self.uvs) != expected_count:
            raise ValueError('The length of uv array is not matched with indices.')
        if (self.normals is not None) and (len(self.normals) != expected_count):
            raise ValueError('The length of normal array is not matched with indices.')
        return self

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.skip)
        validate_programmable_str(self.texture)
        for i in self.uvs:
            validate_programmable_str(i)
        if self.normals is not None:
            for i in self.normals:
                validate_programmable_str(i)
        return self


class Instance(BaseModel):
    identifier: str = Field(frozen=True, strict=True)
    skip: str = Field(frozen=True, strict=True)
    params: dict[str, str] = Field(frozen=True, strict=True)
    transform: str = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.skip)
        for v in self.params.values():
            validate_programmable_str(v)
        validate_programmable_str(self.transform)
        return self


IDENTIFIERS: set[str] = set()


class Prototype(BaseModel):
    identifier: str = Field(frozen=True, strict=True)
    showcase: Optional[Showcase] = Field(frozen=True, strict=True)
    params: list[Param] = Field(frozen=True, strict=True)
    skip: str = Field(frozen=True, strict=True)
    vars: list[Var] = Field(frozen=True, strict=True)
    vertices: list[Vertex] = Field(frozen=True, strict=True)
    faces: list[Face] = Field(frozen=True, strict=True)
    instances: list[Instance] = Field(frozen=True, strict=True)

    @model_validator(mode='after')
    def verify_identifier(self) -> Self:
        global IDENTIFIERS
        if self.identifier in IDENTIFIERS:
            raise ValueError(f'Identifier {self.identifier} is already registered.')
        else:
            IDENTIFIERS.add(self.identifier)
        return self

    @model_validator(mode='after')
    def verify_prog_field(self) -> Self:
        validate_programmable_str(self.skip)
        return self


class Prototypes(RootModel):
    root: list[Prototype] = Field(frozen=True, strict=True)


def validate_json() -> None:
    raw_json_folder = common.get_root_folder() / 'raw_jsons'

    for json_file in raw_json_folder.rglob('*.json'):
        logging.info(f'Validating {json_file} ...')
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                docuement = json.load(f)
                Prototypes.model_validate(docuement)
        except json.JSONDecodeError as e:
            logging.error(f'Can not load file {json_file}. It may not a valid JSON file. Reason: {e}')
        except ValidationError as e:
            logging.error(f'File {json_file} is not correct. Reason: {e}')


if __name__ == '__main__':
    common.setup_logging()
    validate_json()
