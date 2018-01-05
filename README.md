# migration
Scripts for VisIt's SVN to Github Migration

To craft a new set of git repos, we: 

##1) Obtain metadata from svn repo (records of authors, tags, etc)

```bash
python svn_fetch_info.py
```

##2) Obtain trunk and svn RC branches using git svn

This takes quite while due to the size of our repo, ssh disconnects, and failed git prune operations.
Will automate soon to resume and perserve through known failure modes. 

```bash
   mkdir -p checkouts/svn_trunk
   cd checkouts/svn_trunk
   git svn clone svn+ssh://{user}@edison.nersc.gov/project/projectdirs/visit/svn/visit/trunk/src
   cd ../../
```

```bash
   mkdir -p checkouts/svn_2.0RC
   cd checkouts/svn_2.0RC
   git svn clone svn+ssh://{user}@edison.nersc.gov/project/projectdirs/visit/svn/visit/branches/2.0RC/src
````

We alos need to resolve svn author mappings, see _nersc_uname_info.py_


##3) Construct a git repo that grafts our old release structure into a gitflow structure

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
       * Create a branch (rX.Y.Z) that includes proper subset of RC commits for the release
       * Squash merge this into a  single commit on master 
         
         Note: We encounter the same merge issues related to symlinks in this squash process and we can resolve them the same way.

       * Tag the new master commit with vX.Y.Z
