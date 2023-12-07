import bpy, bpy_extras
import typing, os
from . import PROP_preferences
from . import UTIL_functions

## Ballance Texture Usage
#  The aim of this module is to make sure every Ballance texture only have 1 instance in Blender as much as we can 
#  (it mean that if user force to add multiple textures, we can not stop them)
#  
#  All image loading and saving operation should be operated via this module, no matter what your are loading is or is not Ballance textures.
#  This module provide a universal way to check whether texture is a part of Ballance textures and use different strategy to load them.
#  
#  The loading and saving of textures frequently happend when importing or exporting, there is 2 example about them.
#  ```
#  # bmx loading example
#  bmx_texture = blabla()
#  if bmx_texture.is_external(): 
#      tex = UTIL_ballance_texture.load_ballance_texture(bmx_texture.filename)
#  else: 
#      tex = UTIL_ballance_texture.load_other_texture(os.path.join(tempfolder, 'Textures', bmx_texture.filename))
#  texture_process(tex) # process loaded texture
#  
#  # nmo loading example
#  vt_texture = blabla()
#  place_to_load = ""
#  if vt_texture.is_raw_data(): 
#      place_to_load = allocate_place()
#      save_vt_raw_data_texture(vt_texture, place_to_load)
#  if vt_texture.is_original_file() or vt_texture.is_external():
#      place_to_load = vt_texture.filename
#  
#  try_filename = UTIL_ballance_texture.get_ballance_texture_filename(place_to_load)
#  if try_filename:
#      # load as ballance texture
#      tex = UTIL_ballance_texture.load_ballance_texture(try_filename)
#  else:
#      # load as other texture
#      tex = UTIL_ballance_texture.load_other_texture(place_to_load)
#  texture_process(tex) # process loaded texture
#  
#  ```
#  
#  ```
#  # bmx saving example
#  tex: bpy.types.Image = texture_getter()
#  try_filename = UTIL_ballance_texture.get_ballance_texture_filename(
#      UTIL_ballance_texture.get_texture_filepath(tex))
#  if try_filename:
#      write_external_filename(try_filename)
#  else:
#      realpath = UTIL_ballance_texture.generate_other_texture_save_path(tex, tempfolder)
#      UTIL_ballance_texture.save_other_texture(tex, realpath)
#      write_filename(realpath)
#  
#  ```

#region Ballance Texture Assist Functions

_g_BallanceTextureFileNames: set[str] = set((
    # "atari.avi",
    "atari.bmp",
    "Ball_LightningSphere1.bmp",
    "Ball_LightningSphere2.bmp",
    "Ball_LightningSphere3.bmp",
    "Ball_Paper.bmp",
    "Ball_Stone.bmp",
    "Ball_Wood.bmp",
    "Brick.bmp",
    "Button01_deselect.tga",
    "Button01_select.tga",
    "Button01_special.tga",
    "Column_beige.bmp",
    "Column_beige_fade.tga",
    "Column_blue.bmp",
    "Cursor.tga",
    "Dome.bmp",
    "DomeEnvironment.bmp",
    "DomeShadow.tga",
    "ExtraBall.bmp",
    "ExtraParticle.bmp",
    "E_Holzbeschlag.bmp",
    "FloorGlow.bmp",
    "Floor_Side.bmp",
    "Floor_Top_Border.bmp",
    "Floor_Top_Borderless.bmp",
    "Floor_Top_Checkpoint.bmp",
    "Floor_Top_Flat.bmp",
    "Floor_Top_Profil.bmp",
    "Floor_Top_ProfilFlat.bmp",
    "Font_1.tga",
    "Gravitylogo_intro.bmp",
    "HardShadow.bmp",
    "Laterne_Glas.bmp",
    "Laterne_Schatten.tga",
    "Laterne_Verlauf.tga",
    "Logo.bmp",
    "Metal_stained.bmp",
    "Misc_Ufo.bmp",
    "Misc_UFO_Flash.bmp",
    "Modul03_Floor.bmp",
    "Modul03_Wall.bmp",
    "Modul11_13_Wood.bmp",
    "Modul11_Wood.bmp",
    "Modul15.bmp",
    "Modul16.bmp",
    "Modul18.bmp",
    "Modul18_Gitter.tga",
    "Modul30_d_Seiten.bmp",
    "Particle_Flames.bmp",
    "Particle_Smoke.bmp",
    "PE_Bal_balloons.bmp",
    "PE_Bal_platform.bmp",
    "PE_Ufo_env.bmp",
    "Pfeil.tga",
    "P_Extra_Life_Oil.bmp",
    "P_Extra_Life_Particle.bmp",
    "P_Extra_Life_Shadow.bmp",
    "Rail_Environment.bmp",
    "sandsack.bmp",
    "SkyLayer.bmp",
    "Sky_Vortex.bmp",
    "Stick_Bottom.tga",
    "Stick_Stripes.bmp",
    "Target.bmp",
    "Tower_Roof.bmp",
    "Trafo_Environment.bmp",
    "Trafo_FlashField.bmp",
    "Trafo_Shadow_Big.tga",
    "Tut_Pfeil01.tga",
    "Tut_Pfeil_Hoch.tga",
    "Wolken_intro.tga",
    "Wood_Metal.bmp",
    "Wood_MetalStripes.bmp",
    "Wood_Misc.bmp",
    "Wood_Nailed.bmp",
    "Wood_Old.bmp",
    "Wood_Panel.bmp",
    "Wood_Plain.bmp",
    "Wood_Plain2.bmp",
    "Wood_Raft.bmp",
))

