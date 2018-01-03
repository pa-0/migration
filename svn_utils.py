########################
# file: svn_utils.py
########################

import os
from os.path import join as pjoin

from general_utils import *

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


def svn_ls_branches(subpath = "branches"):
    rcode, res = sexe("svn ls %s --verbose" % pjoin(visit_svn_url(),subpath),
                      ret_output = True)
    lines = [ l.strip() for l in res.split("\n") if l.strip() != ""]
    branch_names = [l.split()[-1] for l in lines]
    # cull ./, remove trailing slash
    branch_names = [ b[:-1] for b in branch_names if b != "./"]
    return branch_names

def svn_ls_rc_branches():
    return [b for b in svn_ls_branches() if b.endswith("RC")]

def svn_ls_tags():
    return svn_ls_branches("tags")

def svn_tag_info(tag):
    cmd = "svn log -v -r0:HEAD --stop-on-copy --limit 1 %s" % pjoin(visit_svn_url(),"tags",tag)
    rcode, rout = sexe(cmd,ret_output=True)
    lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
    toks = lines[0].split("|")
    rev, author, date = toks[0], toks[1], toks[2]
    src = lines[-1]
    res = {"rev":  rev,
           "author": author,
           "date": date,
           "full": rout}
    return res

def svn_branch_info(branch):
    cmd = "svn log -v -r0:HEAD --stop-on-copy --limit 1 %s" % pjoin(visit_svn_url(),"branches",branch)
    rcode, rout = sexe(cmd,ret_output=True)
    lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
    toks = lines[0].split("|")
    rev, author, date = toks[0], toks[1], toks[2]
    src = lines[-1]
    res = {"rev":  rev,
           "author": author,
           "date": date,
           "full": rout}
    return res

def svn_tag_rev_map():
    "returns a map from each tage to its svn rev"
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

def svn_list_authors():
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


def git_svn_checkout_src(subpath):
    "git svn clone 'src' for any subpath"
    if not os.path.isdir("src"):
        sexe("git svn clone %s" % pjoin(visit_svn_url(),subpath,"src"))
    else:
        with chdir("src"):
            sexe("git svn fetch")

def git_svn_rev_to_sha_map(src_dir):
    if not os.path.isdir(src_dir):
        return None
    with cchdir(src_dir):
        r = load_json("svn_rev_to_sha_map")
        if not r is None:
            return r
        cmd = "git svn log --show-commit --oneline"
        rcode, rout = sexe(cmd,ret_output=True)
        lines = [ l for l in rout.split("\n") if not l.startswith("-----") and l.strip() != ""]
        for l in lines:
            toks = l.split("|")
            res[toks[0] = toks[1]
        save_json("svn_rev_to_sha_map",res)
        return res




