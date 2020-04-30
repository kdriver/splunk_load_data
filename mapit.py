import requests,os,json,time,uuid
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file",default="log1.json")
parser.add_argument("-t","--twice",action='store_true',default=False)
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
delete_it("formatted.json")


for f in js:
	seconds = int(time.time())
	f['epoch'] = seconds

dump_files("")


outfile = os.path.splitext(json_file)[0] + "_out.json"

with open(outfile,"w") as wf:
	for f in js:
		obj = json.dumps(f)
		wf.write("{}\n".format(obj))

