########################
# file: svn_fetch_info
########################

from svn_utils import *

rcs  = svn_ls_rc_branches()
tags = svn_ls_tags()

tag_map = svn_tag_rev_map()
tag_keys =tag_map.keys()
tag_keys.sort(key=release_key)

for k in tag_keys:
    print k, tag_map[k]

rc_map = svn_rc_creation_map()
rc_keys =rc_map.keys()
rc_keys.sort(key=release_key)

for k in rc_keys:
    print k, rc_map[k]

print json.dumps(svn_list_authors(),indent=2)
