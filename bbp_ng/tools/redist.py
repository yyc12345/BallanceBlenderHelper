import os, argparse, shutil
import common

def create_redist(redist_folder: str) -> None:
    # get plugin root folder and redist folder
    root_folder: str = common.get_plugin_folder()

    # we do not want to use script to recursively delete any folder
    # because we are afraid of accident `rm -rf /*` disaster.
    # but we still need a empty folder to copy file, 
    # so we check whether redist folder is existing and hope user manually clean it.
    redist_folder = os.path.abspath(redist_folder)
    if os.path.exists(redist_folder):
        print(f'"{redist_folder}" is already existing. This may cause problem, please empty it first before running redist script.')
    # make sure redist folder is existing.
    os.makedirs(redist_folder, exist_ok=True)
    
    # copy core python files
    common.conditional_file_copy(
        root_folder,
        redist_folder,
        ('*.py', '*.toml', ),
        None,
        False
    )
    
    # copy jsons
    common.conditional_file_copy(
        os.path.join(root_folder, 'jsons'),
        os.path.join(redist_folder, 'jsons'),
        ('*.json', ),
        None,
        False
    )
    # copy icons
    common.conditional_file_copy(
        os.path.join(root_folder, 'icons'),
        os.path.join(redist_folder, 'icons'),
        ('*.png', ),
        None,
        True
    )
    # copy meshes
    common.conditional_file_copy(
        os.path.join(root_folder, 'meshes'),
        os.path.join(redist_folder, 'meshes'),
        ('*.bin', ),
        None,
        False
    )
    # copy BMap library
    common.conditional_file_copy(
        os.path.join(root_folder, 'PyBMap'),
        os.path.join(redist_folder, 'PyBMap'),
        ('*.py', '*.dll', '*.so', '*.dylib', '*.bin', '*.pdb', ),
        None,
        False
    )

    print('Done.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BBP NG Redist Script')
    parser.add_argument('-o', '--output', required=True, action='store', dest='output', help='The path to redist folder.')
    args = parser.parse_args()
    create_redist(args.output)
