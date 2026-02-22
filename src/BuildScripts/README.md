# Meta Pipeline

Start jenkins server container
Start hypervisors

vmm start VM's
jenkinsPipelineTool run ramdisk-redhat

poll jenkinsPipelineTools check ramdisk-redhat 'till done

stop VM's

start next set of VM's

jenkinsPipelineTool run ramdisk-debbased

poll jenkinsPipelineTools check ramdisk-redhat 'till done

stop VM's

start next set of VM's

jenkinsPipelineTool run ramdisk-macos

poll jenkinsPipelineTools check ramdisk-redhat 'till done

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

Collect reports and post???? - need website or 
something to view or cmdline report

possibly stop jenkins server container
possibly stop hypervisors


