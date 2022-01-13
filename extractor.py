import os
import time
import json
import glob
import shutil
try:
    import psutil
except ImportError:
    print("Installing psutil, please wait...")
    os.system("pip install psutil")
    print("Done installing psutil. \n")
    import psutil
    time.sleep(1)

def make_directory(directory) -> None:
    '''Checks if a directory exists at `directory`, makes it if it doesn't exist'''
    if not os.path.isdir(directory):
        os.makedirs(directory)

def check_file(path:str) -> bool:
    '''Checks if a file exists at the path `path`, returns True if it does and False if it doesn't'''
    try:
        open(path)
        return True
    except FileNotFoundError:
        return False

#this can return different types depending on the json data in the file, but for this use case it always returns a dict
def load_from_file(path:str) -> dict:
    '''Loads JSON data from a file at path `path` and returns the data that was loaded.'''
    with open(path) as indexfile:
        return json.load(indexfile)

def extract(outputdir:str) -> None:
    #on windows, files are usually sorted by name. due to this, the indexes file corresponding to the latest game version will usually be the last one in the list returned by glob
    hashmapping = load_from_file(glob.glob(os.path.join(os.getenv('APPDATA'), ".minecraft", "assets", "indexes", "*.json"))[-1])
    for path, hash in hashmapping['objects'].items():
        #only get sound files
        if not path.endswith('.ogg'):
            continue
        friendlyname = path.split('/')[-1]
        directory = f"{outputdir}{path.replace(friendlyname, '').replace('minecraft/', '').replace('/', f'{os.sep}')}"
        make_directory(directory)
        if check_file(f"{directory}{friendlyname}"):
            continue
        shutil.copyfile(os.path.join(os.getenv('APPDATA'), ".minecraft", "assets", "objects", hash['hash'][:2], hash['hash']), f"{directory}{friendlyname}")

def check_running() -> bool:
    '''Checks if Minecraft is running, returns True if it is and False if it isn't'''
    for i in psutil.process_iter(['name']):
        if i.info['name'].lower() == "javaw.exe":
            return True
    return False
        
print("Checking if you have Minecraft installed in its default directory...")
if not os.path.isdir(f"{os.getenv('APPDATA')}{os.sep}.minecraft"):
    print(f"It doesn't look like you have Minecraft installed in the default directory ('{os.getenv('APPDATA')}\.minecraft'). Run this again after moving Minecraft to that directory.")
    quit()
print("Alright, it looks like you have it installed.")
time.sleep(1)
outputdir = input(f"Enter where you want the files to be saved to (e.g. C:\\Users\\username\\Documents\\Minecraft) or press Enter to save them to '{os.getenv('appdata')}\.minecraft\extractedfiles': \n").strip()
if not outputdir:
    outputdir = f"{os.getenv('APPDATA')}{os.sep}.minecraft{os.sep}extractedfiles{os.sep}"
    print(f"Saving files to the default directory. ({os.getenv('APPDATA')}\.minecraft\extractedfiles)")
else:
    os.sep = list(os.sep)[0]
    print(f"Saving files to '{outputdir}{os.sep}sounds'.")
    outputdir = outputdir + os.sep
time.sleep(1)
make_directory(outputdir)
print("Checking if Minecraft is running...")
if check_running():
    print("Minecraft is running right now. Please close it and run this again, as the files can't be accessed while it's running.")
    quit()
print("Ok, it doesn't appear to be running.")
time.sleep(0.4)
print("Extracting files...")
try:
    extract(outputdir)
except FileNotFoundError:
    print("Hmm, it looks like a file is missing. Open the Minecraft Launcher and click 'Play', then wait for the missing files to download. Quit Minecraft once it starts, and run this again.")
    quit()
print("Done.")
if input("Do you want to open the folder with the extracted files in Explorer? (Y/N) ").lower() == "y":
    print(f"Ok. Opening {outputdir}sounds in 3 seconds...")
    time.sleep(3)
    os.system(f"explorer.exe {outputdir}sounds")
else:
    print("Ok. Exiting...")