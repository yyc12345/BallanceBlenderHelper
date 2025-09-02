# Compile and Distribute Plugin

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

## Translation

The BBP plugin supports multilingual functionality, so we need to extract and update the content to be translated before the official release, and then proceed to the next step after translating all the content.

Blender's multilingual support for plugins is not satisfactory, and BBP's design is relatively special, so BBP adopts a different way to manage translations than the official recommended plugin translation management method of Blender: that is, use PO files to manage translations instead of the officially recommended Python script format.

!!! info "Do NOT submit translations in Python format"
    As mentioned above, BBP uses PO files to manage translations, rather than the Python source format recommended by Blender. However, this does not prevent Blender's multilingual plugins from writing translations in the Python source format into the plugin's source code. Submitting duplicate translations not only increases the repository size but also complicates management. Therefore, BBP requires you to delete the Python-format translations before submission.

    The specific operational method is to open the `bbp_ng/UTIL_translation.py` file before submission and change the value of the translation tuple variable `translations_tuple` to an empty tuple (i.e., `translations_tuple = ()`).

### Extract Translation Template

Before translating, it is important to first recognize that the text requiring translation for BBP consists of two parts. One part is the BBP plugin itself, whose text to be translated can be extracted by Blender's built-in multilingual plugin. The other part is the JSON file in the BME component that describes the structure, where the names of various showcase fields need to be translated. However, this part cannot be handled by Blender's multilingual plugin, as it is dynamically loaded. Fortunately, we have written an extractor that can extract the relevant text to be translated from the BME's JSON file. To do this, execute `uv run extract_jsons.py` in the folder where the previous script was run, and the script will extract the text to be translated and write it into the `i18n/bme.pot` file. Therefore, the next task is simply to extract the translation for the plugin portion.

First, you need to enable Blender's built-in multilingual plugin, "Manage UI translations". To enable it, you may also need to download the source code and translation repository corresponding to your version of Blender. For specific instructions, please refer to the [official Blender Documentation](https://developer.blender.org/docs/handbook/translating/translator_guide/). Once you have enabled the plugin and configured the appropriate related paths in the preferences, you can find the "I18n Update Translation" panel under the "Render" panel. You can then proceed to extract the translations by following these steps:

1. First, ensure that all Blender processes are closed; otherwise, the plugin will remain in a loading state, and modifications to the translated tuple variables will not take effect.
1. Change the value of the translation tuple variable `translations_tuple` in the plugin to an empty tuple (refer to the earlier mentioned submission notes). Setting the translation tuple to empty can reset the translation status of the plugin, ensuring that subsequent text extraction operations are not affected by any existing translations.
1. Open Blender, go to the "I18n Update Translation" panel, click "Deselect All" to uncheck all languages, and then only check the boxes next to the following languages (as BBP currently supports a limited number of languages):
    * Simplified Chinese (简体中文)
1. Click the "Refresh I18n Data" button at the bottom of the section, then in the pop-up window, select "Ballance Blender Plugin". After a short wait, the plugin will complete the extraction of the characters to be translated. At this point, the plugin merely extracts the translation fields into the source code of the plugin in a format recommended by Blender, using Python source code.
1. In order to obtain the desired editable POT file, you need to click the "Export PO" button. In the pop-up window, select the "Ballance Blender Plugin", and you can choose any folder for saving the location (for example, the desktop, as it will generate many files, including our desired POT file). Uncheck the "Update Existing" option on the right and ensure that "Export POT" is checked, then proceed to save. After the export is complete, you will find a translation template file named `blender.pot` and numerous `.po` files named after language identifiers in the folder you selected.
1. You need to copy `blender.pot` to the `i18n` folder and rename it to `bbp_ng.pot`. At this point, we have extracted all the content that needs to be translated.

### Merge Translation Template

There are currently two POT files in the `i18n` folder, which represent two sets of extracted text awaiting translation. We need to merge them. Execute `xgettext -o blender.pot bbp_ng.pot bme.pot` in the `i18n` folder to perform the merge. The merged `i18n/blender.pot` will serve as the translation template.

