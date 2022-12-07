from db import DB, atomic


@atomic
def add_user(pwd: str, passwd: str):
    sql = """
    
    """