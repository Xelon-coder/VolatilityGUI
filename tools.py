from object import File, Processus, Clipboard
from anytree import Node

def generateTree(files,filter=''):

    objectFiles = []

    for file in files:
        if filter in file:
            feilds = [element for element in file.split(' ') if element != '']
            if len(feilds) > 5:
                feilds = feilds[:4]+[''.join(feilds[4:])]
            feilds[4] = "\\General\\"+feilds[4]
            objectFiles.append(File(feilds))

    objectFiles = sorted(objectFiles, key=lambda x: x.level)

    while objectFiles[0].level > 1:
        objectFiles.insert(0,File(['x','x','x','x','\\'.join(objectFiles[0].location[:-1])]))

    objectFiles = sorted(objectFiles, key=lambda x: x.level)

    nodes = {}

    root = Node(objectFiles[0])
    nodes[root.name.name] = root

    nodes,objectFiles = generateRec(nodes,objectFiles)

    return nodes,objectFiles,root

def generateRec(nodes,objectFiles):

    for position,file in enumerate(objectFiles[1:]):
        node = Node(file)
        if node.name not in nodes.keys():
            nodes[node.name.name] = node

            if file.parent not in nodes.keys():
                objectFiles.insert(position,File(['x','x','x','x','\\'.join(file.location[:-1])]))
                nodes,objectFiles = generateRec(nodes,objectFiles)

            parent = nodes[file.parent]
            if parent != node:
                node.parent = parent
            else:
                node.parent = None
            
    return nodes,objectFiles

def generatePsTree(processus,filter=''):
    objectPs = []

    for ps in processus:
        if filter in ps:
            feilds = [element for element in ps.split(' ') if element != ''][:6]
            objectPs.append(Processus(feilds))

    objectPs.insert(0,Processus(['x','General','0','0','x','x']))

    nodes = {}

    root = Node(objectPs[0])
    nodes[root.name.pid] = root

    nodes,objectPs = generatePsRec(nodes,objectPs)

    return nodes,objectPs,root

def generatePsRec(nodes,objectPs):
    for ps in objectPs[1:]:
        node = Node(ps)
        nodes[node.name.pid] = node

    for ps in objectPs[1:]:
        node = nodes[ps.pid]
        if ps.ppid not in nodes: # If ppid doesn't exist set parent to initial processus
            node.parent = nodes[0]
        else:
            node.parent = nodes[ps.ppid]

    return nodes,objectPs

def toClipboardFormat(content):
    
    clipboard = []

    for c in content:
        feilds = [element for element in c.split(' ') if element != '']
        clipboard.append(Clipboard(feilds))
    
    return clipboard