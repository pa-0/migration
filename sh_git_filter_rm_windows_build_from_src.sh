git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch -r src/windowsbuild' \
--prune-empty --tag-name-filter cat -- --all