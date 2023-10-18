import bpy, bpy_extras

## File Browser Usage
#  These created file browser is just a futher wrapper of `bpy_extras.io_utils.ExportHelper`
#  So user must use it like ExportHelper. It mean inhert it and no need to write invoke function.
#  
#  These wrapper also provide general visitor for getting input file name or directory:
#  * general_get_filename()
#  * general_get_directory()
#  
#  For example:
#  ```
#  class BBP_OT_custom_import(bpy.types.Operator, UTIL_file_browser.OpenBmxFile)
#  
#      def execute(self, context):
#          print(self.general_get_filename()) # get file name if support
#          print(self.general_get_directory()) # get file name if support
#      
#  ```

class ImportBallanceImage(bpy_extras.io_utils.ImportHelper):

    # no need to set file ext because we support multiple file ext.
    # see ImportGLTF2 for more info.
    # filename_ext = ".bmp"

    # set with 2 file ext with ; as spelittor
    # see ImportGLTF2 for more info.
    filter_glob: bpy.props.StringProperty(
        default = "*.bmp;*.tga",
        options = {'HIDDEN'}
    )

    def general_get_filename(self) -> str:
        return self.filepath
    
class ImportBmxFile(bpy_extras.io_utils.ImportHelper):

    # set file ext filter
    filename_ext = ".bmx"
    filter_glob: bpy.props.StringProperty(
        default = "*.bmx",
        options = {'HIDDEN'}
    )

    def general_get_filename(self) -> str:
        return self.filepath
    
class ExportBmxFile(bpy_extras.io_utils.ExportHelper):

    # set file ext filter
    filename_ext = ".bmx"
    filter_glob: bpy.props.StringProperty(
        default = "*.bmx",
        options = {'HIDDEN'}
    )

    def general_get_filename(self) -> str:
        return self.filepath
    
class ImportVirtoolsFile(bpy_extras.io_utils.ImportHelper):

    # we support multiple file ext, set like ImportBallanceImage
    # filename_ext = ".nmo"
    filter_glob: bpy.props.StringProperty(
        default = "*.nmo;*.cmo;*.vmo",
        options = {'HIDDEN'}
    )

    def general_get_filename(self) -> str:
        return self.filepath
    
class ExportVirtoolsFile(bpy_extras.io_utils.ExportHelper):

    # only support export nmo file
    filename_ext = ".nmo"
    filter_glob: bpy.props.StringProperty(
        default = "*.nmo",
        options = {'HIDDEN'}
    )

    def general_get_filename(self) -> str:
        return self.filepath
    
class ImportDirectory(bpy_extras.io_utils.ImportHelper):

    # add directory prop to receive directory
    directory: bpy.props.StringProperty()

    # blank filter
    filter_glob: bpy.props.StringProperty(
        default = "",
        options = {'HIDDEN'}
    )
    
    def general_get_directory(self) -> str:
        return self.directory
    