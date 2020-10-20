import os
from app.pylib.StringTools import getFileExt, getFileName

def delete_file(path="", year="", base_dir=""):
    '''
    Attempts to delete a file from the server with a supplied path and base directory.
    Returns int(1) for no operation has been made and int(0) for a completed operation.\n
    Parameters:\n
    :path (str): Path that exists in datastorage in AD or DB.
    :base_dir (str): Base directory from app.config that correspondes to the route.

    '''
    if path == "" or getFileName(path) == "":
        return 1
    if year=="":
        p = os.path.join(base_dir, getFileName(path))
    else:
        p = os.path.join(base_dir, year, getFileName(path))
    try:
        os.remove(p)
    except FileNotFoundError as e:
        return 1
    return 0
    
def find_file(chdir=os.getcwd(), filename=""):
    if filename=="":
        return ""
    elif chdir=="":
        return ""
    else:
        for f in os.listdir(chdir):
            if filename.lower() in f.lower():
                return f