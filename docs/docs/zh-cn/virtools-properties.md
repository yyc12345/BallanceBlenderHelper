# Virtools属性

!!! info "制作中..."
    手册的这部分还在制作当中。稍安勿躁。

## Virtools组

BBP插件为每一个Blender物体添加了新的属性，被称为Virtools Group。与Virtools中的组具有相同的功能。选择一个物体，在`Object`属性面板可以找到`Virtools Group`面板。

![](../imgs/virtools-group.png)

在`Virtools Group`面板中，可以点击添加为物体归组。在点击添加按钮后，可以选择预定义，然后从所有合法的Ballance组名中选择一个添加。或选择自定义，然后输入你想要的组名添加。也可以点击删除按钮，删除选中的Virtools组。最后，可以通过点击垃圾桶按钮一次性删除这个物体的所有组数据（删除前会让你确认）。

BBP还在Blender的其它菜单提供了对Virtools组的访问，具体内容请参阅[按组操作](./group-operations.md)。

## Virtools材质

插件为每一个Blender材质添加了新的属性，被称为Virtools Material。它在Virtools材质与Blender材质之间架起沟通的桥梁。转到`Material`属性面板，选择一个材质，即可以找到`Virtools Material`面板。

![](../imgs/virtools-material.png)

可以在`Virtools Material`面板中设置材质属性，就像在Virtools中操作一般。`Virtools Material`面板中所有的材质参数均为Virtools中材质参数的映射，将准确地反映到最后保存的Virtools文档中。

`Virtools Material`面板提供了预设功能，点击顶部的`Preset`按钮即可开始进行预设。预设功能允许用户使用一些预设的材质设置，例如路面顶面，侧面的材质数据等，方便使用。需要注意的是，使用预设不会影响材质的贴图选项，当应用预设后，您仍然需要手动设置材质的贴图。

`Virtools Material`面板同样提供把`Virtools Material`面板中的材质数据反应到Blender材质上的功能，以在Blender中获得可视的效果。点击顶部的`Apply`按钮即可执行此功能。当您在Blender中保存Virtools文档时，Virtools文档中的材质数据将从`Virtools Material`面板中指定的数值获取，而不会从Blender材质中获取。这意味一个正确的材质设置过程是：先在`Virtools Material`面板中编辑材质参数，然后使用`Apply`按钮将其反映到Blender材质上，而不是直接去编辑Blender材质。

TODO: 添加有关贴图选择按钮的帮助内容

## Virtools贴图

TODO...

![](../imgs/virtools-texture.png)
