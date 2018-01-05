#######################################
# git_graft.py
#######################################

import glob
import shutil

from os.path import join as pjoin

from general_utils import *
from svn_utils import *
from git_utils import *

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




