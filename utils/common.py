import hashlib
from typing import Mapping


def gen_html(content: str):
    import markdown2

    extras = [
        'code-friendly', 'fenced-code-blocks', 'footnotes',
        'tables','code-color','pyshell','nofollow',
        'cuddled-lists','header ids','nofollow'
    ]
    markdown_client = markdown2.Markdown(extras=extras)
    html = """
    <html>
    <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    <style>
        .hll { background-color: #ffffcc }
        .c { color: #0099FF; font-style: italic } /* Comment */
        .err { color: #AA0000; background-color: #FFAAAA } /* Error */
        .k { color: #006699; font-weight: bold } /* Keyword */
        .o { color: #555555 } /* Operator */
        .ch { color: #0099FF; font-style: italic }
        <!--省略一大堆的CSS样式-->
    </style>
    </head>
    <body>
        %s
    </body>
    </html>
    """
    ret = markdown_client.convert(content)
    return html % ret


def get_md5(data):
    """
    获取md5加密密文
    :param data: 明文
    :return: 加密后的密文
    """
    m = hashlib.md5()
    b = data.encode(encoding='utf-8')
    m.update(b)
    return m.hexdigest()

def dump_dict_to_yaml_file(file_name: str, file_content: dict) -> None:
    import yaml
    try:
        with open(file_name, "w") as f:
            yaml.dump(file_content, f)
    except Exception as e:
        print(str(e))


def _merge_dict(a: dict, b: dict, *others: dict) -> dict:
    """
    merge dict a and b, return a new dict
    """
    dst = a.copy()
    for k, v in b.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(b[k], Mapping):
            dst[k] = _merge_dict(dst[k], b[k])
        else:
            dst[k] = b[k]
    if others:
        return _merge_dict(dst, *others)
    else:
        return dst


class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]
