## A draft demonstration of how to build a pipeline of event extraction & temporal extraction (timeline construction / extraction of sequence of events)
- conda create --prefix /shared/why16gzl/Environments/te_env python=3.6
- conda activate /shared/why16gzl/Environments/te_env
- pip install -r /shared/why16gzl/Environments/te_env/requirements_time.txt
- cd /shared/public/ben/temporalextraction
- python server.py 1 5000
  <img width="1792" alt="Screen Shot 2021-07-23 at 2 22 14 AM" src="https://user-images.githubusercontent.com/32129905/126744453-db1b4cfa-fd4c-4ae8-9c0a-34b96f4c3126.png">
- ```curl --request POST --data @/shared/why16gzl/Projects/KAIROS/demo/10901.json -H "Content-type: application/json" http://127.0.0.1:5000/annotate_no_gurobi```
- Save the returned json file in "curl_result.json"

Note: `10901.json` is the result of event extraction (by Hongming's model) from [a HiEve document](https://github.com/why2011btv/JCL_EMNLP20/blob/main/hievents_v2/article-10901.xml) 