def _get_ballance_texture_folder() -> str:
    """!
    Get Ballance texture folder from preferences.

    @exception BBPException Ballance texture folder is not set in preferences

    @return The path to Ballance texture folder.
    """

    pref: PROP_preferences.RawPreferences = PROP_preferences.get_raw_preferences()
    if not pref.has_valid_blc_tex_folder():
        raise UTIL_functions.BBPException("No valid Ballance texture folder in preferences.")
    
    return pref.mBallanceTextureFolder

def _is_path_equal(path1: str, path2: str) -> bool:
    """!
    Check whether 2 path are equal.

    The checker will call os.path.normcase and os.path.normpath in series to regulate the give path.

    @param path1[in] The given absolute path 1
    @param path2[in] The given absolute path 2
    @return True if equal.
    """

    return os.path.normpath(os.path.normcase(path1)) == os.path.normpath(os.path.normcase(path2))

#endregion

#region Ballance Texture Detect Functions

def get_ballance_texture_filename(texpath: str) -> str | None:
    """!
    Return the filename part for valid Ballance texture path.

    If the file name part of given path is not a entry of Ballance texture file name list, function will return None immediately.
    Otherwise, function will check whether the given file path is really point to the Ballance texture folder.

    @exception BBPException Ballance texture folder is not set in preferences

    @param imgpath[in] Absolute path to texture.
    @return File name part of given texture path if given path is a valid Ballance texture path, or None if the path not point to a valid Ballance texture.
    """
    
    # check file name first
    filename: str = os.path.basename(texpath)
    if filename not in _g_BallanceTextureFileNames: return None

    # if file name matched, check whether it located in ballance texture folder
    probe: str = os.path.join(_get_ballance_texture_folder(), filename)
    if not _is_path_equal(probe, texpath): return None

    return filename

def is_ballance_texture_filepath(texpath: str) -> bool:
    """!
    Check whether the given path is a valid Ballance texture.

    Simply call get_ballance_texture_filename() and check whether it return string or None.

    @exception BBPException Ballance texture folder is not set in preferences

    @param imgpath[in] Absolute path to texture.
    @return True if it is Ballance texture.
    @see get_ballance_texture_filename
    """
    
    return get_ballance_texture_filename(texpath) is not None

