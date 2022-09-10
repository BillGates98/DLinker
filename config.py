import json


class Config:

    def __init__(self, file_path='./config/config.json'):
        super().__init__()
        self.file_path = file_path
        self.data = None

    def load(self, key=''):
        f = open(self.file_path,)
        self.data = json.load(f)
        f.close()
        if key:
            return self.data[key]
        else:
            return self.data

    def update(self, parent='', pair={}):
        data = self.load()

        if not parent in data:
            if len(parent.lstrip()) > 0 :
                data[parent] = {}

        if parent in data :
            if isinstance(pair['value'], list):
                data[parent][pair['key']].append(pair['value'])
            else:
                data[parent][pair['key']] = pair['value']
        else:
            if isinstance(pair['value'], list):
                data[pair['key']].append(pair['value'])
            else:
                data[pair['key']] = pair['value']
        result = json.dumps(data, indent=4)
        with open(self.file_path, 'w') as outfile:
            outfile.write(result)
        return result

    def update_prefix(self, key='', value=''):
        data = self.load()
        if not key in data :
            data[key] = value
        result = json.dumps(data, indent=4)
        with open(self.file_path, 'w') as outfile:
            outfile.write(result)
        return result

# Config().load()
# Config().update(parent='regexps', pair={'key': 'PO', 'value': "{[A-Z]}*2"})
# Config().update(parent='prefixs', pair={'key': 'PO', 'value': {
#     'uri': 'plant ontology',
#     'scrap': '',
# }})
# Config().update(parent='predicates', pair={'key': 'OBO', 'value': '0'})
# Config().update(parent='prefixs', pair={'key': 'RO', 'value': {
#     'uri': 'relation ontology',
#     'scrap': '',
# }})
# Config().update(parent='prefixs', pair={'key': 'PB', 'value': {
#     'uri': 'plant biology',
#     'scrap': '',
# }})
# Config().load()
