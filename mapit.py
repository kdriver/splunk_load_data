import requests,os,json,time,uuid
import argparse
from datetime import datetime
from datetime import timedelta


parser = argparse.ArgumentParser()
parser.add_argument("-f","--file",default="log1.json")
parser.add_argument("-p","--prefix",default="./events/")
parser.add_argument("-r","--repeat",type=int,default=0)
cla = parser.parse_args()
print(cla)
json_file = "nipper.json"
if cla.file is not None:
    json_file = cla.file

directory='.'
NDJSON=1
NORMAL=2
filetype=NDJSON

#JSON can be in an array, or newline delimited. Test to see which
with open(json_file) as fn:
    first = fn.readline()
    if first[0] == '[':
        filetype = NORMAL
    fn.close()
#
#  Read in the JSON from Nipper.  The JSON has already been through map.py to fix some issues
#
print("open {} ".format(json_file))
js=[]
with open(json_file) as fn:
    if filetype == NORMAL:
        js=json.load(fn)
    else:
        for line in fn:
            json_object = json.loads(line)
            js = js + [json_object]
print("read in {} json file ok with {} objects\n".format(filetype,len(js)))


def dump_files(skip):
    with open("formatted.json","a") as wf:
        json.dump(js, wf, indent=4)
    
#delete a filename - checking that it exists first 
def delete_it(filename):
    if os.path.exists(filename):    
        os.remove(filename)

#delete all files this script generates before we regenerate them

def read_geodata(geod):
        with open('geodata.json',"r") as geo:
                for line in geo:
                        jo = json.loads(line)
                        hn = jo['device']['hostname']
                        loc = jo['location']
                        geod[hn] = loc

geo_data = {}
read_geodata(geo_data)
print(json.dumps(geo_data,indent=4))


prefix  = "./events/"
if cla.file is not None:
    prefix = cla.prefix

outfile = os.path.splitext(json_file)[0] + "_out.json"

delete_it(outfile)

def write_individual_files(events,seq):
  with open(outfile,"a") as wf:
    for f in events:
        obj = json.dumps(f)
        wf.write("{}\n".format(obj))
        seq = seq + 1
        fn = "{}evt_{}.json".format(prefix,seq)
        fp=open(fn,"w")
        fp.write("{}\n".format(obj))
        fp.close()
    wf.close()
    return seq

#a UUID to uniquly identify this run
session_uuid = str(uuid.uuid4())
print(session_uuid)
seconds = time.time() 
t1 = datetime.now()
seq=0
nipper_id=1

#for every report in the original add the UUID and some text
for report in js:
        report['nipper_session'] = session_uuid
        report['nipper_text'] = "Research Network first audit"
        report['date_time'] = t1.strftime("%a %b %d %H:%M:%S %Y")
        report['epoch'] = seconds
        report['nipper_id'] = nipper_id
        nipper_id = nipper_id + 1
        try:
                hn = report['device']['hostname']
                locn = geo_data[hn]
                report['location'] = locn
                report['device'].pop('not_operating_system',None)
        except Exception as e: 
               pass 

        try:
                finding = report['finding']
                finding.pop('table',None)
                report['finding'] = finding
        except:
                pass

#write out formatted json for ease of use
with open(outfile+'.formatted',"w") as wf:
    wf.write(json.dumps(js,indent=4))

seq=write_individual_files(js,seq)

if cla.repeat != 0:
        for day in range(1,cla.repeat):
                t1 = datetime.now() - timedelta(days=day)
                t1_str = t1.strftime("%a %b %d %H:%M:%S %Y")
                session_uuid = str(uuid.uuid4())
                print(session_uuid)
                #for every report in the original add  a different UUID and text. This simulates a second audit
                seconds = seconds - (60*60*24)
                for report in js:
                        report['nipper_text'] = "Research Network audit"
                        report['nipper_session'] = session_uuid
                        report['date_time'] = t1_str
                        report['epoch'] = seconds
                seq = write_individual_files(js,seq)

