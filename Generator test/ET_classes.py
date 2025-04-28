from typing import Any, List, Optional, TypeVar, Type, cast, Callable
import random
from enum import Enum
from typing import Any, List, Optional
from typing import Any, List
import json
import argparse
T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)
def from_int(x: Any) -> int:
    # assert isinstance(x, int) and not isinstance(x, bool)
    return x

def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x

def to_class(c: Type[T], x: Any) -> dict:
    if isinstance(x, list):
        return [to_class(c, item) for item in x]
    return cast(Any, x).to_dict()

def to_enum(c: Type[EnumT], x: Any) -> Optional[EnumT]:
    if isinstance(x, c):
        return x.value
    else:
        return None
def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]
def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    if isinstance(x, list):
        return [f(y) for y in x]
    else:
        return [f(x)]

def from_none(x: Any) -> Any:
    assert x is None
    return x

def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False

def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)
def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x
def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x

class Workspacepair:
    ph: int
    mt: int

    def __init__(self, ph: int, mt: int) -> None:
        self.ph = ph
        self.mt = mt

    @staticmethod
    def from_dict(obj: Any) -> 'Workspacepair':
        assert isinstance(obj, dict)
        ph = from_int(obj.get("ph"))
        mt = from_int(obj.get("mt"))
        return Workspacepair(ph, mt)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ph"] = from_int(self.ph)
        result["mt"] = from_int(self.mt)
        return result

class Initf(Enum):
    EMPTY = " "
    I = "I"

class Eventlist:
    id: int
    corrgate: int
    name: str
    evworkspacepair: Workspacepair
    value: int
    initf: Initf
    processf: Initf
    calctype: str

    def __init__(self, id: int, corrgate: int, name: str, evworkspacepair: Workspacepair, value: int, initf: Initf, processf: Initf, calctype: str) -> None:
        self.id = id
        self.corrgate = corrgate
        self.name = name
        self.evworkspacepair = evworkspacepair
        self.value = value
        self.initf = initf
        self.processf = processf
        self.calctype = calctype

    @staticmethod
    def from_dict(obj: Any) -> 'Eventlist':
        assert isinstance(obj, dict)
        id = int(from_str(obj.get("id")))
        corrgate = int(from_str(obj.get("corrgate")))
        name = from_str(obj.get("name"))
        evworkspacepair = Workspacepair.from_dict(obj.get("evworkspacepair"))
        value = from_int(obj.get("value"))
        initf = Initf(obj.get("initf"))
        processf = Initf(obj.get("processf"))
        calctype = from_str(obj.get("calctype"))
        return Eventlist(id, corrgate, name, evworkspacepair, value, initf, processf, calctype)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(str(self.id))
        result["corrgate"] = from_str(str(self.corrgate))
        result["name"] = from_str(self.name)
        result["evworkspacepair"] = to_class(Workspacepair, self.evworkspacepair)
        result["value"] = from_int(self.value)
        result["initf"] = to_enum(Initf, self.initf)
        result["processf"] = to_enum(Initf, self.processf)
        result["calctype"] = from_str(self.calctype)
        return result

class Ftheader:
    ftid: int
    gtid: int
    evid: int
    defflag: int
    numgates: int

    def __init__(self, ftid: int, gtid: int, evid: int, defflag: int, numgates: int) -> None:
        self.ftid = ftid
        self.gtid = gtid
        self.evid = evid
        self.defflag = defflag
        self.numgates = numgates

    @staticmethod
    def from_dict(obj: Any) -> 'Ftheader':
        assert isinstance(obj, dict)
        ftid = from_int(obj.get("ftid"))
        gtid = from_int(obj.get("gtid"))
        evid = from_int(obj.get("evid"))
        defflag = from_int(obj.get("defflag"))
        numgates = from_int(obj.get("numgates"))
        return Ftheader(ftid, gtid, evid, defflag, numgates)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ftid"] = from_int(self.ftid)
        result["gtid"] = from_int(self.gtid)
        result["evid"] = from_int(self.evid)
        result["defflag"] = from_int(self.defflag)
        result["numgates"] = from_int(self.numgates)
        return result

