# Ballance Blender Helper

[中文版本](README_ZH.md)

## Brief introduction

This is a Blender plugin which is served for Ballance mapping in Blender.

The latest commit may not be stable to use, please visit the Release page to get a stable version.

## Technical infomation

Used BM file spec can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md)(Chinese only).

Used tools chain principle and the file format located in `meshes` can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md)(Chinese only).

The format of the files which are under the `jsons` folder and belong to the BMERevenge section, can be found in [here](https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_ZH.md)

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

#### 3ds Max Align

Provide 3ds Max like align tools. Current active will be seen as reference object. All selected objects(except active object) will be seen as operating object (So you can select multiple objects to align to the reference object).

#### Create Rail UV

To create UVs for the rails in the map, you need to select the objects that need to add UVs similar to the rails, and then click this button to create.

In the dialog, you can select the material to be used. You can also choose the unfolding mode. For shorter rails, you can choose Point mode. For longer rails, you can use Uniform mode. If you need to manually adjust the zoom ratio, please select Scale mode and specify the ratio (not recommended).

You can also select the projection axis for better UV distribution.

#### Flatten UV

In the object editing mode, it is a operator which is used to attach the currently selected surface to the UV. And you can specific the edge which will be attached into the V axis. Note that only convex faces are supported.

In the edit mode, select the surface, click Flatten UV, and then scroll the slider to select an edge as a reference. If the generated UV is not attached correctly, such as the FloorSide's band is pasted to the bottom, you can reselect the reference edge and redo the operation until it is correct.

### Add Menu

In the add menu, we have added a set of commonly used objects. After adding, the object will move to the 3D cursor.

#### Elements

Add elements, you can also specify attributes such as section when adding (it will not be displayed for unique objects such as start point)

#### Rail section

Add rail section, you can choose monorail or rail (just decide the number of rail section loops added, and will not help you rotate the angle), as well as rail radius and rail span.

#### Floors

Adding floor is part of the BMERevenge project. Basic floor is a basic floor component, and Derived floor is a common component composed of basic components. The extension(length) and the side configuration can be set according to its properties. It also has the advantage of reducing vertices.

It is recommended to merge the vertices by distance, unless there is a need to delete the surface after adding it

## Install

Put `ballance_blender_plugin` into Blender's plugin folder, `scripts/addons_contrib`. Then enable this plugin in Blender's preferences (Don't forget to configure this plugin's settings).

