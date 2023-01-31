# Ballance Blender Helper

[English version](README.md)

## 简介

这是一个用于Blender的插件，其主要是服务于Ballance制图。  
请选择打了tag的最新commit使用。最新的commit不能保证其是稳定可用的。  
本插件囊括了Ballance制图中可能会用到的各种功能。对于一些其它插件可以提供的功能，本插件不再重复提供。建议与下列插件合用以取得更好制图效果：

* [BenjaminSauder/SimpleLattice](https://github.com/BenjaminSauder/SimpleLattice)：快速创建晶格以便变形物体。
* [egtwobits/Mesh Align Plus](https://github.com/egtwobits/mesh_mesh_align_plus)：提供远超Blender原生的对齐功能。

## 技术信息

使用的BM文件标准可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/BMSpec_ZH.md)查找。  
使用的制图链标准以及`meshes`文件夹下的文件的格式可以在[这里](https://github.com/yyc12345/gist/blob/master/BMFileSpec/YYCToolsChainSpec_ZH.md)查找  
`jsons`文件夹下的，隶属于BMERevenge部分的文件的格式可以在[这里](https://github.com/yyc12345/gist/blob/master/BMERevenge/DevDocument_ZH.md)查找  

支持Blender的原则是支持当前最新的 **LTS** 版本，在最新的LTS版本释出之后会花一些时间迁移插件。当前插件基于**3.3.x**版本

## 安装

将`ballance_blender_plugin`直接复制到Blender插件目录`scripts/addons_contrib`内即可。然后在Blender偏好设置中启用即可（请在第一次安装后或更新插件后配置插件设置）。

## 功能介绍

### 插件设置

* External texture folder：请填写为Ballance的`Texture`目录，插件将从此目录下调用外置贴图文件（即Ballance原本带有的贴图文件）
* No component collection：处于此集合中的物体将被强制指定为非Component。如果留空则表示不需要这个功能。此功能通常用于机关模型强制替换。
* Temp texture folder：用于缓存从BM文件中提取的贴图文件，请安排一个平时不会被自动清理的目录。由于Blender会持续从这个目录读取贴图文件，因此不能随意清空。

Temp texture folder不允许同名文件存在，即如果我为2个地图分别导入两个BM，这两个BM中存在贴图文件名相同但图像不同的两个文件，那么后来的文件将会覆盖前面的文件，并进而导致前者导入后的文档再次打开时出现贴图错误。关于这个问题的解决方案，最好的方法是强制打包一次。在导入BM成功之后，选择`文件-外部数据-打包资源`，然后就可以安全清空Temp texture folder所在目录或导入新BM文件。如果有需要可以再点击`文件-外部数据-解包资源`，将贴图重新依赖到工程文件夹下的独立贴图库内。

### BM导入导出

点击`文件-导入-Ballance Map`以导入BM文件。  
在导入发生名称冲突时，可以对贴图，材质，网格，物体这四种类型的数据分别决定是使用现有数据还是创建新的数据。

点击`文件-导出-Ballance Map`以导出BM文件。  
可以选择导出一个集合或者是一个物体（Export mode），并给定对象（Export target）即可。  
尽管插件提供了Virtools组功能，让你可以直接在Blender中归组完毕，但BM导出功能仍然受限于制图链标准。因此如果不按照制图链标准进行命名，那么在导出过程中则无法享受一些便利性功能，例如最终导出的文件可能会过大等。

一旦导出BM，文件中所有的面将全部转换为三角形面，请提前做好备份。  
在导出时，建议使用平铺的集合结构，不要在集合内嵌套集合，因为这样可能会导致一些不必要的问题。  
BM文件的后缀名是BMX，表示BM的压缩。BMX与BM为同一含义。

### Ballance 3D

Ballance 3D是一套简单的用于制图3D相关的轻型工具集合，可以在3D视图左上角菜单栏中找到，菜单名称为Ballance。

#### 3ds Max Align

提供一种类似于3ds Max的对齐方式。当前活动物体将被设为参照对象，当前选中的所有物体（如果参照也被选中则去掉参照对象）将被视为操作对象（因此可以选择多个物体一起对齐到参照对象）。

#### Create Rail UV

为地图中的钢轨创建UV，你需要先选中需要添加类似钢轨UV的物体，然后点击这个按钮以创建。  
在弹出设置窗口中，可以选择使用的材质。还可以选择展开模式，在部分展开模式下，还可以选择投影轴和缩放大小。尽管Ballance最终会为所有钢轨重新上UV，一个在界面中看着赏心悦目的钢轨贴图还是比较重要的。  
如果您需要在Blender中呈现游戏内钢轨的贴图效果（表现为所谓的平滑贴图），您可以选择`TT_ReflectionMapping`展开模式。此功能由逆向游戏所用函数得来。这在渲染地图宣传画时可能会很有用。

#### Flatten UV

在物体编辑模式下，用于将当前选中面按某一边贴附到V轴上的模式，展开到UV上。  
此功能只支持凸多边形面，对于凹多边形面会有未定义行为。

编辑模式下，选中面，点击Flatten UV，然后选中一个边作为参考。  
如果最后生成的边贴附不对，比如把路面花纹贴到了下部，可以重新选择参考边再进行操作，直到正确为止。

### 快速添加结构

在添加菜单中我们添加了一系列较为常用的物体。添加后物体会移动到3D游标处。

#### Elements

添加机关，添加时还可以指定添加的小节等属性（对于飞船等唯一物体不会显示）

#### Rail section

添加钢轨截面，可以选择单轨还是双轨（只是决定添加的界面数量，并不会帮你旋转角度），以及轨道半径和轨道间距（默认值就是标准数据）。

#### Floors

一个非常强大的添加路面功能，隶属于BMERevenge工程的拓展。  
菜单中的Basic floor是基本的路面组件，而Derived floor则是由基本组件组成的常用组件。通常而言，大部分需要的路面都在Derived floor中。  
在选择一个路面后，可以根据其本身属性，设置最多2个延展方向的数值。此外还可以控制侧面和底面是否生成。  
与Ballance Map Editor相比，还具有减少大量无用顶点的优势。

可添加的路面大致分为平路面，凹路面，宽路面以及各类平台。  
此外还有变球器底座，平凹转换路面可供添加。

建议添加后除有特殊需求外，应该立即按距离合并顶点一次以避免各类问题。

### Virtools组

插件为每一个Blender物体添加了新的属性，被称为Virtools Group。与Virtools中的组具有相同的功能。  
选择一个物体，在`物体属性`面板可以找到`Virtools Group`面板。  
可以点击添加与删除图标，为物体归组和取消归组。  
亦可在列表中双击修改组名。

在点击添加按钮后，可以选择预定义，然后从所有合法的Ballance组名中选择一个添加。  
或选择自定义，然后输入你想要的组名添加。  

### Virtools材质

插件为每一个Blender材质添加了新的属性，被称为Virtools Material。它在Virtools材质与Blender材质之间架起沟通的桥梁。  
转到`材质属性`面板，选择一个材质，即可以找到`Virtools Material`面板。  
默认情况下，由用户创建的材质不启用Virtools Material，您可以通过点击`Virtools Material`面板的复选框来启用或关闭它。

在启用Virtools Material后，可以在`Basic Parameters`和`Advanced Parameters`中设置材质属性，就像在Virtools中操作一般。  
`Basic Parameters`是基础材质属性。`Advanced Parameters`则是与透明相关的材质属性，主要用于半透明柱子底部等。  
另外，`Basic Parameters`部分提供了预设功能，允许用户使用一些预设的材质设置，这些设置只影响4种基本颜色，方便使用。

`Operation`中的`Apply Virtools Material`将把Virtools Material应用到Blender材质上。  
而`Parse from Blender Principled BSDF`将尝试将一个原理化BSDF转换为Virtools材质数据。  
如果您是从Blender材质编辑的，请务必对此材质在导出前执行`Parse from Blender Principled BSDF`，或关闭Virtools Material功能，否则材质将无法正确保存。

### 按组选择

选择菜单中新增了一项按照Virtools归组数据进行筛选的功能。

该功能首先有5种不同的选择策略，与Blender的选择方法完全匹配（开始、扩选、相减、反转、相交）。只需像Blender选择那样使用它。
然后，选择你需要的组的名称，然后开始一次选择或筛选。

如果可以，请尽可能使用相减或相交模式。因为这样可以避免分析过多的物体。  
例如先选定一个大致的范围，然后使用相交模式过滤，比直接使用开始模式效率更高。

### 快速归组

插件在2个地方添加了为物体快速归组的功能。  
可以选择一系列物体，然后右键，在物体上下文菜单中找到快速归组功能。  
也可以在大纲窗口中，右键选择的物体，找到快速归组功能。

#### Group into

把选择物体归入你选择的组。  

#### Ungroup from

把选择物体从你选择的组中取消归组。  

#### Clear Grouping

清空选择物体的所有归组信息。

### 自动归组与重命名

在大纲视图中，对任意集合右键，可以得到自动归组与重命名菜单。

本插件目前支持两种命名标准。  
其一为技术信息章节已经阐述的制图链标准，在本插件中的名称为`YYC Tools Chains`。  
其二为[Imengyu/Ballance](https://github.com/imengyu/Ballance)所用命名标准，在本插件中的名称为`Imengyu Ballance`。

这些功能最终只会展示成功与否的一个概括性消息。如果您需要详细查看某个物体为什么不能转换，请点击`窗口-切换系统控制台`，插件在那里有更详细的输出。

#### Rename by Group

根据当前物体的归组信息，为其重命名为合适的名称。  
这通常用在迁移原版地图的过程中。一些Ballance衍生程序没有Virtools组概念，因此需要依赖名称来取得归组信息。

#### Convert Name

在不同命名标准之间切换。  
通常用于在不同Ballance衍生程序中进行转换。

#### Auto Grouping

根据给定的命名标准，为物体自动填充归组信息。  
需要注意的是，原有的归组信息会被覆盖。  
在制图过程中，如果你遵守了某些命名标准，则此功能可以为你自动完成归组功能。

