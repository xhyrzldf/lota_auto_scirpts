import cv2
import pyautogui as pg
import requests
import io
import time
import re
import pandas as pd
import sys
from lota_class import Equipment, ShopEquipment, HexEquipment
from PIL import Image
from requests_toolbelt import MultipartEncoder

talent_count = 1
total_spend_money = 0
already_infinite_q = False
first_break = True
first_shopping = True
first_replace_1 = True
first_replace_2 = True
current_money = 0
shop_count = 0
room_fact = 1  # 空间修正因子

eqs = []
shop_eq = {}

# 读取要购买的装备清单 成为一个dict
reader = pd.read_csv("physical_hard.csv", header=None, sep=',')
print(reader)

for index, row in reader.iterrows():
    shop_eq[row[1]] = ShopEquipment(row[1], row[0], row[2], row[3], row[3])


def get_color(x, y):
    screenshot = pg.screenshot()
    r, g, b = screenshot.getpixel((x, y))
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


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


def handle_talent_45():
    try:
        global talent_count
        while True:
            talent_point = int(parse(2473, 1284, 2513, 1314, 400))
            print('处理天赋点，当前天赋点为: ' + str(talent_point))
            if talent_point >= 7 and talent_count <= 8:
                handle_challenge()
                pg.leftClick(450, 1369)  # 打开页面

                if talent_count == 1:
                    pg.tripleClick(1090, 611)  # 天赋论
                elif talent_count == 2:
                    pg.tripleClick(1084, 476)  # 神器挑战
                elif talent_count == 3:
                    pg.tripleClick(1492, 475)  # 杀羊
                elif talent_count == 4:
                    pg.tripleClick(688, 475)  # 金钱增加
                elif talent_count == 5:
                    pg.tripleClick(1902, 879)  # 消块达人
                elif talent_count == 6:
                    pg.tripleClick(696, 614)  # 杀怪加属性
                elif talent_count == 7:
                    pg.tripleClick(1081, 743)  # 加爆率
                elif talent_count == 8:
                    pg.tripleClick(671, 874)  # 加爆率
                else:
                    pg.leftClick(450, 1369)  # 关闭页面
                    break
                talent_count = talent_count + 1
                pg.leftClick(450, 1369)  # 关闭页面
            else:
                break
    except Exception as ex:
        print(ex)


def handle_talent_hard():
    try:
        global talent_count
        while True:
            talent_point = int(parse(2473, 1284, 2513, 1314, 400))
            print('处理天赋点，当前天赋点为: ' + str(talent_point))
            if talent_point >= 7 and talent_count <= 10:
                handle_challenge()
                pg.leftClick(450, 1369)  # 打开页面
                if talent_count == 1:
                    pg.tripleClick(1838, 485)  # 无限Q
                    global already_infinite_q
                    already_infinite_q = True
                elif talent_count == 2:
                    pg.tripleClick(1090, 611)  # 天赋论
                elif talent_count == 3:
                    pg.tripleClick(688, 475)  # 金钱增加
                elif talent_count == 4:
                    pg.tripleClick(696, 614)  # 杀怪加属性
                elif talent_count == 5:
                    pg.tripleClick(702, 735)  # 杀怪加攻击力
                elif talent_count == 6:
                    pg.tripleClick(696, 876)  # 杀怪加法强
                elif talent_count == 7:
                    pg.tripleClick(1902, 879)  # 消块达人
                elif talent_count == 8:
                    pg.tripleClick(1829, 753)  # 平A哥
                elif talent_count == 9:
                    pg.tripleClick(1885, 606)  # 强化E
                elif talent_count == 10:
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


def handle_shopping():
    global current_money
    while True:
        try:
            current_money = int(parse(2256, 1279, 2362, 1316, 250))
        except Exception as ex:
            print('处理购买装备发生异常')
            current_money = 0
        if current_money < 800:
            break
        # 购买装备 按D键
        pg.leftClick(2205, 1379)
        buy_equipment_pos()

    pg.leftClick(1271, 1098)


