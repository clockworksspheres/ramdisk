import sys

sys.path.append("..")

#####
# LOGGING
#               <----- Least logging    ------------    Most Logging ---------->
LogPriority = { "CRITICAL":50, "ERROR":40, "WARNING":30, "VERBOSE":20, "INFO":20, "DEBUG":10 }

DEFAULT_LOG_LEVEL=LogPriority["INFO"]
#                              ^^^^^ Input log level here...
#####

