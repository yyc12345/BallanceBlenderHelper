# Legacy Alignment

`Ballance - 3ds Max Align` provides an alignment function similar to the way alignment works in 3ds Max.

The so-called legacy alignment feature is a perfect reimplementation of the 3ds Max alignment operations in Blender. It makes it possible for many mappers who switch from 3ds Max to Blender to get up to speed faster and provides some convenient alignment operations. The image below shows legacy alignment in action.

![](../imgs/legacy-align.png)

## Usgae

Legacy alignment supports aligning multiple objects to a single object by first selecting the objects to be aligned in turn, then selecting the reference object at the end of the alignment (i.e. making it the active object), and then clicking `Ballance - 3ds Max Align` to bring up the legacy alignment panel, after which you can start the alignment operation.

## Introduction of the Panel

In the panel, `Align Axis` specifies the axis you want to align to, you can multi-select here to specify more than one axis, without specifying any axis you will not be able to do the alignment operation, and thus you will not be able to click the `Apply` button.

`Current Object` indicates which instance was picked as the alignment reference. You may choose an active object in the scene, typically the last object you selected, or the 3D cursor. It is important to note that if you select active object mode, the active object will be excluded from the alignment operation and will not be moved, as the reference object is immovable. Conversely, if you select the 3D cursor, the active object will be included within the scope of the alignment operation.

`Current Object Align Mode` is the alignment mode for aligning to a reference object, which only appears when you select the active object in `Current Object`. Since the 3D cursor is merely a point, while objects occupy a certain space, we need to select a point in this space according to a specific pattern (described later) to be used for subsequent alignment operations. In this option, you specify what value you need to align to, with available selections including `Min` (minimum value on axis), `Center (Bounding Box)` (center of the bounding box), `Center (Axis)` (origin of the object), and `Max` (maximum value on axis). These options are consistent with the alignment options in 3ds Max.

The `Target Objects Align Mode` are the objects that are being aligned, there may be many of them, in this option it is also specified what values you need to refer to them for alignment. The options have the same meaning as `Current Object`.

The `Apply` button, when clicked, will press the current page's configuration into the operation stack and reset the settings above, allowing you to start a new round of alignment operations without having to perform a legacy alignment again. The number of operations in the stack is shown below the `Apply` button.

!!! info "What the Apply button does"
    Understanding this part is not useful for mapping, and you don't need to read what's in this box unless you're interested.

    By design, Blender doesn't support so-called "operations inside the Operator", but with a few tricks we simulated Apply effect similar to the one in 3ds Max.
    
    The Apply button is actually a specially displayed BoolProperty that listens to its value change event and, while avoiding recursive calls, records the current setting in a hidden CollectionProperty and resets its own value and displayed properties to make a visual "apply". Operator processes the alignment requirements accumulated in the CollectionProperty in turn when executing.
