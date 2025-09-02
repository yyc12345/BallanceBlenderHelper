# Technical Information

## Standards and Protocol Documentation

* BM File Specification: https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md
* Mapping toolchain standards and format of files in the `meshes' folder: https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md
* Format of the JSON file for BMERevenge: https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_v2.0_ZH.md

## Development Auxiliary Package

This plugin works with the `fake-bpy-module` module to implement type hinting to speed up development. Use the following command to install Blender's type hinting library.

* Blender 3.6: `pip install fake-bpy-module-latest==20230627`
* Blender 4.2: `pip install fake-bpy-module-latest==20240716`
* Blender 4.5: `pip install fake-bpy-module-latest==20250604`

The primary reason for this is that the `fake-bpy-module` has not timely released packages suitable for the specified Blender version. Therefore, I can only install it by selecting the daily build version that is closest to the date of the corresponding Blender version leaving from the `main` branch (as daily builds only compile from the `main` branch).

!!! question "Why not use Blender's official bpy module?"
    Blender provides an official package named `bpy` on PyPI, but we will not adopt it as our development auxiliary package. This is because it basically repackages Blender into a module (which basically means you are downloading Blender again), allowing you to manipulate Blender through Python. This is contrary to our purpose of using a package that only provides type hints to assist in plugin development.

## Version Rule

The version number format of BBP follows [Semantic Versioning](https://semver.org), but with slight differences:

* The major version number is only increased when the entire plugin is reconstructed.
* The minor version number is used for regular updates.
* The patch version number is incremented when there is no modification for any functionalities. For example, version 4.2.1 only includes updates for macOS Blender without changing any features.

Before the formal release of BBP, there are typically three phased versions: Alpha version, Beta version, and RC version. The Alpha version focuses on functional updates, used to verify whether newly added or modified features are functioning correctly, and does not include documentation or translations. The Beta version is focus on plugin documentation, while the RC version concentrates on plugin translations. However, these three versions do not always exist; if the update content is minimal, some versions may be skipped, or a direct release may occur.
