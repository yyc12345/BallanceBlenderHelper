# Compile and Distribute Plugin

!!! info "Not latest version"
    This translated page is not the latest version because the modification of source page. Please see source page of the latest version.

This page will guide you in compiling the plugin as well as distributing it.

## Compiling LibCmo with BMap

BBP's Virtools file native import/export functionality relies on BMap and its Python binding PyBMap. In order to distribute the plugin, we need to first compile BMap and its predecessor LibCmo, and before doing so, you need to check the version of BMap you need. Because BBP doesn't always use the latest version of BMap, e.g. if you're compiling an older version of BBP, it's obviously not possible to rely on the latest version of BMap. BMap is constantly being upgraded, and the functionality it provides is constantly changing, and different versions of BMap are incompatible. BBP usually states the version of BMap it uses at the time of release, but if BBP doesn't point it out, you may need to look for the most recent version of BMap that compiles with the version of BBP at the time of its release.

After specifying the version, you need to visit [LibCmo GitHub repository](https://github.com/yyc12345/libcmo21). Then clone the project and use the Git command to go to the corresponding version (or just download the source code of the corresponding version). Then follow LibCmo's compilation manual to compile to get BMap. on Windows, you'll usually get the files `BMap.dll` and `BMap.pdb`. On Linux, it will be `BMap.so`.

Then we need to configure PyBMap, which comes with LibCmo. Please follow the manual of PyBMap to combine the compiled binary BMap library with PyBMap. That is to complete the PyBMap configuration.

Then we need to copy the configured PyBMap to our project under `bbp_ng/PyBMap` to complete this step.

## Generate Thumbnails and Compress JSON

BBP comes with a built-in set of custom icons, as well as the JSON files needed by its component BME to describe the structure. By batch generating thumbnails and compressing JSON operations, the size of these parts can be reduced, making them suitable for loading in Blender and easier to distribute.

Go to the `bbp_ng/tools` folder and run `python3 build_icons.py` which will batch generate thumbnails (this requires the PIL library, please install it via pip in advance). It actually generates thumbnails from the original images in the `bbp_ng/raw_icons` directory and stores them in the `bbp_ng/icons` folder. Running `python3 build_jsons.py` will compress the JSON, which actually reads, compresses, and writes the raw JSON files from the `bbp_ng/raw_jsons` directory into the `bbp_ng/jsons` folder.

## Packaging

Starting from Blender 4.2 LTS, plugins are packaged using Blender's own packaging feature.

Assuming that the final output file is `redist/bbp_ng.zip`. If you are in the root directory of the project, execute the `blender --command extension build --source-dir bbp_ng --output-filepath redist/bbp_ ng.zip` command in a command line window to finish packaging. Please note `blender` is the executable Blender program.

Blender will package the plugin according to the instructions in `blender_manifest.toml` with the following files excluded:

* `bbp_ng/raw_icons`: raw thumbnail folder.
* `bbp_ng/raw_jsons`: raw JSON folder.
* `bbp_ng/tools`: tools for compiling.
* `bbp_ng/.style.yapf`: code style description file.
* `bbp_ng/.gitignore`: gitignore
* `bbp_ng/icons/.gitkeep`: folder placeholder
* `bbp_ng/jsons/.gitkeep`: folder placeholder

## Generating Help Documentation

Although this project will utilize the GitHub Page feature to provide help documentation, sometimes you may need to provide an offline version of the help documentation, this section will explain how to generate an offline version of the help documentation.

First you need to install `mkdocs` and `pymdown-extensions` via pip. Then go to the `docs` folder and run `mkdocs build --no-directory-urls`. After running the command you get a folder called `site`, which is the help documentation that can be viewed offline.
