
import json

def loading_json(FT_Number):

    FT_Number_start = 1
    FT_Number_end = FT_Number
    with open("base-json.json", "r") as f:

        base = json.load(f)

        # parameters = fault_tree.factors
        base['saphiresolveinput']['header'][
            'projectpath'] = '"projectpath": "Edatadrive82NCState-NEUPModelsGenericPWR Model-debug",'
        base['saphiresolveinput']['header']['eventtree']['name'] = '"",'
        base['saphiresolveinput']['header']['eventtree']['number'] = "1,"
        base['saphiresolveinput']['header']['eventtree']['initevent'] = "13,"
        base['saphiresolveinput']['header']['eventtree']['seqphase'] = "1"
        base['saphiresolveinput']['header']['flagnum'] = "0,"
        base['saphiresolveinput']['header']['ftcount'] = FT_Number
        base['saphiresolveinput']['header']['fthigh'] = "TBD 139 # largest ID of the FTs"
        base['saphiresolveinput']['header']['sqcount'] = seq_num
        base['saphiresolveinput']['header']['sqhigh'] = "TBD The highest sequence unique internal number in the list of sequences"
        base['saphiresolveinput']['header']['becount'] = 1 + FT_Number #+# of basic events from each fault tree
        base['saphiresolveinput']['header']['behigh'] = "TBD the highest integer ID number of BEs"
        base['saphiresolveinput']['header']['mthigh'] = 1
        base['saphiresolveinput']['header']['phhigh'] = 1
        base['saphiresolveinput']['header']['truncparam']['ettruncopt'] = 'NormalProbCutOff'
        base['saphiresolveinput']['header']['truncparam']['fttruncopt'] = 'GlobalProbCutOff'
        base['saphiresolveinput']['header']['truncparam']['sizeopt'] = 'ENoTrunc'
        base['saphiresolveinput']['header']['truncparam']['ettruncval'] = 1.000E-14
        base['saphiresolveinput']['header']['truncparam']['fttruncval'] = 1.000E-14
        base['saphiresolveinput']['header']['truncparam']['sizeval'] = 99
        base['saphiresolveinput']['header']['truncparam']['transrepl'] = "test"
        base['saphiresolveinput']['header']['truncparam']['transzones'] = "test"
        base['saphiresolveinput']['header']['truncparam']['translevel'] = 0
        base['saphiresolveinput']['header']['truncparam']['usedual'] = "test"
        base['saphiresolveinput']['header']['truncparam']['dualcutoff'] = 0.000E+00
        base['saphiresolveinput']['header']['workspacepair']['ph'] = 1
        base['saphiresolveinput']['header']['workspacepair']['mt'] = 1
        base['saphiresolveinput']['header']['iworkspacepair']['ph'] = 1
        base['saphiresolveinput']['header']['iworkspacepair']['mt'] = 1
        #


        sysgatelist = []
        faulttreelist = []
        sequencelist  = []

# you will need to add the gatelist/logic for each fault tree here.

        for i in range(FT_Number_start,FT_Number_end + 1):
            sysgate = {
                'name': "cool",  # fault_tree.name
                'id': 139,
                'gateid': "cool",  # int(fault_tree.top_gate.name.strip('"root'))
                'gateorig': "cool",  # int(fault_tree.top_gate.name.strip('root'))
                'gatepos': 0,
                'eventid': 99996,
                'gatecomp': "cool",  # int(fault_tree.top_gate.name.strip('root'))
                'comppos': 0,
                'bddsuccess': "test",
                'done': "test"
            }
            sysgatelist.append(sysgate)

            faulttree = {
                'ftheader': {
                    'ftid': 139,
                    'gtid': "cool",  # int(fault_tree.top_gate.name.strip('root'))
                    'evid': 99996,
                    'defflag': 0,
                    'numgates': "cool"  # len(fault_tree.gates)
                }
                # Add other properties for fault tree logic
            }
            faulttreelist.append(faulttree)

            seqlist = {
                "seqid": 1,
                "etid": 1,
                "initid": 13,
                "qmethod": "M",
                "qpasses": 0,
                "numlogic": 2,
                "blocksize": 2,
                "logiclist": [
                    262145,
                    262146
                ]
            }
            sequencelist.append(seqlist)
        base['saphiresolveinput']['sysgatelist'] = sysgatelist
        base['saphiresolveinput']['faulttreelist'] = faulttreelist
        base['saphiresolveinput']['sequencelist'] = sequencelist

        with open("ET.json", "w") as f:
            json.dump(base, f, indent=4)

FT_Number = int(input("Enter the # of fault trees to be linked to the event tree: "))

def calculate_maximum_sequences(FT_Number):
    maximum_sequences = 2 ** FT_Number - 1
    return maximum_sequences

print("maximum number of sequences based on the # of fault trees chosen is:", calculate_maximum_sequences(FT_Number))
Sequence_Number = int(input("Enter the # of sequences to be assumed as \"FAILURE\" and to be solved by SAPHSOLVE:"))
if Sequence_Number > calculate_maximum_sequences(FT_Number):
    print ("error: number of sequences to be solved should be less than the maximum number of sequences")
else:
    seq_num = calculate_maximum_sequences(FT_Number)
    loading_json(FT_Number)
#note for myself, that you shouldn't print the input if the number of sequence is so large
# loading_json(FT_Number)
