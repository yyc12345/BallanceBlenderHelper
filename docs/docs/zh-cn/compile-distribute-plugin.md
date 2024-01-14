# 编译与分发插件

本页面将指导你编译插件以及分发它。

## 编译LibCmo与BMap

BBP的Virtools文件原生导入导出功能依赖BMap以及其Python绑定PyBMap来实现。为了分发插件，我们需要首先编译BMap及其前置LibCmo。而在编译前，你需要先确认你需要的BMap版本。因为BBP并不总是使用最新的BMap，例如你正在编译一个旧版的BBP，其显然不可能依赖最新的BMap。BMap也在不断升级中，其提供的功能也在不断变化，不同版本的BMap是不兼容的。BBP通常会在发布时写明其所用的BMap版本，如果BBP没有指出，你可能需要寻找与BBP发布时最近的BMap版本来编译。

在明确版本后，你需要访问[LibCmo位于GitHub的存储库](https://github.com/yyc12345/libcmo21)。然后克隆项目，使用Git命令转到对应版本（或者直接下载对应版本的源码）。然后按照LibCmo的编译手册编译得到BMap。在Windows上，你通常会得到`BMap.dll`和`BMap.pdb`这两个文件。而在Linux上，则会是`BMap.so`。

然后我们需要配置PyBMap。PyBMap是随LibCmo一起提供的。请按照PyBMap的手册，将编译得到的二进制BMap库，和PyBMap结合在一起。即完成PyBMap配置。

然后我们需要将配置好的PyBMap拷贝到本项目的`bbp_ng/PyBMap`下即可完成此步。

## 生成缩略图和压缩JSON

BBP内置了一系列自定义图标，以及其组件BME需要的用于描述结构的JSON文件。通过批量生成缩略图和压缩JSON的操作，可以减小这些部分的大小，使得其适合在Blender中加载，也更方便分发。

转到`bbp_ng/tools`文件夹下，运行`python3 build_icons.py`将批量生成缩略图（此功能需要PIL库，请提前通过pip安装）。其实际上是将`bbp_ng/raw_icons`目录下的原始图片生成对应的缩略图并存储于`bbp_ng/icons`文件夹下。运行`python3 build_jsons.py`将压缩JSON。其实际上是将`bbp_ng/raw_jsons`目录下的原始JSON文件读取，压缩，再写入到`bbp_ng/jsons`文件夹下。

## 打包

将`bbp_ng`文件夹压缩成ZIP文件即可完成打包工作。需要注意的是下列文件或文件夹不应被打包：

* `bbp_ng/raw_icons`：原始图片文件夹。
* `bbp_ng/raw_jsons`：原始JSON文件夹。
* `bbp_ng/.style.yapf`：代码风格描述文件
* `bbp_ng/.gitignore`：gitignore
* `bbp_ng/icons/.gitkeep`：文件夹占位符
* `bbp_ng/jsons/.gitkeep`：文件夹占位符

打包后的ZIP文件打开后如果有且只有`bbp_ng`一个文件夹，则代表打包成功。切勿直接将`bbp_ng` **内部的文件** 直接打包到ZIP文件中。

这样打包后的ZIP文件既可以直接通过Blender插件的安装功能直接安装，也可以解压在插件目录下完成安装。

## 生成帮助文档

虽然本项目会利用GitHub Page功能提供帮助文档，但有时您可能需要提供帮助文档的离线版本，本节将会介绍如何生成离线版本的帮助文档。

首先您需要通过pip安装`mkdocs`和`pymdown-extensions`。然后转到`docs`文件夹下，运行`mkdocs build --no-directory-urls`。运行命令后得到一个名为`site`的文件夹，其中就是可以离线浏览的帮助文档。
