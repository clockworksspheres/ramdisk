#!/usr/bin/env -S python3 -u

###############################################################################
#                                                                             #

#                                                                             #
###############################################################################

#--- Native python libraries
import os
import re
import sys
import socket
import subprocess
# import types
import platform
import time
import traceback
import pathlib

sys.path.append("../..")

from ramdisk.config import DEFAULT_LOG_LEVEL, LogPriority

if sys.platform.startswith('win32'):
    import win32api
    from ramdisk.lib.windows_utilities import is_windows_process_elevated

else:
    import pwd

try:
    from ramdisk.lib.localize import VERSION
except ImportError or AssertionError:
    VERSION = '0.0.1'


# FISMACAT must be one of ['high', 'medium', 'low']

try:
    from randisk.lib.localize import FISMACAT
except ImportError or AssertionError:
    FISMACAT = 'low'

euid = 90000000
process_is_elevated = False
if sys.platform.startswith("win32"):
    if is_windows_process_elevated():
        process_is_elevated = True
else:
    euid = os.geteuid()
    if os.geteuid() == 0:
        process_is_elevated = True
if process_is_elevated:
    try:
        import dmidecode
        DMI = True
    except ImportError:
        DMI = False
else:
    DMI = False

# third party libraries
from ramdisk.lib.run_commands import RunWith as RunWith


