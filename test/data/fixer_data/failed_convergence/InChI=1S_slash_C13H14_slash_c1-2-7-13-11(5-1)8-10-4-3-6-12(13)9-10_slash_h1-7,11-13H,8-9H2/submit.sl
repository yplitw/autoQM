#!/bin/bash -l
#SBATCH -p regular
#SBATCH -N 1
#SBATCH -t 2:00:00
#SBATCH -J InChI=1S_slash_C13H14_slash_c1-2-7-13-11(5-1)8-10-4-3-6-12(13)9-10_slash_h1-7,11-13H,8-9H2
#SBATCH -C haswell
#SBATCH -o out.log

module load g09

g09 input.inp