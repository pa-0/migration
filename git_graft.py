#######################################
# git_graft.py
#######################################

import glob
from os.path import join as pjoin

from general_utils import *


def git_add_svn_as_remote(name,path):
    "adds a git remote, so we can use it to obtain branches"
    sexe("git remote add %s %s/.git" % (name,path))

def git_setup_new_repo():
    if os.path.isdir("git_repo/visit-src"):
        shutil.rmtree("git_repo/visit-src")
    with cchdir("git_repo/visit-src"):
        sexe("git init")
        sexe("git checkout -b develop")
        checkouts = glob.glob(pjoin("..","checkouts","*"))
        for co in checkouts:
            git_add_svn_as_remote(co,
                                  pjoin("..","checkouts",co,"src"))

#######################################
# Soup of git commands we will need
######################################
#
# Create an RC Branch
# git co develop
# git checkout -b branchname <DEVELOP_COMMIT>
#
# Create and Tag a Release
# git co master
# git merge --theirs --squash <Z.YRC_COMMIT>
# git commit --author="John Doe <john@doe.com>" -m "merge for release z.y.x"
# git tag -a vz.y.x -m "tagging version z.y.x"
# 
#


