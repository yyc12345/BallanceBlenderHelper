import bpy, bpy_extras
import os, typing
from . import UTIL_preferences, UTIL_functions

#region Texture Functions

g_ballanceTextureSet = set((
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
    "Wood_Raft.bmp"
))

def is_ballance_texture_path(imgpath: str) -> bool:
    """
    Check whether the given path is Ballance texture.

    @param imgpath[in] Path to check.
    @return True if it is Ballance texture.
    """

    filename: str = os.path.basename(imgpath)
    return filename in g_ballanceTextureSet

def is_ballance_texture(tex: bpy.types.Image) -> bool:
    """
    Check whether the provided image is Ballance texture according to its referenced file path.

    @remark
    + Throw exception if no valid Ballance texture folder set in preferences.

    @param tex[in] The image.
    @return True if it is Ballance texture.
    """
    
    # check preference
    pref: UTIL_preferences.RawPreferences = UTIL_preferences.get_raw_preferences()
    if not pref.has_valid_blc_tex_folder():
        raise UTIL_functions.BBPException("No valid Ballance texture folder in preferences.")
    
    # resolve image path
    absfilepath: str = bpy_extras.io_utils.path_reference(
        tex.filepath, bpy.data.filepath, pref.mBallanceTextureFolder,
        'ABSOLUTE', "", None, None
    )
    
    # test gotten file path
    return is_ballance_texture_path(absfilepath)

def load_ballance_texture(texname: str) -> bpy.types.Image:
    """
    Load Ballance texture.

    @remark
    + The returned image may be redirected to a existing image according to its file path, because all Ballance textures are shared.
    + The loaded image is saved as external. No pack will be operated because plugin assume all user have Ballance texture folder.
    + An exception will be thrown if user do not set Ballance texture path in preferences.

    @param texname[in] the file name (not the path) of loading Ballance texture. Invalid file name will raise exception.
    @return The loaded image.
    """
    
    # check preference
    pref: UTIL_preferences.RawPreferences = UTIL_preferences.get_raw_preferences()
    if not pref.has_valid_blc_tex_folder():
        raise UTIL_functions.BBPException("No valid Ballance texture folder in preferences.")
    
    # check texture name
    if texname not in g_ballanceTextureSet:
        raise UTIL_functions.BBPException("Invalid Ballance texture file name.")
    
    # load image
    # check existing image in any case. because we need make sure ballance texture is unique.
    filepath: str = os.path.join(pref.mBallanceTextureFolder, texname)
    return bpy.data.images.load(filepath, check_existing = True)

def load_other_texture(texname: str) -> bpy.types.Image:
    """
    Load the Texture which is not a part of Ballance texture.

    This function is different with load_ballance_texture(). It can be seen as the opposition of load_ballance_texture().
    This function is used in loading the temp images created by BMX file resolving or Virtools engine. 
    Because these tmep file will be deleted after importing, this function need pack the loaded file into blender file immediately after loading.

    @remark
    + The loaded texture will be immediately packed into blender file.
    + Loading will NOT check any loaded image according to file path.

    @param texname[in] the FULL path to the loading image.
    @return The loaded image.
    """
    
    # load image first
    # always do not check the same image.
    ret: bpy.types.Image = bpy.data.images.load(texname, check_existing = False)
    
    # then immediately pack it into file.
    ret.pack()
    
    # return image
    return ret

def save_other_texture(tex: bpy.types.Image, filepath: str) -> None:
    """
    Save the texture which is not a part of Ballance texture.

    @remark
    + This function is the reverse operation of load_other_texture()
    + This function accept textures which is packed or not packed in blender file.

    @param tex[in] The saving texture
    @param filepath[in] The dest path to saving texture.
    """
    tex.save(filepath)

#endregion

#region Ballance Textures Constance in Blender

class BBP_PG_ballance_texture_item(bpy.types.PropertyGroup):
    texture_name: bpy.props.StringProperty(
        name = "Texture Name", 
        default = "",
    )

    texture_pointer: bpy.props.PointerProperty(
        name = "Texture Pointer",
        type = bpy.types.Image,
    )

