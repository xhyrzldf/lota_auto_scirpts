need_array = ['全知', '幻寂', '赛丽', '隐之', '创世', '遮面']


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


class ShopEquipment:
    def __init__(self, color_hex, name, priority, initial_owned, actual_owned):
        self.color_hex = color_hex
        self.name = name
        self.priority = priority
        self.initial_owned = initial_owned
        self.actual_owned = actual_owned

    def reset(self):
        self.actual_owned = self.initial_owned

    def __str__(self) -> str:
        return str(self.name)


class HexEquipment:

    def __init__(self, name, hex):
        self.name = name
        self.hex = hex

    def __str__(self) -> str:
        return str(self.name) + "," + self.hex

    def __hash__(self):
        return hash(self.name + self.hex)

    def __eq__(self, other):
        if self.name == other.name and self.hex == other.hex:
            return True
        else:
            return False