class Gatelist:
    gateid: int
    gatetype: str
    numinputs: int
    gateinput: Optional[List[int]]
    eventinput: Optional[List[int]]

    def __init__(self, gateid: int, gatetype: str, numinputs: int, gateinput: Optional[List[int]] = None, eventinput: Optional[List[int]] = None) -> None:
        self.gateid = gateid
        self.gatetype = gatetype
        self.numinputs = numinputs
        self.gateinput = gateinput if gateinput is not None else []
        self.eventinput = eventinput if eventinput is not None else []

    @staticmethod
    def from_dict(obj: Any) -> 'Gatelist':
        assert isinstance(obj, dict)
        gateid = from_int(obj.get("gateid"))
        gatetype = from_str(obj.get("gatetype"))
        numinputs = from_int(obj.get("numinputs"))
        gateinput = from_union([lambda x: from_list(from_int, x), from_none], obj.get("gateinput"))
        eventinput = from_list(from_int, obj.get("eventinput"))
        return Gatelist(gateid, gatetype, numinputs, gateinput, eventinput)

    def to_dict(self) -> dict:
        result: dict = {}
        result["gateid"] = from_int(self.gateid)
        result["gatetype"] = from_str(self.gatetype)
        result["numinputs"] = from_int(self.numinputs)
        if  len(self.gateinput) > 0:
            result["gateinput"] = from_union([lambda x: from_list(from_int, x), from_none], self.gateinput)
        if len(self.eventinput) > 0:
            result["eventinput"] = from_union([lambda x: from_list(from_int, x), from_none], self.eventinput)
        return result
class Faulttreelist:
    ftheader: Ftheader
    gatelist: List[Gatelist]

    def __init__(self, ftheader: Ftheader, gatelist: List[Gatelist]) -> None:
        self.ftheader = ftheader
        self.gatelist = gatelist

    @staticmethod
    def from_dict(obj: Any) -> 'Faulttreelist':
        assert isinstance(obj, dict)
        ftheader = Ftheader.from_dict(obj.get("ftheader"))
        gatelist = from_list(Gatelist.from_dict, obj.get("gatelist"))
        return Faulttreelist(ftheader, gatelist)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ftheader"] = to_class(Ftheader, self.ftheader)
        result["gatelist"] = from_list(lambda x: to_class(Gatelist, x), self.gatelist)
        return result

class Eventtree:
    name: str
    number: int
    initevent: int
    seqphase: int

    def __init__(self, name: str, number: int, initevent: int, seqphase: int) -> None:
        self.name = name
        self.number = number
        self.initevent = initevent
        self.seqphase = seqphase

    @staticmethod
    def from_dict(obj: Any) -> 'Eventtree':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        number = from_int(obj.get("number"))
        initevent = from_int(obj.get("initevent"))
        seqphase = from_int(obj.get("seqphase"))
        return Eventtree(name, number, initevent, seqphase)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["number"] = from_int(self.number)
        result["initevent"] = from_int(self.initevent)
        result["seqphase"] = from_int(self.seqphase)
        return result
