"""
<Egemen M. Aras/>
This script creates fault-trees in the format of open-psa mef.
"""

import os
import xml.etree.ElementTree as ET
import re
import random
random.seed(123)

# pathXFTAModels ="C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/models/xfta"
# pathSCRAMModels = "C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/models/scram"
# pathSAPHSOLVEModels = "C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/models/saphsolve"
#
# pathXFTAResults ="C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/results/xfta"
# pathSCRAMResults = "C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/results/scram"
# pathSAPHSOLVEResults = "C:/Users/emaras/Desktop/Repo/Gitlab/openpra/ft_solver/results/saphsolve"

# XFTAExecDir = "C:/Users/emaras/Desktop/Repo/xfta/xfta-1-3-1-win32/xftar"
# def runXFTA(XFTAConfigName):
#     commandToRunXFTA = XFTAExecDir +" "+ XFTAConfigName
#     print(commandToRunXFTA)
#     os.system(commandToRunXFTA)
#
# def runSCRAM(inputFile):
#     commandToRunSCRAM = "docker run -it --rm -v " + os.getcwd() + "/models/scram:/scram supra scram /scram/" + inputFile + "--mocus --probability --importance > models/scram/" + inputFile + ".txt"
#     print(commandToRunSCRAM)
#     os.system(commandToRunSCRAM)

gateList = ['or','and']
gateListOR = ['or']
gateListAND = ['and']
failureProb = 0.05
n = 5
while (n<=5):

    def configFileGenXFTA(name):

        with open('xfta.template', 'r') as file:
            filedata = file.read()
        filedata = re.sub("NAME", name, filedata)
        with open("xfta-" + name, 'w') as file:
            file.write(filedata)

    def generateXML(fileName):

        root = ET.Element('opsa-mef')
        faultTreeName = ET.SubElement(root,'define-fault-tree',{'name':'FT'})
        modelData = ET.SubElement(root, 'model-data')


        for gateNumber in range(1,n+1):
            if gateNumber ==(n):
                defineGate = ET.SubElement(faultTreeName, 'define-gate', {'name': 'g' + str(gateNumber)})
                gateType = ET.SubElement(defineGate, random.choice(gateListAND))
                basicEvent1 = ET.SubElement(gateType, 'basic-event', {'name': 'be' + str(gateNumber)})
                basicEvent2 = ET.SubElement(gateType, 'basic-event', {'name': 'bee' + str(gateNumber)})
                #gate = ET.SubElement(gateType, 'gate', {'name': 'g' + str(gateNumber + 1)})

                basicEventValue1 = ET.SubElement(modelData, 'define-basic-event', {'name': 'be' + str(gateNumber)})
                basicEventValu1Assign = ET.SubElement(basicEventValue1, 'float', {'value': str(failureProb)})
                basicEventValue2 = ET.SubElement(modelData, 'define-basic-event', {'name': 'bee' + str(gateNumber)})
                basicEventValu2Assign = ET.SubElement(basicEventValue2, 'float', {'value': str(failureProb)})
            elif gateNumber%2 ==0:
                defineGate = ET.SubElement(faultTreeName, 'define-gate', {'name': 'g' + str(gateNumber)})
                gateType = ET.SubElement(defineGate, random.choice(gateListAND))
                basicEvent1 = ET.SubElement(gateType, 'basic-event', {'name': 'be' + str(gateNumber)})
                basicEvent2 = ET.SubElement(gateType, 'basic-event', {'name': 'bee' + str(gateNumber)})
                gate = ET.SubElement(gateType, 'gate', {'name': 'g' + str(gateNumber + 1)})

                basicEventValue1 = ET.SubElement(modelData, 'define-basic-event', {'name': 'be' + str(gateNumber)})
                basicEventValu1Assign = ET.SubElement(basicEventValue1, 'float', {'value': str(failureProb)})
                basicEventValue2 = ET.SubElement(modelData, 'define-basic-event', {'name': 'bee' + str(gateNumber)})
                basicEventValu2Assign = ET.SubElement(basicEventValue2, 'float', {'value': str(failureProb)})
            else:
                defineGate = ET.SubElement(faultTreeName, 'define-gate', {'name': 'g' + str(gateNumber)})
                gateType = ET.SubElement(defineGate, random.choice(gateListOR))
                basicEvent1 = ET.SubElement(gateType, 'basic-event', {'name': 'be' + str(gateNumber)})
                basicEvent2 = ET.SubElement(gateType, 'basic-event', {'name': 'bee' + str(gateNumber)})
                gate = ET.SubElement(gateType, 'gate', {'name': 'g' + str(gateNumber + 1)})

                basicEventValue1 = ET.SubElement(modelData, 'define-basic-event', {'name': 'be' + str(gateNumber)})
                basicEventValu1Assign = ET.SubElement(basicEventValue1, 'float', {'value': str(failureProb)})
                basicEventValue2 = ET.SubElement(modelData, 'define-basic-event', {'name': 'bee' + str(gateNumber)})
                basicEventValu2Assign = ET.SubElement(basicEventValue2, 'float', {'value': str(failureProb)})



        tree = ET.ElementTree(root)
        tree.write(fileName, xml_declaration=True, encoding='utf-8')

    if __name__=='__main__':
        generateXML('ft-openpsa-'+str(n)+'Gates.xml')
        configFileGenXFTA('ft-openpsa-'+str(n)+'Gates.xml')
        # runXFTA(pathXFTAModels + " " + "xfta-ft-openpsa-"+str(n)+"Gates.xml")
        # runSCRAM('ft-openpsa-'+str(n)+'Gates.xml')
    n+=1