def get_texture_filepath(tex: bpy.types.Image) -> str:
    """!
    Get the file path referenced by the given texture.

    This function will try getting the referenced file path of given texture, including packed or not packed texture.

    This function will try resolving the file path when given texture is packed according to the path of 
    current opend blender file and Ballance texture folder speficied in preferences.

    If resolving failed, it may return blender packed data url, for example `\\./xxx.bmp`

    @exception BBPException Ballance texture folder is not set in preferences

    @param tex[in] The image where the file name need to be got.
    @return The resolved absolute file path.
    """

    # resolve image path
    absfilepath: str = bpy_extras.io_utils.path_reference(
        tex.filepath, bpy.data.filepath, _get_ballance_texture_folder(),
        'ABSOLUTE', "", None, None
    )

    # return resolved path
    return absfilepath
    
def is_ballance_texture(tex: bpy.types.Image) -> bool:
    """!
    Check whether the provided image is Ballance texture according to its referenced file path.

    A simply calling combination of get_texture_filepath and is_ballance_texture_filepath

    @exception BBPException Ballance texture folder is not set in preferences

    @param tex[in] The texture to check.
    @return True if it is Ballance texture.
    @see get_texture_filepath, is_ballance_texture_filepath
    """
    
    return is_ballance_texture_filepath(get_texture_filepath(tex))

#endregion

#region Ballance Texture Load & Save

def load_ballance_texture(texname: str) -> bpy.types.Image:
    """!
    Load Ballance texture.

    + The returned image may be redirected to a existing image according to its file path, because all Ballance textures are shared.
    + The loaded image is saved as external. No pack will be operated because plugin assume all user have Ballance texture folder.

    @exception BBPException Ballance texture folder is not set in preferences, or provided file name is invalid.

    @param texname[in] the file name (not the path) of loading Ballance texture. Invalid file name will raise exception.
    @return The loaded image.
    """
    
    # check texture name
    if texname not in _g_BallanceTextureFileNames:
        raise UTIL_functions.BBPException("Invalid Ballance texture file name.")
    
    # load image
    # check existing image in any case. because we need make sure ballance texture is unique.
    filepath: str = os.path.join(_get_ballance_texture_folder(), texname)
    ret: bpy.types.Image = bpy.data.images.load(filepath, check_existing = True)

    return ret

def load_other_texture(texname: str) -> bpy.types.Image:
    """!
    Load the Texture which is not a part of Ballance texture.

    This function is different with load_ballance_texture(). It can be seen as the opposition of load_ballance_texture().
    This function is used when loading the temp images created by BMX file resolving or Virtools engine. 
    Because these temp file will be deleted after importing, this function need pack the loaded file into blender file immediately after loading.

    @remark
    + The loaded texture will be immediately packed into blender file.
    + Loading will NOT check any loaded image according to file path.

    @param texname[in] the absolute path to the loading image.
    @return The loaded image.
    """
    
    # load image first
    # always do not check the same image.
    ret: bpy.types.Image = bpy.data.images.load(texname, check_existing = False)
    
    # then immediately pack it into file.
    ret.pack()
    
    return ret

def generate_other_texture_save_path(tex: bpy.types.Image, file_folder: str) -> str:
    """!
    Generate the path to saved file.

    This function first get file name from texture, then combine it with given dest file folder, 
    and return it.
    Frequently used with save_other_texture to create its parameter.

    @param tex[in] The saving texture
    @param filepath[in] The absolute path to the folder where the texture will be saved.
    @return The path to saved file.
    """
    return os.path.join(file_folder, os.path.basename(get_texture_filepath(tex)))

def save_other_texture(tex: bpy.types.Image, filepath: str) -> None:
    """!
    Save the texture which is not a part of Ballance texture.

    This function is frequently used when exporting something.
    Usually used to save the texture loaded by load_other_texture, because the texture loaded by load_ballance_texture do not need save.
    This function accept textures which is packed or not packed in blender file.

    @param tex[in] The saving texture
    @param filepath[in] The absolute path to saving file.
    """
    # MARK: must use keyword to assign param otherwise blender will throw error.
    tex.save(filepath = filepath)

#endregion