def handle_shopping_hard():
    global shop_count, current_money, first_shopping

    while True:
        rank = shop_count % 10
        print('消费装备,rank = ', rank)
        try:
            # 第一次会直接算一次钱
            if first_shopping:
                current_money = int(parse(2256, 1279, 2362, 1316, 250))
                first_shopping = False

        except Exception as ex:
            print('处理购买装备发生异常')
            current_money = 0
        # 没钱了 或者 E CD好了 就结束购买 或者已经结束刷钱阶段就再判断一下商店菜单
        finish = False

        # 每10次检查一下是不是在结算页面了
        if rank % 10 == 0:
            menu_string = parse(1355, 839, 1483, 870, 500)
            print('装备页面的菜单检测，当前rank = ' + str(rank) + ',当前菜单栏检测文字值 = ' + menu_string)
            if '菜单' in menu_string:
                finish = True

        if current_money < 800 or get_color(245, 1340) == '#cb5238' or finish:
            break
        # 购买装备 按D键
        shop_count += 1
        pg.leftClick(1291, 1093)

        # 检查Boss是否到来
        if rank == 2 or rank == 5 or rank == 8:
            check_boss_exists()

        # 检查大前排血量
        if rank == 3 or rank == 6 or rank == 9:
            stay_live()

        pg.leftClick(2205, 1379)
        buy_equipment_pos()
        # 临时计算，用于加速装备购买
        current_money -= 800

    pg.leftClick(1271, 1098)


def check_current_room_fast():
    """通过计算的方式获得空格子数量,相比于读取更快速"""
    # 初始为0，合成金箍棒fact - 1 ,每次合成神器fact - 1
    used_room = 0

    # 如果actual_owned = 1 或者 2
    for eq in shop_eq.values():
        if eq.actual_owned == 1 or eq.actual_owned == 2:
            used_room += 1
        elif eq.actual_owned == 3:
            used_room += 2
        elif eq.actual_owned == 4:
            used_room += 1

    final_room = 8 - (used_room + room_fact)
    print('room is : ', final_room)

    return final_room


def check_current_room():
    # 通过读取的方式来获得空格子
    # 945 , 1373 994 96 1090 97 1187 96 1283 97 1380 97 1477 96 1573 1670
    room1 = [949, 1371]
    room2 = [1036, 1377]
    room3 = [1133, 1377]
    room4 = [1232, 1374]  # 5
    room5 = [1330, 1374]  # 5
    room6 = [1427, 1374]  # 5
    room7 = [1515, 1378]  # 5
    room8 = [1608, 1378]  # 5

    room_count = 0

    c1 = get_color(room1[0], room1[1])
    c2 = get_color(room2[0], room2[1])
    c3 = get_color(room3[0], room3[1])
    c4 = get_color(room4[0], room4[1])
    c5 = get_color(room5[0], room5[1])
    c6 = get_color(room6[0], room6[1])
    c7 = get_color(room7[0], room7[1])
    c8 = get_color(room8[0], room8[1])
    if c1 == '#222225':
        room_count += 1
    if c2 == '#222225':
        room_count += 1
    if c3 == '#222225':
        room_count += 1
    if c4 == '#222225':
        room_count += 1
    if c5 == '#222225':
        room_count += 1
    if c6 == '#222225':
        room_count += 1
    if c7 == '#222225':
        room_count += 1
    if c8 == '#222225':
        room_count += 1

    return room_count


def achieve_money():
    pg.leftClick(50, 1368)
    pg.leftClick(1279, 744)


def open_auto_battle():
    print('打开自动战斗')
    # 检测自动战斗
    if parse(1889, 1321, 1946, 1352, 500) == '自动':
        pg.leftClick(1922, 1290)
        pg.moveTo(1243, 595)
        time.sleep(0.01)


