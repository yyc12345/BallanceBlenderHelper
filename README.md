# Ballance Blender Helper

[中文版本](README_ZH.md)

## Brief Introduction

This is a Blender plugin which is served for Ballance mapping in Blender.  
The latest commit may not be stable to use, please use the latest commit with git tag as the stable version.  
This plugin contain various aspect of Ballance mapping. However, if some features can be easily gotten from other Blender plugin, this plugin will not provide them duplicatedly. We highly recommend that use this plugin with following plugins.

* [BenjaminSauder/SimpleLattice](https://github.com/BenjaminSauder/SimpleLattice): Create lattice quickly to transform object.
* [JulienHeijmans/quicksnap](https://github.com/JulienHeijmans/quicksnap): Provide powerful align functions which far beyond vanilla Blender align function.

## Technical Infomation

Used BM file spec can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md) (Chinese only).  
Used tools chain principle and the file format located in `meshes` can be found in [there](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md) (Chinese only).  
The format of the files which are under the `jsons` folder and belong to the BMERevenge section, can be found in [here](https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_ZH.md) (Chinese only).

This plugin will continuously support Blender lastest **LTS** version. This plugin will migrate to new version when the new LTS version released. Currently, it based on Blender **3.6.x**.

## Installation

Put `ballance_blender_plugin` into Blender's plugin folder, `scripts/addons`. Then enable this plugin in Blender's preferences (DO NOT forget to configure this plugin's settings after first installation or updating plugin.).

> **Note**
After the version 3.3 supporting Blender 3.6 LTS, you should install this plugin in `scripts/addons`, not `scripts/addons_contrib` due to Blender do not support testing plugin anymore. If you still have old version in `scripts/addons_contrib`, please **DELETE** it **BEFORE** install the new version.

## Feature Introduction

### Plugin Settings

* External Texture Folder: Please fill in the `Texture` directory of Ballance, the plugin will refer the external texture file from this directory (the texture file originally with Ballance)
* No Component Collection: Objects located in this collection will be forced to be set as non-component. If left blank, this function will be shutdown. This function is frequently used in forced component replacement.
* Temp Texture Folder: used to cache texture files extracted from BM files. Please arrange a directory that will not be automatically cleaned up. Since Blender will continue to read texture files from this directory, it can not be emptied casually. 

Temp Texture Folder does not allow files with duplicated name. Because of this, imagine this situation, there are two texture files with the same name in two BM files, but they represent different images. When you import them one by one for different maps. The later file will overwrite the previous file, And this will cause a texture error when the first Blender document was opened again. For the solution of this issue, the best way is to force packaging once. After successfully importing the BM, click `File - External Data - Pack Resources`, then you can clear Temp Texture Folder safely. With your preference, you also can click `File - External Data - Unpack Resources` to extract textures. This operation will extract and re-refer all textures into standalone texture folder within the folder where this Blender document is.

### BM Import / Export

Click `File - Import - Ballance Map` to import BM file.  
When name conflicts occur during importing BM, you have ability to choose different strategies for 4 different data types, Texture, Material, Mesh and Object. You can specify them to create a new instance or use current data block.

Click `File - Export - Ballance Map` to export a BM file.  
You can export a collection or an object (Export Mode), and specify target (Export Target) correspondingly.  
Although plugin provide Virtools Group feature and give you ability to grouping object in Blender. The export function also depend on Tools Chain Principle. Because of this, if you do not follow Tools Chain Principle, some convenient features will be disabled, for example, your exported BM file may larger than common one.

It should be noted that once the BM is exported, all the faces in the file will be converted to triangular faces, please make a backup in advance.  
It is recommended to use a flat collection structure, do not put a collection within another collection, which may cause some unnecessary problems.  
The suffix name of BM file is BMX, X stands for compression. BMX and BM is the same thing.

### Ballance 3D

Ballance 3D is a set of light tools related to 3D operations, which can be found in the upper left corner menu bar of 3D View. This menu is named as Ballance.

#### 3ds Max Align

Provide 3ds Max like align tools. Current active object will be seen as reference object. All selected objects (except active object) will be seen as operating object (So you can select multiple objects to align to a single object).

#### Create Rail UV

To create UVs for the rails in the map, you need to select the objects that need to add UVs similar to the rails, and then click this button to create.  
In the dialog, you can select the material to be used. You can also choose the unfolding mode. In some unfolding modes, projection axis and zoom ratio options is available. Although Ballance will process all rail UV in game internally, it is essential that give a perfect UV in designer.  
If you want that the rail have in-game UV (it represent as smooth texture), you can choose `TT_ReflectionMapping` unfolding mode. This mode is written with the reverse work of game used function. This unfolding mode may be useful when you creating advertisement image in Blender for your map.

#### Flatten UV

In the object editing mode, it is a operator which is used to attach the currently selected surface to the UV. And you can specific the edge which will be attached into the V axis.  
Note that only convex face is supported. Applying this for a concave face will cause undefined behavior.

In the edit mode, select the surface, click Flatten UV, and then scroll the slider to select an edge as a reference.  
If the generated UV is not attached correctly, such as the FloorSide's band is pasted to the bottom, you can reselect the reference edge and redo the operation until it is correct.

For the UV flatten by plugin, it must have a scale property. For example, the UV scale of normal floor is 5. However, the UV scale of sink floor is slightly larger than 5. Because the sink floor is "sink" in the floor block. There are 2 methods provided by plugin to getting this proper scale number. You can choose one from Scale Mode.  
The first method is that user specify a direct scale number. You just need select Scale Size in Scale Mode and fill with a proper scale number. This option is frequently used for fill a large borderless floor.  
The second method is reference point mode. You need specify a reference point and corresponding U component of its UV. Plugin will calculate the scale size automatically. This method is used for expanding a path of floor.

### Quick Struct Adder

In the add menu, we have added a set of commonly used objects. After adding, the object will move to the 3D cursor.

#### Elements

Add elements, you can also specify attributes such as section when adding (it will not be displayed for unique objects such as start point)

#### Rail section

Add rail section, you can choose monorail or rail (just decide the number of rail section loops added, and will not help you rotate the angle), as well as rail radius and rail span (default value is standard value).

#### Floors

A powerful floor adder feature belong to the extension of BMERevenge project.  
In menu, Basic Floor is basic floor component. Derived Floor is consisted by basic floor components. Commonly, frequently used models are located in Derived Floor section.  
After selecting a floor type, you can assign 2 expand value at most, according to its property. You also can use options to decide whether side faces and bottom face can be generated.  
Comparing with trditional Ballance Map Editor, this function can massively reduce useless vertices.

The floor type can be simply grouped as Flat Floor, Sink Floor, Wide Floor and Platform.  
Additionally, Trafo Block and Transition between Flat Floor and Sink Floor are available.

It is recommended to merge the vertices by distance, unless you need do some special work.

### Virtools Group

Plugin add a new property for each Blender objects, called Virtools Group. It takes the same functionality of Group in Virtools.  
Select an object, You can find `Virtools Group` panel in `Object Properties` panel.  
Click Add or Delete icon to group or ungroup for object.  
Double click item in list to rename it.

After click Add button, you can choose Predefined option, and select a name from all legal Ballance used group names.  
Or, choose Custom option and write your own group name.

### Virtools Material

Plugin add a new property for each Blender materials, called Virtools Material. It create a bridge between Virtools Material and Blender Material.  
Navigate to `Material Properties` panel, select a material, you can find `Virtools Material` panel.  
In default, user created material will not enable Virtools Material feature. You need to click checkbox of `Virtools Material` panel to enable or disable it.

After enable Virtools Material, `Basic Parameters` section and `Advanced Parameters` section can be set. Set your material peroperties just like operating in Virtools.  
Just like its name, `Basic Parameters` is basic material properties. `Advanced Parameters` is mainly related to transparent properties and usually used in the bottom of transparent column.  
Additionally, `Basic Parameters` section provide a preset function, allowing user to use some preset material settings, which only affect 4 basic colors, just for convenient using.

In `Operation` section, `Apply Virtools Material` will clean all existed Blender material and create a new material graph according to Virtools material properties.  
And, `Parse from Blender Principled BSDF` will try parsing a Principled BSDF to Virtools material.  
If your material highly rely on Blender material, please execute `Parse from Blender Principled BSDF` or disable Virtools Material feature before exporting BM file, otherwise material can not be saved correctly.

### Select by Virtools Group

Plugin add a selection function according to Virtools Group in Select menu.

This function firstly have 5 different selection strategies which is exactly matched with Blender selection method. Just use it like Blender selection (Set, Extend, Subtract, Invert, Intersect).  
Then, select your group name to start a selection.

If you can, using Subtract or Intersect modes would be better than other modes. Because these modes avoid analyzing too many objects.
For example, first, select a rough range, and then use the Intersect mode to filter objects, which is more efficient than directly using the Start mode to select.

### Quick Grouping

Plugin add quick grouping menu in 2 places.
You can select various objects, right click and find quick grouping menu in Object Context menu.  
Also you can pick objects in Outline View and right click them, find quick grouping menu in Object menu.

#### Group into

Group selected objects into your specified group. 

#### Ungroup from

Ungroup selected objects from your specified group. 

#### Clear Grouping

Clean the grouping infomation for selected objects.

### Auto Grouping & Rename

In Outline View, you can find auto grouping and rename menu via right click any collection.

This plugin now support 2 name standard.  
First one has been introduced in Technical Infomation chapter. In plugin, its name is `YYC Tools Chains`.  
The second one is used by [Imengyu/Ballance](https://github.com/imengyu/Ballance). In plugin, its name is `Imengyu Ballance`.

All functions within this menu will only output a summary when finishing. If you want to check out some objects in detail, please click `Window - Switch System Terminal`. Plugin output a detailed report in that place.

#### Rename by Group

Rename object with proper name according to its Virtools Group properties.  
This usually use when migrating original map. Some Ballance derived applications do not have Group concept. They rely on name to get group infomations.

#### Convert Name

Convert name between different name standard.  
Frequently used in convertion between 2 different Ballance derived applications.

#### Auto Grouping

Auto grouping according to specified name standard.  
Please pay attention that previous grouping infomations will be overwritten.  
If you following some mapping standard during all mapping stages, this function will auto grouping all objects for you.

