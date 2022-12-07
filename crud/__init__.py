from typing import List, Union
from sqlalchemy.engine.row import Row

def fetch_res_to_dict(res: Union[Row, List[Row]]) -> Union[dict, List[dict]]:
    if isinstance(res, list):
        result = []
        for row in res:
            temp = {}
            cols = list(row.keys())
            for col, val in zip(cols, row):
                temp[col] = val
            result.append(temp)
        return result
    elif isinstance(res, Row):
        result = {}
        cols = list(res.keys())
        for col, val in zip(cols, res):
            result[col] = val
        return  result
    else:
        raise Exception("parameter type error, needs Row object")
