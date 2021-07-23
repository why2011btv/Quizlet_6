
- conda create --prefix /shared/why16gzl/Environments/te_env python=3.6
- conda activate /shared/why16gzl/Environments/te_env
- pip install -r /shared/why16gzl/Environments/te_env/requirements_time.txt
- cd /shared/public/ben/temporalextraction
- python server.py 1 5000
  <img width="1792" alt="Screen Shot 2021-07-23 at 2 22 14 AM" src="https://user-images.githubusercontent.com/32129905/126744453-db1b4cfa-fd4c-4ae8-9c0a-34b96f4c3126.png">
- ```curl --request POST --data @/shared/why16gzl/Projects/KAIROS/demo/10901.json -H "Content-type: application/json" http://127.0.0.1:5000/annotate_no_gurobi```
- Save the returned json file in "curl_result.json"
