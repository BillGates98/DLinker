#!/bin/bash

#SBATCH --job-nam=Automatic-alignment

#SBATCH -p highmemdell

#SBATCH -c 25 

#SBATCH --mail-user=billhappi@gmail.com

#SBATCH --mail-type=ALL 

> ./logs/running.log

i=1;
params=``
for param in "$@" 
do
    i=$((i + 1));
    params=`echo $params $param`
done

echo "All params : ". $params

## module load system/python/3.8.12
# python3.8 ./main.py $params
python3.8 ./candidate_entities_pairs.py $params
python3.8 ./score_computation.py

### sh ./job.sh --alpha_predicate 1 --alpha 0.88 --phi 2 --measure low