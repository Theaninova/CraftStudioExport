# CraftStudioExport
This is an Export Plugin for Blender Version 2.80 that allows you to export your models (all beit in a limited way) to a file format that is capable of bein imported into CraftStudio

## Thigs that work
* Rotation in Object mode
* Position in Object and Edit mode, the Origin of the object will be at the correct position through the pivot offset
* Parenting, as long as you reset the inverse Matrix of the parent. To do this, select the child, the go to `Object > Parent > Clear Parent Iverse` or press `alt + P` and select `Clear Parent Inverse`. The parent will then also be the hierarchial parent in CraftStudio.

## Usage
At the current point in time, this plugin is still very limited. For a correct export, make sure that
* Your cubes are not scaled in Object Mode. If you used the object mode to scale, you can press `ctrl + a` and select scale to fix that.
* Your cubes are only rotated using Object Mode. If you rotated the cube in edit mode, there is no way to fix it.
* Child objects have their Parent's Inverse Matrix reset.
