1.  Installation of Python 3.8, pip, and dependencies for this project :

    """
        python(>=3.8) : https://www.python.org/
        spacy(>=3.3.1) : https://pypi.org/project/spacy/
        
        $ pip install -r requirements.txt
    """

    Note : If you encounter dependency errors, 
            please add them using the following command : 
            
            $ pip install 'dependency name'.

2.  Specification of datasets in the 'datasets.txt' file located at the root of this project:
    
    """ 
        spaten_hobbit,source.nt,target.nt,valid_same_as.ttl
        ...
    """

    Note :
        * 'doremus' corresponds to the name of the subfolder for the dataset in the folders './inputs/', './outputs/', './validations/'.
        * 'source.ttl' corresponds to the source file to be used in the 'doremus' folder.
        * 'target.ttl' corresponds to the target file to be used in the 'doremus' folder.
        * 'valid_same_as.ttl' corresponds to the ground truth file used to analyze evaluation scores.

3.  Execution of evaluations :

        The main file is './job_evaluation.sh', which generates the linking process command
        with associated hyperparameters for each dataset in './datasets.txt'.
        
        """
            $ sh ./job_evaluation.sh ./datasets.txt
        """

4.  Evaluation results:
        The different outputs can be found in the file './fast_log.txt'.
        Note: We copied the results of our evaluations to the file './others_fast_logs.txt'.
