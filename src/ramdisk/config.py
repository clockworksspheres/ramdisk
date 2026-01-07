import sys

sys.path.append("..")

#####
# LOGGING
#               <----- Least logging    ------------    Most Logging ---------->
LogPriority = { "SUBCRIT": 5, "CRITICAL":10, "ERROR":20, "WARNING":30, "VERBOSE":40, "INFO":20, "DEBUG":50 }

# DEFAULT_LOG_LEVEL=LogPriority["DEBUG"]
DEFAULT_LOG_LEVEL=LogPriority["CRITICAL"]
#                              ^^^^^ Input log level here...
#####
# Default Ramdisk Size in Mb
DEFAULT_RAMDISK_SIZE=500
#
#####
# Default path to Windows AIM Toolkit ramdisk command line tool
AIM_LL = "C:\\Program Files\\AIM Toolkit\\aim_ll.exe"
#
#####
# 
#
#####
