
# connect to registration table

# search targets to push
# 1. get target jobs with "job_failed_convergence" 
# 2. check if job files are in scratch archive
# 3. move files to workspace
# 4. rename old input file to *.bak, 
#    create new input file
# 5. change job status to 
#    "job_recreated_for_convergence"
