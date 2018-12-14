#######################################
# git_graft.py
#######################################

import glob
import shutil

from os.path import join as pjoin

from general_utils import *
from svn_utils import *
from git_utils import *


def git_graft_initial_setup():
    print "[checking rc git svn repos]"
    svn_check_rc_git_svn_repos()
    print "[setting up new git repo]"
    git_setup_new_repo()
    print "[connecting git svn remotes]"
    git_connect_git_svn_remotes()

def git_graft_setup_develop():
    print "[setting up git develop branch]"
    git_setup_develop()

def git_graft_create_rc_branches():
    # for each rc, create rc branch
    rcs = svn_ls_rc_branches()
    for rc in rcs:
        if os.path.isdir( git_svn_rc_checkout_dir(rc)):
            print "[creating rc branch %s]" % rc
            git_create_rc_branch(rc)

def git_graft_tag_releases():
    # for each release, create squashed commit to master
    rcs = svn_ls_rc_branches()
    for rc in rcs:
      print "[tagging releases off off rc %s]" % rc
      for release in svn_release_tags_for_rc(rc):
           print "[tagging release %s]" % release
           git_create_branch_for_tag_release(release)
           git_merge_release_to_master_and_tag(release)

def git_graft():
    #git_graft_initial_setup()
    #git_graft_setup_develop()
    #git_graft_create_rc_branches()
    #git_graft_tag_releases()
    git_final_cleaup()
    git_gen_lfs_migrate_script()

if __name__ == "__main__":
    git_graft()

#git_graft()
#rcs = svn_ls_rc_branches()
#for rc in rcs:
#    for release in svn_release_tags_for_rc(rc):
#        git_create_branch_for_tag_release(release)
#        git_merge_release_to_master_and_tag(release)


#git_create_rc_branch("2.13RC")
#for release in svn_release_tags_for_rc("2.2RC"):
#    git_create_branch_for_tag_release(release)
#    git_merge_release_to_master_and_tag(release)


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




