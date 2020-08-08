# Ballance Blender Helper

[中文版本](README_ZH.md)

## Brief introduction

This is a Blender plugin which is served for Ballance mapping in Blender.

Currently, it only contain fundamental functions. More useful features will be added in future.

## Technical infomation

Used BM file spec can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md)(Chinese only).

Used tools chain principle and the file format located in `meshes` can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md)(Chinese only).

This plugin will continuously support Blender lastest **LTS** version. This plugin will migrate to new version when the new LTS version released. Currently, it based on Blender 2.83.x.

## Function introduction

### Plugin settings

* External texture folder: Please fill in the Texture directory of Ballance, the plugin will call the external texture file from this directory (the texture file originally with Ballance)
* No component collection: Objects in this collection will be forced to be set as non-Component. If left blank, this function will be shutdown.
* Temp texture folder: used to cache texture files extracted from BM files. Please arrange a directory that will not be automatically cleaned up. Since Blender will continue to read texture files from this directory, it cannot be emptied at will. And it also does not allow files with the same name to exist, that is, if I import two BMs for two maps, and there are two files with the same name but different images in the two BMs, the later files will overwrite the previous files , And in turn caused a texture error when the first blender document was opened again. For solving this problem, please refer to the subsequent BM import / export

### BM import / export

For import, in order to prevent texture errors, the best way is to force packaging once. After successfully importing the BM, choose to pack all into the blend file, and then clear the directory where the Temp texture folder is located, and then click Unpack to file if necessary, this operation will re-depend the textures in the texture library under the project folder.

For export, you can choose to export a collection or an object (Export mode), and specify the target (Export target).

It should be noted that once the BM is exported, all the faces in the file will be converted to triangular faces, please make a backup in advance. And it is recommended to use a flat collection structure, do not put a collections within another collection, which may cause some unnecessary problems.

### Ballance 3D

Ballance 3D is a set of light tools related to 3D operations, which can be found in the upper right corner of the 3D view.

#### Super Align

Provide 3ds Max like align tools. Current active will be seen as reference object. All selected objects(except active object) will be seen as operating object (So you can select multiple objects to align to the reference object).

#### Create Rail UV

Create UV for rails. You should select the object which you want add rail like UV to. Then, click this menu. Before doing this, you need make sure all selected object have at least 1 UV map (If it have more than 1 UV map, only the first UV map will be changed).

## Install

Put `ballance_blender_plugin` into Blender's plugin folder, `scripts/addons_contrib`. Then enable this plugin in Blender's preferences (Don't forget to configure this plugin's settings).

## Dev plan

* Add elements in Add menu.
* The assisted tools for creating custom floor in Blender (for example: add UV for floor).
