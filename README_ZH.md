# Ballance Blender Helper

[English version](README.md)

## 简介

这是一个用于Blender的插件，其主要是服务于Ballance制图。

目前仅仅包含比较基本的功能，其余的更多有用的功能将在未来版本中进行开发

## 技术信息

使用的BM文件标准可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md)查找

使用的制图链标准以及`meshes`文件夹下的文件的格式可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md)查找

支持Blender的原则是支持当前最新的 **LTS** 版本，在最新的LTS版本释出之后会花一些时间迁移插件。当前插件基于2.83.x版本

## 功能介绍

### 插件设置

* External texture folder：请填写为Ballance的Texture目录，插件将从此目录下调用外置贴图文件（即Ballance原本带有的贴图文件）
* No component collection：处于此集合中的物体将被强制指定为非Component。如果留空则表示不需要这个功能。
* Temp texture folder：用于缓存从BM文件中提取的贴图文件，请安排一个平时不会被自动清理的目录。由于Blender会持续从这个目录读取贴图文件，因此不能随意清空。并且其也不允许同名文件存在，即如果我为2个地图分别导入两个BM，这两个BM中存在贴图文件名相同但图像不同的两个文件，那么后来的文件将会覆盖前面的文件，并进而导致前者导入后的文档再次打开时出现贴图错误。关于解决这个问题的方法，请参考后续的BM导入导出

### BM导入导出

对于导入而言，为了防止贴图出错，最好的方法是强制打包一次。在导入BM成功之后，选择全部打包到blend文件，然后清空Temp texture folder所在目录，然后如果有需要可以再点击解包到文件，将贴图重新依赖到工程文件夹下的贴图库内。

对于导出，可以选择导出一个集合或者是一个物体（Export mode），并给定对象（Export target）即可。

需要注意的是，一旦导出BM，文件中所有的面将全部转换为三角形面，请做好备份。并且建议使用平铺的集合结构，不要在集合内嵌套集合，可能会导致一些不必要的问题。

### Ballance 3D

Ballance 3D是一套简单的用于制图3D相关的轻型工具集合，可以在3D视图右上角找到。

#### Super Align

提供一种类似于3ds Max的对齐方式。当前活动物体将被设为参照对象，当前选中的所有物体（如果参照也被选中则去掉参照对象）将被视为操作对象（因此可以选择多个物体一起对齐到参照对象）。

#### Create Rail UV

为地图中的钢轨创建UV，你需要先选中需要添加类似钢轨UV的物体，然后点击这个按钮以创建。在创建之前需要保证选中物体在右侧属性列表中至少有一个UV（若有多个UV则会只操作第一个）。

## 安装

将`ballance_blender_plugin`直接复制到Blender插件目录`scripts/addons_contrib`内即可。然后在Blender偏好设置中启用即可（记得配置插件设置）。

## 后续开发计划

* 直接从添加菜单中添加机关
* 在Blender中创建自定义路面的辅助工具（例如辅助添加路面UV等）
