from nltk.corpus import wordnet as wn

def verb_or_not(word):
    '''
    # AN EXAMPLE USAGE: Determine whether a word is a verb (that can be potentially treated as an event)
    words = ['left', 'led', 'Food', 'temperature', 'sicknesses']
    for w in words:
        print(verb_or_not(w))
    '''
    for meaning in wn.synsets(word):
        if meaning.pos() == 'v':
            return 1
    return 0


import json
import requests
import pprint
from datetime import datetime
pp = pprint.PrettyPrinter(indent=4)

def ee_to_ta(file_name, extracted_events):
    '''
    ee_to_ta converter: from event extraction result to ta
    event extraction version: the one that outputs "extracted_events.json" at Jul 22, 2021 06:15
    file path: /shared/hzhangal/Projects/zero-event-extraction/quizlet6/quizlet6_data/extracted_events.json
    
    input:
    @file_name: e.g., 'quizlet6_data/L0C04CJ13.rsd.txt'
    @extracted_events: the dict loaded from "extracted_events.json"
    
    output:
    extracted_events in ta format
    '''
    fname = file_name.split("/")[1]
    #original_content = extracted_events[file_name]['original_content']  # too noisy, so abort
    #sentences = extracted_events[file_name]['sentences']  # too noisy, so abort
    #text = ' '.join(sentences)
    events = extracted_events[file_name]['events']
    text = ''
    
    '''prepare for ta slots'''
    tokens = []
    relations = []
    constituents = []
    sentEndPos = []
    sentence_id = -1
    for sent in events:
        if len(sent) > 0:  # ignore the sent if it's blank (of great possibility)
            sentence_id += 1
            tokens.extend(sent[0]['tokens'])
            text += ' '.join(sent[0]['tokens'])
            text += ' '
            sentEndPos.append(len(text))
        for event in sent:
            trigger  = ' '.join(sent[0]['tokens'][event['trigger']['position'][0]:event['trigger']['position'][1]])
            if verb_or_not(trigger):
                constituents.append({"start": event['trigger']['position'][0], \
                                     "end": event['trigger']['position'][1], \
                                     "label": "event", \
                                     "properties": {'sentence_id': sentence_id, \
                                                    'predicate': trigger,\
                                                    'SenseNumber': '', \
                                                    }, \
                                     "score": 1.0, \
                                     })
    
    '''start to construct ta from here'''
    ta = {}
    ta["corpusID"] = fname
    ta["id"] = ""
    ta["sentences"] = {"generator": "ee_to_ta", "score":1.0, "sentenceEndPositions": sentEndPos}
    ta["text"] = text
    ta["tokens"] = tokens
    ta["views"] = [{"viewData": [{"constituents": constituents, \
                                  "generator": "cogcomp_kairos_event_ie_v1.0", \
                                  "relations": relations, \
                                  "score": 1.0, \
                                  "viewName": "event_extraction", \
                                  "viewType": 'edu.illinois.cs.cogcomp.core.datastructures.textannotation.PredicateArgumentView', \
                                 }],\
                    'viewName': 'Event_extraction'
                   }]
    return ta

def fullTextDuration(ta, out_f):
    url = 'http://127.0.0.1:5000/annotate_no_gurobi'
    payload = json.dumps(ta)
    file_name = ta["corpusID"]
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=payload, headers=headers)
    try:
        data = json.loads(r.text)
        print("Writing results for " + file_name + "...")
        with open(out_f, 'w') as outfile:
            json.dump(data, outfile)
        return 0
    
    except:
        print("ERROR occurs in processing " + file_name + "!")
        return 1

import operator
def order_by(origin, ee):
    '''
    Given the relations between each pair of events temporally, and also the distance between them
    We can construct a sequence of events
    On an axis, the event "origin" happens at time 0, 
    if event A is before "origin" by distance of x, it happens at -x
    We can choose each event as an origin
    And induce n possible sequences of temporally ordered events
    We choose the most possible sequence that gets most votes
    '''
    event_map = {origin: 0}
    for relation in ee['views'][0]['viewData'][0]['relations']:
        if relation['srcConstituent'] == origin or relation['targetConstituent'] == origin:
            if relation['relationName'] == 'before':
                if relation['srcConstituent'] == origin:
                    event_map[relation['targetConstituent']] = relation['properties']['distance']
                else:
                    event_map[relation['srcConstituent']] = (-1) * relation['properties']['distance']
            else:
                if relation['srcConstituent'] == origin:
                    event_map[relation['targetConstituent']] = (-1) * relation['properties']['distance']
                else:
                    event_map[relation['srcConstituent']] = relation['properties']['distance']
                    
    sorted_e = sorted(event_map.items(), key=operator.itemgetter(1))
    return [m[0] for m in sorted_e]


json_file = '/shared/hzhangal/Projects/zero-event-extraction/quizlet6/quizlet6_data/extracted_events.json'
dir_path = "/shared/why16gzl/Projects/KAIROS/Quizlet/Quizlet_6/te_out/"

with open(json_file) as f:
    ee = json.load(f)
    # Test
    #if True:
    #    file_name = "quizlet6_data/L0C04CJ13.rsd.txt"
    for file_name in ee.keys():
        ta = ee_to_ta(file_name, ee)
        out_f = dir_path + ta["corpusID"] + ".json"
        fullTextDuration(ta, out_f)
        with open(out_f) as f:
            ta = json.load(f)
        possible_timeline = {}
        for i in range(len(ta['views'][0]['viewData'][0]['constituents'])):
            temp_order = repr(order_by(i, ta))
            if temp_order not in possible_timeline.keys():
                possible_timeline[temp_order] = 1
            else:
                possible_timeline[temp_order] += 1

        ta['views'][0]['viewData'][0]['temporalOrder'] = max(possible_timeline.items(), key=operator.itemgetter(1))[0]
        now = datetime.now()
        ta['timestamp'] = now.strftime("%d/%m/%Y %H:%M:%S")
        with open(out_f, 'w') as outfile:
            json.dump(ta, outfile)