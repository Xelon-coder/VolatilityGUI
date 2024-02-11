from anytree import Node

class File:

    def __init__(self,feilds):
        if len(feilds) != 5:
            print("ERROR")
            exit(-1)
        self.offset = feilds[0]
        self.ptr = feilds[1]
        self.hnd = feilds[2]
        self.access = feilds[3]

        self.location = [element for element in feilds[4].replace('\\\\','\\').split('\\') if element != '']
        self.name = self.location[-1]

        self.level = len(self.location)

        if self.level == 1:
            self.parent = self.location[0]
        else:
            self.parent = self.location[-2]

class Processus:

    def __init__(self,feilds):
        
        self.offset = feilds[0]
        self.name = feilds[1]
        self.pid = int(feilds[2])
        self.ppid = int(feilds[3])
        self.thds = feilds[4]
        self.hnds = feilds[5]

class Clipboard:

    def __init__(self,feilds):
        self.session = feilds[0]
        self.winstation = feilds[1]
        self.format = feilds[2]
        self.handle = feilds[3]
        self.object = feilds[4]
        self.data = feilds[6]