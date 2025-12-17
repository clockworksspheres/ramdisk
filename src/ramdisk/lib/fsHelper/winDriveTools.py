import os
import re
import subprocess
import traceback

def getDrivePath(path):
    """
    get the drive out of the path
    """
    drive, tail = os.path.splitdrive(path)
    #print(drive)
    return drive


def findDrive(path):
    """
    Find the drive that the path is connected to - 
    
    if exists, return true, if it doesn't exist, return false
    
    """

    found = False
    #pattern = pattern = r"^(.*?)(\\*)?$"
    drivelist = []

    result = subprocess.check_output("mountvol")

    for line in result.splitlines():

        try:
            path = cleanTrailingSlashes(path)
            drivelist = []
            line = str(line)
            if re.search(":\\\\$", line):
                try:
                    drive = getDrivePath(line)
                    drivelist.append(drive)
                except:
                    pass

        except IOError as err:
            print(f"{err}")
            print(traceback.format_exc(err))

    drive = getDrivePath(path)
    if drive in drivelist:
        found = True
    else:
        found = False
    return found
        

def findMountName(device):
    """
    """
    result = subprocess.run(["aim_ll", "-l", "-u", device], capture_output=True, text=True)
    
    mntName = ""
    for line in result.stdout.splitlines():
        #print(line)
        if re.match("^  Mounted at ", line):
            mntName = line.split("Mounted at ")[-1]
    #print(mntName)
    return mntName

def cleanDrivePath(path):
    # if one or more slashes are found, replace them with two slashes
    cleanPath = re.sub(r"\\{1,}", r"\\\\", path)
    # print(cleanPath)
    return cleanPath

def cleanTrailingSlashes(path):
    """
    Return the path without trailing slashes
    """
    path2return = ""
    # Regex: capture everything up to but not including the final backslash
    pattern = r"^(.*?)(\\*){1,}$"

    match = re.match(pattern, path)
    if match:
        path2return = match.group(1)   # everything before the optional trailing slash
        # print("Directory:", path2return)

    return path2return


if __name__ == "__main__":

    path = r"D:\Projects\Project_2025_Version3\\"

    path = cleanTrailingSlashes(path)
    print(path)

    driveExists = findDrive(path)
    drive = getDrivePath(path)
    if not driveExists:
        print(f"Drive {drive} does not exist")
    else:
        print(f"Drive {drive} Exists")

    home_dir = os.path.expanduser("~")
    print(home_dir + "\n\n")


    print("\n-----\n")

    deviceName = findMountName("000100")
    print(deviceName)


