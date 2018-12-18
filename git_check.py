#######################################
# git_graft.py
#######################################

import glob
import shutil

from os.path import join as pjoin

from general_utils import *
from svn_utils import *
from git_utils import *


def gen_tag_tarball(rel):
    with cchdir(git_repo_dir()):
        sexe("git checkout v%s" % rel)
        sexe("tar -czvf visit.test.%s.tar.gz src/" % rel)

def git_check_gen_tag_tarballs():
    # for each release, create squashed commit to master
    rcs = svn_ls_rc_branches()
    for rc in rcs:
      if not rc.startswith("1."):
          print "[checking releases off of rc %s]" % rc
          for release in svn_release_tags_for_rc(rc):
              print "[gen tarball for release %s]" % release
              gen_tag_tarball(release)

def find_pairs():
    res = {}
    rts =glob.glob(pjoin("release_tarballs","*"))
    for r in rts:
         r_val = os.path.split(r)[1]
         r_val = r_val[len("visit"):]
         r_val = r_val[:r_val.find(".tar.gz")]
         print r, r_val
         t = pjoin("new_tarballs","visit.test.%s.tar.gz" % r_val)
         if os.path.isfile(t):
             res[r] = t
    return res

def stage_pair(a,b):
    af = os.path.abspath(a)
    bf = os.path.abspath(b)
    r_val = os.path.split(af)[1]
    r_val = r_val[len("visit"):]
    r_val = r_val[:r_val.find(".tar.gz")]
    print r_val
    with cchdir("_extract"):
        odir = "stage_%s_old" % r_val
        os.mkdir(odir)
        with cchdir(odir):
            sexe("tar -xzvf %s" % af)
        ndir = "stage_%s_new" % r_val
        os.mkdir(ndir)
        print odir, ndir
        with cchdir(ndir):
            sexe("tar -xzvf %s" % bf)
        sexe("diff -bur stage_%s_new/src/ stage_%s_old/visit%s/src/ > mout_diff_%s.txt" % (r_val,r_val,r_val,r_val), fatal_on_error=False)
         


def git_check():
    #git_check_gen_tag_tarballs() 
    #
    p = find_pairs()
    for k,v in p.items():
    #     if k.count("2.13.3") > 0:
         stage_pair(k,v)
    #    sys.exit(0)

if __name__ == "__main__":
    git_check()