def close_auto_battle():
    # 检测自动战斗
    print('关闭自动战斗')
    auto_battle_msg = parse(1889, 1321, 1946, 1352, 500)
    if auto_battle_msg == '手动':
        pg.leftClick(1922, 1290)
        pg.moveTo(1243, 595)
        time.sleep(0.01)
    elif auto_battle_msg == '自动':
        print('当前战斗模式已经是非自动战斗')
    elif not auto_battle_msg == '自动':
        print('检测到战斗既不是手动,也不是自动,尝试检测是否是主菜单')


def not_buy():
    pg.leftClick(1291, 1093)


def get_eq_u_want(hex_array, pos) -> ShopEquipment:
    pos1_hex, pos2_hex, pos3_hex, pos4_hex = hex_array[0], hex_array[1], hex_array[2], hex_array[3]

    if pos == 1:
        return shop_eq[pos1_hex]
    elif pos == 2:
        return shop_eq[pos2_hex]
    elif pos == 3:
        return shop_eq[pos3_hex]
    elif pos == 4:
        return shop_eq[pos4_hex]


def confirm_buy(eq_want_buy: ShopEquipment, pos):
    """确认购买，针对树枝做特殊的逻辑处理"""

    # 如果购买的是树枝，那么加完之后进行计算如果等于4了则自动重置为0
    if pos != 0:
        eq_want_buy.actual_owned += 1
        if eq_want_buy.name == '铁树枝干':
            if eq_want_buy.actual_owned >= 4:
                eq_want_buy.actual_owned = 0

    if pos == 1:
        pg.leftClick(636, 466)
    elif pos == 2:
        pg.leftClick(1042, 466)
    elif pos == 3:
        pg.leftClick(1448, 466)
    elif pos == 4:
        pg.leftClick(1854, 466)


