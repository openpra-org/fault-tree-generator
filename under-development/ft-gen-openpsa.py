"""
<Egemen M. Aras/>
This script creates fault-trees in the format of open-psa mef.
"""
#importing The ElemtTree XML API
import xml.etree.ElementTree as ET
import random
random.seed(10)

gateList = ['or']

def generateXML(fileName):

    root = ET.Element('opsa-mef')
    faultTreeName = ET.SubElement(root,'define-fault-tree',{'name':'FT'})
    modelData = ET.SubElement(root, 'model-data')

    n = int(input('Please enter the number of gates :\t'))
    if n == 0:
        print("Please a number between 1 and 495!")
    for gateNumber in range(1,n+1):
        if gateNumber ==(n):
            defineGate = ET.SubElement(faultTreeName, 'define-gate', {'name': 'g' + str(gateNumber)})
            gateType = ET.SubElement(defineGate, random.choice(gateList))
            basicEvent1 = ET.SubElement(gateType, 'basic-event', {'name': 'be' + str(gateNumber)})
            basicEvent2 = ET.SubElement(gateType, 'basic-event', {'name': 'bee' + str(gateNumber)})
            #gate = ET.SubElement(gateType, 'gate', {'name': 'g' + str(gateNumber + 1)})

            basicEventValue1 = ET.SubElement(modelData, 'define-basic-event', {'name': 'be' + str(gateNumber)})
            basicEventValu1Assign = ET.SubElement(basicEventValue1, 'float', {'value': str(0.01)})
            basicEventValue2 = ET.SubElement(modelData, 'define-basic-event', {'name': 'bee' + str(gateNumber)})
            basicEventValu2Assign = ET.SubElement(basicEventValue2, 'float', {'value': str(0.01)})
        else:
            defineGate = ET.SubElement(faultTreeName, 'define-gate', {'name': 'g'+str(gateNumber)})
            gateType = ET.SubElement(defineGate,random.choice(gateList))
            basicEvent1 =ET.SubElement(gateType,'basic-event',{'name':'be'+str(gateNumber)})
            basicEvent2 = ET.SubElement(gateType, 'basic-event', {'name': 'bee' + str(gateNumber)})
            gate = ET.SubElement(gateType,'gate',{'name':'g'+str(gateNumber+1)})

            basicEventValue1 = ET.SubElement(modelData, 'define-basic-event', {'name': 'be' + str(gateNumber)})
            basicEventValu1Assign = ET.SubElement(basicEventValue1,'float', {'value': str(0.01)})
            basicEventValue2 = ET.SubElement(modelData, 'define-basic-event', {'name': 'bee' + str(gateNumber)})
            basicEventValu2Assign = ET.SubElement(basicEventValue2,'float', {'value': str(0.01)})


    tree = ET.ElementTree(root)
    tree.write(fileName, xml_declaration=True, encoding='utf-8')

if __name__=='__main__':
    generateXML('base-fault-tree.xml')