class Truncparam:
    ettruncopt: str
    fttruncopt: str
    sizeopt: str
    ettruncval: float
    fttruncval: float
    sizeval: int
    transrepl: bool
    transzones: bool
    translevel: int
    usedual: bool
    dualcutoff: int

    def __init__(self, ettruncopt: str, fttruncopt: str, sizeopt: str, ettruncval: float, fttruncval: float, sizeval: int, transrepl: bool, transzones: bool, translevel: int, usedual: bool, dualcutoff: int) -> None:
        self.ettruncopt = ettruncopt
        self.fttruncopt = fttruncopt
        self.sizeopt = sizeopt
        self.ettruncval = ettruncval
        self.fttruncval = fttruncval
        self.sizeval = sizeval
        self.transrepl = transrepl
        self.transzones = transzones
        self.translevel = translevel
        self.usedual = usedual
        self.dualcutoff = dualcutoff

    @staticmethod
    def from_dict(obj: Any) -> 'Truncparam':
        assert isinstance(obj, dict)
        ettruncopt = from_str(obj.get("ettruncopt"))
        fttruncopt = from_str(obj.get("fttruncopt"))
        sizeopt = from_str(obj.get("sizeopt"))
        ettruncval = from_float(obj.get("ettruncval"))
        fttruncval = from_float(obj.get("fttruncval"))
        sizeval = from_int(obj.get("sizeval"))
        transrepl = from_bool(obj.get("transrepl"))
        transzones = from_bool(obj.get("transzones"))
        translevel = from_int(obj.get("translevel"))
        usedual = from_bool(obj.get("usedual"))
        dualcutoff = from_int(obj.get("dualcutoff"))
        return Truncparam(ettruncopt, fttruncopt, sizeopt, ettruncval, fttruncval, sizeval, transrepl, transzones, translevel, usedual, dualcutoff)

    def to_dict(self) -> dict:
        result: dict = {}
        result["ettruncopt"] = from_str(self.ettruncopt)
        result["fttruncopt"] = from_str(self.fttruncopt)
        result["sizeopt"] = from_str(self.sizeopt)
        result["ettruncval"] = to_float(self.ettruncval)
        result["fttruncval"] = to_float(self.fttruncval)
        result["sizeval"] = from_int(self.sizeval)
        result["transrepl"] = from_bool(self.transrepl)
        result["transzones"] = from_bool(self.transzones)
        result["translevel"] = from_int(self.translevel)
        result["usedual"] = from_bool(self.usedual)
        result["dualcutoff"] = from_int(self.dualcutoff)
        return result
class Header:
    projectpath: str
    eventtree: Eventtree
    flagnum: int
    ftcount: int
    fthigh: int
    sqcount: int
    sqhigh: int
    becount: int
    behigh: int
    mthigh: int
    phhigh: int
    truncparam: Truncparam
    workspacepair: Workspacepair
    iworkspacepair: Workspacepair

    def __init__(self, projectpath: str, eventtree: Eventtree, flagnum: int, ftcount: int, fthigh: int, sqcount: int, sqhigh: int, becount: int, behigh: int, mthigh: int, phhigh: int, truncparam: Truncparam, workspacepair: Workspacepair, iworkspacepair: Workspacepair) -> None:
        self.projectpath = projectpath
        self.eventtree = eventtree
        self.flagnum = flagnum
        self.ftcount = ftcount
        self.fthigh = fthigh
        self.sqcount = sqcount
        self.sqhigh = sqhigh
        self.becount = becount
        self.behigh = behigh
        self.mthigh = mthigh
        self.phhigh = phhigh
        self.truncparam = truncparam
        self.workspacepair = workspacepair
        self.iworkspacepair = iworkspacepair

    @staticmethod
    def from_dict(obj: Any) -> 'Header':
        assert isinstance(obj, dict)
        projectpath = from_str(obj.get("projectpath"))
        eventtree = Eventtree.from_dict(obj.get("eventtree"))
        flagnum = from_int(obj.get("flagnum"))
        ftcount = from_int(obj.get("ftcount"))
        fthigh = from_int(obj.get("fthigh"))
        sqcount = from_int(obj.get("sqcount"))
        sqhigh = from_int(obj.get("sqhigh"))
        becount = from_int(obj.get("becount"))
        behigh = from_int(obj.get("behigh"))
        mthigh = from_int(obj.get("mthigh"))
        phhigh = from_int(obj.get("phhigh"))
        truncparam = Truncparam.from_dict(obj.get("truncparam"))
        workspacepair = Workspacepair.from_dict(obj.get("workspacepair"))
        iworkspacepair = Workspacepair.from_dict(obj.get("iworkspacepair"))
        return Header(projectpath, eventtree, flagnum, ftcount, fthigh, sqcount, sqhigh, becount, behigh, mthigh, phhigh, truncparam, workspacepair, iworkspacepair)

    def to_dict(self) -> dict:
        result: dict = {}
        result["projectpath"] = from_str(self.projectpath)
        result["eventtree"] = to_class(Eventtree, self.eventtree)
        result["flagnum"] = from_int(self.flagnum)
        result["ftcount"] = from_int(self.ftcount)
        result["fthigh"] = from_int(self.fthigh)
        result["sqcount"] = from_int(self.sqcount)
        result["sqhigh"] = from_int(self.sqhigh)
        result["becount"] = from_int(self.becount)
        result["behigh"] = from_int(self.behigh)
        result["mthigh"] = from_int(self.mthigh)
        result["phhigh"] = from_int(self.phhigh)
        result["truncparam"] = to_class(Truncparam, self.truncparam)
        result["workspacepair"] = to_class(Workspacepair, self.workspacepair)
        result["iworkspacepair"] = to_class(Workspacepair, self.iworkspacepair)
        return result
