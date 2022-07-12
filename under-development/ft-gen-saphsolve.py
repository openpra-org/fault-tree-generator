"""
{Egemen M. Aras}
This script creates event-tree(s) / fault-tree(s) in the format of SAPHIRE JSInp.

"""

import json
import itertools
import random
random.seed(123)

numGates = 1000
while(numGates<=50000):
    def ftGenSaphire(fileName):

    #"""reading the json file from sample base"""
        with open ("base-json.json", "r") as f:
            base = json.load(f)


    #    """base parameters"""
        #<======================================================================================>#
    #    """header"""
        projectPath = " "
        eventTreeName =" "
        eventTreeNumber = 0 #do not include event tree
        initEvent = 0 #do not include event tree
        seqPhase = 1 #default
        flagNum = 0 #default
        ftcount = 1 #includes 1 FT in 1 .json file
        fthigh = 11
        sqcount = 0 #set 0(zero) for fault tree
        sqhigh = 0 #default
        #becount = 1 #should be total number of element in eventlist, will update it
        #behigh = 1 #should be highest number of basic event ID, will update it
        mthigh = 1 #default
        phhigh = 1 #default
        ettruncopt = ["NormalProbCutOff" , "NoProbCutOff" , "CondNormalProbCutOff"]
        fttruncopt = ["GlobalProbCutOff" , "NoProbCutOff" , "SystemProbCutOff"]
        sizeopt = ["ENoTrunc" , "ESizeTrunc" , "EZoneTrunc"]
        truncETTRun = ettruncopt[0] #default 1, pick from the list
        truncFTTRun = fttruncopt[0] #default 1, pick from the list
        truncSizePpt = sizeopt[0] #default 1, pick from the list
        truncETTruncval = pow(10,-14) #benchmark value
        truncFTTruncval = pow(10,-14) #benchmark value
        truncSizeval = 99 # default
        truncTransrepl = False # default
        truncTranszones = False # default
        truncTranslevel = 0 # default
        truncUsedual = False # default
        truncDualcutoff = pow(0.0,1) #default
        workSpacePairPH = 1 #default
        workSpacePairMT = 1 #default
        iworkSpacePairPH = 1 #default
        iworkSpacePairMT = 1 #default
        #<======================================================================================>#


        #<======================================================================================>#
        """sysgatelist"""
        sysGateList = base['saphiresolveinput']['sysgatelist']
        sysgatelistName = "FT-Top-Event" #top-event name
        sysgatelistID = fthigh # unique for each FT
        sysgatelistgateID = 1 #top-gate number
        sysgatelistgateOrig = sysgatelistgateID
        sysgatelistGatePos = 0
        sysgatelistEventID = 99
        sysgatelistGateComp = sysgatelistgateID
        sysgatelistCompPos = 0 #default
        sysgatelistCompFlag = " " #default
        sysgatelistGateFlag = " " #default
        sysgatelistGateT = " " #default
        sysgatelistBddSuccess = False #default
        sysgatelistdone = False #default
        #<======================================================================================>#


        #<======================================================================================>#
        """faulttreelist"""
        faultTreeList = base['saphiresolveinput']['faulttreelist']
        ftheaderFTID = fthigh
        ftheaderGtID = sysgatelistgateID
        ftheaderEvID = sysgatelistEventID
        ftheaderDefFlag = 0 #default

        gateList=base['saphiresolveinput']['faulttreelist'][0]['gatelist']

        gatelistGateTypeList = ['or','and']
        gatelistGateTypeListOR = ['or']
        gatelistGateTypeListAND = ['and']
        gatelistNumInputsList = [3]


        for ftheaderNumGates in range(numGates):
            if ftheaderNumGates%2==0:
                gateList[ftheaderNumGates]['gateid'] = ftheaderNumGates + 1
                gateList[ftheaderNumGates]['gatetype'] = random.choice(gatelistGateTypeListOR)
                gateList[ftheaderNumGates]['numinputs'] = random.choice(gatelistNumInputsList)
                gateList[ftheaderNumGates]['eventinput'] = [100 + ftheaderNumGates, 1000 + ftheaderNumGates]
                gateList[ftheaderNumGates]['gateinput'] = [ftheaderNumGates + 1 + 1]
            else:
                gateList[ftheaderNumGates]['gateid'] = ftheaderNumGates + 1
                gateList[ftheaderNumGates]['gatetype'] = random.choice(gatelistGateTypeListAND)
                gateList[ftheaderNumGates]['numinputs'] = random.choice(gatelistNumInputsList)
                gateList[ftheaderNumGates]['eventinput'] = [100 + ftheaderNumGates, 1000 + ftheaderNumGates]
                gateList[ftheaderNumGates]['gateinput'] = [ftheaderNumGates + 1 + 1]
            if gateList[ftheaderNumGates]['gateid'] == numGates:
                gateList[ftheaderNumGates]['gateid'] = ftheaderNumGates + 1
                gateList[ftheaderNumGates]['gatetype'] = random.choice(gatelistGateTypeListAND)
                gateList[ftheaderNumGates]['numinputs'] = random.choice(gatelistNumInputsList) - 1
                gateList[ftheaderNumGates]['eventinput'] = [100 + ftheaderNumGates, 1000 + ftheaderNumGates]
                del gateList[ftheaderNumGates]['gateinput']

            dictCopy = gateList[ftheaderNumGates].copy()
            gateList.append(dictCopy)
        del gateList[-1]

        #<======================================================================================>#


        #<======================================================================================>#
        """sequencelist"""
        """empty for FT"""
        # sequencelist = base['saphiresolveinput']['sequencelist']
        # sequencelistSeqID = " "
        # sequencelistETID = " "
        # sequencelistInitID = " "
        # sequencelistQMethod = " "
        # sequencelistQPasses = " "
        # sequencelistNumLogic = " "
        # sequencelistBlockSize = " "
        # sequencelistLogicList = " "
        #<======================================================================================>#


        #<======================================================================================>#
        """eventlist"""
        eventlist = base['saphiresolveinput']['eventlist']
        eventlistID = sysgatelistEventID
        eventlistCorrGate = sysgatelistgateID
        eventlistName = sysgatelistName
        eventlistEvworkspacepariPH = 1
        eventlistEvworkspacepariMT = 1
        eventlistValue = 1
        eventlistInitf = " "
        eventlistProcessf = " "
        eventlistCalcType = "1"
        #<======================================================================================>#


        #<======================================================================================>#
        #<======================================================================================>#
        """writing parameters to json"""

        #<======================================================================================>#
        """header"""
        base['saphiresolveinput']['header']['projectpath'] = projectPath
        base['saphiresolveinput']['header']['eventtree']['name'] = eventTreeName
        base['saphiresolveinput']['header']['eventtree']['number'] = eventTreeNumber
        base['saphiresolveinput']['header']['eventtree']['initevent'] = initEvent
        base['saphiresolveinput']['header']['eventtree']['seqphase'] = seqPhase
        base['saphiresolveinput']['header']['flagnum'] = flagNum
        base['saphiresolveinput']['header']['ftcount'] = ftcount
        base['saphiresolveinput']['header']['fthigh'] = fthigh
        base['saphiresolveinput']['header']['sqcount'] = sqcount
        base['saphiresolveinput']['header']['sqhigh'] = sqhigh
        #base['saphiresolveinput']['header']['becount'] = becount
        #base['saphiresolveinput']['header']['behigh'] = behigh
        base['saphiresolveinput']['header']['mthigh'] = mthigh
        base['saphiresolveinput']['header']['phhigh'] = phhigh
        base['saphiresolveinput']['header']['truncparam']['ettruncopt'] = truncETTRun
        base['saphiresolveinput']['header']['truncparam']['fttruncopt'] = truncFTTRun
        base['saphiresolveinput']['header']['truncparam']['sizeopt'] = truncSizePpt
        base['saphiresolveinput']['header']['truncparam']['ettruncval']=truncETTruncval
        base['saphiresolveinput']['header']['truncparam']['fttruncval'] = truncFTTruncval
        base['saphiresolveinput']['header']['truncparam']['sizeval'] = truncSizeval
        base['saphiresolveinput']['header']['truncparam']['transrepl'] = truncTransrepl
        base['saphiresolveinput']['header']['truncparam']['transzones'] = truncTranszones
        base['saphiresolveinput']['header']['truncparam']['translevel'] = truncTranslevel
        base['saphiresolveinput']['header']['truncparam']['usedual'] = truncUsedual
        base['saphiresolveinput']['header']['truncparam']['dualcutoff'] = truncDualcutoff
        base['saphiresolveinput']['header']['workspacepair']['ph'] = workSpacePairPH
        base['saphiresolveinput']['header']['workspacepair']['mt'] = workSpacePairMT
        base['saphiresolveinput']['header']['iworkspacepair']['ph'] = iworkSpacePairPH
        base['saphiresolveinput']['header']['iworkspacepair']['mt'] = iworkSpacePairMT
        #<======================================================================================/>#


        #<======================================================================================>#
        """sysgatelist"""
        base['saphiresolveinput']['sysgatelist'][0]['name'] = sysgatelistName #[0] means we have only 1 gate
        base['saphiresolveinput']['sysgatelist'][0]['id'] = sysgatelistID
        base['saphiresolveinput']['sysgatelist'][0]['gateid'] = sysgatelistgateID
        base['saphiresolveinput']['sysgatelist'][0]['gateorig'] = sysgatelistgateOrig
        base['saphiresolveinput']['sysgatelist'][0]['gatepos'] = sysgatelistGatePos
        base['saphiresolveinput']['sysgatelist'][0]['eventid'] = sysgatelistEventID
        base['saphiresolveinput']['sysgatelist'][0]['gatecomp'] = sysgatelistGateComp
        base['saphiresolveinput']['sysgatelist'][0]['comppos'] = sysgatelistCompPos
        base['saphiresolveinput']['sysgatelist'][0]['compflag'] = sysgatelistCompFlag
        base['saphiresolveinput']['sysgatelist'][0]['gateflag'] = sysgatelistGateFlag
        base['saphiresolveinput']['sysgatelist'][0]['gatet'] = sysgatelistGateT
        base['saphiresolveinput']['sysgatelist'][0]['bddsuccess'] = sysgatelistBddSuccess
        base['saphiresolveinput']['sysgatelist'][0]['done'] = sysgatelistdone
        #<======================================================================================/>#



        #<======================================================================================>#
        """faulttreelist"""
        base['saphiresolveinput']['faulttreelist'][0]['ftheader']['ftid'] = ftheaderFTID
        base['saphiresolveinput']['faulttreelist'][0]['ftheader']['gtid'] = ftheaderGtID
        base['saphiresolveinput']['faulttreelist'][0]['ftheader']['evid'] = ftheaderEvID
        base['saphiresolveinput']['faulttreelist'][0]['ftheader']['defflag'] = ftheaderDefFlag
        base['saphiresolveinput']['faulttreelist'][0]['ftheader']['numgates'] = ftheaderNumGates +1
        # #<======================================================================================/>#


        #<======================================================================================>#
        """sequencelist"""
        # base['saphiresolveinput']['sequencelist'][0]['seqid'] = sequencelistSeqID
        # base['saphiresolveinput']['sequencelist'][0]['etid'] = sequencelistETID #must be equal to event eventTreeName
        # base['saphiresolveinput']['sequencelist'][0]['initid'] = sequencelistInitID #must be equal to initEvent
        # base['saphiresolveinput']['sequencelist'][0]['qmethod'] = sequencelistQMethod
        # base['saphiresolveinput']['sequencelist'][0]['qpasses'] = sequencelistQPasses
        # base['saphiresolveinput']['sequencelist'][0]['numlogic'] = sequencelistNumLogic
        # base['saphiresolveinput']['sequencelist'][0]['blocksize'] = sequencelistBlockSize
        # base['saphiresolveinput']['sequencelist'][0]['logiclist'] = sequencelistLogicList
        # #<======================================================================================/>#



        # #<======================================================================================>#
        """eventlist"""
        base['saphiresolveinput']['eventlist'][3]['id'] = eventlistID
        base['saphiresolveinput']['eventlist'][3]['corrgate'] = eventlistCorrGate
        base['saphiresolveinput']['eventlist'][3]['name'] = eventlistName
        base['saphiresolveinput']['eventlist'][3]['evworkspacepair']['ph'] = eventlistEvworkspacepariPH
        base['saphiresolveinput']['eventlist'][3]['evworkspacepair']['mt'] = eventlistEvworkspacepariMT
        base['saphiresolveinput']['eventlist'][3]['value'] = eventlistValue
        base['saphiresolveinput']['eventlist'][3]['initf'] = eventlistInitf
        base['saphiresolveinput']['eventlist'][3]['processf'] = eventlistProcessf
        base['saphiresolveinput']['eventlist'][3]['calctype'] = eventlistCalcType

        basicEventList = []
        for item in range(len(gateList)):
            basicEventList.append(gateList[item]['eventinput'])
        basicEventList=(list(itertools.chain(*basicEventList)))

        becount = 4+len(basicEventList)
        base['saphiresolveinput']['header']['becount'] = becount
        behigh = max(basicEventList)
        base['saphiresolveinput']['header']['behigh'] = behigh

        eventList=base['saphiresolveinput']['eventlist']

        for numBasicEvents in range(len(basicEventList)):
            eventList[numBasicEvents+4]['id'] = basicEventList[numBasicEvents]
            eventList[numBasicEvents+4]['corrgate'] = 0
            eventList[numBasicEvents+4]['name'] = str(basicEventList[numBasicEvents])
            eventList[numBasicEvents+4]['evworkspacepair']['ph'] = 1
            eventList[numBasicEvents+4]['evworkspacepair']['mt'] = 1
            eventList[numBasicEvents+4]['value'] = 0.05
            eventList[numBasicEvents+4]['initf'] = " "
            eventList[numBasicEvents+4]['processf'] = " "
            eventList[numBasicEvents+4]['calctype'] = 1
            dictCopy = eventList[numBasicEvents].copy()
            eventList.append(dictCopy)
        del eventList[-1]
        del eventList[-1]
        del eventList[-1]
    #<======================================================================================/>#
        with open (fileName, "w") as f:
            json.dump(base, f, indent=4)

#writing the manipulated base file in a new json file
    if __name__=='__main__':
        ftGenSaphire('ft-saphsolve-'+str(numGates)+'Gates.JSInp')
    numGates+=1000
