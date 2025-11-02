"""
Math operations for the game
"""
import math

class Operation:
    """คลาสสำหรับเก็บการดำเนินการทางคณิตศาสตร์"""
    def __init__(self, symbol, func):
        self.symbol = symbol  # สัญลักษณ์ที่แสดงบน gate เช่น '+5', 'x2', '√'
        self.func = func      # ฟังก์ชันที่จะนำไปใช้กับจำนวนคน
    
    def apply(self, crowd):
        """ใช้ effect กับ crowd"""
        self.func(crowd)

class OperationPool:
    """Pool ของ operations สำหรับแต่ละระดับ"""
    
    @staticmethod
    def get_level_1_operations():
        """Level 1: บวก ลบ คูณ พื้นฐาน"""
        return [
            Operation('+10', lambda c: c.add_people(10)),
            Operation('+20', lambda c: c.add_people(20)),
            Operation('+30', lambda c: c.add_people(30)),
            Operation('+50', lambda c: c.add_people(50)),
            Operation('-5', lambda c: c.remove_people(5)),
            Operation('-10', lambda c: c.remove_people(10)),
            Operation('-20', lambda c: c.remove_people(20)),
            Operation('-30', lambda c: c.remove_people(30)),
            Operation('-50', lambda c: c.remove_people(50)),
            Operation('x2', lambda c: c.multiply_people(2)),
            Operation('x3', lambda c: c.multiply_people(3)),
        ]
    
    @staticmethod
    def get_level_2_operations():
        """Level 2: เพิ่ม หาร รากที่สอง ยกกำลัง"""
        return [
            Operation('x2', lambda c: c.multiply_people(2)),
            Operation('x3', lambda c: c.multiply_people(3)),
            Operation('x4', lambda c: c.multiply_people(4)),
            Operation('x5', lambda c: c.multiply_people(5)),
            Operation('÷2', lambda c: c.divide_people(2)),
            Operation('÷3', lambda c: c.divide_people(3)),
            Operation('÷4', lambda c: c.divide_people(4)),
            Operation('÷5', lambda c: c.divide_people(5)),
            Operation('÷6', lambda c: c.divide_people(6)),
            Operation('÷7', lambda c: c.divide_people(7)),
            Operation('÷8', lambda c: c.divide_people(8)),
            Operation('÷10', lambda c: c.divide_people(10)),
            Operation('√', lambda c: c.sqrt_people()),
            Operation('^2', lambda c: c.power_people(2)),
            Operation('^3', lambda c: c.power_people(3)),
            Operation('+30', lambda c: c.add_people(30)),
            Operation('-30', lambda c: c.remove_people(30)),
        ]
    
    @staticmethod
    def get_level_3_operations():
        """Level 3: ยากสุด"""
        return [
            Operation('x2', lambda c: c.multiply_people(2)),
            Operation('x3', lambda c: c.multiply_people(3)),
            Operation('x4', lambda c: c.multiply_people(4)),
            Operation('x5', lambda c: c.multiply_people(5)),
            Operation('÷2', lambda c: c.divide_people(2)),
            Operation('÷3', lambda c: c.divide_people(3)),
            Operation('÷5', lambda c: c.divide_people(5)),
            Operation('÷7', lambda c: c.divide_people(7)),
            Operation('÷10', lambda c: c.divide_people(10)),
            Operation('÷15', lambda c: c.divide_people(15)),
            Operation('÷20', lambda c: c.divide_people(20)),
            Operation('√', lambda c: c.sqrt_people()),
            Operation('^2', lambda c: c.power_people(2)),
            Operation('^3', lambda c: c.power_people(3)),
            Operation('+40', lambda c: c.add_people(40)),
            Operation('-40', lambda c: c.remove_people(40)),
        ]