class Sequencelist:
    seqid: int
    etid: int
    initid: int
    qmethod: str
    qpasses: int
    numlogic: int
    blocksize: int
    logiclist: List[int]

    def __init__(self, seqid: int, etid: int, initid: int, qmethod: str, qpasses: int, numlogic: int, blocksize: int, logiclist: List[int]) -> None:
        self.seqid = seqid
        self.etid = etid
        self.initid = initid
        self.qmethod = qmethod
        self.qpasses = qpasses
        self.numlogic = numlogic
        self.blocksize = blocksize
        self.logiclist = logiclist

    @staticmethod
    def from_dict(obj: Any) -> 'Sequencelist':
        assert isinstance(obj, dict)
        seqid = from_int(obj.get("seqid"))
        etid = from_int(obj.get("etid"))
        initid = from_int(obj.get("initid"))
        qmethod = from_str(obj.get("qmethod"))
        qpasses = from_int(obj.get("qpasses"))
        numlogic = from_int(obj.get("numlogic"))
        blocksize = from_int(obj.get("blocksize"))
        logiclist = from_list(from_int, obj.get("logiclist"))
        return Sequencelist(seqid, etid, initid, qmethod, qpasses, numlogic, blocksize, logiclist)

    def to_dict(self) -> dict:
        result: dict = {}
        result["seqid"] = from_int(self.seqid)
        result["etid"] = from_int(self.etid)
        result["initid"] = from_int(self.initid)
        result["qmethod"] = from_str(self.qmethod)
        result["qpasses"] = from_int(self.qpasses)
        result["numlogic"] = from_int(self.numlogic)
        result["blocksize"] = from_int(self.blocksize)
        result["logiclist"] = from_list(from_int, self.logiclist)
        return result
