########################
# file: svn_utils.py
########################

import os
from os.path import join as pjoin

from general_utils import *

from nersc_uname_info import uname_info as nersc_uname_info


class SVNRev(object):
    def __init__(self,string_val):
        self.val = int(string_val[1:]) # remove leading r

    def number(self):
        return self.val

    def __str__(self):
        return "r%d" % self.value


class SVNTag(object):
    def __init__(self,string_val):
        self.val = [ int(v) for v in string_val.split(".")]

    def value(self):
        return self.val

    def major(self):
        return self.val[0]

    def minor(self):
        return self.val[1]

    def patch(self):
        return self.val[2]
    
    def rc(self):
        return ("%d.%d" % (self.major(),self.minor())) + "RC"

    def __str__(self):
        return ".".join(self.vals)


def release_key(a):
    "used to sort visit release keys"
    atoks = a.split(".")
    if len(atoks)  == 2:
        if atoks[-1].endswith("RC"):
            atoks[-1] = atoks[-1][:-2]
    atoks = [ int(v) for v in atoks]
    r = (atoks[0] * 1000000)  + (atoks[1] * 10000)
    if len(atoks) > 2:
        r += atoks[2] * 100
    if len(atoks) > 3:
        r += atoks[3]
    return r

def visit_svn_url(uname="cyrush",anon=False):
    "URL to use to fetch svn"
    if not anon:
        return "svn+ssh://%s@edison.nersc.gov/project/projectdirs/visit/svn/visit/" % uname
    else:
        return "http://visit.ilight.com/svn/visit/"


def svn_generate_authors_file():
    f = open("info_nersc_authors.txt","w")
    for k,v in nersc_uname_info().items():
        if v["email"].count("@") == 0:
            print "warning: missing email for %s" % k
        f.write("%s = %s <%s>\n" % (k,v["name"],v["email"]))

def svn_ls_branches(subpath = "branches"):
    "lists branches at given subpath"
    rcode, res = sexe("svn ls %s --verbose" % pjoin(visit_svn_url(),subpath),
                      ret_output = True)
    lines = [ l.strip() for l in res.split("\n") if l.strip() != ""]
    branch_names = [l.split()[-1] for l in lines]
    # cull ./, remove trailing slash
    branch_names = [ b[:-1].strip() for b in branch_names if b != "./"]
    return branch_names


def svn_tag_info(tag):
    "provides info about a given tag"
    cmd = "svn log -v -r0:HEAD --stop-on-copy --limit 1 %s" % pjoin(visit_svn_url(),"tags",tag)
    rcode, rout = sexe(cmd,ret_output=True)
    lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
    toks = lines[0].split("|")
    toks = [ t.strip() for t in toks]
    rev, author, date = toks[0], toks[1], toks[2]
    src = lines[-1]
    res = {"rev":  rev,
           "author": author,
           "date": date,
           "full": rout}
    return res

def svn_branch_info(branch):
    "provides info about a given svn branch"
    cmd = "svn log -v -r0:HEAD --stop-on-copy --limit 1 %s" % pjoin(visit_svn_url(),"branches",branch)
    rcode, rout = sexe(cmd,ret_output=True)
    lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
    toks = lines[0].split("|")
    toks = [ t.strip() for t in toks]
    rev, author, date = toks[0], toks[1], toks[2]
    src = lines[-1]
    res = {"rev":  rev,
           "author": author,
           "date": date,
           "full": rout}
    return res


#
# note: many of these methods cache results in json files to speed things up
#       to clear these files use clear_json_files() in general_utils
#


def svn_ls_rc_branches():
    "returns a sorted list of svn rc branches"
    r = read_json("svn_rc_branches")
    if not r is None:
        return r    
    res = [b for b in svn_ls_branches() if b.endswith("RC")]
    res.sort(key=release_key)
    save_json("svn_rc_branches",res)
    return res

def svn_ls_tags():
    "returns a sorted list of svn tags"
    r = read_json("svn_tags")
    if not r is None:
        return r
    res = svn_ls_branches("tags")
    res.sort(key=release_key)
    save_json("svn_tags",res)
    return res

def svn_tag_rev_map():
    "returns a map from each tag to its svn rev"
    r = read_json("svn_tag_rev_map")
    if not r is None:
        return r
    res = {}
    tags = svn_ls_tags()
    for tag in tags:
        tinfo = svn_tag_info(tag)
        res[tag] = tinfo["rev"]
    save_json("svn_tag_rev_map",res)
    return res


def svn_rc_creation_map():
    "returns a map from each rc to its svn creation rev"
    r = read_json("svn_rc_creation_map")
    if not r is None:
        return r
    res = {}
    rcs = svn_ls_rc_branches()
    for rc in rcs:
        tinfo = svn_branch_info(rc)
        res[rc] = tinfo["rev"]
    save_json("svn_rc_creation_map",res)
    return res