### Create New Language Translation

If BBP needs to support more languages in the future, you will need to create the corresponding PO translation files for the new languages from the POT files. You can create them through one of the following methods.

* By using software such as Poedit to open the POT file, select function like create new translation from it, and then save to create.
* Create a new language PO translation file using commands such as `msginit -i blender.pot -o zh_HANS.po -l zh_CN.utf8`.

There are various ways to create, but the only point to note is that you need to set the file name (if the file name is incorrect, Blender will refuse to accept it) and the area name (which will be used when using `msginit`, with the purpose of ensuring UTF8 format encoding) as shown in the table below.

|Language|File Name|Area Name|
|:---|:---|:---|
|Simplified Chinese (简体中文)|`zh_HANS.po`|`zh_CN.utf8`|

### Update Language Translation

Creating new language translations is not common; a more common practice is to update existing language translation files based on translation templates. You can update them through one of the following methods.

* Open the PO file using software such as Poedit, and then select to update from the POT file.
* Update using commands such as `msgmerge -U zh-HANS.po blender.pot --backup=none`.

### Start Translating

After updating the PO translation files for all languages, you may choose your preferred method for translation, such as using Poedit or editing directly.

The BBP requires the use of the KDE community's translation standards to standardize the translations of plugins. For example, you can find the KDE community's translation standards for Simplified Chinese on the [KDE China](https://kde-china.org/tutorial.html) website.

### Write Translation Back

The translation in PO format cannot be recognized by Blender. Therefore, after the translation is completed, you also need to utilize Blender's multilingual plugin to convert the PO file back into a translation in Python source code format that Blender can recognize. Due to issues with the design of Blender's multilingual plugin, we cannot directly use the "Import PO" function to convert the PO file back into Python source code format. You need to follow the steps below sequentially in order to import the PO translation into the plugin:

1. First, ensure that all Blender processes are closed; otherwise, the plugin will remain in a loading state, and modifications to the translated tuple variables will not take effect.
1. Change the value of the translation tuple variable `translations_tuple` in the plugin to an empty tuple (refer to the earlier notes regarding submissions). The purpose of this step is to ensure that the entire plugin lacks translation entries, so that when using the "Import PO" feature, Blender's multilingual plugin will consider all fields stored in the PO file as needing translation, thereby preventing situations where only a portion of the translations is imported (as the translations for the BME portion were merged later).
1. Open Blender, navigate to the "I18n Update Translation" panel, and following the procedure used when extracting the translation template, select only the languages that need to be translated from the language list.
1. Click the "Import PO" button in the bottom row, then select the "Ballance Blender Plugin" in the pop-up window, and choose the `i18n` folder for import. In this way, we have completed the process of importing the PO file into a Python source code format recognizable by Blender.

## Packaging

Starting from Blender 4.2 LTS, plugins are packaged using Blender's own packaging feature.

Assuming that the final output file is `redist/bbp_ng.zip`. If you are in the root directory of the project, execute the `blender --command extension build --source-dir bbp_ng --output-filepath redist/bbp_ ng.zip` command in a command line window to finish packaging. Please note `blender` is the executable Blender program.

Blender will package the plugin according to the instructions in `blender_manifest.toml` with the following files excluded:

* `__pycache__/`：Python cache.
* `.style.yapf`：code style description file.
* `.gitignore`：gitignore
* `.gitkeep`：folder placeholder
* `.md`：documentation

## Generating Help Documentation

Although this project will utilize the GitHub Page feature to provide help documentation, sometimes you may need to provide an offline version of the help documentation, this section will explain how to generate an offline version of the help documentation.

First you need to install `mkdocs` and `pymdown-extensions` via pip. Then go to the `docs` folder and run `mkdocs build --no-directory-urls`. After running the command you get a folder called `site`, which is the help documentation that can be viewed offline.
