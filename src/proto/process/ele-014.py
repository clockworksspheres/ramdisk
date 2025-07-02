

import sys
import getpass

sys.path.append("../..")

from ramdisk.lib.run_commands import RunWith

passwd = getpass.getpass()

runner = RunWith()

command = ["ls", "-lah", "/tmp/"]
runner.setCommand(command)
output, error, retval = runner.runWithSudo(passwd)

print(str(output))