class Sysgatelist:
    name: str
    id: int
    gateid: int
    gateorig: int
    gatepos: int
    eventid: int
    gatecomp: int
    comppos: int
    compflag: Initf
    gateflag: Initf
    gatet: Initf
    bddsuccess: bool
    done: bool

    def __init__(self, name: str, id: int, gateid: int, gateorig: int, gatepos: int, eventid: int, gatecomp: int, comppos: int, compflag: Initf, gateflag: Initf, gatet: Initf, bddsuccess: bool, done: bool) -> None:
        self.name = name
        self.id = id
        self.gateid = gateid
        self.gateorig = gateorig
        self.gatepos = gatepos
        self.eventid = eventid
        self.gatecomp = gatecomp
        self.comppos = comppos
        self.compflag = compflag
        self.gateflag = gateflag
        self.gatet = gatet
        self.bddsuccess = bddsuccess
        self.done = done

    @staticmethod
    def from_dict(obj: Any) -> 'Sysgatelist':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        id = from_int(obj.get("id"))
        gateid = from_int(obj.get("gateid"))
        gateorig = from_int(obj.get("gateorig"))
        gatepos = from_int(obj.get("gatepos"))
        eventid = from_int(obj.get("eventid"))
        gatecomp = from_int(obj.get("gatecomp"))
        comppos = from_int(obj.get("comppos"))
        compflag = Initf(obj.get("compflag"))
        gateflag = Initf(obj.get("gateflag"))
        gatet = Initf(obj.get("gatet"))
        bddsuccess = from_bool(obj.get("bddsuccess"))
        done = from_bool(obj.get("done"))
        return Sysgatelist(name, id, gateid, gateorig, gatepos, eventid, gatecomp, comppos, compflag, gateflag, gatet, bddsuccess, done)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["id"] = from_int(self.id)
        result["gateid"] = from_int(self.gateid)
        result["gateorig"] = from_int(self.gateorig)
        result["gatepos"] = from_int(self.gatepos)
        result["eventid"] = from_int(self.eventid)
        result["gatecomp"] = from_int(self.gatecomp)
        result["comppos"] = from_int(self.comppos)
        result["compflag"] = to_enum(Initf, self.compflag)
        result["gateflag"] = to_enum(Initf, self.gateflag)
        result["gatet"] = to_enum(Initf, self.gatet)
        result["bddsuccess"] = from_bool(self.bddsuccess)
        result["done"] = from_bool(self.done)
        return result
class Saphiresolveinput:
    header: Header
    sysgatelist: List[Sysgatelist]
    faulttreelist: List[Faulttreelist]
    sequencelist: List[Sequencelist]
    eventlist: List[Eventlist]

    def __init__(self, header: Header, sysgatelist: List[Sysgatelist], faulttreelist: List[Faulttreelist], sequencelist: List[Sequencelist], eventlist: List[Eventlist]) -> None:
        self.header = header
        self.sysgatelist = sysgatelist
        self.faulttreelist = faulttreelist
        self.sequencelist = sequencelist
        self.eventlist = eventlist

    @staticmethod
    def from_dict(obj: Any) -> 'Saphiresolveinput':
        assert isinstance(obj, dict)
        header = Header.from_dict(obj.get("header"))
        sysgatelist = from_list(Sysgatelist.from_dict, obj.get("sysgatelist"))
        faulttreelist = from_list(Faulttreelist.from_dict, obj.get("faulttreelist"))
        sequencelist = from_list(Sequencelist.from_dict, obj.get("sequencelist"))
        eventlist = from_list(Eventlist.from_dict, obj.get("eventlist"))
        return Saphiresolveinput(header, sysgatelist, faulttreelist, sequencelist, eventlist)

    def to_dict(self) -> dict:
        result: dict = {}
        result["header"] = to_class(Header, self.header)
        result["sysgatelist"] = from_list(lambda x: to_class(Sysgatelist, x), self.sysgatelist)
        result["faulttreelist"] = from_list(lambda x: to_class(Faulttreelist, x), self.faulttreelist)
        result["sequencelist"] = from_list(lambda x: to_class(Sequencelist, x), self.sequencelist)
        result["eventlist"] = from_list(lambda x: to_class(Eventlist, x), self.eventlist)
        return result
class Welcome:
    version: str
    saphiresolveinput: Saphiresolveinput

    def __init__(self, version: str, saphiresolveinput: Saphiresolveinput) -> None:
        self.version = version
        self.saphiresolveinput = saphiresolveinput

    @staticmethod
    def from_dict(obj: Any) -> 'Welcome':
        assert isinstance(obj, dict)
        version = from_str(obj.get("version"))
        saphiresolveinput = Saphiresolveinput.from_dict(obj.get("saphiresolveinput"))
        return Welcome(version, saphiresolveinput)

    def to_dict(self) -> dict:
        result: dict = {}
        result["version"] = from_str(self.version)
        result["saphiresolveinput"] = to_class(Saphiresolveinput, self.saphiresolveinput)
        return result
def welcome_from_dict(s: Any) -> Welcome:
    return Welcome.from_dict(s)
def welcome_to_dict(x: Welcome) -> Any:
    return to_class(Welcome, x)


