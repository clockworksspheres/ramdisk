# Meta Pipeline

https://github.com/clockworksspheres/vmm.git
https://github.com/clockworksspheres/jenkinsTools.git

Using these two tools, do the following:

Start jenkins server container
Start hypervisors

start VM's
jenkinsPipelineTool run ramdisk-redhat pipeline

poll jenkinsPipelineTools check ramdisk-redhat 'till done

stop VM's

start next set of VM's

jenkinsPipelineTool run ramdisk-debbased

poll jenkinsPipelineTools check ramdisk-debbased 'till done

stop VM's

start next set of VM's

jenkinsPipelineTool run ramdisk-macos

poll jenkinsPipelineTools check ramdisk-macos 'till done

stop VM's

start next set of VM's

jenkinsPipelineTool run ramdisk-windows

poll jenkinsPipelineTools check ramdisk-windows 'till done

stop VM's

rheloutput = jenkinsPipelineTools check ramdisk-redhat --get-full-run
deboutput = jenkinsPipelineTools check ramdisk-debbased --get-full-run
macosoutput = jenkinsPipelineTools check ramdisk-macos --get-full-run
win32output = jenkinsPipelineTools check ramdisk-windows --get-full-run

(need to write the --get-full-run integration)

report the four json reports somewhere?

Possibly collect reports and post???? - need website or 
something to view or cmdline report

possibly stop jenkins server container
possibly stop hypervisors


