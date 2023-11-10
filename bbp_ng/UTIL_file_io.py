import bpy, mathutils
import struct, os, io, typing
from . import UTIL_virtools_types

_FileWriter_t = io.BufferedWriter
_FileReader_t = io.BufferedReader

#region Writer Functions

def write_string(fs: _FileWriter_t, strl: str) -> None:
    count = len(strl)
    write_uint32(fs, count)
    fs.write(strl.encode("utf_32_le"))

def write_uint8(fs: _FileWriter_t, num: int) -> None:
    fs.write(struct.pack("<B", num))

def write_uint32(fs: _FileWriter_t, num: int) -> None:
    fs.write(struct.pack("<I", num))

def write_uint64(fs: _FileWriter_t, num: int) -> None:
    fs.write(struct.pack("<Q", num))

def write_bool(fs: _FileWriter_t, boolean: bool) -> None:
    if boolean:
        write_uint8(fs,  1)
    else:
        write_uint8(fs,  0)

def write_float(fs: _FileWriter_t, fl: float) -> None:
    fs.write(struct.pack("<f", fl))

def write_world_matrix(fs: _FileWriter_t, mat: UTIL_virtools_types.VxMatrix) -> None:
    fs.write(struct.pack("<16f", *mat.to_tuple()))

def write_color(fs: _FileWriter_t, colors: UTIL_virtools_types.VxColor) -> None:
    fs.write(struct.pack("<fff", *colors.to_tuple_rgb()))

def write_uint32_array(fs: _FileWriter_t, vals: typing.Iterable[int], count: int) -> None:
    fs.write(struct.pack('<' + str(count) + 'I', *vals))

def write_float_array(fs: _FileWriter_t, vals: typing.Iterable[float], count: int) -> None:
    fs.write(struct.pack('<' + str(count) + 'f', *vals))

#endregion

#region Reader Functions

def peek_stream(fs: _FileReader_t) -> bytes:
    res = fs.read(1)
    fs.seek(-1, os.SEEK_CUR)
    return res

def read_float(fs: _FileReader_t) -> float:
    return struct.unpack("f", fs.read(4))[0]

def read_uint8(fs: _FileReader_t) -> int:
    return struct.unpack("B", fs.read(1))[0]

def read_uint32(fs: _FileReader_t) -> int:
    return struct.unpack("I", fs.read(4))[0]

def read_uint64(fs: _FileReader_t) -> int:
    return struct.unpack("Q", fs.read(8))[0]

def read_string(fs: _FileReader_t) -> str:
    count = read_uint32(fs)
    return fs.read(count * 4).decode("utf_32_le")

def read_bool(fs: _FileReader_t) -> None:
    return read_uint8(fs) != 0

def read_world_materix(fs: _FileReader_t, mat: UTIL_virtools_types.VxMatrix) -> None:
    mat.from_tuple(struct.unpack("<16f", fs.read(16 * 4)))

def read_color(fs: _FileReader_t, target: UTIL_virtools_types.VxColor) -> None:
    target.from_const_rgb(struct.unpack("fff", fs.read(3 * 4)))

def read_uint32_array(fs: _FileReader_t, count: int) -> tuple[int, ...]:
    fmt: struct.Struct = struct.Struct('<' + str(count) + 'I')
    return fmt.unpack(fs.read(fmt.size))

def read_float_array(fs: _FileReader_t, count: int) -> tuple[float, ...]:
    fmt: struct.Struct = struct.Struct('<' + str(count) + 'f')
    return fmt.unpack(fs.read(fmt.size))

#endregion
