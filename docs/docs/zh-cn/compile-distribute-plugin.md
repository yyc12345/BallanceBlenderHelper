# 编译与分发插件

本页面将指导你编译插件以及分发它。

## 编译LibCmo与BMap

BBP的Virtools文件原生导入导出功能依赖BMap以及其Python绑定PyBMap来实现。为了分发插件，我们需要首先编译BMap及其前置LibCmo。而在编译前，你需要先确认你需要的BMap版本。因为BBP并不总是使用最新的BMap，例如你正在编译一个旧版的BBP，其显然不可能依赖最新的BMap。BMap也在不断升级中，其提供的功能也在不断变化，不同版本的BMap是不兼容的。BBP通常会在发布时写明其所用的BMap版本，如果BBP没有指出，你可能需要寻找与BBP发布时最近的BMap版本来编译。

在明确版本后，你需要访问[LibCmo位于GitHub的存储库](https://github.com/yyc12345/libcmo21)。然后克隆项目，使用Git命令转到对应版本（或者直接下载对应版本的源码）。然后按照LibCmo的编译手册编译得到BMap。在Windows上，你通常会得到`BMap.dll`和`BMap.pdb`这两个文件。而在Linux上，则会是`BMap.so`。

然后我们需要配置PyBMap。PyBMap是随LibCmo一起提供的。请按照PyBMap的手册，将编译得到的二进制BMap库，和PyBMap结合在一起。即完成PyBMap配置。

然后我们需要将配置好的PyBMap拷贝到本项目的根目录下即可完成此步（即存在`bbp_ng/PyBMap`文件夹，为配置好的PyBMap）。

## 生成资源

BBP的正常运行离不开一系列资源文件，而这些资源文件则需要一些处理才能够正常使用。

为了生成这些资源文件，首先需要转到`scripts`文件夹下，执行`uv sync`指令来还原脚本环境（需提前安装Astral UV）。

### 生成缩略图

BBP内置了一系列自定义图标，但这些图标都以其原始大小存储在库中。通过批量生成缩略图的操作，可以减小这些部分的大小，使得其适合在Blender中加载，也更方便分发。

执行`uv run build_icons.py`来生成缩略图。其实际上是将`assets/icons`目录下的原始图片生成对应的缩略图并存储于`bbp_ng/icons`文件夹下。

### 生成JSON文件

BBP中的BME组件依赖一系列JSON文件来描述原型。这些描述文件以JSON5格式存储在库中，方便编写者阅读。通过批量生成操作，将这些JSON5文件转换为JSON文件并压缩其大小，可以方便其在Blender中加载，以及方便插件分发。

如果你是插件开发者，或者是这些原型的编写者，那么你在生成JSON文件前，还需要额外地进行一项操作：验证JSON文件的正确性。BBP插件在加载这些JSON文件时会默认这些文件都是正确的，无错误的。如果将有错误的JSON文件放入（例如缺少部分字段或者拼写错误等），则会导致Blender在创建原型时抛出错误。所以验证JSON文件的正确性很有必要。执行`uv run validate_jsons.py`来验证所有原型文件。如果没有任何报错，则验证无误。需要注意的是，验证器并非完美的，它只能尽可能地验证数据，确保一些常见的错误，例如字段名称拼写错误等，不会发生，并不能100%保证验证后的文件没有错误。

对于编译人员而言，只需要执行`uv run build_jsons.py`来生成JSON文件即可。其实际上是将`assets/jsons`目录下的原始JSON5文件读取，压缩，再以JSON格式写入到`bbp_ng/jsons`文件夹下。

### 生成机关网格

BBP中内置了Ballance所有机关占位符的网格信息。执行`uv run build_meshes.py`来部署这些内容，其简单地将`assets/meshes`下的网格文件复制到`bbp_ng/meshes`文件夹下。

## 翻译

BBP插件支持多语言功能，因此在正式发布前我们需要先提取并更新要翻译的内容，翻译完所有内容后，再进行下一步操作。

Blender对于插件的多语言支持不尽如人意，且BBP的设计比较特殊，因此BBP采用了一套与Blender官方推荐的插件翻译管理方式不同的方式来管理翻译：即使用PO文件来管理翻译，而非官方推荐的Python脚本格式。

!!! info "不要提交Python格式的翻译"
    如上文所述，BBP使用PO文件来管理翻译，而不是Blender官方建议的Python源码格式。但这并不能阻止Blender的多语言插件将Python源码格式的翻译写入到插件源码中。重复提交翻译不仅增加仓库体积，也不利于管理，因此BBP要求你在提交前需要删除Python格式的翻译。

    具体的操作方法是在提交前，打开`bbp_ng/UTIL_translation.py`文件，将翻译元组变量`translations_tuple`的值改为空元组（即`translations_tuple = ()`）。

### 提取翻译模板

在翻译之前，首先你需要意识到，BBP需要翻译的文本由两部分组成，一部分是BBP插件本身，可以通过Blender自带的多语言插件来实现待翻译文本的提取。另一部分是BME组件中的用于描述结构的JSON文件，其中各个展示用字段的名称需要进行翻译，而这一部分Blender的多语言插件无能为力，因为它是动态加载的。幸运的是，我们已经写好了一个提取器，可以提取BME的JSON文件中的相关待翻译文本。就是在上一步运行脚本的文件夹中，执行`uv run extract_jsons.py`，脚本就会提取待翻译文本并写入`i18n/bme.pot`文件中。那么接下来的任务就只剩下提取插件部分的翻译了。

首先你需要启用Blender内置的多语言插件Manage UI translations。为了启用它，你可能还需要下载对应Blender版本的源代码和翻译仓库，具体操作方法可参考[Blender的官方文档](https://developer.blender.org/docs/handbook/translating/translator_guide/)。在启用插件并在偏好设置中配置了合适的相关路径后，你就可以在Render面板下找到I18n Update Translation面板，接下来就可以提取翻译了。按照以下步骤提取翻译：

1. 首先确保关闭了所有Blender进程，否则插件会保持在加载状态，对翻译元组变量的修改会不起作用。
1. 将插件中翻译元组变量`translations_tuple`的值改为空元组（参见前文有关提交的注意事项）。将翻译元组设置为空可以将插件的翻译状态归零，使得后文进行的文本提取操作不会受到已有翻译的干扰。
1. 打开Blender，转到I18n Update Translation面板，点击Deselect All取消所有语言的选中，然后仅勾选下列语言右侧的框（因为BBP目前仅支持有限的语言）：
    * Simplified Chinese (简体中文)
1. 点击最下方一栏的Refresh I18n Data按钮，然后在弹出的窗口中选择Ballance Blender Plugin，等待一会后，插件就会完成待翻译字符的提取。此时插件只是将他们按照Blender推荐的方式，以Python源码的格式将翻译字段提取到了插件的源代码中。
1. 为了获得我们希望的，可以用于编辑的POT文件，还需要点击Export PO按钮，在弹出的窗口中选择Ballance Blender Plugin，保存的位置可以选择任意的文件夹（例如桌面，因为它会产生许多文件，其中只有POT文件才是我们想要的），取消勾选右侧的Update Existing选项并确保Export POT是勾选的，最后进行保存。导出完成后，可以在你选择的文件夹中找到一个名为`blender.pot`的翻译模板文件，以及众多以语言标识符为文件名的`.po`文件。
1. 你需要复制`blender.pot`到`i18n`文件夹下，并将其重命名为`bbp_ng.pot`。至此我们提取了所有需要翻译的内容。

### 合并翻译模板

现在`i18n`文件夹下有两个POT文件，分别代表了两部分提取的待翻译文本，我们需要把他们合并起来。在`i18n`文件夹执行`xgettext -o blender.pot bbp_ng.pot bme.pot`来进行合并。合并完成后的`i18n/blender.pot`将用作翻译模板。

### 创建新语言翻译

如果未来BBP需要支持更多语言，你需要从POT文件为新语言创建其对应的PO翻译文件。你可以通过以下方式之一来创建它们。

* 通过使用Poedit等软件打开POT文件，选择创建新的翻译，再进行保存来创建。
* 通过诸如`msginit -i blender.pot -o zh_HANS.po -l zh_CN.utf8`的命令来创建新语言的PO翻译文件。

创建的方式多种多样，唯一需要注意的是你需要按下表所示设定文件名（文件名错误，Blender会拒绝接受）和区域名称（使用`msginit`时会用到，目的是确保是UTF8格式编码的）。

|语言|文件名|区域名称|
|:---|:---|:---|
|Simplified Chinese (简体中文)|`zh_HANS.po`|`zh_CN.utf8`|

### 更新语言翻译

创建新的语言翻译并不常见，更为常见的操作是根据翻译模板，对现有语言翻译文件进行更新。你可以通过以下方式之一来更新它们

* 通过Poedit等软件打开PO文件，再选择从POT文件更新。
* 通过诸如`msgmerge -U zh-HANS.po blender.pot --backup=none`的命令来更新。

### 进行翻译

在更新完所有语言的PO翻译文件后，你可以选择你喜欢的方式来进行翻译，例如使用Poedit或直接进行编辑。

BBP要求使用KDE社区的翻译规范来规范插件的翻译。例如你可以在[KDE中国相关网页](https://kde-china.org/tutorial.html)找到KDE社区有关简体中文的翻译标准。

### 翻译回写

PO格式的翻译并不能被Blender识别，因此在翻译完成后，你还需要继续借助Blender的多语言插件，将PO文件回写成Blender可识别的Python源码格式的翻译。由于Blender的多语言插件设计的问题，我们不能直接使用Import PO功能将PO文件回写成Python源码格式。你需要按照下列步骤依次操作才可以将PO翻译导入插件中：

1. 首先确保关闭了所有Blender进程，否则插件会保持在加载状态，对翻译元组变量的修改会不起作用。
1. 将插件中翻译元组变量`translations_tuple`的值改为空元组（参见前文有关提交的注意事项）。这一步操作的意图是让整个插件不存在翻译条目，这样之后在使用Import PO功能的时候，Blender的多语言插件就会认为PO文件中存储的所有字段都是要翻译的，就不会出现只导入了一部分翻译的情况（因为BME部分的翻译是后来合并入的）。
1. 打开Blender，转到I18n Update Translation面板，按照提取翻译模板时的操作方法，在语言列表中仅选中需要翻译的语言。
1. 点击最下方一栏的Import PO按钮，然后在弹出的窗口中选择Ballance Blender Plugin，然后选择`i18n`文件夹进行导入。这样我们就完成了将PO文件导入为Blender可识别的Python源码格式的操作。

## 打包

从Blender 4.2 LTS开始，插件使用Blender自带的打包功能进行打包。

假定在项目根目录下执行命令，最终输出文件为`redist/bbp_ng.zip`，那么在命令行窗口中执行`blender --command extension build --source-dir bbp_ng --output-filepath redist/bbp_ng.zip`命令即可完成打包。其中`blender`为Blender的可执行程序。

Blender会根据`blender_manifest.toml`的指示，在排除下列文件的情况下将插件打包：

* `__pycache__/`：Python缓存
* `.style.yapf`：代码风格描述文件
* `.gitignore`：gitignore
* `.gitkeep`：文件夹占位符
* `.md`：文档

## 生成帮助文档

虽然本项目会利用GitHub Page功能提供帮助文档，但有时你可能需要提供帮助文档的离线版本，本节将会介绍如何生成离线版本的帮助文档。

首先你需要通过pip安装`mkdocs`和`pymdown-extensions`。然后转到`docs`文件夹下，运行`mkdocs build --no-directory-urls`。运行命令后得到一个名为`site`的文件夹，其中就是可以离线浏览的帮助文档。
