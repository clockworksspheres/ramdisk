import sys

sys.path.append("..")

#####
# LOGGING
#               <----- Least logging    ------------    Most Logging ---------->
LogPriority = { "SUBCRIT": 5, "CRITICAL":10, "ERROR":20, "WARNING":30, "VERBOSE":40, "INFO":20, "DEBUG":50 }

DEFAULT_LOG_LEVEL=LogPriority["CRITICAL"]
#                              ^^^^^ Input log level here...
#####

