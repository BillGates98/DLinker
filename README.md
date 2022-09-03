# DLinker
## _RDF Data Linking tool_

[![N|solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

DLinker is an RDF data linking tool.
- Depend of four hyperparameters(measure_level, alpha_predicate, alpha  and phi)
- the strength of the similarity search measure 'measure_level'
- acceptance threshold for similar predicates 'alpha_predicate'
- acceptance threshold for similar literals 'alpha'
- number of accepted similarity pairs 'phi'

## Evaluations 
- Doremus data(https://github.com/DOREMUS-ANR/doremus-playground/tree/master/DHT) : 
    * Precision : 0.965
    * Recall : 1
    * F-measure : 0.982
## Features

- Take only pairs of files in the inputs path('./inputs/') with the names 'source.ttl' and 'target.ttl'
- Compute pairs predicates
- Compute similars literals
- Once the data is in place the whole thing can be launched with the sbatch file('./job.sh') without forgot the hyperparameters
- Place results in the output path('./outputs')
- Place valid pairs in the file '/validations/valid_same_as.ttl'
- Compute score similarity from this python script ('./score_computation.py')


## Tech

Dillinger uses a number of open source projects to work properly:

- [Python >=3.8] - Awesome Language who is an interpreted, multi-paradigm and multi-platform programming language.!
- [Visual Studio Code Editor] - awesome text editor
- [markdown-it] - Markdown parser done right. Fast and easy to extend.

## Installation

Python version [(>=3.8)](https://www.python.org/) to run.
Spacy version [(>=3.4.1)](https://pypi.org/project/spacy/) to run.

Install the dependencies and devDependencies and start the server.

```sh
pip install spacy
```

## Execution from the project base

From a Shell Script file :

```sh
sh ./job.sh --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1
```

```sh
#!/bin/bash

#SBATCH --job-nam=Automatic-Linking
#SBATCH -p highmemdell
#SBATCH -c 25 
#SBATCH --mail-user=`youremail@domain`
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
python3.8 ./main.py $params
python3.8 ./candidate_entities_pairs.py $params
python3.8 ./score_computation.py ## can be commented
```
