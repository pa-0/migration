########################
# file: general_utils
########################

import sys
import os
import subprocess
import json
import datetime
import glob
import shutil

from os.path import join as pjoin

script_path =  os.path.split(os.path.abspath(__file__))[0]
def root_dir():
    return script_path


def sexe(cmd,ret_output=False,echo = True,fatal_on_error=True, env=None):
        """ Helper for executing shell commands. """
        kwargs = {"shell":True}
        if not env is None:
            kwargs["env"] = env
        if echo:
            print "[exe: %s]" % cmd
        if ret_output:
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.STDOUT
            p = subprocess.Popen(cmd,**kwargs)
            rout =p.communicate()[0]
            res = p.returncode,rout
        else:
            res = subprocess.call(cmd,**kwargs),""
        if fatal_on_error and res[0] != 0:
            print("ERROR! rcode = %d" % res[0])
            if ret_output:
                print res[1]
            sys.exit(res[0])
        return res

def split_lines(txt):
     return [ l for l in txt.split("\n") if l.strip() != ""]

class cchdir():
    def __init__(self, dirname):
        self.dirname = dirname
        self.oldwd =  os.getcwd()

    def __enter__(self):
        if not os.path.isdir(self.dirname):
            print "[creating directory %s]" % self.dirname
            os.makedirs(self.dirname)
        print "[changing working directory to %s]" % self.dirname
        os.chdir(self.dirname)

    def __exit__(self, *args):
        print "[changing working directory to %s]" % self.oldwd
        os.chdir(self.oldwd)

def timenow():
    return datetime.datetime.now()
    
def timestamp(t=None,sep="_"):
    """ Creates a timestamp that can easily be included in a filename. """
    if t is None:
        t = timenow()    
    sargs = (t.year,t.month,t.day,t.hour,t.minute,t.second)
    sbase = "".join(["%04d",sep,"%02d",sep,"%02d",sep,"%02d",sep,"%02d",sep,"%02d"])
    return sbase % sargs

def read_json(name):
    fname = "info_" + name + ".json"
    if not os.path.isfile(fname):
        return None
    return json.load(open(fname))

def save_json(name,data):
    json.dump(data,open("info_" + name + ".json","w"))
    return data

def clear_json_files():
    fs = glob.glob("info*.json")
    if len(fs) == 0:
        print "no info*.json files found"
        return 
    des_dir = "_info_%s" % timestamp()
    print "moving json files to %s" % des_dir
    os.mkdir(des_dir)
    for f in fs:
        shutil.move(f,des_dir)

