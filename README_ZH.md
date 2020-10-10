# Ballance Blender Helper

[English version](README.md)

## 简介

这是一个用于Blender的插件，其主要是服务于Ballance制图。

目前仅仅包含比较基本的功能，其余的更多有用的功能将在未来版本中进行开发。

请使用Release中打tag的最新版本，最新的commit不能保证其是稳定可用的

## 技术信息

使用的BM文件标准可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md)查找

使用的制图链标准以及`meshes`文件夹下的文件的格式可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md)查找

`jsons`文件夹下的，隶属于BMERevenge部分的文件的格式可以在[这里](https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_ZH.md)查找

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

#### 3ds Max Align

提供一种类似于3ds Max的对齐方式。当前活动物体将被设为参照对象，当前选中的所有物体（如果参照也被选中则去掉参照对象）将被视为操作对象（因此可以选择多个物体一起对齐到参照对象）。

#### Create Rail UV

为地图中的钢轨创建UV，你需要先选中需要添加类似钢轨UV的物体，然后点击这个按钮以创建。

在弹出设置窗口中，可以选择使用的材质。还可以选择展开模式，对于较短的钢轨，可以选择Point模式，对于较长的钢轨，可以使用Uniform模式，如果需要手动调整缩放比，请选择Scale模式并指定比率（不推荐）。

### Flatten UV

在物体编辑模式下，用于将当前选中面按某一边贴附到V轴上的模式，展开到UV上。注意，只支持凸边面。

编辑模式下，选中面，点击Flatten UV，然后滚动滑条选中一个边作为参考，如果最后生成的边贴附不对，比如把路面花纹贴到了下部，可以撤销并重新选择参考边，直到正确为止。

### 添加菜单

在添加菜单中我们添加了一套较为常用的物体。添加后物体会移动到3D游标处。可以用Shift+A调出。

#### Elements

添加机关，添加时还可以指定添加的小节等属性（对于飞船等唯一物体不会显示）

#### Rail section

添加钢轨截面，可以选择单轨还是双轨（只是决定添加的界面数量，并不会帮你旋转角度），以及轨道半径和轨道间距

#### Floors

添加路面，隶属于BMERevenge工程的拓展。Basic floor是基本的路面组件，而Derived floor则是由基本组件组成的常用组件。可以根据其属性设置其延展，以及各边是否显示。其还具有减少顶点的优点。

建议添加后除非有消除面的需求外，应该立即按距离合并顶点一次以避免各类问题

## 安装

将`ballance_blender_plugin`直接复制到Blender插件目录`scripts/addons_contrib`内即可。然后在Blender偏好设置中启用即可（记得配置插件设置）。

