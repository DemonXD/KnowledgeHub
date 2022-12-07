from db import DB, atomic

@atomic
def get_now():
    cur = DB.session.execute("select date('now')")
    print(cur.fetchone())

@atomic
def show_tables():
    try:
        cur = DB.session.execute(
            "select name from sqlite_schema where type='table' and name not like 'sqlite_%'"
        )
        print(cur.fetchall())
    except Exception as e:
        print(str(e))
