import json
import requests
import pprint
pp = pprint.PrettyPrinter(indent=4)

'''
def sent_end_pos(sentences):
    # end char corresponds to the space after the sentence, but not the period
    end_pos = []
    count = 0
    for sent in sentences:
        count += len(sent)
        end_pos.append(count)
        count += 1
    return end_pos
'''

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
            constituents.append({"start": event['trigger']['position'][0], \
                                 "end": event['trigger']['position'][1], \
                                 "label": "event", \
                                 "properties": {'sentence_id': sentence_id, \
                                                'predicate': ' '.join(sent[0]['tokens'][event['trigger']['position'][0]:event['trigger']['position'][1]]),\
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
    
json_file = '/shared/hzhangal/Projects/zero-event-extraction/quizlet6/quizlet6_data/extracted_events.json'
dir_path = "/shared/why16gzl/Projects/KAIROS/Quizlet/Quizlet_6/te_out/"

with open(json_file) as f:
    ee = json.load(f)
    for file_name in ee.keys():
        ta = ee_to_ta(file_name, ee)
        out_f = dir_path + ta["corpusID"]
        #pp.pprint(ta)
        #print(ta)
        fullTextDuration(ta, out_f)

