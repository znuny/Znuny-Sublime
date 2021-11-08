#!/bin/bash
#
# Simply start-script to execute the ZnnyCodePolicy in Sublime.
# Auto: Falko Sperker
# Date: 08.11.2021
# 
# --
# This software comes with ABSOLUTELY NO WARRANTY. For details, see
# the enclosed file COPYING for license information (AGPL). If you
# did not receive this file, see http://www.gnu.org/licenses/agpl.txt.
# --

StrPathAndFile=$1
StrGitRepoFolder="github" # Folder that includes your GitHub repositories. 
StrZnunyCodePolicyFile="/Users/falko/Work/github/ZnunyCodePolicy/bin/otrs.CodePolicy.pl"

# count the Directory-Level until the folder sources. This is necessary to divide the path correctly.
IntFolderLevel=$(echo ${StrPathAndFile%$StrGitRepoFolder*} | grep -o / | wc -l)

# add two more level to get into the project folder
IntFolderLevel=$((IntFolderLevel+2))

# Split $StrPathAndFile into the path ($StrPathName) and the file ($StrFile)
StrPathName=$(echo $StrPathAndFile | cut -d'/' -f-$IntFolderLevel)/
StrFile=${StrPathAndFile#$StrPathName}

# enter the path
cd $StrPathName

# run the CodeChecker
perl $StrZnunyCodePolicyFile --file $StrFile

