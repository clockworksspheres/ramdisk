import re
import os
import sys

def getMountData():
    """
    """
    pass

def getDevice():
    """
    """
    with open("mountData.txt", "r") as mountFile:
        for line in mountFile:
            print(line)
            if re.match("Created device.*", line):
                print("FOUND DEVICE: ", line.split()[2])
                break

if __name__=="__main__":

    getDevice()

