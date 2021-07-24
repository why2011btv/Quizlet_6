#!/bin/bash

suffix=".ben"
path=$1
files=$(ls $path)
for filename in $files
do
	out_file=$filename$suffix
	nohup curl --request POST --data @$filename -H "Content-type: application/json" http://127.0.0.1:5000/annotate_no_gurobi > $out_file 2>&1 &
done

