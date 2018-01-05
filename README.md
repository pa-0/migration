# migration
Scripts for VisIt's SVN to Github Migration

## Creating new visit-src git repo

To craft a new git repos that provides VisIt's source developer and release history, we: 

### Obtain metadata from svn repo (records of authors, tags, etc)

```bash
python svn_fetch_info.py
```

### Obtain trunk and svn RC branches using git svn

This takes quite while due to the size of our svn repo, ssh disconnects, failed git prune operations, etc.

You should be able to keep running the following script iteratively until everything succeeds. 

```bash
python svn_git_clone_branches.py
```

Note: We have a few email address that we need to resolve for svn author mappings, see `nersc_uname_info.py`


### Construct a git repo that grafts our old release structure into a gitflow structure

```bash
python git_graft.py
```

* Create master and develop branches that share an initial dummy commit
* Merge svn trunk (from git svn clone) into develop
* For each RC branch:
  * Create an RC branch off of the develop at the appropriate ref point
  * Merge svn RC (from git svn clone)
    
    Note: We use `git merge -X theirs` to allow the svn RC content to prevail in the case of any conflicts. 
    That said, there are some conflicts that `git merge -X theirs` can't resolve. The only cases I have seen
    are related to symlinks, and can easily be resolved with automated `git checkout --thiers` arm-twisting. 
      
     * For each release on the RC:
       * Tag the start and ending commits for the release on the RC
       * Create a branch (rX.Y.Z) that includes proper subset of RC commits for the release
       * Squash merge this into a  single commit on master 
         
         Note: We encounter the same merge issues related to symlinks in this squash process and we can resolve them the same way.

       * Tag the new master commit with vX.Y.Z


##  TODOS and future scripts

* Extend scripts to pull out data, test, and other history from svn
* Create script to obtain all unique TPL tarballs from SVN (we will host outside of git)


