
import pandas as pd 
import json 






# Given data
R_edge_data = {"inputs" :{
    "RFS": {
       "N": [0, 0.6, 0.65],
        "M":[0.6, 0.65, 0.7],
        "F":[0.65, 0.7, 1]}
    ,
    "RBS": {
        "N": [0, 0.6, 0.65],
        "M":[0.6, 0.65, 0.7],
        "F":[0.65, 0.7, 1]}

},

"outputs" : {
    "Speed": {
        "S":[0.01, 0.1],
         "M":[0.1, 0.2],
         "H":[0.2, 0.3]
    },
    "Direction": {
        "R": [0.1, 0.3],
        "S": [-0.1, 0.1],
        "L": [-0.3, -0.1]
    }


}
}


op_data = {
    "inputs":{
    "FRS": {
        "N": [0.0, 0.25, 0.6],
        "M": [0.25, 0.6, 0.7],
        "F": [0.6, 0.7,1.0],
    },
    "F": {
        "N": [0.0, 0.25, 0.75],
        "M": [0.25, 0.75, 0.85],
        "F": [0.75, 0.85,1],
    },
    "FLS": {
        "N": [0.0, 0.25, 0.6],
        "M": [0.25, 0.6, 0.7],
        "F": [0.6, 0.7,1],
    },
},



"outputs" : {
    "Speed": {
        "S":[0.01, 0.1],
         "M":[0.1, 0.2],
         "H":[0.2, 0.3]
    },
    "Direction": {
        "R": [0.1, 0.3],
        "S": [-0.1, 0.1],
        "L": [-0.3, -0.1]
    }


}}





with open("right_edge_ranges.json",'w') as f :
    json.dump(R_edge_data,f)


with open("obstacle_avoidance_ranges.json",'w') as f :
    json.dump(op_data,f)


