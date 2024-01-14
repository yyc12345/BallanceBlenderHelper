# 技术信息

* BM文件标准：https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md
* 制图工具链标准及`meshes`文件夹下的文件的格式：https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md
* BMERevenge的JSON文件的格式：https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_v2.0_ZH.md

本插件配合了`fake-bpy-module`模块来实现类型提示以加快开发速度。本插件目前基于Blender 3.6，因此使用`pip install fake-bpy-module-latest==20230627`来安装Blender的类型提示库。 这主要是因为`fake-bpy-module`没有发布官方的适用于Blender 3.6的包，因此我只能通过选择最接近Blender 3.6版本发布时间的每日编译版本来安装它。
