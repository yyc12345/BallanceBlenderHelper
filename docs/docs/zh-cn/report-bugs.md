# 报告问题

## 什么会出错

BBP不是完美的，由于BBP的Virtools文件导入导出模块是由C++编写的，因此BBP比其他插件更容易出错，且出错的后果可能会更严重（包括但不限于内存泄漏，误删除用户文件（像[少前2事件](https://www.163.com/dy/article/IGUHP2TE0526D7OK.html)一样）等）。

在Blender中，如果插件执行出错，你将会观察到：

* 期待的效果没有达成
* 鼠标处弹出一大堆你看不懂的堆栈输出文本
* 使用`Window - Toggle System Console`打开控制台后，可以观察到Python的异常输出。

## 哪部分出错了

对于BBP插件而言，如果你在Python异常输出中观察到类似于`BMap operation failed`的字样，或者在`<插件安装位置>/PyBMap`文件夹下观察到了`IronPad.log`文件，则说明BBP插件的由C++编写的BMap部分出错了，**你需要立即保存你当前的Blender文档，并退出Blender。** 因为此时插件已处于非正常状态，你不应继续任何操作。

如果并没有上述情况，那么这就只是普通的Python代码执行错误，不需要过度担心，但错误仍然是致命的，建议做完所有必要的操作后退出Blender并报告错误。

## 向何处报告

如果你有GitHub账户，你可以在[BBP的存储库的Issue页面](https://github.com/yyc12345/BallanceBlenderHelper/issues)中创建并汇报问题。

如果做不到，且你有合适的渠道可以联系到插件作者，则直接汇报给插件作者也是可以的。

## 报告的内容

首先你需要详细描述你是如何引发这个错误的，这个错误有什么结果。如果可以上传导致错误的文档，请尽量上传（如果不方便公开发布，可以通过邮件等私有渠道发送给作者）。

你还需要提供Blender控制台中输出的Python堆栈报告（使用`Window - Toggle System Console`打开控制台）。如果你的错误是BMap部分的错误，你还需要提供`<插件安装位置>/PyBMap`文件夹下的`IronPad.log`和`IronPad.dmp`文件以方便开发者定位错误。
