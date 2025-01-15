import re


def extract_numbers(s: str) -> list[str]:
    """
    提取字符串中的所有数字，返回一个包含数字的列表。
    :param s: 输入字符串
    :return: 包含数字的列表（以字符串形式返回）
    """
    return re.findall(r"\d+", s)
