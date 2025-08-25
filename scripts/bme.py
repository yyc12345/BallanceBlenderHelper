import enum
from typing import Optional
from pydantic import BaseModel, RootModel, Field, model_validator, ValidationError


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


class Showcase(BaseModel):
    title: str = Field(frozen=True, strict=True)
    category: str = Field(frozen=True, strict=True)
    icon: str = Field(frozen=True, strict=True)
    type: ShowcaseType = Field(frozen=True)
    cfgs: list[ShowcaseCfg] = Field(frozen=True, strict=True)


class Param(BaseModel):
    field: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)


class Var(BaseModel):
    field: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)


class Vertex(BaseModel):
    skip: str = Field(frozen=True, strict=True)
    data: str = Field(frozen=True, strict=True)


class Face(BaseModel):
    skip: str = Field(frozen=True, strict=True)
    texture: str = Field(frozen=True, strict=True)
    indices: list[int] = Field(frozen=True, strict=True)
    uvs: list[str] = Field(frozen=True, strict=True)
    normals: Optional[list[str]] = Field(frozen=True, strict=True)


class Instance(BaseModel):
    identifier: str = Field(frozen=True, strict=True)
    skip: str = Field(frozen=True, strict=True)
    params: dict[str, str] = Field(frozen=True, strict=True)
    transform: str = Field(frozen=True, strict=True)


class Prototype(BaseModel):
    identifier: str = Field(frozen=True, strict=True)
    showcase: Optional[Showcase] = Field(frozen=True, strict=True)
    params: list[Param] = Field(frozen=True, strict=True)
    skip: str = Field(frozen=True, strict=True)
    vars: list[Var] = Field(frozen=True, strict=True)
    vertices: list[Vertex] = Field(frozen=True, strict=True)
    faces: list[Face] = Field(frozen=True, strict=True)
    instances: list[Instance] = Field(frozen=True, strict=True)


class Prototypes(RootModel):
    root: list[Prototype] = Field(frozen=True, strict=True)