def buy_equipment_pos():
    # 读取装备信息 装备名 以及对应位置上的颜色 636,466 1042,466 1448,466 406
    global first_replace_1, first_replace_2, room_fact
    pos1x = 664
    pos1y = 618
    pos2x = 664 + 406 * 1
    pos2y = 618
    pos3x = 664 + 406 * 2
    pos3y = 618
    pos4x = 664 + 406 * 3
    pos4y = 618

    pos1_hex = get_color(pos1x, pos1y)
    pos2_hex = get_color(pos2x, pos2y)
    pos3_hex = get_color(pos3x, pos3y)
    pos4_hex = get_color(pos4x, pos4y)

    max_pri = 0
    pos_final = 0

    if pos1_hex in shop_eq.keys():
        eq1 = shop_eq[pos1_hex]
        if eq1.priority > max_pri:
            if eq1.actual_owned < 4:
                max_pri = eq1.priority
                pos_final = 1

    if pos2_hex in shop_eq.keys():
        eq2 = shop_eq[pos2_hex]
        if eq2.priority > max_pri:
            if eq2.actual_owned < 4:
                max_pri = eq2.priority
                pos_final = 2

    if pos3_hex in shop_eq.keys():
        eq3 = shop_eq[pos3_hex]
        if eq3.priority > max_pri:
            if eq3.actual_owned < 4:
                max_pri = eq3.priority
                pos_final = 3

    if pos4_hex in shop_eq.keys():
        eq4 = shop_eq[pos4_hex]
        if eq4.priority > max_pri:
            if eq4.actual_owned < 4:
                max_pri = eq4.priority
                pos_final = 4

    global total_spend_money
    total_spend_money += 800

    cr = check_current_room_fast()
    hex_array = [pos1_hex, pos2_hex, pos3_hex, pos4_hex]
    branches_number = shop_eq['#241706'].actual_owned

    if pos_final != 0:
        eqw = get_eq_u_want(hex_array, pos_final)
        # cr > 2 ，自由购买
        if cr > 2:
            confirm_buy(eqw, pos_final)
        # cr = 2 且 树枝!= 0 那么可以购买任意可以购买的装备 ,如果树枝 = 0，则只能买树枝/1/3 星装备
        if cr == 2:
            if branches_number != 0:
                confirm_buy(eqw, pos_final)
            elif branches_number == 0:
                if eqw.name == '铁树枝干' or eqw.actual_owned == 1 or eqw.actual_owned == 3:
                    confirm_buy(eqw, pos_final)
                else:
                    not_buy()
        # cr = 1 且 0<树枝<3  first_replace_1 = True , 可以购买 那么可以购买装备数量=2的非树枝装备一件 ，重置first_replace_1=False
        # 树枝 = 3 ，则可以直接购买
        #
        if cr == 1:
            if first_replace_1 and 0 < branches_number < 3:
                if eqw.name != '铁树枝干' and eqw.actual_owned == 2:
                    confirm_buy(eqw, pos_final)
                    first_replace_1 = False
                elif eqw.name == '铁树枝干' or eqw.actual_owned == 1 or eqw.actual_owned == 3:
                    confirm_buy(eqw, pos_final)
                else:
                    not_buy()
            elif branches_number == 3:
                confirm_buy(eqw, pos_final)
            # cr = 1 且 first_replace_1 = False ,则只能买树枝/1/3 星装备
            else:
                if eqw.name == '铁树枝干' or eqw.actual_owned == 1 or eqw.actual_owned == 3:
                    confirm_buy(eqw, pos_final)
                else:
                    not_buy()
        # cr = 0 且 购买的是树枝(数量=2) 且 first_replace_2 = True，则顶掉金箍棒 重置 first_replace_1 first_replace_2为False
        # 当树枝数 = 3时 同样有一次 购买装备数量=2的非树枝装备一件
        if cr == 0:
            if first_replace_2 and eqw.name == '铁树枝干' and branches_number == 2:
                confirm_buy(eqw, pos_final)
                # 顶替金箍棒的位置
                time.sleep(0.1)
                pg.leftClick(948, 1399)
                first_replace_1 = False
                first_replace_2 = False
                room_fact -= 1
            elif first_replace_1 and first_replace_2 and branches_number == 3 and eqw.name != '铁树枝干' and eqw.actual_owned == 2:
                confirm_buy(eqw, pos_final)
                # 顶替金箍棒的位置
                time.sleep(0.1)
                pg.leftClick(948, 1399)
                first_replace_1 = False
                first_replace_2 = False
                room_fact -= 1
            elif eqw.name == '铁树枝干' or eqw.actual_owned == 1 or eqw.actual_owned == 3:
                confirm_buy(eqw, pos_final)
            else:
                not_buy()
    else:
        not_buy()

    # if pos_final == 1:
    #     # 当前格子如果<=2了 则只买树枝 以及 已购买装备数量等于 1 或者 3 的装备
    #     if cr > 2:
    #         confirm_buy(shop_eq[pos1_hex])
    #
    #     if cr <= 2:
    #         if shop_eq[pos1_hex].name == '铁树枝干' or shop_eq[pos1_hex].actual_owned == 1 or shop_eq[
    #             pos1_hex].actual_owned == 3:
    #             confirm_buy(shop_eq[pos1_hex])
    #     elif first_replace_1 and cr == 0:
    #         shop_eq[pos1_hex].actual_owned += 1
    #         pg.leftClick(636, 466)
    #         time.sleep(0.1)
    #         pg.leftClick(948, 1399)
    #         first_replace_1 = False
    #     else:
    #         shop_eq[pos1_hex].actual_owned += 1
    #         pg.leftClick(636, 466)
    # elif pos_final == 2:
    #     if cr <= 2:
    #         if shop_eq[pos2_hex].name == '铁树枝干' or shop_eq[pos2_hex].actual_owned == 1 or shop_eq[
    #             pos2_hex].actual_owned == 3:
    #             shop_eq[pos2_hex].actual_owned += 1
    #             pg.leftClick(1042, 466)
    #     elif first_replace_1 and cr == 0:
    #         shop_eq[pos2_hex].actual_owned += 1
    #         pg.leftClick(636, 466)
    #         time.sleep(0.1)
    #         pg.leftClick(948, 1399)
    #         first_replace_1 = False
    #     else:
    #         shop_eq[pos2_hex].actual_owned += 1
    #         pg.leftClick(1042, 466)
    #
    # elif pos_final == 3:
    #     if cr <= 2:
    #         if shop_eq[pos3_hex].name == '铁树枝干' or shop_eq[pos3_hex].actual_owned == 1 or shop_eq[
    #             pos3_hex].actual_owned == 3:
    #             shop_eq[pos3_hex].actual_owned += 1
    #             pg.leftClick(1448, 466)
    #     elif first_replace_1 and cr == 0:
    #         shop_eq[pos3_hex].actual_owned += 1
    #         pg.leftClick(636, 466)
    #         time.sleep(0.1)
    #         pg.leftClick(948, 1399)
    #         first_replace_1 = False
    #     else:
    #         shop_eq[pos3_hex].actual_owned += 1
    #         pg.leftClick(1448, 466)
    #
    # elif pos_final == 4:
    #     if cr <= 2:
    #         if shop_eq[pos4_hex].name == '铁树枝干' or shop_eq[pos4_hex].actual_owned == 1 or shop_eq[
    #             pos4_hex].actual_owned == 3:
    #             shop_eq[pos4_hex].actual_owned += 1
    #             pg.leftClick(1854, 466)
    #     elif first_replace_1 and cr == 0:
    #         shop_eq[pos4_hex].actual_owned += 1
    #         pg.leftClick(636, 466)
    #         time.sleep(0.1)
    #         pg.leftClick(948, 1399)
    #         first_replace_1 = False
    #     else:
    #         shop_eq[pos4_hex].actual_owned += 1
    #         pg.leftClick(1854, 466)
    # else:
    #     pg.leftClick(1291, 1093)