class TextureManager():
    """
    A wrapper for texture visiting.
    
    All texture visiting should be passed by this class, including getting, adding and removing.
    This class is mainly served for importing and exporting. In these situation, texture need to be loaded or saved.
    This class support `with` syntax.
    This class is not thread safe and only can have one instance at the same time.
    """

    gSingletonOccupation: typing.ClassVar[bool] = False

    mIsValid: bool
    mTextureDict: dict[str, bpy.types.Image]

    def __init__(self):
        self.mIsValid = False
        self.mTextureDict = {}

    def __enter__(self):
        # check singleton
        if TextureManager.gSingletonOccupation:
            raise UTIL_functions.BBPException('TextureManager fail to create as a singleton.')

        # check preference
        pref: UTIL_preferences.RawPreferences = UTIL_preferences.get_raw_preferences()
        if not pref.has_valid_blc_tex_folder():
            raise UTIL_functions.BBPException("No valid Ballance texture folder in preferences.")
        
        # parse ballance textures
        blctexs: bpy.types.CollectionProperty = bpy.context.scene.ballance_textures
        item: BBP_PG_ballance_texture_item
        for item in blctexs:
            # only add valid one
            if item.texture_pointer:
                self.mTextureDict[item.texture_name] = item.texture_pointer
        
        # set to valid
        TextureManager.gSingletonOccupation = True
        self.mIsValid = True

        # return self
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.mIsValid:
            # sync self dict to global blc textures
            blctexs: bpy.types.CollectionProperty = bpy.context.scene.ballance_textures
            invalid_idx: list[int] = []
            # update existing one.
            item: BBP_PG_ballance_texture_item
            for idx, item in enumerate(blctexs):
                newtex: bpy.types.Image | None = self.mTextureDict.get(item.texture_name, None)
                if newtex:
                    item.texture_pointer = newtex
                    del self.mTextureDict[item.texture_name]    # delete for future using

                # if this entry still is None, add it in remove list
                if item.texture_pointer is None:
                    invalid_idx.append(idx)
            # remove invalid index, from tail to head
            invalid_idx.reverse()
            for idx in invalid_idx:
                blctexs.remove(idx)
            # add new one
            # because all old one has bee synced to collection and deleted
            # so the remain pairs in dict is the new one
            # we can simply iterate it and add them
            for k, v in self.mTextureDict:
                it: BBP_PG_ballance_texture_item = blctexs.add()
                it.texture_name = k
                it.texture_pointer = v

            # release singleton
            TextureManager.gSingletonOccupation = False
            self.mIsValid = False

    def dispose(self):
        self.__exit__(self, None, None, None)

    def get_image(self, filepath: str) -> bpy.types.Image:
        if not self.mIsValid:
            raise UTIL_functions.BBPException('Try to call invalid TextureManager class.')

        if is_ballance_texture_path(filepath):
            filename: str = os.path.basename(filepath)
            # load as ballance image
            tex: bpy.types.Image = load_ballance_texture(filename)
            # update tex
            self.mTextureDict[filename] = tex
            # return img
            return tex
        else:
            # simply load it
            return load_other_texture(filepath)

    def save_image(self, tex: bpy.types.Image, filepath: str):
        if not self.mIsValid:
            raise UTIL_functions.BBPException('Try to call invalid TextureManager class.')
        
        # file only need to be saved for non-ballance image
        if not is_ballance_texture(tex):
            save_other_texture(tex, filepath)

#endregion

def register() -> None:
    # register ballance texture collection into scene
    bpy.utils.register_class(BBP_PG_ballance_texture_item)
    bpy.types.Scene.ballance_textures = bpy.props.CollectionProperty(type = BBP_PG_ballance_texture_item)

def unregister() -> None:
    del bpy.types.Scene.ballance_textures
    bpy.utils.unregister_class(BBP_PG_ballance_texture_item)
