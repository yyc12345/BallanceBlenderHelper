import math, typing

class BBPException(Exception):
    """
    The exception thrown by Ballance Blender Plugin
    """
    pass

def clamp_float(v: float, min_val: float, max_val: float) -> float:
    """!
    @brief Clamp a float value

    @param v[in] The value need to be clamp.
    @param min_val[in] The allowed minium value, including self.
    @param max_val[in] The allowed maxium value, including self.
    @return Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_float().")

    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v

def clamp_int(v: int, min_val: int, max_val: int) -> int:
    """!
    @brief Clamp a int value

    @param v[in] The value need to be clamp.
    @param min_val[in] The allowed minium value, including self.
    @param max_val[in] The allowed maxium value, including self.
    @return Clamped value.
    """
    if (max_val < min_val): raise BBPException("Invalid range of clamp_int().")

    if (v < min_val): return min_val
    elif (v > max_val): return max_val
    else: return v


_TLimitIterator = typing.TypeVar('_TLimitIterator')
def limit_iterator(it: typing.Iterator[_TLimitIterator], limit_count: int) -> typing.Iterator[_TLimitIterator]:
    """!
    A generator wrapper for another generator to make sure the length of the given generator output entries 
    is not greater (<= less equal) than given number.

    @param it[in] A iterator need to be limited. Use iter(ls) if your passing value is not a generator (eg. tuple, list)
    @param limit_count[in] The count to limit. Must be a positive number. Can be 0.
    @return A generator with limited length. Use tuple(ret) if you just want to convert it to a tuple.
    """
    counter: int = 0
    while counter < limit_count:
        # if no elements in given iterator, StopIteration will raise. 
        # It is okey because it naturally stop the iteration of this generator.
        yield next(it)
        counter += 1
