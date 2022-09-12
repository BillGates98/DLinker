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
- put validation parameter after introduice the file ine validation path 'validation'

## Evaluations 
- HOBBIT and SPATEN([url](https://users.ics.forth.gr/~jsaveta/.index.php?dir=OAEI_HOBBIT_LinkDiscovery/Spatial/Spaten_LinesTOLines/CONTAINS/)) :
   ``` sh ./job.sh --input_path ./inputs/spaten_hobbit/ --output ./outputs/spaten_hobbit --alpha_predicate 1 --alpha 0.3 --phi 1 --measure_level 0 --validation ./validations/spaten_hobbit/valid_same_as.nt ```
   * Precision : 1.0
   * Recall : 1.0
   * F-measure : <b>1.0</b>
- Doremus data ([url](https://github.com/DOREMUS-ANR/doremus-playground/tree/master/DHT)) : 
    ``` sh ./job.sh --input_path ./inputs/doremus/ --output ./outputs/doremus/ --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 2 --validation ./validations/doremus/valid_same_as.ttl  ```
    * Precision : 0.966
    * Recall : 1.0
    * F-measure : <b>0.983</b>
- SPIMBENCH data([url](http://users.ics.forth.gr/~jsaveta/.index.php?dir=OAEI_IM_SPIMBENCH)) : 
   ``` sh ./job.sh --input_path ./inputs/spimbench/ --output ./outputs/spimbench/ --alpha_predicate 1 --alpha 1 --phi 1 --measure_level 1 --validation ./validations/spimbench/valid_same_as.ttl  ```
    * Precision : 0.786
    * Recall : 1.0
    * F-measure : <b>0.880</b>
> Make sure you have this in the './outputs/spimbench/similars_predicates.csv' the content below :
>
> predicate_1,value_1,predicate_2,value_2,similarities <br/>
> `<http://www.bbc.co.uk/ontologies/creativework/title>`,http://www.bbc.co.uk/ontologies/creativework/title,                                               `<http://www.bbc.co.uk/ontologies/creativework/title>`,http://www.bbc.co.uk/ontologies/creativework/title,1.0
>  

## Features

- Take only pairs of files in the inputs path('./inputs/') with any names. Example : 'source.ttl' and 'target.ttl'
- Compute pairs predicates
- Compute similars literals
- Once the data is in place the whole thing can be launched with the sbatch file('./job.sh') without forgot the hyperparameters
- Place results in the output path('./outputs')
- Place valid pairs in the file '/validations/valid_same_as.ttl' and call in argument with 'validation'
- Compute score similarity from this python script ('./score_computation.py')


## Tech

DLinker is implemented with below elements to work properly :

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
sh ./job.sh --alpha_predicate 1 --alpha 0.88 --phi 2 --measure_level 1 --shared_frequency 3 
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
python3.8 ./score_computation.py $params ## can be commented
```
