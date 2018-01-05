#######################################
# git_graft.py
#######################################

import glob
import shutil

from os.path import join as pjoin

from general_utils import *
from svn_utils import *



def git_add_remote(name,path):
    "adds a git remote, so we can use it to obtain branches"
    sexe("git remote add %s %s/.git" % (name,path))

def git_svn_find_closest_rev(src_dir,rev):
    #print "lookin for %s in %s" % (rev,src_dir)
    rev_map = git_svn_rev_to_sha_map(src_dir)
    # exact match
    if rev in rev_map.keys():
        return rev
    # need to find closest commit before this
    rev = int(rev[1:])
    revs = rev_map.keys()
    revs = [ int(r[1:]) for r in revs]
    revs.sort()
    last = revs[0]
    for k in revs:
         if k < rev:
             last = k
         else:
             return "r%d" % last
    return "r%d" % last

def git_svn_tag_sha_range(tag):
    rc = svn_tag_to_rc(tag)
    rc_co_dir = git_svn_rc_checkout_dir(rc)
    rc_st, rc_end = svn_tag_range(tag)

    
    rc_root_st  = git_svn_find_closest_rev(rc_co_dir,rc_st)
    rc_root_end = git_svn_find_closest_rev(rc_co_dir,rc_end)
    
    sha_st  = git_svn_rev_to_sha_map(rc_co_dir)[rc_root_st]
    sha_end = git_svn_rev_to_sha_map(rc_co_dir)[rc_root_end]
    return sha_st, rc_root_st, sha_end, rc_root_end


def git_svn_rc_branch_sha_info(rc):
    rc_rev  = svn_rc_creation_map()[rc]
    rc_trunk_root = git_svn_find_closest_rev("checkouts/svn_trunk/src",rc_rev)
    sha = git_svn_rev_to_sha_map("checkouts/svn_trunk/src")[rc_trunk_root]
    print rc
    print "rc creation rev:", rc_rev
    print "closest trunk rev,sha:", rc_trunk_root,sha
    return rc_rev, rc_trunk_root, sha


def git_svn_rc_checkout_dir(rc):
    return pjoin(root_dir(),"checkouts","svn_" + rc,"src")


def git_repo_dir():
    return pjoin(root_dir(),"git_repo","visit-src")

def git_ls_branches():
    rcode, rout = sexe("git branch",ret_output=True)
    remotes = [ l[:1].strip() for l in rout.split("\n") if l.strip() != ""]

def git_ls_remotes():
    rcode, rout = sexe("git remote",ret_output=True)
    return split_lines(rout)

def git_ls_conflicts():
    rcode,rout = sexe("git status", ret_output=True)
    lines = split_lines(rout)
    res = []
    unmerged = False
    for l in lines:
        if unmerged:
            res.append(l.split(":")[1].strip())
        elif l.count("to mark resolution)") > 0:
           unmerged = True
    return res

def git_conflicts_checkout_and_add_theirs():
    cfiles = git_ls_conflicts()
    for cfile in cfiles:
        sexe("git checkout --theirs %s" % cfile)
        sexe("git add %s" % cfile)

def git_setup_new_repo():
    if os.path.isdir(git_repo_dir()):
        dest = "_visit_src_%s" % timestamp()
        print "[moving existing repo to %s]" %dest
        shutil.move(git_repo_dir(),pjoin("git_repo",dest))
    with cchdir(git_repo_dir()):
        sexe("git init")
        sexe("touch .gitignore")
        sexe("git add .gitignore")
        sexe('git commit -m "initialize repo"')

def git_connect_git_svn_remotes():
    with cchdir(git_repo_dir()):
        for k,v in svn_git_svn_checkout_dirs().items():
            path = pjoin(v,"src")
            print "[adding remote: %s (%s)]" % (k,path)
            git_add_remote(k,path)

def git_fetch_all_remotes():
    with cchdir(git_repo_dir()):
        for r in git_ls_remotes():
            sexe("git fetch %s" % r)

