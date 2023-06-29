#!/bin/bash
i=1;
params=``
for param in "$@" 
do
    i=$((i + 1));
    params=`echo $params $param`
done

# echo "All params : ". $params

python3.8 ./candidate_entities_pairs.py $params
python3.8 ./score_computation.py $params

### sh ./job.sh --input_path ./inputs/doremus/ --output ./outputs/doremus --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1 --validation ./validations/doremus/valid_same_as.ttl
