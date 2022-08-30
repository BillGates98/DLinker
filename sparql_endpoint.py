from rdflib import Graph , Literal, RDF, URIRef
from rdflib.namespace import RDF
import log
import re
import urllib
import requests
import json
from dump import dump
from config import Config


class SparqlEndpoint: 

    def __init__(self, graph=None, subject=''):
        self.config = Config().load()
        self.subject = subject
        self.datas = []

    def threat_datas(self, datas=None):
        outputs = []
        for data in datas : 
            for binding in data['results']['bindings'] :
                tmp = {
                    'p': binding['p']['value'],
                    'o': binding['o']['value']
                }
                if not tmp in outputs :
                    outputs.append(tmp)
        return outputs

    def run_get(self, api_encoded='', headers=None):
        try:
            r = requests.get(api_encoded,  headers=headers)
            if r.status_code == requests.codes.ok :
                data_json = json.loads(r.text)
                self.datas.append(data_json)                
            else:
                raise                
        except Exception as _:
            log.error('GET #Request on the ressource ' + api_encoded + ' failed')
        return
    
    def run_post(self, api_encoded='', payload=None, headers=None):
        try:
            r = requests.post(api_encoded, headers=headers, data=payload)
            if r.status_code == requests.codes.ok :
                data_json = json.loads(r.text)
                if len(data_json['results']['bindings']) > 0 :
                    self.datas.append(data_json)
                self.datas.append(data_json)                                
            else: 
                raise
        except Exception as _:
            log.error('POST #Request on the ressource ' + api_encoded + ' failed')
        return

    def run(self):
        query = "SELECT ?p ?o WHERE { ?s ?p ?o .}".replace('?s', '<' + self.subject + '>')
        dump().write_to_txt(file_path='./outputs/motifs/queries.txt', values=[query])
        endpoints = self.config['endpoints']
        for endpoint in endpoints :
            api = endpoint['api'].strip()
            verb = endpoint['verb'].strip().lower()
            param = endpoint['params'][0].strip()
            headers = endpoint['headers'] if 'headers' in endpoint else ''
            if int(endpoint['status'].strip()) == 1 :
                if verb == 'get' :
                    api = api.replace(param, urllib.parse.quote(query.encode('utf-8')))
                    self.run_get(api_encoded=api)
                elif verb == 'post' :
                    payload = {}
                    payload[param] = query
                    self.run_post(api_encoded=api,payload=payload, headers=headers)
        return self.threat_datas(datas=self.datas)
        
