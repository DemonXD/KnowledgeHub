import time
from typing import List
from db import DB, atomic
from crud import fetch_res_to_dict

from schema.note import Note


@atomic
def list_note() -> List[Note]:
    sql = """
    select * from note where is_deleted=0 order by created_at desc limit 20;
    """
    cur = DB.session.execute(sql)
    results = cur.fetchall()
    if results != []:
        result = fetch_res_to_dict(results)
        result = [Note(**res) for res in result]
    else:
        result = []
    
    return result

@atomic
def search_note(search_flag: str, search_content: str) -> List[Note]:
    sql = """
    select * from note where {}='{}' and is_deleted=0 order by created_at desc;
    """.format(search_flag, search_content)

    cur = DB.session.execute(sql)
    results = cur.fetchall()

    if results != []:
        result = fetch_res_to_dict(results)
        result = [Note(**res) for res in result]
    else:
        result = []
    
    return result


@atomic
def add_note(note: Note):
    # 不输出None值字段: note.dict(exclude_none=True)
    note_key_value_dict = note.dict(exclude_none=True)
    field_string = ",".join(note_key_value_dict.keys())
    value_placeholder = ",".join(["'{" + key + "}'" for key in note_key_value_dict.keys()])
    sql = """
    insert into note({field_string})
    values
    ({value_placeholder})
    """.format(field_string=field_string, value_placeholder=value_placeholder)
    try:
        DB.session.execute(sql.format(**note_key_value_dict))
        DB.session.commit()
    except Exception as e:
        DB.session.rollback()
        raise e
    else:
        return note

@atomic
def update_note(note: Note):
    """
    note 一定存在, 所以这里不需要再进行校验了,且为了方便,
    这里对数据做全量更新。
    """
    now_timestamp = time.time()
    sql = """
        update note 
        set 
            content='{}',
            modified_at={}
        where uid='{}';
    """.format(note.content, now_timestamp, note.uid)
    try:
        DB.session.execute(sql)
        DB.session.commit()
    except Exception as e:
        DB.session.rollback()
        raise e

@atomic
def delete_note(note: Note):
    sql = """
        update note set is_deleted=1 where uid='{}'
    """.format(note.uid)

    try:
        DB.session.execute(sql)
        DB.session.commit()
    except Exception as e:
        DB.session.rollback()
        raise e