def handle_45():
    time.sleep(3)
    global talent_count, first_replace_1, first_replace_2, total_spend_money, current_money, shop_count, first_shopping, first_break
    while True:
        # 是否是结算界面 1342,1065,1404,1095
        if parse(1342, 1065, 1404, 1095, 500) == '确定':
            print('进入结算界面,重置一些全局变量')
            total_spend_money = 0
            talent_count = 1
            current_money = 0
            shop_count = 0
            first_shopping = True
            first_break = True
            first_replace_1 = True
            first_replace_2 = True
            for e in shop_eq.values():
                e.reset()
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

        open_auto_battle()

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
            handle_talent_45()
            handle_rewards()
            handle_equipment()
        elif current_time == 0:
            handle_challenge()
            handle_window()
            handle_rewards()
        else:
            handle_window()
            handle_challenge()
            handle_talent_45()
            handle_rewards()
            handle_shopping()

        time.sleep(5)


def infinite_q():
    # Q位置 1367,670
    pg.leftClick(240, 1368)
    time.sleep(0.1)
    infinite_count = 0
    while True:
        pg.leftClick(42, 1381)
        pg.leftClick(1183, 827)  # 实际Q的位置
        infinite_count += 1
        if not get_color(262, 1385) == '#543e29':
            break


def handle_hard_final_rewards():
    """处理深渊的最终奖励"""
    global already_infinite_q, total_spend_money, talent_count, first_break, first_replace_1, first_replace_2, first_shopping, current_money, shop_count, room_fact
    # 检测是否是深渊的结算页面
    menu_string = parse(1355, 839, 1483, 870, 500)
    print('处理深渊结算页面，menu_string = ', menu_string)
    if '主菜单' in menu_string:
        # 重置一些全局变量
        already_infinite_q = False
        total_spend_money = 0
        talent_count = 1
        current_money = 0
        shop_count = 0
        room_fact = 1
        first_shopping = True
        first_break = True
        first_replace_1 = True
        first_replace_2 = True
        for e in shop_eq.values():
            e.reset()

        # 处理掉落池
        handle_drop_pool()

        # 点击返回主菜单
        pg.leftClick(1419, 859)
        time.sleep(1)

        # 点击深渊挑战
        pg.leftClick(1050, 727)
        time.sleep(1)

        # 点击生成队伍
        pg.leftClick(1289, 684)
        time.sleep(1)

        # 点击确定进入
        pg.leftClick(1280, 907)
        time.sleep(1)