def git_setup_develop():
    with cchdir(git_repo_dir()):
        # fetch remote
        sexe("git fetch svn_trunk")
        sexe("git checkout -b develop")
        sexe('git merge -m "merge svn trunk as git develop" svn_trunk/master')

def git_create_rc_branch(rc):
    # find the sha that corresponds to the proper trunk rev
    rc_rev, rc_trunk_rev, sha = git_svn_rc_branch_sha_info(rc)
    with cchdir(git_repo_dir()):
        # fetch remote with svn RC commits
        sexe("git fetch svn_%s" % rc)
        # create rc branch off of develop at proper rev
        sexe("git checkout develop")
        sexe("git checkout -b %s %s" % (rc,sha))
        # merge svn RC commits into new rc branch
        merge_msg = "merge svn branch as git %s branch" % rc
        # we may actually have conflicts
        rcode,rout = sexe('git merge -X theirs -m "%s" svn_%s/master' % (merge_msg,rc),fatal_on_error=False)
        # check if conflicts were the reason we failed
        if rcode != 0 and len(git_ls_conflicts()) == 0:
            print "[UNKNOWN ERROR with merge -- stopping]"
            sys.exit(-1)
        elif rcode != 0:
            # checkout 'thiers' to resolve final conflicts
            git_conflicts_checkout_and_add_theirs()
            sexe('git commit -m "%s"' % (merge_msg))

  
def git_create_branch_for_tag_release(tag):
    rc = svn_tag_to_rc(tag)
    sha_st, rv_st, sha_end, rv_end  = git_svn_tag_sha_range(tag)
    print "[%s tag range on git %s Branch: %s %s (svn revs: %s %s)]" % (tag,rc,sha_st,sha_end, rv_st,rv_end)
    with cchdir(git_repo_dir()):
        sexe("git checkout %s" % rc)
        sexe("git checkout -b r%s %s" % (tag,sha_st))
        sexe("git merge %s" % sha_end)

def git_merge_release_to_master_and_tag(tag):
    with cchdir(git_repo_dir()):
        sexe("git checkout master")
        rcode, rout = sexe("git merge -X theirs --squash r%s" % tag,fatal_on_error=False)
        # check if conflicts were the reason we failed
        if rcode != 0 and len(git_ls_conflicts()) == 0:
            print "[UNKNOWN ERROR with merge -- stopping]"
            sys.exit(-1)
        elif rcode != 0:
            # checkout 'thiers' to resolve final conflicts
            git_conflicts_checkout_and_add_theirs()
        # TODO: add --author="John Doe <john@doe.com>"         
        sexe('git commit -m "%s release"' % tag)
        sexe('git tag -a v%s -m "tag r%s"' % (tag,tag))


def git_graft():
    svn_check_rc_git_svn_repos()
    rcs = svn_ls_rc_branches()
    git_setup_new_repo()
    git_connect_git_svn_remotes()
    git_setup_develop()
    # for each rc, create rc branch
    for rc in rcs:
        if os.path.isdir( git_svn_rc_checkout_dir(rc)):
            git_create_rc_branch(rc)
    # for each release, create squashed commit to master
    for rc in rcs:
      for release in svn_release_tags_for_rc(rc):
           git_create_branch_for_tag_release(release)
           git_merge_release_to_master_and_tag(release)

#git_graft()

with cchdir(git_repo_dir()):
    git_ls_conflicts()


# create each release on master
# for each tag, prep a branch off of the rc that will provide a source for us
# to squash merge to #  master  to do this, we need the commit ranges for the tags

#git_create_rc_branch("2.0RC")
#git_create_branch_for_tag_release("2.0.0")
#git_merge_release_to_master_and_tag("2.0.0")
#git_create_branch_for_tag_release("2.0.2")
#git_merge_release_to_master_and_tag("2.0.2")

#git_create_rc_branch("2.1RC")

#git_create_branch_for_tag_release("2.1.1")
#git_merge_release_to_master_and_tag("2.1.1")
#git_create_branch_for_tag_release("2.1.1")
#git_merge_release_to_master_and_tag("2.1.1")




