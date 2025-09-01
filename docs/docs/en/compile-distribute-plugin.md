# Compile and Distribute Plugin

!!! info "Not latest version"
    This translated page is not the latest version because the modification of source page. Please see source page of the latest version.

This page will guide you in compiling the plugin as well as distributing it.

## Compiling LibCmo with BMap

BBP's Virtools file native import/export functionality relies on BMap and its Python binding PyBMap. In order to distribute the plugin, we need to first compile BMap and its predecessor LibCmo, and before doing so, you need to check the version of BMap you need. Because BBP doesn't always use the latest version of BMap, e.g. if you're compiling an older version of BBP, it's obviously not possible to rely on the latest version of BMap. BMap is constantly being upgraded, and the functionality it provides is constantly changing, and different versions of BMap are incompatible. BBP usually states the version of BMap it uses at the time of release, but if BBP doesn't point it out, you may need to look for the most recent version of BMap that compiles with the version of BBP at the time of its release.

After specifying the version, you need to visit [LibCmo GitHub repository](https://github.com/yyc12345/libcmo21). Then clone the project and use the Git command to go to the corresponding version (or just download the source code of the corresponding version). Then follow LibCmo's compilation manual to compile to get BMap. on Windows, you'll usually get the files `BMap.dll` and `BMap.pdb`. On Linux, it will be `BMap.so`.

Then we need to configure PyBMap, which comes with LibCmo. Please follow the manual of PyBMap to combine the compiled binary BMap library with PyBMap. That is to complete the PyBMap configuration.

Then we need to copy the configured PyBMap to our project under `bbp_ng/PyBMap` to complete this step.

## Generate Resources

BBP needs some resoures to run, and these resources need to be processed before using them.

For generating these resrouces, we firstly need to navigate to `scripts` directory, and execute `uv sync` to restore the environment for scripts (Astral UV required).

### Generate Thumbnails

BBP comes with a built-in set of custom icons, however these icons are stored as their original size in repository for keeping convenient editing and high quality. We need to reduce the size of these icons to make them are easy to be loaded on Blender and easy for distribution by generating thumbnails for them.

Execute `uv run build_icons.py` to generate thumbnails. It actually generates thumbnails from the original images in the `assets/icons` directory and stores them in the `bbp_ng/icons` folder.

### Generate JSONs

The BME component in BBP relies on a series of JSON files to describe the prototype. These profiles are stored in the library in JSON5 format, making them easy for writers to read and write. We converte these JSON5 files to JSON files and compressing their size makes them easier to load in Blender, as well as to facilitate plugin distribution, by batchly generating them.

If you are the plugin developer or writer of these prototypes, you need to do an additional thing before generating these JSON files: verify these JSON files. The BBP plugin will assume that these JSON files are correct when loading them. If you put a JSON file with errors (e.g. missing some fields or has some typos, etc.), it will cause Blender to throw an error when creating prototype. Therefore, it is necessary to verify these JSON files. Execute `uv run validate_jsons.py` to verify all prototype files. If there are no errors, it means that everything is okey. It is important to note that the validator is not perfect, it can only verify the data as much as possible to ensure that some common erros (e.g. typo in field name) will not occur. It can not make 100% sure about that there is no error inside these files.

For compilers, all you need to do is that execute `uv run build_jsons.py` to generate JSON files. It actually reads, compresses, and writes the original JSON5 files in `assets/jsons` directory to the `bbp_ng/jsons` folder in JSON format.

### Generate Element Meshes

BBP has built-in mesh data for all Ballance element placeholders. Execute `uv run build_jsons.py` to deploy these meshes, which simply copies the mesh files under `assets/jsons` folder to `bbp_ng/jsons` folder.

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
