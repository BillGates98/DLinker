#!/bin/bash

#SBATCH --job-nam=automatic-alignment

#SBATCH -p highmemdell

#SBATCH -c 20 

#SBATCH --mail-user=billhappi@gmail.com

#SBATCH --mail-type=ALL 

# module load system/python/3.8.12
rm -rf ./nohup.out

> ./logs/running.log

# module load system/python/3.8.12
# python -m venv .env
# source .env/bin/activate
# srun -p highmemdell --nodelist=node29 --pty nohup python3.8 ./candidate_entities_pairs.py &
# &
# python3.8 ./main.py

# python3.8 ./main.py
python3.8 ./candidate_entities_pairs.py
python3.8 ./score_computation.py

# srun -p highmemdell --nodelist=node28 --pty python ./main.py
# python3.8 ./main.py 
#cp ./outputs/same_as_entities.ttl ./inputs/
#python3.8 ./merge_graph.py