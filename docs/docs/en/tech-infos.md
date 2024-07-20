# Technical Information

* BM File Specification: https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md
* Mapping toolchain standards and format of files in the `meshes' folder: https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md
* Format of the JSON file for BMERevenge: https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_v2.0_ZH.md

This plugin works with the `fake-bpy-module` module to implement type hinting to speed up development. Use the following command to install Blender's type hinting library.

* Blender 3.6: `pip install fake-bpy-module-latest==20230627`
* Blender 4.2: `pip install fake-bpy-module-latest==20240716`

The main reason for doing this is that `fake-bpy-module` doesn't release an official package for the given Blender version, so I had to install it by choosing the daily build closest to the release time of the corresponding Blender version.
