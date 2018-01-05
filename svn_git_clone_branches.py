##################################
# file: svn_git_clone_branches.py
##################################


from os.path import join as pjoin
from svn_utils import *

def git_svn_clone(branch):
    dest = pjoin(root_dir(),"checkouts","svn_%s" % branch)
    rc_start_revs = svn_rc_creation_map()
    print "[checking git svn clone at %s]" % dest
    with cchdir(dest):
        rev_str = None
        if branch != "trunk":
            rev_id = SVNRev(rc_start_revs[branch])
            # start looking one rev before ...
            rev_str = "r%d" % (rev_id.number()-1)
        if not git_svn_check_clone(rev_str):
            if branch == "trunk":
                git_svn_clone_src("%s" % branch)   
            else:
                # for an rc we know where the branches start, 
                # use this to speed up the clone

                git_svn_clone_src("branches/%s" % branch, rev=rev_str)
        else:
            print "[git svn clone at %s is up to date]" % dest

def git_svn_clone_all():
    branches = svn_ls_rc_branches()
    branches.append("trunk")
    for b in branches:
        git_svn_clone(b)

#git_svn_clone("2.11RC")

if __name__ == "__main__":
    git_svn_clone_all()