import random

# Example usage:
ft_count = 2
gate_count = 4
be_count = 8
seed_value = 0
# ...
fault_tree_list = []
event_list = []
system_gate_list = []

workspacepair = Workspacepair(ph=1, mt=1)


def monte_carlo_fault_tree_distribution(ft_count, gate_count, be_count, seed=None):
    if seed is not None:
        random.seed(seed)
    gate_id_counter = 1
    used_gate_ids = set()
    used_event_ids = set()
    max_event_id = 0  # Initialize the maximum event_id to 0
    for ft_id in range(1, ft_count + 1):
        gatelist = []
        num_gates_in_ft = gate_count // ft_count + (1 if ft_id <= gate_count % ft_count else 0)
        num_be_in_ft = be_count // ft_count + (1 if ft_id <= be_count % ft_count else 0)

        # Generate unique gate IDs for this fault tree
        all_gate_ids = list(range(1, gate_count + 1))
        gate_ids = random.sample(all_gate_ids, num_gates_in_ft)
        all_gate_ids = [gate_id for gate_id in all_gate_ids if gate_id not in gate_ids and gate_id not in used_gate_ids]

        # Generate unique basic event IDs for this fault tree
        all_be_ids = list(range(ft_count * gate_count + 1, ft_count * gate_count + be_count + 1))
        event_ids = random.sample(all_be_ids, num_be_in_ft)
        all_be_ids = [be_id for be_id in all_be_ids if be_id not in event_ids and be_id not in used_event_ids]
        max_event_id = max(max_event_id, max(event_ids))


        # Start gate_id from 1 for each fault tree
        event = Eventlist(
            id=ft_id,
            corrgate="0",
            name=f"FT-{ft_id}",
            evworkspacepair=Workspacepair(ph=1, mt=1),
            value=1.00000E+00,
            initf=Initf.EMPTY,
            processf=Initf.EMPTY,
            calctype='1'
        )
        event_list.append(event)
        while len(gatelist) < num_gates_in_ft:
            gate_id = gate_id_counter
            available_gate_ids = [id for id in gate_ids if id != gate_id]
            num_gate_inputs = min(num_gates_in_ft - 1, random.randint(0, num_gates_in_ft - 1))
            num_gate_inputs = min(num_gates_in_ft - 1, random.randint(0, num_gates_in_ft - 1))
            selected_gate_ids = random.sample(available_gate_ids, num_gate_inputs)
            gate_ids = [id for id in gate_ids if id not in selected_gate_ids]
            used_gate_ids.update(selected_gate_ids)

            num_available_events = len(event_ids)
            num_event_inputs = min(num_gates_in_ft - num_gate_inputs, num_available_events)
            selected_event_ids = random.sample(event_ids, num_event_inputs)
            event_ids = [be_id for be_id in event_ids if be_id not in selected_event_ids]
            used_event_ids.update(selected_event_ids)
            total = selected_gate_ids + selected_event_ids
            num_input = len(total)
            max_event_id = max(max_event_id, max(selected_event_ids))
            # top = max(event_ids)
            # print(top)
            gate = Gatelist(
                gateid=gate_id,
                gatetype=random.choice(["and", "or"]),
                numinputs=num_input,
                gateinput=selected_gate_ids if selected_gate_ids else None,
                eventinput=selected_event_ids if selected_event_ids else []
            )

            for event_id in selected_event_ids:
                event = Eventlist(
                    id= event_id,
                    corrgate="0",
                    name=f"BE-{event_id}",
                    evworkspacepair=Workspacepair(ph=1, mt=1),
                    value=random.uniform(0, 1),
                    initf=Initf.EMPTY,
                    processf=Initf.EMPTY,
                    calctype='1'
                )
                event_list.append(event)
            gate_id_counter += 1
            gatelist.append(gate)

        top_gate = random.choice(gatelist)
        top_gate_id = top_gate.gateid
        max_event_id = max(max_event_id, max(event_ids))
        # print(max_event_id)
        ftheader = Ftheader(
            ftid=ft_id,
            gtid=top_gate_id,
            evid=ft_id,
            defflag=0,
            numgates=num_gates_in_ft
        )

        sysgatelist =Sysgatelist(
            name=f"FT-{ft_id}",
            id=ft_id,
            gateid=top_gate_id,
            gateorig=top_gate_id,
            gatepos=0,
            eventid=ft_id,
            gatecomp=top_gate_id,
            comppos=0,
            compflag=Initf.EMPTY,
            gateflag=Initf.EMPTY,
            gatet=Initf.EMPTY,
            bddsuccess=False,
            done=False
        )
        system_gate_list.append(sysgatelist)
        fault_tree = Faulttreelist(ftheader=ftheader, gatelist=gatelist)
        fault_tree_list.append(fault_tree)
    eventlist_1 = Eventlist(id=max_event_id + 103, corrgate=0, name="<TRUE>", evworkspacepair=workspacepair,
                            value=1.00000E+00, initf=Initf.EMPTY, processf=Initf.EMPTY, calctype="1")
    eventlist_2 = Eventlist(id=max_event_id + 102, corrgate=0, name="<FALSE>", evworkspacepair=workspacepair,
                            value=0.00000, initf=Initf.EMPTY, processf=Initf.EMPTY, calctype="1")
    eventlist_3 = Eventlist(id=max_event_id + 101, corrgate=0, name="<PASS>", evworkspacepair=workspacepair,
                            value=1.00000E+00, initf=Initf.EMPTY, processf=Initf.EMPTY, calctype="1")
    eventlist_4 = Eventlist(id=max_event_id + 100, corrgate=0, name="INIT-EV", evworkspacepair=workspacepair,
                            value=1.00000E+00, initf=Initf.I, processf=Initf.EMPTY, calctype="N")
    event_list.append(eventlist_1)
    event_list.append(eventlist_2)
    event_list.append(eventlist_3)
    event_list.append(eventlist_4)

    return max_event_id


