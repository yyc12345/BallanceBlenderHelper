# Legacy Alignment

`Ballance - 3ds Max Align` provides an alignment function similar to the way alignment works in 3ds Max.

The so-called legacy alignment feature is a perfect reimplementation of the 3ds Max alignment operations in Blender. It makes it possible for many mappers who switch from 3ds Max to Blender to get up to speed faster and provides some convenient alignment operations. The image below shows legacy alignment in action.

![](../imgs/legacy-align.png)

## Usgae

Legacy alignment supports aligning multiple objects to a single object by first selecting the objects to be aligned in turn, then selecting the reference object at the end of the alignment (i.e. making it the active object), and then clicking `Ballance - 3ds Max Align` to bring up the legacy alignment panel, after which you can start the alignment operation.

## Introduction of the Panel

In the panel, `Align Axis` specifies the axis you want to align to, you can multi-select here to specify more than one axis, without specifying any axis you will not be able to do the alignment operation, and thus you will not be able to click the `Apply` button.

`Current Object` is the alignment reference object, which is the active object in the scene, usually the last object you selected. This option specifies what value you need to reference for alignment, with `Min` (minimum value on axis), `Center (Bounding Box)` (center of the bounding box), `Center (Axis)` (origin of the object), and `Max` (maximum value on axis) available. These options are consistent with the alignment options in 3ds Max.

The `Target Objects` are the objects that are being aligned, there may be many of them, in this option it is also specified what values you need to refer to them for alignment. The options have the same meaning as `Current Object`.

The `Apply` button, when clicked, will press the current page's configuration into the operation stack and reset the settings above, allowing you to start a new round of alignment operations without having to perform a legacy alignment again. The number of operations in the stack is shown below the `Apply` button.

!!! info "What the Apply button does"
    Understanding this part is not useful for mapping, and you don't need to read what's in this box unless you're interested.

    By design, Blender doesn't support so-called "operations inside the Operator", but with a few tricks we simulated Apply effect similar to the one in 3ds Max.
    
    The Apply button is actually a specially displayed BoolProperty that listens to its value change event and, while avoiding recursive calls, records the current setting in a hidden CollectionProperty and resets its own value and displayed properties to make a visual "apply". Operator processes the alignment requirements accumulated in the CollectionProperty in turn when executing.