class Environment(object):
    """
    The Environment class collects commonly used information about the
    execution platform and makes it available to the rules.
    """

    def __init__(self):
        self.rw = RunWith()
        self.operatingsystem = ''
        self.osreportstring = ''
        self.osfamily = ''
        self.hostname = ''
        self.ipaddress = ''
        self.macaddress = ''
        self.osversion = ''
        self.major_ver = ''
        self.minor_ver = ''
        self.trivial_ver = ''
        self.systemtype = ''
        self.numrules = 0
        self.version = VERSION
        if sys.platform.startswith("win32"):
            self.euid = win32api.GetUserName()
            currpwd = os.environ['USERPROFILE']
        else:
             self.euid = os.geteuid()
             currpwd = pwd.getpwuid(self.euid)
        self.test_mode = ""
        self.script_path = ""
        self.resources_path = ""
        self.rules_path = ""
        self.log_path = ""
        self.icon_path = ""
        self.conf_path = ""
        if sys.platform.startswith("win32"):
            self.homedir = os.environ['USERPROFILE']
        else:
            try:
                self.homedir = currpwd[5]
                # self.homedir = os.environ['USERPROFILE']
            except IndexError:
                self.homedir = '/dev/null'
        self.installmode = False
        self.verbosemode = False
        self.debugmode = False
        self.runtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.systemfismacat = 'low'
        self.determinefismacat()
        self.collectinfo()

    def setsystemtype(self):
        '''
        determine whether the current system is based on:
        launchd
        systemd
        sysvinit (init)
        or upstart
        set the variable self.systemtype equal to the result

        
        '''

        validtypes = ['launchd', 'systemd', 'init', 'upstart']
        cmdlocs = ["/usr/bin/ps", "/bin/ps"]
        cmdbase = ""
        cmd = ""
        self.systemtype = ""

        # buld the command
        for cl in cmdlocs:
            if os.path.exists(cl):
                cmdbase = cl
        if cmdbase:
            cmd = cmdbase + " -p1"

        try:

            if cmd:
                # run the command
                self.rw.setCommand(cmd)
                output, _, _ = self.rw.communicate()
                #cmdoutput = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True, text=True)
                #outputlines = cmdoutput.stdout.readlines()
                outputlines = output.split("\n")
                for line in outputlines:
                    line = str(line)
                    # print("        line: " + str(line))
                    for vt in validtypes:
                        if re.search(vt, line, re.IGNORECASE):
                            self.systemtype = vt
                            # print("type: " + str(vt))

            else:
                print(str(__name__) + ":Unable to determine systemtype. Required utility 'ps' does not exist on this system")
        except OSError:
            print(str(__name__) + ":Unable to determine systemtype. Required utility 'ps' does not exist on this system")



        if self.systemtype not in validtypes and DEFAULT_LOG_LEVEL >= LogPriority["VERBOSE"]:
            print(str(__name__) + ":This system is based on an unknown architecture")
        elif DEFAULT_LOG_LEVEL >= LogPriority["VERBOSE"]:
            print(str(__name__) + ":Determined that this system is based on " + str(self.systemtype) + " architecture")

    def getsystemtype(self):
        '''
        return the systemtype - either:
        launchd, systemd, init, or upstart
        (could potentially return a blank string)

        @return: self.systemtype
        @rtype: string

        
        '''

        return self.systemtype

    def setinstallmode(self, installmode):
        """
        Set the install mode bool value. Should be true if the prog should run
        in install mode.

        @param bool: installmode
        @return: void
        
        """
        try:
            if type(installmode) is bool:
                self.installmode = installmode
        except (NameError):
            # installmode was undefined
            pass

    def getinstallmode(self):
        """
        Return the current value of the install mode bool. Should be true if
        the program is to run in install mode.

        @return: bool : installmode
        
        """
        return self.installmode

    def setverbosemode(self, verbosemode):
        """
        Set the verbose mode bool value. Should be true if the prog should run
        in verbose mode.

        @param bool: verbosemode
        @return: void
        
        """
        try:
            if isinstance(verbosemode, bool):
                self.verbosemode = verbosemode
        except NameError:
            # verbosemode was undefined
            pass

    def getverbosemode(self):
        """
        Return the current value of the verbose mode bool. Should be true if
        the program is to run in verbose mode.

        @return: bool : verbosemode
        
        """
        return self.verbosemode

    def setdebugmode(self, debugmode):
        """
        Set the verbose mode bool value. Should be true if the prog should run
        in verbose mode.

        @param bool: debugmode
        @return: void
        
        """
        try:
            if isinstance(debugmode, bool):
                self.debugmode = debugmode
        except NameError:
            # debugmode was undefined
            pass

    def getdebugmode(self):
        """
        Return the current value of the debug mode bool. Should be true if the
        program is to run in debug mode.

        @return: bool : debugmode
        
        """
        return self.debugmode

    def getostype(self):
        """
        Return the detailed operating system type.

        @return string :
        
        """
        return self.operatingsystem

    def getosreportstring(self):
        """
        Return the detailed operating system type with full version info.

        @return string :
        
        """
        return self.osreportstring

    def getosfamily(self):
        """Return the value of self.osfamily which should be linux, darwin,
        solaris or freebsd.
        @return string :
        
        """
        return self.osfamily

    def getosver(self):
        """
        Return the OS version as a string.

        @return string :
        
        """
        return self.osversion

    def gethostname(self):
        """
        Return the hostname of the system.

        @return: string
        
        """
        return self.hostname

    def getipaddress(self):
        """
        Return the IP address associated with the host name.

        @return string :
        
        """
        return self.ipaddress

    def getmacaddr(self):
        """
        Return the mac address in native format.

        @return string :
        
        """
        return self.macaddress

    def geteuid(self):
        """
        Return the effective user ID

        @return int :
        
        """
        return self.euid

    def geteuidhome(self):
        """
        Returns the home directory of the current effective user ID.

        @return: string
        
        """
        return self.homedir

    def getversion(self):
        """
        Returns the version of the this program.

        @return: string
        
        """
        return self.version

    def collectinfo(self):
        """
        Private method to populate data.

        @return: void
        
        """
        # print 'Environment Running discoveros'
        self.discoveros()
        # print 'Environment running setosfamily'
        self.setosfamily()
        # print 'Environment running guessnetwork'
        self.guessnetwork()
        self.collectpaths()
        self.determinefismacat()
        self.setsystemtype()

    def discoveros(self):
        """
        Discover the operating system type and version
        @return : void
        
        """
        # Alternative (better) implementation for Linux
        if os.path.exists('/usr/bin/lsb_release'):
            self.rw.setCommand(["/usr/bin/lsb_release", "-dr"])
            output, _, _ = self.rw.communicate()
            #proc = subprocess.Popen('/usr/bin/lsb_release -dr',
            #                        shell=True, stdout=subprocess.PIPE,
            #                        close_fds=True, text=True)
            #description = proc.stdout.readline()
            output = output.splitlines()
            description = output[0]
            release = output[1]
            description = description.split()
            #print(description)
            del description[0]
            description = " ".join(description)
            self.operatingsystem = description
            self.osreportstring = description
            release = release.split()
            release = "".join(release[1])
            self.osversion = "".join(release)
            #print(f"Description: {"".join(description)}")
            #print(f"Release: {"".join(release)}")
        elif os.path.exists('/etc/redhat-release'):
            with open('/etc/redhat-release', 'r') as relfile:
                release = relfile.read()
            release = release.split()
            opsys = ''
            for element in release:
                if re.search('release', element):
                    break
                else:
                    opsys = opsys + " " + element
            self.operatingsystem = opsys
            self.osreportstring = opsys
            index = 0
            for element in release:
                if re.search('release', element):
                    index = index + 1
                    osver = release[index]
                else:
                    index = index + 1
            self.osversion = osver
        elif os.path.exists('/etc/gentoo-release'):
            with open('/etc/gentoo-release', 'r') as relfile:
                release = relfile.read()
            release = release.split()
            opsys = ''
            for element in release:
                if re.search('release', element):
                    break
                else:
                    opsys = opsys + " " + element
            self.operatingsystem = opsys
            self.osreportstring = opsys
            index = 0
            for element in release:
                if re.search('release', element):
                    index = index + 1
                    osver = release[index]
                else:
                    index = index + 1
            self.osversion = osver

        # added support for os-release file
        # method of getting version information
        elif os.path.isfile('/etc/os-release'):
            with open('/etc/os-release', 'r') as relfile:
                contentlines = relfile.readlines()
                for line in contentlines:
                    if re.search(r'VERSION\=', line, re.IGNORECASE):
                        sline = line[+8:].split()
                        sline[0] = sline[0].replace('"', '')
                        self.osversion = sline[0]
                    elif re.search(r'NAME\=', line, re.IGNORECASE):
                        sline = line[+5:].split()
                        sline[0] = sline[0].replace('"', '')
                        self.operatingsystem = sline[0]
                self.osreportstring = self.operatingsystem +  ' ' + self.osversion

        elif os.path.exists('/usr/bin/sw_vers'):
            self.rw.setCommand(["/usr/bin/sw_vers", "-productName"])
            output, _, _ = self.rw.communicate()
            # print("Product Name: " + str(output))
            description = output
            description = description.strip()

            self.rw.setCommand(["/usr/bin/sw_vers", "-productVersion"])
            output, _, _ = self.rw.communicate()
            release = output.strip()
            self.operatingsystem = description
            self.osversion = release

            self.rw.setCommand("/usr/bin/sw_vers", "-buildVersion")
            output, _, _ = self.rw.communicate()
            build = output.strip()

            opsys = str(description) + ' ' + str(release) + ' ' + str(build)
            self.osreportstring = opsys

        elif re.match(r'win32$', sys.platform):
            try:
                platform_data = platform.system()
                description = platform_data[0]
                release = platform_data[2]
                build = platform_data[3]
                opsys = str(description).strip() + ' ' + str(release) + ' ' + str(build) 
            except Exception as err:
                print(traceback.format_exc())
                raise()
            self.osreportstring = opsys

    def getosmajorver(self):
        '''
        return the major revision number of the 
        OS version as a string

        @return: self.major_ver
        @rtype: string
        
        '''

        ver = self.getosver()
        try:
            self.major_ver = ver.split('.')[0]
        except IndexError:
            self.major_ver = ver

        return self.major_ver

    def getosminorver(self):
        '''
        return the minor revision number of the 
        OS version as a string

        @return: self.minor_ver
        @rtype: string
        
        '''

        ver = self.getosver()
        try:
            self.minor_ver = ver.split('.')[1]
        except IndexError:
            self.minor_ver = ver

        return self.minor_ver

    def getostrivialver(self):
        '''
        return the trivial revision number of the 
        OS version as a string

        @return: self.trivial_ver
        @rtype: string
        
        '''

        ver = self.getosver()
        try:
            self.trivial_ver = ver.split('.')[2]
        except IndexError:
            self.trivial_ver = ver

        return self.trivial_ver

    def setosfamily(self):
        """
        Private method to detect and set the self.osfamily property. This is a
        fuzzy classification of the OS.
        """
        uname = sys.platform
        if uname.lower().startswith("linux"):
            self.osfamily = 'linux'
        elif uname.lower() == 'darwin':
            self.osfamily = 'darwin'
        elif uname == 'sunos5':
            self.osfamily = 'solaris'
        elif uname == 'freebsd9':
            self.osfamily = 'freebsd'

    def guessnetwork(self):
        """
        This private method checks the configured interfaces and tries to
        make an educated guess as to the correct network data. self.ipaddress
        and self.macaddress will be updated by this method.
        """
        if sys.platform.startswith('darwin'):
            self.hostname = ''
            self.ipaddress = ''
            self.macaddress = ''
            return
        # regex to match mac addresses
        macre = '(([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})'

        ipaddress = ''
        macaddress = '00:00:00:00:00:00'

        hostname = socket.getfqdn()
        try:
            try:
                ipdata = socket.gethostbyname_ex(hostname)
                iplist = ipdata[2]
                iplist.remove('127.0.0.1')
            except ValueError:
                # tried to remove loopback when it's not present, continue
                pass
            if len(iplist) >= 1:
                ipaddress = iplist[0]
            else:
                ipaddress = '127.0.0.1'
        except socket.gaierror:
            # If we're here it's because socket.getfqdn did not in fact return
            # a valid hostname and gethostbyname errored.
            ipaddress = self.getdefaultip()

        # In ifconfig output macaddresses are always one line before the ip
        # address.
        if sys.platform.startswith("linux"):
            cmd = '/sbin/ifconfig'
        elif os.path.exists('/usr/sbin/ifconfig'):
            cmd = '/usr/sbin/ifconfig -a'
        else:
            cmd = '/sbin/ifconfig -a'
        self.rw.setCommand(cmd)
        output, _, _ = self.rw.communicate()
        netdata = output
        #proc = subprocess.Popen(cmd, shell=True,
        #                        stdout=subprocess.PIPE, close_fds=True, text=True)
        #netdata = proc.stdout.readlines()

        for line in netdata:
            line = str(line)
            # print "processing: " + line
            match = re.search(macre, line)
            if match is not None:
                # print 'Matched MAC address'
                macaddress = match.group()
            if re.search(ipaddress, line):
                # print 'Found ipaddress'
                break

        self.hostname = hostname
        self.ipaddress = ipaddress
        self.macaddress = macaddress

    def getdefaultip(self):
        """
        This method will return the ip address of the interface
        associated with the current default route.

        @return: string - ipaddress
        
        """
        if sys.platform.startswith('darwin'):
            ipaddr = ''
            gateway = ''
            return ipaddr
        ipaddr = '127.0.0.1'
        gateway = ''
        if os.path.exists('/usr/bin/lsb_release'):
            try:
                routecmd = subprocess.Popen('/sbin/route -n', shell=True,
                                            stdout=subprocess.PIPE,
                                            close_fds=True, text=True)
                routedata = routecmd.stdout.readlines()
            except OSError:
                return ipaddr
            for line in routedata:
                if re.search(r'^default|^0.0.0.0|^\*', line):
                    line = line.split()
                    try:
                        gateway = line[1]
                    except IndexError:
                        return ipaddr
        else:
            try:
                if os.path.exists('/usr/sbin/route'):
                    cmd = '/usr/sbin/route -n get default'
                else:
                    cmd = '/sbin/route -n get default'
                #self.rw.setCommand(cmd)
                #output, _, _ = self.rw.communicate()
                #print(str(output))
                #routdata = output.strip()
                routecmd = subprocess.Popen(cmd, shell=True,
                                            stdout=subprocess.PIPE,
                                            close_fds=True, text=True)
                routedata = routecmd.stdout.readlines()
            except OSError:
                return ipaddr
            for line in routedata:
                line = str(line)
                if re.search('gateway:', line):
                    line = line.split()
                    try:
                        gateway = line[1]
                    except IndexError:
                        return ipaddr
        if gateway:
            iplist = self.getallips()
            for level in [1, 2, 3, 4]:
                matched = self.matchip(gateway, iplist, level)
                if len(matched) == 1:
                    ipaddr = matched[0]
                    break
        if sys.platform.startswith('darwin'):
            ipaddr = ''
            gateway = ''
        return ipaddr

    def matchip(self, target, iplist, level=1):
        """
        This method will when given an IP try to find matching ip
        from a list of IP addresses. Matching will work from left to right
        according to the level param. If no match is found
        the loopback address will be returned.

        @param string: ipaddress
        @param list: list of ipaddresses
        @param int: level
        @return: list - ipaddresses
        
        """
        quad = target.split('.')
        if level == 1:
            network = quad[0]
        elif level == 2:
            network = quad[0] + '.' + quad[1]
        elif level == 3:
            network = quad[0] + '.' + quad[1] + '.' + quad[2]
        elif level == 4:
            return ['127.0.0.1']
        matchlist = []
        for addr in iplist:
            if re.search(network, addr):
                matchlist.append(addr)
        if len(matchlist) == 0:
            matchlist.append('127.0.0.1')
        return matchlist

    def getallips(self):
        """
        This method returns all ip addresses on all interfaces on the system.

        @return: list of strings
        
        """
        iplist = []
        cmd = ''
        if os.path.exists('/usr/sbin/ip'):
            cmd = '/usr/sbin/ip address'
        elif os.path.exists('/sbin/ip'):
            cmd = '/sbin/ip address'
        elif os.path.exists('/usr/sbin/ifconfig'):
            cmd = '/usr/sbin/ifconfig -a'
        elif os.path.exists('/sbin/ifconfig'):
            cmd = '/sbin/ifconfig -a'
        try:
            #self.rw.setCommand(cmd)
            ifcmd = subprocess.Popen(cmd, shell=True,
                                     stdout=subprocess.PIPE,
                                     close_fds=True, text=True)
            ifdata = ifcmd.stdout.readlines()
            #output, _, _ = self.rw.communicate()
            #ifdata = output.strip()
        except(OSError):
            # self.logdispatch, self.logger are not used in this file, as this code is intended to be run before
            # a logger is loaded
            print(traceback.format_exc())
            # TODO - Need error handler
            raise
        for line in ifdata:
            line = str(line)
            if re.search('inet addr:', line):
                try:
                    line = line.split()
                    addr = line[1]
                    addr = addr.split(':')
                    addr = addr[1]
                    iplist.append(addr)
                except(IndexError):
                    continue
            elif re.search('inet ', line):
                try:
                    line = line.split()
                    addr = line[1]
                    addr = addr.split('/')
                    addr = addr[0]
                    iplist.append(addr)
                except(IndexError):
                    continue
        return iplist

    def get_system_serial_number(self):
        """
        Find and return the
        Serial number of the local machine
        
        @return: string
        """
        systemserial = '0'
        if DMI and self.euid == 0:
            try:
                system = dmidecode.system()
                for key in system:
                    try:
                        systemserial = system[key]['data']['Serial Number']
                    except(IndexError, KeyError):
                        continue
                    system = system.strip()
            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        elif os.path.exists('/usr/sbin/system_profiler'):
            profilerfetch = '/usr/sbin/system_profiler SPHardwareDataType'
            self.rw.setCommand(profilerfetch)
            output, _, _ = self.rw.communicate()
            '''
            cmd3 = subprocess.Popen(profilerfetch, shell=True,
                                    stdout=subprocess.PIPE,
                                    close_fds=True, text=True)
            cmd3output = cmd3.stdout.readlines()
            '''
            for line in output.splitlines():
                line = line.strip()
                if re.search('Serial Number (system):', line):
                    line = line.split(':')
                    try:
                        systemserial = line[1]
                    except(IndexError, KeyError):
                        pass
        systemserial = systemserial
        return systemserial

    def get_chassis_serial_number(self):
        """
        Find and return the
        Chassis serial number
        
        @requires: string
        """
        chassisserial = '0'
        if DMI and self.euid == 0:
            try:
                chassis = dmidecode.chassis()
                for key in chassis:
                    chassisserial = chassis[key]['data']['Serial Number']
                chassisserial = chassisserial.strip()
            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        
        return chassisserial

    def get_system_manufacturer(self):
        """
        Find and return the
        System manufacturer
        
        @return: string
        """
        systemmfr = 'Unk'
        if DMI and self.euid == 0:
            try:
                system = dmidecode.system()
                for key in system:
                    try:
                        systemmfr = system[key]['data']['Manufacturer']
                    except(IndexError, KeyError):
                        continue
                systemfr = systemfr.strip()
            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        return systemmfr

    def get_chassis_manfacturer(self):
        """
        Find and return the
        Chassis manufacterer
        
        @return: string
        """
        chassismfr = 'Unk'
        if DMI and self.euid == 0:
            try:
                chassis = dmidecode.chassis()
                for key in chassis:
                    chassismfr = chassis[key]['data']['Manufacturer']
                chassismfr = chassismfr.strip()
            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        return chassismfr

    def get_sys_uuid(self):
        """
        Find and return a unique identifier for the system. On most systems
        this will be the UUID of the system. On Solaris SPARC this will be
        a number that is _hopefully_ unique as that platform doesn't have
        UUID numbers.
        
        @return: string
        """
        uuid = '0'
        if DMI and self.euid == 0:
            try:
                system = dmidecode.system()
                for key in system:
                    try:
                        uuid = system[key]['data']['UUID']
                    except(IndexError, KeyError):
                        continue
            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        elif os.path.exists('/usr/sbin/dmidecode') and self.euid == 0:
            uuidfetch = '/usr/sbin/dmidecode -s system-uuid'
            self.rw.setCommand(uuidfetch)
            uuid, _, _ = self.rw.communicate()
            #cmd1 = subprocess.Popen(uuidfetch, shell=True,
            #                        stdout=subprocess.PIPE,
            #                        close_fds=True, text=True)
            #uuid = cmd1.stdout.readline()
        elif os.path.exists('/usr/sbin/smbios'):
            smbiosfetch = '/usr/sbin/smbios -t SMB_TYPE_SYSTEM 2>/dev/null'
            cmd2 = subprocess.Popen(smbiosfetch, shell=True,
                                    stdout=subprocess.PIPE,
                                    close_fds=True, text=True)
            cmdoutput = cmd2.stdout.readlines()
            line = line.strip()
            for line in cmdoutput:
                if re.search('UUID:', line):
                    line = line.split()
                    try:
                        uuid = line[1]
                    except(IndexError, KeyError):
                        pass
        elif os.path.exists('/usr/sbin/system_profiler'):
            profilerfetch = '/usr/sbin/system_profiler SPHardwareDataType'
            self.rw.setCommand(profilerfetch)
            output, _, _ = self.rw.communicate()
            '''
            cmd3 = subprocess.Popen(profilerfetch, shell=True,
                                    stdout=subprocess.PIPE,
                                    close_fds=True, text=True)
            cmd3output = cmd3.stdout.readlines()
            '''
            for line in output.splitlines():
                line = line.strip()
                if re.search('UUID:', line):
                    line = line.split()
                    try:
                        uuid = line[2]
                    except(IndexError, KeyError):
                        pass
        elif platform.system() == 'SunOS':
            fetchhostid = '/usr/bin/hostid'
            cmd1 = subprocess.Popen(fetchhostid, shell=True,
                                    stdout=subprocess.PIPE,
                                    close_fds=True, text=True)
            uuid = cmd1.stdout.readline()
            uuid = uuid.strip()
        return uuid

    def ismobile(self):
        '''
        Returns a bool indicating whether or not the system in question is a
        laptop. The is mobile method is used by some rules that have alternate
        settings for laptops.
        
        @return: bool - true if system is a laptop
        '''
        ismobile = False
        dmitypes = ['LapTop', 'Portable', 'Notebook', 'Hand Held',
                    'Sub Notebook']
        if DMI and self.euid == 0:
            try:
                chassis = dmidecode.chassis()
                for key in chassis:
                    chassistype = chassis[key]['data']['Type']
                if chassistype in dmitypes:
                    ismobile = True

            except(IndexError, KeyError):
                # got unexpected data back from dmidecode
                pass
        elif os.path.exists('/usr/sbin/system_profiler'):
            profilerfetch = '/usr/sbin/system_profiler SPHardwareDataType'
            cmd3 = subprocess.Popen(profilerfetch, shell=True,
                                    stdout=subprocess.PIPE,
                                    close_fds=True,
                                    text=True)
            cmd3output = cmd3.stdout.readlines()
            for line in cmd3output:
                if re.search('Book', line):
                    ismobile = True
                    break
        return ismobile

    def issnitchactive(self):
        """
        Returns a bool indicating whether or not the little snitch program is
        active. Little snitch is a firewall utility used on Mac systems and can
        interfere with STONIX operations.
        
        @return: bool - true if little snitch is running
        """
        issnitchactive = False
        if self.osfamily == 'darwin':
            cmd = 'ps axc -o comm | grep lsd'
            littlesnitch = 'lsd'
            proc = subprocess.Popen(cmd, shell=True,
                                    stdout=subprocess.PIPE, close_fds=True, text=True)
            netdata = proc.stdout.readlines()
            for line in netdata:
                # print "processing: " + line
                match = re.search(littlesnitch, line)
                if match is not None:
                    # print 'LittleSnitch Is Running'
                    issnitchactive = True
                    break
        return issnitchactive

    def collectpaths(self):
        """
        Determine how stonix is run and return appropriate paths for:

        icons
        rules
        conf
        logs

        
        """
        try:
            script_path_zero = sys._MEIPASS
        except AttributeError:
            script_path_zero = os.path.realpath(sys.argv[0])

        try:
            script_path_one = os.path.realpath(sys.argv[1])
        except IndexError:
            script_path_one = ""

        self.test_mode = False
        #####
        # Check which argv variable has the script name -- required to allow
        # for using the eclipse debugger.
        if re.search("stonix.py$", script_path_zero) or \
           re.search("stonix$", script_path_zero):
            #####
            # Run normally
            self.script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            #####
            # Run with Eclipse debugger -- Eclipse debugger will never try
            # to run the "stonix" binary blob created by pyinstaller,
            # so don't include here.
            # print "DEBUG: Environment.collectpaths: unexpected argv[0]" + \
            #       ": " + str(sys.argv[0])
            if re.search("stonix.py$", script_path_one) or \
               re.search("stonixtest.py$", script_path_one):
                script = script_path_one.split("/")[-1]
                script_path = "/".join(script_path_one.split("/")[:-1])

                if re.match("^stonixtest.py$", script) and \
                   os.path.exists(script_path_one) and \
                   os.path.exists(os.path.join(script_path, "stonixtest.py")) and \
                   os.path.exists(os.path.join(script_path, "stonix.py")):
                    self.test_mode = True
                    self.script_path = os.path.dirname(os.path.realpath(sys.argv[1]))
                else:
                    print("ERROR: Cannot run using this method")
            else:
                #print "DEBUG: Cannot find appropriate path, building paths for current directory"
                try:
                    self.script_path = sys._MEIPASS
                except AttributeError:
                    self.script_path = os.path.dirname(os.path.realpath(sys.argv[0]))

        #####
        # Set the rules & stonix_resources paths
        # ##
        # create the self.resources_path
        self.resources_path = os.path.join(self.script_path,
                                           "stonix_resources")
        # ##
        # create the self.rules_path
        self.rules_path = os.path.join(self.script_path,
                                       "stonix_resources",
                                       "rules")
        #####
        # Set the log file path
        if self.geteuid() == 0:
            self.log_path = '/var/log'
        else:
            userpath = self.geteuidhome()
            self.log_path = os.path.join(userpath, '.stonix')
            if userpath == '/dev/null':
                self.log_path = '/tmp'

        #####
        # Set the icon path
        self.icon_path = os.path.join(self.resources_path, 'gfx')

        #####
        # Set the configuration file path
        self.conf_path = "/etc/stonix.conf"

    def determinefismacat(self):
        '''
        This method pulls the fimsa categorization from the localize.py
        localization file. This allows a site to prepare special packages for
        use on higher risk systems rather than letting the system administrator
        self select the higher level.

        @return: string - low, med, high
        
        '''
        if FISMACAT not in ['high', 'med', 'low']:
            raise ValueError('FISMACAT invalid: valid values are low, med, high')
        else:
            return FISMACAT

    def get_test_mode(self):
        """
        Getter test mode flag

        
        """
        return self.test_mode

    def get_script_path(self):
        """
        Getter for the script path

        
        """
        return self.script_path

    def get_icon_path(self):
        """
        Getter for the icon path

        
        """
        return self.icon_path

    def get_rules_path(self):
        """
        Getter for rules path

        
        """
        return self.rules_path

    def get_config_path(self):
        """
        Getter for conf file path

        
        """
        return self.conf_path

    def get_log_path(self):
        """
        Getter for log path

        
        """
        return self.log_path

    def get_resources_path(self):
        """
        Getter for stonix resources directory

        
        """
        return self.resources_path

    def getruntime(self):
        '''
        Return the runtime recorded.

        
        '''
        return self.runtime

    def setnumrules(self, num):
        '''
        Set the number of rules that apply to the system. This information is
        used by the log dispatcher in the run metadata.

        @param num: int - number of rules that apply to this host
        
        '''
        if not isinstance(num, int):
            raise TypeError('Number of rules must be an integer')
        elif num < 0:
            raise ValueError('Number of rules must be a positive integer')
        else:
            self.numrules = num

    def getnumrules(self):
        '''
        Return the number of rules that apply to this host.

        
        '''
        return self.numrules

    def getsystemfismacat(self):
        '''
        Return the system FISMA risk categorization.

        @return: string - low, med, high
        
        '''
        return self.systemfismacat

    def setsystemfismacat(self, category):
        '''
        Set the systems FISMA risk categorization. The risk categorization
        cannot be set lower than the default risk level set in FISMACAT in
        localize.py

        @param category: string - low, med, high
        
        '''

        if category not in ['high', 'med', 'low']:
            raise ValueError('SystemFismaCat invalid: valid values are low, med, high')
        elif self.systemfismacat == 'high':
            self.systemfismacat = 'high'
        elif self.systemfismacat == 'med' and category == 'high':
            self.systemfismacat = 'high'
        elif self.systemfismacat == 'low' and category == 'high':
            self.systemfismacat = category

if __name__ == "__main__":

    env = Environment()

    myos = env.discoveros()

    print(env.osreportstring)