# Generate fault trees using the Monte Carlo method with the specified seed
monte_carlo_fault_tree_distribution(ft_count, gate_count, be_count, seed=seed_value)


eventtree = Eventtree(name="Tree", number=1, initevent=114, seqphase=1)
trunc_param = Truncparam("NormalProbCutOff", "GlobalProbCutOff", "ENoTrunc", 1.0e-14, 1.0e-14, 99, False, False, 0, False, 0.0)
# Create an instance of Saphiresolveinput
header = Header(projectpath="path/to/project", eventtree=eventtree, flagnum=0, ftcount=ft_count, fthigh=ft_count, sqcount=1, sqhigh=1, becount=4+ft_count+5, behigh=117, mthigh=1, phhigh=1, truncparam=trunc_param, workspacepair=workspacepair, iworkspacepair=workspacepair)
# sysgatelist = [Sysgatelist(name="Gate1", id=1, gateid=2, gateorig=3, gatepos=4, eventid=5, gatecomp=6, comppos=7, compflag=Initf.I, gateflag=Initf.EMPTY, gatet=Initf.EMPTY, bddsuccess=True, done=False)]
sequencelist = [Sequencelist(seqid=1, etid=1, initid=114, qmethod="M", qpasses=0, numlogic=2, blocksize=2, logiclist=[262145, 262146])]

# Convert the Welcome instance to a dictionary

saphiresolveinput = Saphiresolveinput(header=header, sysgatelist=system_gate_list, faulttreelist=fault_tree_list, sequencelist=sequencelist, eventlist=event_list)
welcome = Welcome(version="1.0.0", saphiresolveinput=saphiresolveinput)

# Convert the instance to a dictionary
welcome_dict = welcome.to_dict()
def write_json_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write JSON data to a file.")
    parser.add_argument("output_file", help="Name of the output JSON file")
    args = parser.parse_args()

    output_file = args.output_file
    write_json_to_file(welcome_dict, output_file)

    print("JSON data has been written to:", output_file)
