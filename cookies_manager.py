from typing import List, Dict


class CookieRotator:
    def __init__(self, cookies_list: List[Dict[str, str]]):
        if not cookies_list:
            raise ValueError("Cookies list cannot be empty.")
        self.cookies_list = cookies_list
        self.index = -1  # 初始化索引

    def get_next_cookie(self) -> Dict[str, str]:
        """循环获取下一个 cookie"""
        self.index = (self.index + 1) % len(self.cookies_list)
        return self.cookies_list[self.index]
