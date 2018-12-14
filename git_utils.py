#######################################
# git_utils.py
#######################################

import glob
import shutil
import datetime

from os.path import join as pjoin

from general_utils import *
from svn_utils import *


def datetime_to_git_date_format(dt):
    return dt.strftime('%a %b %d %H:%M:%S %Y')

def git_add_remote(name,path):
    "adds a git remote, so we can use it to obtain branches"
    if not os.path.isdir(pjoin(path,".git")):
         print "[ERROR ADDING REMOTE: %s does not have a .git dir]" % path
         sys.exit(-1)
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
    rc_trunk_root = git_svn_find_closest_rev("checkouts/svn_trunk/trunk/",rc_rev)
    sha = git_svn_rev_to_sha_map("checkouts/svn_trunk/trunk")[rc_trunk_root]
    print rc
    print "rc creation rev:", rc_rev
    print "closest trunk rev,sha:", rc_trunk_root,sha
    return rc_rev, rc_trunk_root, sha


def git_repo_dir():
    return pjoin(root_dir(),"git_repo","visit-src")

def git_ls_commits():
    rcode, rout = sexe("git log",ret_output=True)
    res = []
    c = {}
    msg = ""
    for l in rout.split("\n"):
        if l.startswith("commit "):
            if msg != "":
                c["message"] = msg
                res.append(dict(c))
            c = {}
            msg =""
            c["sha"] = l.split(" ")[1]
        elif l.startswith("Author: "):
            c["author"] = l[len("Author: "):].strip()
        elif l.startswith("Date: "):
            c["date"] = l[len("Date: "):].strip()
        else:
            msg += l
    c["message"] = msg
    res.append(dict(c))
    return res


def git_ls_clearquest_commits():
    cmts = git_ls_commits()
    res = []
    for c in cmts:
        if c["author"] == "Hank Childs <hank@uoregon.edu>":
            if c["message"].count(" Update from ") > 0:
                res.append(c)
            elif c["message"].count(" Initial repo entry ") > 0:
                res.append(c)
        if c["author"] == "Cyrus Harrison <cyrush@llnl.gov>":
            if c["message"].count("initialize repo") > 0:
                res.append(c)
    return res

def visit_clearquest_date_to_git_date(cmt):
    # finds the clearquest commit date from our svn commit message
    # and turns it to the proper date string for a git commit
    if cmt["message"].count("initialize repo") > 0:
        cq_date = "June 1, 2003"
    else:
        cq_date = cmt["message"][cmt["message"].find(" Update from ") + len(" Update from "):]
        cq_date = cq_date[:cq_date.find("git-svn-id")].strip()
        if cq_date == "repo entry":
            cq_date = "June 1, 2003"
    dt = datetime.datetime.strptime(cq_date, '%B %d, %Y')
    return datetime_to_git_date_format(dt) + " -0700"

def git_write_clearquest_commit_date_filter():
    cmd = "git filter-branch -f --env-filter \\\n"
    cmd += "'"
    for cmt in git_ls_clearquest_commits():
        ndate = visit_clearquest_date_to_git_date(cmt)
        cmd += git_gen_commit_filter_case(cmt["sha"],ndate)
    cmd += "'\n"
    open("sh_git_fix_clearquest_commit_dates.sh","w").write(cmd)

    
def git_gen_commit_filter_case(sha,ndate):
    return """
    if [ $GIT_COMMIT = %s ]
     then
         export GIT_AUTHOR_DATE="%s"
         export GIT_COMMITTER_DATE="%s"
    fi
    """ % (sha,ndate,ndate)


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
        if l.count("renamed") > 0 :
            f = l.split(":")[1].strip()
            f = f.split(" ")[0].strip()
            res.append(f)
        if unmerged and l.count(":") > 0:
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
            # strip off svn_
            path = pjoin(v,k[4:])
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

def git_generate_rc_branch_patch(rc):
    with cchdir(pjoin("checkouts","svn_%s" % rc,"%s" % rc)):
         cs = git_ls_commits()
         num_commits = len(cs)
         # first commit is always the svn copy, which is huge
         # and we don't need a patch for it 
         patch_commits = num_commits -1
         cmd = "git format-patch -%d --stdout > pgen_%s.patch" % (patch_commits,rc)
         sexe(cmd)

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
        sys.exit(-1)
        merge_msg = "merge svn branch as git %s branch" % rc
        # we may actually have conflicts
        rcode,rout = sexe('git merge -m "%s" svn_%s/master' % (merge_msg,rc),fatal_on_error=False)
        #rcode,rout = sexe('git merge -X theirs -m "%s" svn_%s/master' % (merge_msg,rc),fatal_on_error=False)
        # check if conflicts were the reason we failed
        if rcode != 0 and len(git_ls_conflicts()) == 0:
            print "[UNKNOWN ERROR with merge -- stopping]"
            sys.exit(-1)
        elif rcode != 0:
            print "[stopping on conflict -- stopping]"
            sys.exit(-1)
            # checkout 'thiers' to resolve final conflicts
            git_conflicts_checkout_and_add_theirs()
            sexe('git commit -m "%s"' % (merge_msg))
  
def git_create_branch_for_tag_release(tag):
    rc = svn_tag_to_rc(tag)
    sha_st, rv_st, sha_end, rv_end  = git_svn_tag_sha_range(tag)
    print "[%s tag range on git %s Branch: %s %s (svn revs: %s %s)]" % (tag,rc,sha_st,sha_end, rv_st,rv_end)
    with cchdir(git_repo_dir()):
        sexe("git checkout %s" % rc)
        sexe('git tag -a r%s.release.start -m "tag r%s start" %s' % (tag,tag,sha_st))
        sexe('git tag -a r%s.release.end   -m "tag r%s end" %s' % (tag,tag,sha_end))
        sexe("git checkout -b r%s %s" % (tag,sha_st))
        sexe("git merge %s" % sha_end)


def svn_date_to_git_date(svn_date):
    #ex = '2010-08-04 07:20:43 -0700 (Wed, 04 Aug 2010)'
    svn_date = svn_date[:svn_date.find("(")].strip()
    utc_offset = svn_date[svn_date.rfind(" "):]
    svn_date = svn_date[:svn_date.rfind(" ")]
    dt = datetime.datetime.strptime(svn_date, '%Y-%m-%d %H:%M:%S')
    return datetime_to_git_date_format(dt) + utc_offset


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
        sexe('git commit -m "%s release"' % tag)
        tag_info = svn_tag_info(tag)
        tag_date = svn_date_to_git_date(tag_info["date"])
        sexe('GIT_AUTHOR_DATE="%s" GIT_COMMITTER_DATE="%s" git tag -a v%s -m "tag r%s"' % (tag_date,tag_date,tag,tag))




