# Report Issue

## What Can Go Wrong

BBP is not perfect, and since BBP's Virtools file import/export module is written in C++, BBP is more prone to errors than other plugins, and the consequences of errors can be more serious (including but not limited to memory leaks, accidental deletion of user files, etc.).

In Blender, you will observe if the plugin execution goes wrong:

* The expected effect is not achieved
* A large stack of output text pops up at the mouse that you can't read
* After opening the console using `Window - Toggle System Console`, you can observe the Python exception output.

## What Part Went Wrong

For the BBP plugin, if you observe something like `BMap operation failed` in the Python exception output, or the `IronPad.log` file in the `<Plugin-Install-Location>/PyBMap` folder, it means that The BBP plugin's BMap section, written in C++, is in error, and **you need to immediately save your current Blender document and exit Blender**. Because the plugin is in an abnormal state at this point, you should not continue any operations.

If there is no such thing as the above, then this is just a normal Python code execution error and you don't need to worry too much about it, but the error is still fatal and it is recommended to exit Blender and report the error after doing all the necessary operations.

## Where to Report

If you have a GitHub account, you can create and report issues in [Issue page of BBP repository](https://github.com/yyc12345/BallanceBlenderHelper/issues).

If you can't do that and you have proper way to contact with plugin author, then reporting directly to the plugin author is fine.

## The Content of the Report

First of all you need to describe in detail how you raise this error and what are the results of this error. If you can upload the documentation that led to the error, please try to do so (if it's not convenient to post it publicly, you can send it to the author through a private way such as email).

You also need to provide the Python stack report output in the Blender console (use `Window - Toggle System Console` to open the console). If your error is an error in the BMap section, you also need to provide the `IronPad.log` and `IronPad.dmp` files in the `<Plugin-Install-Location>/PyBMap` folder to make it easier for developers to locate the error.
