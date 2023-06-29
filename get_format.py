def get_format(value=''):
    extensions = ['.rdf', '.owl', '.xml']
    for ext in extensions :
        if ext in value : 
            return 'xml'
    return 'trig'