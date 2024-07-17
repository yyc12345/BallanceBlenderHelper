# 技术信息

* BM文件标准：https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md
* 制图工具链标准及`meshes`文件夹下的文件的格式：https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md
* BMERevenge的JSON文件的格式：https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_v2.0_ZH.md

本插件配合了`fake-bpy-module`模块来实现类型提示以加快开发速度。使用如下命令来安装Blender的类型提示库。

* Blender 3.6: `pip install fake-bpy-module-latest==20230627`
* Blender 4.2: `pip install fake-bpy-module-latest==20240716`

这么做主要是因为`fake-bpy-module`没有发布官方的适用于指定Blender版本的包，因此我只能通过选择最接近Blender对应版本发布时间的每日编译版本来安装它。
