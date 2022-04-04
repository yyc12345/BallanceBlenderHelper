import bpy, bmesh, bpy_extras, mathutils
import struct, shutil, os

# writer

def write_string(fs,str):
    count=len(str)
    write_uint32(fs,count)
    fs.write(str.encode("utf_32_le"))

def write_uint8(fs,num):
    fs.write(struct.pack("B", num))

def write_uint32(fs,num):
    fs.write(struct.pack("I", num))

def write_uint64(fs,num):
    fs.write(struct.pack("Q", num))

def write_bool(fs,boolean):
    if boolean:
        write_uint8(fs, 1)
    else:
        write_uint8(fs, 0)

def write_float(fs,fl):
    fs.write(struct.pack("f", fl))

def write_world_matrix(fs, matt):
    mat = matt.transposed()
    fs.write(struct.pack("ffffffffffffffff",
    mat[0][0],mat[0][2], mat[0][1], mat[0][3],
    mat[2][0],mat[2][2], mat[2][1], mat[2][3],
    mat[1][0],mat[1][2], mat[1][1], mat[1][3],
    mat[3][0],mat[3][2], mat[3][1], mat[3][3]))

def write_3vector(fs, x, y ,z):
    fs.write(struct.pack("fff", x, y ,z))

def write_color(fs, colors):
    write_3vector(fs, colors[0], colors[1], colors[2])

def write_2vector(fs, u, v):
    fs.write(struct.pack("ff", u, v))

def write_face(fs, v1, vt1, vn1, v2, vt2, vn2, v3, vt3, vn3):
    fs.write(struct.pack("IIIIIIIII", v1, vt1, vn1, v2, vt2, vn2, v3, vt3, vn3))

# reader

def peek_stream(fs):
    res = fs.read(1)
    fs.seek(-1, os.SEEK_CUR)
    return res

def read_float(fs):
    return struct.unpack("f", fs.read(4))[0]

def read_uint8(fs):
    return struct.unpack("B", fs.read(1))[0]

def read_uint32(fs):
    return struct.unpack("I", fs.read(4))[0]

def read_uint64(fs):
    return struct.unpack("Q", fs.read(8))[0]

def read_string(fs):
    count  = read_uint32(fs)
    return fs.read(count*4).decode("utf_32_le")

def read_bool(fs):
    return read_uint8(fs) != 0

def read_world_materix(fs):
    p = struct.unpack("ffffffffffffffff", fs.read(4*4*4))
    res = mathutils.Matrix((
    (p[0], p[2], p[1], p[3]),
    (p[8], p[10], p[9], p[11]),
    (p[4], p[6], p[5], p[7]),
    (p[12], p[14], p[13], p[15])))
    return res.transposed()

def read_3vector(fs):
    return struct.unpack("fff", fs.read(3*4))

def read_2vector(fs):
    return struct.unpack("ff", fs.read(2*4))

def read_face(fs):
    return struct.unpack("IIIIIIIII", fs.read(4*9))

def read_component_face(fs):
    return struct.unpack("IIIIII", fs.read(4*6))


