# Install Plugin

## Determining the Version

The principle of BBP's Blender support is to support the latest **LTS** version, and to spend some time migrating the plugin after the latest LTS version is released. The current plugin version **4.0** is based on Blender version **4.2.x**.

Theoretically, BBP will work fine on other versions of Blender if no major changes have been made. For example you can try to run BBP plugin based on Blender 3.6 LTS on Blender 4.0. However, the developers of BBP do not deal with bugs that only appear in non-LTS versions. before installing the plugin, please select the appropriate version.

## Uninstall the Old Plugin

If you have used BBP before then you need to uninstall it first. Older versions of BBP are usually installed in the following locations:

* `<Blender>/3.6/scripts/addons/ballance_blender_plugin`: BBP 3.0 or lower version.
* `<Blender>/3.6/scripts/addons_contrib/ballance_blender_plugin`: BBP 3.0 or lower version.
* `<Blender>/3.6/scripts/addons/bbp_ng`: BBP 4.0 internal test version
* `%APPDATA%/Blender Foundation/Blender/3.6/scripts/addons/bbp_ng`: BBP 4.0 internal test version
* `%APPDATA%/Blender Foundation/Blender/4.2/extensions/user_default/bbp_ng`: BBP 4.0 or higher version

You just need to disable the plugin in Blender first (uncheck the box in front of the plugin name) and then delete these folders (if they exist) to uninstall the plugin completely. The `<Blender>` in the path refers to the location of your Blender installation. The `3.6` and `4.2` in the path are the version numbers of your Blender installation, which need to be adjusted according to the version you have installed, and subsequent occurrences of version numbers should be understood as the same meanings.

!!! warning "Should not use Blender's plugin uninstall feature"
    It is not possible to uninstall BBP using the plugin uninstall function on the Blender plugins page, because BBP loads the Virtools file read/write library BMap into Blender as soon as it is loaded by Blender (whether it is enabled or not). if you remove it while Blender is running, you will get an access denied error. Therefore you must manually delete the plugin directory after closing Blender.

    If you are really not sure where the plugin is installed, you can find the `File` property in the Addons page of Blender's Preferences, and the folder it points to where the file is located is the folder to be deleted.

!!! info "`ballance_blender_plugin` and `bbp_ng`"
    `ballance_blender_plugin` is the module name of the old version of the BBP plugin (before version 4.0) and `bbp_ng` is the module name of the new version of the BBP plugin (after and including version 4.0). Both are provided in order to ensure that the user actually deleted the old version of the plugin.

!!! info "`addons` and `addons_contrib`"
    After Blender version 3.6 LTS, i.e. BBP version 3.3, Blender no longer supports Testing type plugins. As a result, the `addons_contrib` folder, which was dedicated to installing Testing plugins, is no longer used, and plugins need to be installed uniformly in `addons`. Both are provided to ensure that the user actually deletes the old version of the plugin.

!!! info "`addons` and `extensions`"
    In Blender version 4.2 LTS, Blender uses Extensions instead of Addons to describe plugins. This has resulted in a change in where plugins are installed. Both are provided in order to ensure that the user actually removes the old version of the plugin.

## Download Plugin

You can download the latest plugin via [the Release page of the GitHub codebase for this project](https://github.com/yyc12345/BallanceBlenderHelper/releases). Plugins are provided as ZIP archives.

In addition, you can also get this plugin in the mapping tutorial web disk provided by yyc12345:

* Overworld: [Mega](https://mega.nz/#F!CV5SyapR!LbduTW51xmkDO4EDxMfH9w) (located in `Mapping` directory)
* Chinese Region Only: [Baidu Web Disk](https://pan.baidu.com/s/1QgWz7A7TEit09nPUeQtL7w?pwd=hf2u) (Extract code: hf2u, located under `制图插件（新）`)

!!! warning “Do not download this repository directly for use”
    Please do not download this project's repository directly for use. First of all, because the latest commit is not guaranteed to be stable and available. The second reason is that this project contains some C++ code that needs to be compiled, and must be compiled before it can be used. See [Compile and Distribute Plugin](./compile-distribute-plugin.md) for more information.

## Install Plugin

Open Blender, click `Edit - Preferences`, in the window that opens go to the `Add-ons` tab, click on the arrow at the top right of the window and then click on the `Install from Disk.... ` button, select the ZIP archive you just downloaded, and the installation will be completed. If you don't see it in the list you can click the Refresh button or restart Blender.

You can also choose to install the plugin manually (if the above installation method fails), go to `%APPDATA%/Blender Foundation/Blender/4.2/extensions/user_default`, create a folder named `bbp_ng` and go inside it, extract the downloaded ZIP archive to this folder, start Blender and you will find BBP in the list of addons.

The name of BBP plugin in the list is `Ballance Blender Plugin`, when you find it, you can enable the plugin by checking the box on the left side of the name. The Preferences window after the plugin is installed is shown below.

![](../imgs/config-plugin.png)

After **installing or updating** the plugin, be sure to [configure plugin](./configure-plugin.md) before using it, see the next section for details.
