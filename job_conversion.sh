#!/bin/bash
while IFS=',,,' read -r dataset sourcef targetf validsameas; do
    echo "Dataset truths : $line will converted ...0%"
    mv ./validations/$dataset/refalign.rdf ./validations/$dataset/refalign.xml
    python3.8 ./convert_xml_to_graph.py --input_data ./validations/$dataset/refalign.xml --input_path ./inputs/$dataset/ --output_path ./validations/$dataset/
    echo "File : $line will converted ...100%"
done < "$1"