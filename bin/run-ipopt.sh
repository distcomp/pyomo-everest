#!/bin/bash
export OPENMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
hostname > $1.log.txt
# ipopt $1.nl -AMPL option_file_name=$2 2>&1 >> $1.log.txt
# Keep stderr separately
ipopt $1.nl -AMPL option_file_name=$2 >> $1.log.txt 2> $1.err.txt