def handle_hard():
    global current_money

    # 开启自动，刷到7点天赋点无限Q
    global already_infinite_q, first_break

    while True:
        print('新一轮循环')
        # 结算页面
        time.sleep(1)

        # 处理结算页面
        handle_hard_final_rewards()

        # 处理终极神器
        handle_final_equipment()

        if first_break:
            # 分解一次装备
            handle_equipment()
            first_break = False

        if not already_infinite_q:
            open_auto_battle()

        # 处理天赋
        handle_talent_hard()

        # 如果Boss在 就打开自动战斗
        check_boss_exists()

        # 保证前排血量
        stay_live()

        # 如果点了无限Q,那么关闭自动，开始无限Q
        if already_infinite_q:
            close_auto_battle()

        # 修正金钱数
        try:
            current_money = int(parse(2256, 1279, 2362, 1316, 250))
        except Exception as ex:
            print('处理购买装备发生异常')
            current_money = 0

        # E 无CD就无限Q 直到Q有CD ，E CD期间就消费
        if already_infinite_q:
            boss_come = parse(1179, 107, 1252, 141, 400) == 'BOSS' or parse(1179, 107, 1252, 141, 400) == 'BOS5' or parse(1179, 107, 1252, 141, 400) == 'BO5S' or parse(1179, 107, 1252, 141, 400) == 'BO55'
            if get_color(245, 1340) == '#cb5238' and (not boss_come):
                infinite_q()
                check_boss_exists()
            elif get_color(245, 1340) == '#52231a':
                handle_shopping_hard()
        # 结束刷钱阶段时，只有有boss在且E可以用会启动无限Q
        elif check_boss_is_live():
            if get_color(245, 1340) == '#cb5238':
                check_boss_exists()
                infinite_q()

        # 什么时候结束刷钱？ 总消费数 > 80w 结束刷钱 开启自动模式 正常消费
        print('总消费数' + str(total_spend_money))
        if total_spend_money > 800000:
            already_infinite_q = False
            handle_shopping_hard()

        # 捡箱子
        handle_rewards()


def handle_final_equipment():
    global room_fact
    # 处理不朽神器
    if get_color(565, 1199) == '#f9cd19':
        print('发现神器,处理')
        room_fact -= 1
        pg.leftClick(565, 1199)
        time.sleep(0.2)
        pg.leftClick(467, 1126)


def check_boss_is_live():
    pg.leftClick(1336, 585)
    time.sleep(0.1)
    while True:
        if get_color(75, 275) == '#fe6347':
            return True
        else:
            return False


def check_boss_exists():
    # 点击Boss ，然后查看血条颜色
    print('检查Boss血条')
    while True:
        # 在Boss死亡前要一直保持自动战斗
        pg.leftClick(1341, 587)
        time.sleep(0.1)
        boss_color = get_color(82, 273)
        time.sleep(0.1)
        if boss_color == '#fe5b3d':
            print('检测到Boss血条存在,尝试打开自动战斗')
            open_auto_battle()
            if '菜单' in parse(1355, 839, 1483, 870, 500):
                break
        else:
            print('没有检测到Boss血条，当前颜色为, ', boss_color, '尝试关闭自动战斗')
            close_auto_battle()
            break


