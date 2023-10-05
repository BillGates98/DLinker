module load python

sh ./job.sh --input_source ./inputs/agrold/source.nt --input_target ./inputs/agrold/target.nt --output_path ./outputs/agrold/ --alpha_predicate 1 --alpha 0.2 --phi 1 --measure_level 0 --validation ./validations/agrold/valid_same_as.ttl