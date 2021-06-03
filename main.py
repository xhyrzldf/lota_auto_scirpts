import cv2
import pyautogui as pg
import requests
import io
import time
import re
from PIL import Image
from requests_toolbelt import MultipartEncoder

need_array = ['全知', '幻寂', '赛丽', '隐之', '创世', '遮面']
talent_count = 1


class Equipment:
    """装备类"""

    def __init__(self, eq_type, name, level):
        self.eq_type = eq_type
        self.name = name
        self.level = level

    def __str__(self) -> str:
        return str(self.eq_type) + " " + self.name + " " + str(self.level)

    def is_need(self):
        """判断这件装备是否需要(在装备列表里)"""
        if self.level == 0:
            return True

        if self.level <= 60:
            return False

        for n in need_array:
            if n in self.name:
                return True
        return False


def parse(x, y, xw, yh, compress):
    img = pg.screenshot(region=[x, y, xw - x, yh - y])  # x,y,w,h
    # img.save('F:/images/1.jpeg')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='jpeg')
    img_byte_arr = img_byte_arr.getvalue()

    url = "http://192.168.1.105:8089/api/tr-run/"

    payload = {'compress': compress}
    files = [
        ('file', ('1.jpeg', img_byte_arr, 'image/jpeg'))
    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    results = eval(response.text)

    res_len = len(results['data']['raw_out'])

    if results['code'] != 200 or res_len == 0:
        return 'empty'
    else:
        string = ""
        for ele in results['data']['raw_out']:
            string += ele[1]
        result = re.sub(r'\d、|\s', '', string)
        return result


def generate_equipment(suit_string, level_string: str):
    try:
        if level_string == 'empty':
            level_number = 0
        else:
            level_number = int(level_string)
    except Exception as ex:
        print('数字处理异常')
        print(ex)
        level_number = 1

    if '套装' in suit_string:
        return Equipment(1, suit_string, level_number)
    else:
        if level_string == 'empty':
            return Equipment(0, "", 0)
        else:
            return Equipment(0, "", level_number)


def handle_equipment():
    # 打开装备页面
    pg.leftClick(437, 35)
    start_x = 153
    start_y = 413
    length = 146
    height = 111
    for i in range(0, 4):
        for j in range(0, 8):
            # 判断一下是否有箱子要捡
            handle_rewards()
            mid_x = start_x + length * j
            mid_y = start_y + height * i
            pg.moveTo(mid_x, mid_y)
            # 生成装备对象
            suit_string = parse(mid_x + 547, mid_y + 73, mid_x + 848, mid_y + 118, 300)
            level_string = parse(mid_x - 49, mid_y, mid_x - 23, mid_y + 32, 400)
            equipment = generate_equipment(suit_string, level_string)
            # 根据装备对象来判断是否分解
            # type = 0 直接分解
            print(equipment)
            if not equipment.is_need():
                self_break(mid_x, mid_y)
            elif equipment.level == 0:
                break
    # 退出界面
    pg.leftClick(1783, 52)


def self_break(x, y):
    """自分解装备"""
    # 点击右键
    pg.moveTo(x, y)
    pg.rightClick()
    pg.moveTo(x + 137, y + 100)
    pg.leftClick()
    # 判断是否是橙装
    is_orange = parse(1167, 733, 1238, 769, 500)
    if is_orange == '确定':
        pg.leftClick(1180, 752)


def handle_talent():
    try:
        global talent_count
        while True:
            talent_point = int(parse(2473, 1284, 2513, 1314, 400))
            print('处理天赋点，当前天赋点为: ' + str(talent_point))
            if talent_point >= 7:
                handle_challenge()
                pg.leftClick(450, 1369)  # 打开页面
                if talent_count == 1:
                    pg.tripleClick(1090, 611)  # 天赋论
                elif talent_count == 2:
                    pg.tripleClick(1084, 476)  # 神器挑战
                elif talent_count == 3:
                    pg.tripleClick(688, 475)  # 金钱增加
                elif talent_count == 4:
                    pg.tripleClick(1492, 475)  # 杀羊
                elif talent_count == 5:
                    pg.tripleClick(1902, 879)  # 消块达人
                elif talent_count == 6:
                    pg.tripleClick(687, 881)  # 杀怪加法强
                elif talent_count == 7:
                    pg.tripleClick(696, 614)  # 杀怪加属性
                elif talent_count == 8:
                    pg.tripleClick(1081, 743)  # 加爆率
                else:
                    pg.leftClick(450, 1369)  # 关闭页面
                    break
                talent_count = talent_count + 1
                pg.leftClick(450, 1369)  # 关闭页面
            else:
                break
    except Exception as ex:
        print(ex)


def handle_challenge():
    if parse(1320, 429, 1409, 489, 500) == '挑战':
        print('处理挑战')
        pg.leftClick(811, 637)


def handle_rewards():
    if parse(525, 520, 666, 590, 500) == '宝箱':
        print('处理宝箱')
        pg.click(686, 693, 9, 0.2, button='left')
        pg.leftClick(668, 803)


def handle_window():
    if parse(1336, 36, 1415, 77, 500) == '当前':
        print('处理窗口')
        pg.leftClick(1783, 52)


if __name__ == '__main__':
    time.sleep(3)
    while True:
        # 是否是结算界面 1342,1065,1404,1095 queding 1250,1082
        if parse(1342, 1065, 1404, 1095, 500) == '确定':
            print('进入结算界面')
            pg.click(1250, 1082, 4, 0.5, button='left')
            pg.leftClick(1367, 1079)
        # 是否是初始界面
        while True:
            if parse(1222, 105, 1277, 137, 500) == '战斗':
                print('进入初始界面')
                talent_count = 1
                time.sleep(5)
            else:
                break

        # 检测自动战斗
        if parse(1889, 1321, 1946, 1352, 500) == '自动':
            pg.leftClick(1922, 1290)
            pg.moveTo(1243, 595)
            time.sleep(0.01)

        # 根据当前分钟数执行逻辑
        time_string = parse(1354, 4, 1393, 35, 450)
        current_time = 0
        try:
            if time_string == 'empty':
                current_time = 0
            else:
                current_time = int(time_string)
        except Exception as ex:
            print('处理时间时出现异常')
            print(ex)
            current_time = 0
        print('当前的时间为：' + str(current_time))
        if current_time == 14 or current_time == 11 or current_time == 7 or current_time == 3:
            handle_challenge()
            handle_talent()
            handle_rewards()
            handle_equipment()
        elif current_time == 1 or current_time == 0:
            handle_challenge()
            handle_window()
            handle_rewards()
        else:
            handle_window()
            handle_challenge()
            handle_talent()
            handle_rewards()

        time.sleep(5)