def check_boss_come():
    # 如果发现BOSS快来了 就打开自动，一直等到BOSS词条结束后过10秒继续
    if parse(1179, 107, 1252, 141, 400) == 'BOSS' or parse(1179, 107, 1252, 141, 400) == 'BOS5' or parse(1179, 107, 1252, 141, 400) == 'BO5S' or parse(1179, 107, 1252, 141, 400) == 'BO55':
        open_auto_battle()
        time.sleep(20)


def handle_drop_pool():
    """处理深渊掉落池的装备，只捡套装"""
    initial_x = 2061
    initial_y = 761
    adjust_time = 0
    is_pool_start = False
    tmp_flag = True

    while tmp_flag:
        # 鼠标每次滑动96个y 所有的y
        initial_y = 761 - adjust_time * 9
        print(initial_y)

        for i in range(0, 5):
            for j in range(0, 5):
                if get_color(initial_x + j * 107, initial_y + i * 87) == '#c8ffd6':
                    pg.leftClick(initial_x + j * 107, initial_y + i * 87)
                    pg.moveTo(2152, 388)
                    time.sleep(0.1)

        # 开始正常滑动后 正常滑动一次
        if is_pool_start:
            pg.moveTo(2505, 704)
            pg.scroll(-87)
            adjust_time += 1
            time.sleep(0.5)

        # 首先滑动鼠标直到开始作用了为止
        while True:
            # 没有滚动条的话就直接结束
            if not get_color(2518, 843) == 'd08d53':
                tmp_flag = False
                break

            if not get_color(2518, 1066) == '#d08d53':
                pg.moveTo(2505, 704)
                pg.scroll(-87)
                time.sleep(0.5)
            else:
                if not is_pool_start:
                    adjust_time = 1
                is_pool_start = True
                break

        if get_color(2520, 1172) == '#d08d53':
            break


def stay_live():
    # 如果大牛生命值少于 50% 就手动点光法的加血
    # 大牛位置 1051,918
    # 313,275 #fe6347
    pg.leftClick(968, 960)
    pg.sleep(0.01)
    if not get_color(372, 275) == '#fe6347':
        give_hp()


def give_hp():
    """点一个加血方块(仅限光法)"""
    while True:
        if get_color(809, 1283) == '#edf2fe':
            pg.leftClick(809, 1283)
            break
        elif get_color(919, 1285) == '#e1e8f6':
            pg.leftClick(919, 1285)
            break
        elif get_color(1020, 1287) == '#ecf4fd':
            pg.leftClick(1020, 1287)
            break
        elif get_color(1124, 1280) == '#eaefff':
            pg.leftClick(1124, 1280)
            break
        elif get_color(1225, 1283) == '#eef0fe':
            pg.leftClick(1225, 1283)
            break
        elif get_color(1326, 1283) == '#edf1fd':
            pg.leftClick(1326, 1283)
            break
        elif get_color(1431, 1279) == '#e8edfd':
            pg.leftClick(1431, 1279)
            break
        elif get_color(1536, 1282) == '#e6eafa':
            pg.leftClick(1536, 1282)
            break
        elif get_color(1637, 1281) == '#e9edfd':
            pg.leftClick(1637, 1281)
            break
        elif get_color(1738, 1280) == '#eef4fe':
            pg.leftClick(1738, 1280)
            break
        else:
            if get_color(1738, 1280) == '#110d18':
                # 已经在菜单页面了 break
                break
            else:
                pg.leftClick(1738, 1280)


if __name__ == '__main__':
    time.sleep(3)
    handle_hard()
    # handle_45()

    # handle_hard()

    # handle_shopping() Q  #5b301a- 不可用  #e07636 - 可用 45,1339
    # E #52231a - 不可用 #cb5238 - 可用
    # print(get_color(245, 1340))
    # 1179,107,1252,141 BOSS

    # print(get_color(262, 1389)) # #de9578 - 超过15秒了 #5a3c31 - 没超15秒
