# DLinker Automatic version

"Magical Wizard for RDF Data (knowledge graphs) Linking: Turning tangled data into spellbinding connections!"

"Clone and execute all commands at the root."

**1. Installation of Python 3.8, pip, and dependencies for this project:**

```plaintext
python(>=3.8) : [Download Python](https://www.python.org/)
spacy(>=3.3.1) : [spacy on PyPI](https://pypi.org/project/spacy/)

$ pip install -r ./requirements.txt
```

Note: If you encounter dependency errors, please add them using the following command:

```plaintext
$ pip install 'dependency name'
```

**2. Specification of datasets in the 'datasets.txt' file located at the root of this project:**

```plaintext
spaten_hobbit,source.nt,target.nt,valid_same_as.ttl
...
```

Note:
- 'spaten_hobbit' corresponds to the name of the subfolder for the dataset in the folders `./inputs/`, `./outputs/`, `./validations/`.
- 'source.(nt/ttl)' corresponds to the source file to be used in the 'spaten_hobbit' folder.
- 'target.(nt/ttl)' corresponds to the target file to be used in the 'spaten_hobbit' folder.
- 'valid_same_as.ttl' corresponds to the ground truth file used to analyze evaluation scores.

**3. Launch evaluations :**

The main file is `./job_evaluation.sh`, which generates the linking process command with associated hyperparameters for each dataset in `./datasets.txt`.

```plaintext
$ sh ./job_evaluation.sh ./datasets.txt
```

**4. Evaluation results:**

The different outputs can be found in the file `./fast_log.txt`.

**Note:** We copied the results of our evaluations to the file `./others_fast_logs.txt`.

**5. Hyperparameter adjusted from generate command to select all similar instances of spaten_hobbit:**

From automatic : 
```plaintext
$ sh ./job.sh --input_source ./inputs/spaten_hobbit/source.nt --input_target ./inputs/spaten_hobbit/target.nt --output ./outputs/spaten_hobbit/ --alpha_predicate 1.0 --alpha 0.958080772383294 --phi 1 --measure_level 0 --validation ./validations/spaten_hobbit/valid_same_as.ttl
```
To reajusted (only *alpha* hyper-parameter) :
```plaintext
$ sh ./job.sh --input_source ./inputs/spaten_hobbit/source.nt --input_target ./inputs/spaten_hobbit/target.nt --output ./outputs/spaten_hobbit/ --alpha_predicate 1.0 --alpha 0.308080772383294 --phi 1 --measure_level 0 --validation ./validations/spaten_hobbit/valid_same_as.ttl
```
