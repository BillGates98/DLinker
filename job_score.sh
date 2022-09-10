#!/bin/bash

#SBATCH --job-nam=Automatic-alignment

#SBATCH -p highmemdell

#SBATCH -c 25 

#SBATCH --mail-user=billhappi@gmail.com

#SBATCH --mail-type=ALL 

# > ./logs/running.log
# > ./outputs/logs/comparisons.txt
# > ./outputs/logs/links.txt

i=1;
params=``
for param in "$@" 
do
    i=$((i + 1));
    params=`echo $params $param`
done

# echo "All params : ". $params

## module load system/python/3.8.12
python3.8 ./score_computation.py $params

### sh ./job_score.sh --input_path ./inputs/doremus/ --output ./outputs/doremus --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1 --validation ./validations/doremus/valid_same_as.ttl