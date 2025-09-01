# 技术信息

## 标准与协议文档

* BM文件标准：https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md
* 制图工具链标准及`meshes`文件夹下的文件的格式：https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md
* BMERevenge的JSON文件的格式：https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_v2.0_ZH.md

## 开发辅助包

本插件配合了`fake-bpy-module`模块来实现类型提示以加快开发速度。使用如下命令来安装Blender的类型提示库。

* Blender 3.6: `pip install fake-bpy-module-latest==20230627`
* Blender 4.2: `pip install fake-bpy-module-latest==20240716`
* Blender 4.5: `pip install fake-bpy-module-latest==20250604`

这么做主要是因为`fake-bpy-module`没有很及时地发布适用于指定Blender版本的包，因此我只能通过选择最接近Blender对应版本离开`main`主线时间的每日编译版本来安装它（因为每日编译版本只编译`main`主线）。

!!! info "不采用Blender官方的bpy模块"
    Blender在PyPI上提供了官方的名为`bpy`的包，但我们不会采用它作为我们的开发辅助包。因为它基本上就是将Blender打包成了一个模块（也就意味着你基本上又把Blender重新下载了一遍），使得你可以通过Python来操纵Blender。这与我们使用一个仅提供类型提示的包来辅助我们插件开发的目的相悖。

## 版本号规则

BBP的版本号格式遵循[语义化版本](https://semver.org/lang/zh-CN/)。但略有区别：

* 主版本号只在重构整个插件时提升。
* 次版本号是常规更新使用。
* 修订号则是在不修改任何功能的情况下递增的版本号。例如4.2.1版本仅增加了对macOS Blender的更新，不更改任何功能。

在BBP发布一个正式版前，通常有3个阶段性版本，分别是：Alpha版本，Beta版本和RC版本。Alpha版本专注于功能性更新，用于检验新添加或修改的功能是否正常工作，不包含文档和翻译。Beta版本则专注于插件文档，而RC版本则关注于插件翻译。但这三个版本并非总是存在，如果更新内容较少，则可能会跳过其中一些版本，或直接进行发布。
