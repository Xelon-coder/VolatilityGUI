import subprocess
import re
from colorama import Fore
from tools import *

# Globals for volat
MEMORY_FILE = "dump"
VOLATILITY_PATH = "volatility/vol.py"

# Globals for colors
G_INFO = Fore.BLUE+"[-]"+Fore.RESET
G_NEW = Fore.GREEN+"[+]"+Fore.RESET
G_ERROR = Fore.RED+"[!]"+Fore.RESET
G_LIST = Fore.MAGENTA+"[*]"+Fore.RESET

class VolatilityInfo:

    def __init__(self,file,path):
        self.memoryFile = file
        self.volatilityPath = path
        self.profile = ""
        self.dumpDirectory = ""

        self.stringFiles = []
        self.objectFiles = []
        self.stringPs = []
        self.objectPs = []

    # Returns stdout and stderr result of volatility command
    def runVolatilityCommand(self,plugin,*args):

        # Use python2 by default
        volatilityCommand = ["python2", self.volatilityPath, plugin, "-f", self.memoryFile]

        volatilityCommand.extend(args)

        if self.profile:
            volatilityCommand.append('--profile='+self.profile)
        try:
            process = subprocess.Popen(volatilityCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.communicate()
        except:
            print(G_ERROR,'Error when creating process')
            exit(-1)


    # Returns all possible profile
    # Set by default the first profile
    # If no profile was found returns an error
    def determineProfile(self):

        print(G_INFO,'Searching profile(s) for file :',self.memoryFile)
        stdout, stderr = self.runVolatilityCommand("imageinfo")
        
        attributeList = stdout.decode('utf-8').split('\n')
        suggestedProfile = [element for element in attributeList if 'Suggested' in element]
        
        if len(suggestedProfile) != 1:
            print(G_ERROR,"Error on imageinfo : ",suggestedProfile)
            exit(-1)

        regex  = r'.* : ([\w\d_]+(?:, [\w\d_]+)*)'
        profilesSearch = re.search(regex,suggestedProfile[0])
        profiles = profilesSearch.group(1).split(', ')

        if profiles[0] == 'No':
            print(G_ERROR,'No profile found')
            exit(-1)

        print(G_NEW,'Profile found')
        for p in profiles:
            print('     ',G_LIST+p)

        self.profile = profiles[0]

        return profiles
    
    # Returns files tree structure with the root
    def findFiles(self):

        print(G_INFO,"Searching files")

        stdout, stderr = self.runVolatilityCommand("filescan")
        
        result = stdout.decode('utf-8').split('\n')
        files = []

        for i,element in enumerate(result):
            if "Offset(P)" in element:
                files = result[i+2:-1]

        if len(files) < 1:
            print(G_ERROR,"No files found")
        
        else:
            print(G_NEW,len(files),"files has been found")
            self.stringFiles= files
            nodes,self.objectFiles,root = generateTree(files)
            return nodes,root
    
    # Returns processus list tree structure with root
    def findPsList(self):

        print(G_INFO,"Searching psList")
        stdout, stderr = self.runVolatilityCommand("pslist")
        
        result = stdout.decode('utf-8').split('\n')
        ps = []

        for i,element in enumerate(result):
            if "Offset(V)" in element:
                ps = result[i+2:-1]
        
        if len(ps) < 1:
            print(G_ERROR,"No processus found")

        else:
            print(G_NEW,len(ps),"processus has been found")
            self.stringPs= ps
            nodes,self.objectPs,root = generatePsTree(ps)
            return nodes,root
    
    # Returns filtered files list
    def filterFiles(self,filter):
        if len(self.stringFiles) == 0:
            self.findFiles()
        nodes,self.objectFiles,root = generateTree(self.stringFiles,filter=filter)
        return nodes,root
    
    # Returns filtered processus list
    def filterPs(self,filter):
        if len(self.stringPs) == 0:
            self.findPsList()
        nodes,self.objectPs,root = generatePsTree(self.stringPs,filter=filter)
        return nodes,root

    # Returns TrueCrypt passphrase list if found
    def findTruecryptPassphrase(self):
        print(G_INFO,"Searching Truecrypt master key")
        stdout, stderr = self.runVolatilityCommand("truecryptpassphrase")
        
        result = stdout.decode('utf-8').split('\n')
        passphrases = []

        for element in result:
            if "Found" in element:
                passphrases.append(element)
        
        if len(passphrases) == 0:
            print(G_ERROR,"No passphrase found")
        else:
            print(G_NEW,len(passphrases)," passphrases found")
            for p in passphrases:
                print("    ",G_LIST,p)

        return passphrases
    
    # Dump
    def dump(self,pid,folder,type):
        print(G_INFO,"Trying to dump",type,"from",pid)
        stdout, stderr = self.runVolatilityCommand(type,'-p',pid,'-D',folder)
        
        stderr = stderr.decode('utf-8').split('\n')
        for line in stderr:
            if "ERROR" in line:
                print(G_ERROR,line)
                return

        result = stdout.decode('utf-8').split("\n")

        for line in result:
            if "Writing" in line or "OK" in line:
                print(G_NEW,type,"was dump on",folder,"folder")
                return
        
        print(G_ERROR,type," wasn't dump")

    # Memory Dump
    def memDump(self,pid,folder):
        self.dump(pid,folder,"memdump")

    # Processus Dump
    def procDump(self,pid,folder):
        self.dump(pid,folder,"procdump")

    # Dump files
    def dumpFiles(self,offset,folder):
        print(G_INFO,"Trying to dump file from offset",offset)
        stdout, stderr = self.runVolatilityCommand("dumpfiles",'-Q',offset,'-D',folder)
        
        stderr = stderr.decode('utf-8').split('\n')
        for line in stderr:
            if "ERROR" in line:
                print(G_ERROR,line)
                return

        result = stdout.decode('utf-8').split("\n")

        for line in result:
            if "DataSectionObject" in line:
                print(G_NEW,"file was dump on",folder,"folder")
                return

        print(G_ERROR,"file wasn't dump")

    # View clipboard content
    def clipboard(self):
        print(G_INFO,"Searching clipboard content")
        stdout, stderr = self.runVolatilityCommand("clipboard")
        
        result = stdout.decode('utf-8').split("\n")
        
        content = []

        for i,element in enumerate(result):
            if "Session" in element:
                content = result[i+2:-1]
        
        if len(content) < 1:
            print(G_ERROR,"No content was found")
        
        else:
            print(G_NEW,len(content),"content was found in clipboard")
            return toClipboardFormat(content)

#Vi = VolatilityInfo(MEMORY_FILE,VOLATILITY_PATH)
#Vi.determineProfile()
#_, root = Vi.filterFiles(".exe") # Only .exe files

#displayTree(root)