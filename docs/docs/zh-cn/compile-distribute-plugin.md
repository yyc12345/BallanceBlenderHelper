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

从Blender 4.2 LTS开始，插件使用Blender自带的打包功能进行打包。

假定在项目根目录下执行命令，最终输出文件为`redist/bbp_ng.zip`，那么在命令行窗口中执行`blender --command extension build --source-dir bbp_ng --output-filepath redist/bbp_ng.zip`命令即可完成打包。其中`blender`为Blender的可执行程序。

Blender会根据`blender_manifest.toml`的指示，在排除下列文件的情况下将插件打包：

* `bbp_ng/raw_icons`：原始图片文件夹。
* `bbp_ng/raw_jsons`：原始JSON文件夹。
* `bbp_ng/tools`：编译用工具。
* `bbp_ng/.style.yapf`：代码风格描述文件
* `bbp_ng/.gitignore`：gitignore
* `bbp_ng/icons/.gitkeep`：文件夹占位符
* `bbp_ng/jsons/.gitkeep`：文件夹占位符

## 生成帮助文档

虽然本项目会利用GitHub Page功能提供帮助文档，但有时你可能需要提供帮助文档的离线版本，本节将会介绍如何生成离线版本的帮助文档。

首先你需要通过pip安装`mkdocs`和`pymdown-extensions`。然后转到`docs`文件夹下，运行`mkdocs build --no-directory-urls`。运行命令后得到一个名为`site`的文件夹，其中就是可以离线浏览的帮助文档。