def svn_ls_authors():
    "returns a list of all svn authors"
    r = read_json("svn_authors")
    if not r is None:
        return r
    res = {}
    cmd = "svn log --quiet %s" % visit_svn_url()
    rcode, rout = sexe(cmd,ret_output=True)
    lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
    for l in lines:
        toks = l.split("|")
        uname = toks[1].strip()
        res[uname] = l
    res = res.keys()
    save_json("svn_authors",res)
    return res

def svn_tag_to_rc(tag):
    "converts a tag string to rc name"
    return SVNTag(tag).rc()

def svn_tag_range(tag):
    """
    returns the start and last rev of a tag.
    We need this to create branches for squash merges to release.
    """
    # rev last is the actual tag rev
    rev_last = svn_tag_rev_map()[tag]
    
    # rev_start is either the prev release
    #  or its the beginning of the rc branch
    t_val = SVNTag(tag)
    if t_val.patch() == 0:
        rc = svn_tag_to_rc(tag)
        rev_start = svn_rc_creation_map()[rc]
    else:
        ok = False
        prev_tag = "%d.%d.%d" % (t_val.major(), t_val.minor(), t_val.patch() -1 )
        # fix missing release 2.0.1 doesn't exist, we only have
        # 2.0.0 and 2.0.2
        if prev_tag == "2.0.1":
            rc = svn_tag_to_rc(tag)
            rev_start = svn_rc_creation_map()[rc]
        else:
            rev_start = svn_tag_rev_map()[prev_tag]
    return rev_start, rev_last    


def svn_release_tags_for_rc(rc):
    res = []
    # trim "RC"
    rc_root = rc[:-2]
    tags = svn_ls_tags()
    for t in tags:
        if t.startswith(rc_root +"."):
            res.append(t)
    res.sort(key=release_key)
    return res

def svn_git_svn_checkout_dirs():
    cos = glob.glob(pjoin(root_dir(),"checkouts","svn_*"))
    res = {}
    for co in cos:
        name = os.path.split(co)[1]
        res[name] = co
    return res


def svn_check_rc_git_svn_repos():
    cos = svn_git_svn_checkout_dirs()
    rcs = svn_ls_rc_branches()
    ok = True
    for rc in rcs:
        rc_cos = [ v[4:] for v in cos.keys()]
        if not rc in rc_cos:
            print "missing checkout of %s" % rc
            ok = False
    return ok


def git_svn_clone_src(subpath,rev=None):
    "git svn clone 'src' for any subpath"
    fetch_range = " "
    if not rev is None:
       fetch_range = " -%s:HEAD " % rev
    print fetch_range
    subpath_final = os.path.split(subpath)[-1]
    if not os.path.isdir(subpath_final):
        authors_txt = pjoin(root_dir(),"info_nersc_authors.txt")
        cmd = "git svn clone --authors-file=%s" % authors_txt
        cmd += fetch_range
        cmd += '--ignore-paths="releases|svninfo|third_party|vendor_branches|windowsbuild" '
        cmd += pjoin(visit_svn_url(),subpath)
        sexe(cmd)
    else:
        with chdir(subpath_final):
            # check for gc file, prune case
            gc_file = pjoin(".git","gc.txt")
            if os.path.isfile(gc_file):
                sexe("git prune")
                os.remove(gc_file)
            cmd = "git svn fetch"
            cmd += fetch_range
            sexe(cmd)

def git_svn_rev_to_sha_map(src_dir):
    "returns a map from svn rev to git sha for a git svn repo at src_dir"
    if not os.path.isdir(src_dir):
        print "BAD SRC DIR: %s" % src_dir
        return None
    with cchdir(src_dir):
        r = read_json("svn_rev_to_sha_map")
        if not r is None:
            return r
        res = {}
        cmd = "git svn log --show-commit --oneline"
        rcode, rout = sexe(cmd,ret_output=True)
        lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
        for l in lines:
            toks = l.split("|")
            res[toks[0].strip()] = toks[1].strip()
        save_json("svn_rev_to_sha_map",res)
        return res

def git_svn_check_clone(rev = None):
    rcode = 1
    fetch_range = ""
    if not rev is None:
       fetch_range = " -%s:HEAD " % rev
    if os.path.isdir("src"):
        with cchdir("src"):
            cmd = "git svn fetch"
            cmd += fetch_range
            rcode, rout = sexe(cmd, fatal_on_error = False)
    return rcode == 0


def git_svn_rc_checkout_dir(rc):
    return pjoin(root_dir(),"checkouts","svn_" + rc,"src")



