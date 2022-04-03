import pathlib, zipfile, os, shutil
from . import UTILS_constants

def compress(folder, zip_file):
    # remove target file first
    if os.path.isfile(zip_file):
        os.remove(zip_file)
    
    # compress data
    with zipfile.ZipFile(zip_file, mode= 'w', compression= zipfile.ZIP_DEFLATED, compresslevel= 9, allowZip64= False) as zip_obj:
        # set global comment
        zip_obj.comment = UTILS_constants.bmfile_globalComment

        # iterate folder and add files
        for folder_name, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                # construct zip_entry
                abstract_filepath = os.path.join(folder_name, filename)
                relative_filepath = os.path.relpath(abstract_filepath, folder)
                zip_entry = zipfile.ZipInfo.from_file(abstract_filepath, arcname= relative_filepath)
                zip_entry.compress_type = zipfile.ZIP_DEFLATED

                # compress file
                with open(abstract_filepath, 'rb') as fs_in:
                    with zip_obj.open(zip_entry, mode= 'w') as zip_in:
                        # References
                        # https://stackoverflow.com/questions/53254622/zipfile-header-language-encoding-bit-set-differently-between-python2-and-python3
                        # set unicode flag after opening internal file.
                        # for the shit implement of python module zipfile, we need set Deflated:Maximum manually
                        zip_entry.flag_bits |= UTILS_constants.bmfile_flagUnicode 
                        zip_entry.flag_bits |= UTILS_constants.bmfile_flagDeflatedMaximum
                        # copy file
                        shutil.copyfileobj(fs_in, zip_in)

               
def decompress(folder, zip_file):
    with zipfile.ZipFile(zip_file, mode= 'r', compression= zipfile.ZIP_DEFLATED, compresslevel= 9, allowZip64= False) as zip_obj:
        for zip_entry in zip_obj.infolist():
            if (zip_entry.flag_bits & UTILS_constants.bmfile_flagUnicode) == 0:
                # lost unicode flag, throw error
                raise Exception("Zip Entry lost UNICODE flag.")

            # decompress file
            zip_obj.extract(zip_entry, path= folder)


            
        