import requests
import json
import biliBV
import regex as re
import wikitextparser as wtp
from time import mktime
from datetime import datetime
from typing import *


def parse_date(raw: str, fmt: str) -> int:
    "将一定格式的日期字符串转化为时间戳"
    date_str = re.sub(r"\s\s", " ", raw.strip())
    dt = datetime.strptime(date_str, fmt)
    return int(mktime(dt.timetuple()))


def parse_template(tpl: wtp.Template) -> Dict:
    "把wikitextparser中的模板解析成字典"
    dic = {"template": tpl.name.strip()}
    for arg in tpl.arguments:
        value = arg.value.strip().replace("&lt;", "<")
        if value[:2] == "{{":
            value = parse_template(wtp.parse(value).templates[0])
        elif re.match(r"BV[\dA-Z]+", value):
            value = biliBV.decode(value)
        try:
            value = parse_date(value, "%Y-%m-%d %H:%M")
        except Exception:
            pass
        try:
            value = parse_date(value, "%Y年%m月%d日 %H:%M")
        except Exception:
            pass
        try:
            value = eval(value)
        except Exception:
            pass
        dic[arg.name.strip()] = value
    return dic


def parse_all_templates(wiki: str) -> List[Dict]:
    "wiki文本中寻找模板并解析成字典"
    parse_result = []
    for i in wtp.parse(wiki).templates:
        parse_result.append(parse_template(i.templates[0]))
    return parse_result


def get(l: int, r: int):
    with open("data/VCjournal.json", "a", encoding="utf-8") as f:
        for i in range(l, r + 1):
            if l >= 118:
                wiki = requests.get(
                    f"https://zh.moegirl.org/index.php?title=%E5%91%A8%E5%88%8AVOCALOID%E4%B8%AD%E6%96%87%E6%8E%92%E8%A1%8C%E6%A6%9C{i}&action=edit").text
                brick = "VOCALOID_Chinese_Ranking/bricks"
            else:
                brick = "VOCALOID_Chinese_Ranking/bricks-newsong period"
                if l >= 54:
                    wiki = requests.get(
                        f"https://zh.moegirl.org/index.php?title=%E4%B8%AD%E6%96%87VOCALOID%E6%96%B0%E6%9B%B2%E6%8E%92%E8%A1%8C%E6%A6%9C{i}&action=edit").text
                else:
                    wiki = requests.get(
                        f"https://zh.moegirl.org/index.php?title=%E6%B4%9B%E5%A4%A9%E4%BE%9D%E6%96%B0%E6%9B%B2%E6%8E%92%E8%A1%8C%E6%A6%9C{i}&action=edit").text

            parsed_templates = parse_all_templates(wiki)
            head = [i for i in parsed_templates if i["template"]
                    == "VOCALOID Chinese Ranking"][0]
            OP = [i for i in parsed_templates if i["template"] ==
                  brick and i.get("color") == "#AA0000"]
            SH = [i for i in parsed_templates if i["template"] ==
                  brick and i.get("color") == "#CCCC00"]
            main = [i for i in parsed_templates if i["template"] ==
                    brick and i.get("color") == None]
            pickup = [i for i in parsed_templates if i["template"] ==
                      brick and i.get("color") == "#FF9999"]
            history = [i for i in parsed_templates if i["template"] ==
                       brick and i.get("color") == "#663300"]
            ED = [i for i in parsed_templates if i["template"] ==
                  brick and i.get("color") == "#4FC1E9"]
            print(json.dumps({**head, "OP": OP and OP[0] or None, "SH": SH, "main": main,
                              "pickup": pickup, "history": history, "ED": ED and ED[0] or None},
                             ensure_ascii=False), end=",", file=f)
            print(f"{i}期已完成！")


if __name__ == '__main__':
    get(409, 413)
