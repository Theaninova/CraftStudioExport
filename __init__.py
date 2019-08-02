# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "CraftStudio (.csmodel)",
    "author" : "Thea Schöbl",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "File > Export > CraftStudio (.csmodel)",
    "description" : "Export mesh to CraftStudio Model (.csmodel)",
    "warning" : "",
    "category" : "Import-Export"
}

import bpy
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector
import time
import struct

FILE_SIGNATURE = bytes([0x00, 0x05, 0x00])

# This is where the magic happenes
def do_export(context, props, filepath):
    file = open(filepath, "wb")

    file.write(FILE_SIGNATURE) #File signature

    model_collection = bpy.data.collections['CSMODEL']
    current_id = 0

    #TODO: determine the amount of blocks
    amount_of_blocks = len(model_collection.all_objects)
    file.write(amount_of_blocks.to_bytes(2, byteorder='little', signed=False))
    file.write(amount_of_blocks.to_bytes(2, byteorder='little', signed=False))
    #Yes, we actually need it twice for whatever reason. I didn't invent this format.

    name_id_dict = {}
    name_pivot_dict = {}

    for obj in model_collection.all_objects:
        name_id_dict[obj.data.name] = current_id #Save the object to the dictonary for parenting
        name_pivot_dict[obj.data.name] = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector()) #Calculate the center of the object
        current_id = current_id + 1 #Increment ID, as each one is unique

    #START DOING BLOCK STUFF
    for obj in model_collection.all_objects:
        file.write(name_id_dict[obj.data.name].to_bytes(2, byteorder='little', signed=False)) #Write the ID
        
        #Check Parents
        if obj.parent is not None and obj.parent.data is not None:
            #Check and write parent ID
            file.write(name_id_dict[obj.parent.data.name].to_bytes(2, byteorder='little', signed=False))
        else:
            file.write(0xFFFF.to_bytes(2, byteorder='little', signed=False)) #No parent

        #Write Name
        file.write(len(obj.data.name).to_bytes(1, byteorder='little', signed=False))
        if len(obj.data.name) >= 0xFF: #TODO: check if that is correct
            print('FATAL ERROR: name is longer than 16 characters')
            return False
        file.write(str.encode(obj.data.name))

        #Write Position
        obj_location = obj.location if obj.parent is None or obj.parent.data is None else obj.location - name_pivot_dict[obj.parent.data.name]
        for val in obj_location:
            file.write(bytearray(struct.pack("f", val/16)))
        
        #Write Pivot Offset
        object_center = name_pivot_dict[obj.data.name]
        for val in object_center:
            file.write(bytearray(struct.pack("f", val/16)))

        #Size as Float
        size = obj.dimensions #Just take the dimensions
        for val in size:
            file.write(bytearray(struct.pack("f", val)))

        #Rotation
        quaternion = obj.rotation_euler.to_quaternion()
        for val in quaternion:
            file.write(bytearray(struct.pack("f", val)))

        #TODO: Proper Size
        block_size = [1, 1, 1]
        for val in block_size:
            file.write(val.to_bytes(2, byteorder='little', signed=False))

        file.write(0x1.to_bytes(1, byteorder='little', signed=False))

        #TODO: Proper UV Map
        def_uv = [0, 0]
        for i in range(0, 6):
            for val in def_uv:
                file.write(val.to_bytes(4, byteorder='little', signed=False)) #No parent
        
        file.write(0x000000.to_bytes(3, byteorder='little', signed=False)) #TODO: figure out what this does
        file.write(0x000000.to_bytes(3, byteorder='little', signed=False)) #TODO: figure out what this does

    #End of file or something like that, idk.
    file.write(0xB500.to_bytes(2, byteorder='big', signed=False)) #DON'T CHANGE BYTE ORDER
    file.write(0x0000.to_bytes(2, byteorder='little', signed=False))

    file.flush()
    file.close()

    return True

class Export_csmodel(bpy.types.Operator, ExportHelper):
    """Export the active Object as a .csmodel file"""
    bl_idname = "export_shape.csmodel"
    bl_label = "Export CraftStudio Model (.csmodel)"

    filename_ext = ".csmodel"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj is not None
            and obj.type in {'MESH'}
        )

    def execute(self, context):
        start_time = time.time()

        props = self.properties
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        exported = do_export(context, props, filepath)

        if exported:
            print('finished export in %s seconds' %
                  ((time.time() - start_time)))
            print(filepath)
        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        if True:
            wm.fileselect_add(self)
            return {'RUNNING_MODAL'}
        elif True:
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            return wm.invoke_props_popup(self, event)
        elif False:
            return self.execute(context)

def menu_func_export_button(self, context):
    self.layout.operator(Export_csmodel.bl_idname, text="CraftStudio Model (.csmodel)")

classes = [
    Export_csmodel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_button)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_button)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
