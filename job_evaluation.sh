#!/bin/bash
> ./fast_log.txt
while IFS=',,,' read -r dataset sourcef targetf validsameas; do
    echo "- Dataset processing : $dataset will be processed ...0%" >> ./fast_log.txt
    output=$(python3.8 ./computehyperparameter.py --source_file ./inputs/$dataset/$sourcef --target_file ./inputs/$dataset/$targetf --training_file ./validations/$dataset/$validsameas)
    # output=$(python3.8 ./computehyperparameter.py --source_file ./inputs/$dataset/$sourcef --target_file ./inputs/$dataset/$targetf --training_file ./validations/$dataset/$validsameas >> ./fast_log.txt)
    echo $output >> ./fast_log.txt
    last_line=$(echo "$output" | tail -n 1)
    substring="sourcef"
    substring2="targetf"
    new_command=$(echo "$last_line" | sed "s/$substring/$sourcef/g")
    new_command=$(echo "$new_command" | sed "s/$substring2/$targetf/g")
    echo $new_command >> ./fast_log.txt
    ($new_command) >> ./fast_log.txt # Alert : here is the line that executes the command generated with the hyperparameters on a dataset
    # $newcommand can have as value, the one located at line 21 in this file
    # or can just be commented to have the values of the hyperparameters 
    # in the command to evaluate
    echo "File : $dataset will be processed ...100%" >> ./fast_log.txt
done < "$1"

### sh ./job_evaluation.sh ./datasets.txt
### Example : sh ./job.sh --input_path ./inputs/doremus/ --output ./outputs/doremus --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1 --validation ./validations/doremus/valid_same_as.ttl


# sh ./job.sh --input_source ./inputs/doremus/source.ttl --input_target ./inputs/doremus/target.ttl --output_path ./outputs/doremus/ --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1 --validation ./validations/doremus/valid_same_as.ttl