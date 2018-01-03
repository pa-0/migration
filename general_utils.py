########################
# file: general_utils
########################

import sys
import os
import subprocess
import json

from os.path import join as pjoin

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


class cchdir():
    def __init__(self, dirname):
        self.dirnane = dirname
        self.oldwd =  os.getcwd()

    def __enter__(self):
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)
        os.chdir(self.dirname)

    def __exit__(self, *args):
        os.chdir(self.oldwd)

def timestamp():
    return str(datetime.datetime.now())

def read_json(name):
    fname = "info_" + name + ".json"
    if not os.path.isfile(fname):
        return None
    return json.load(open(fname))

def save_json(name,data):
    json.dump(data,open("info_" + name + ".json","w"))
    return data
