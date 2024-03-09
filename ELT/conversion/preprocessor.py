import re
from fractions import Fraction


class Preprocessor:
    def __init__(self):
        pass
    
    # 정규표현식을 사용하여 문자열에서 숫자와 단위를 추출하는 함수
    def extract_grams_by_regex(self, input_string):
        matches = re.findall(r'(\d+\.?\d*)\s*(밀리리터|ml|mL|cc|CC|g|그램|리터|L|kg|Kg|KG|킬로그램)', input_string)

        grams = 0
        # 추출한 숫자와 단위에 따라 그램으로 변환합니다.
        for match in matches:
            value, unit = match
            if unit in ['밀리리터', 'ml', 'mL', 'cc', 'CC', 'g', '그램']:
                grams += float(value)
            elif unit in ['리터', 'L', 'kg', 'Kg', 'KG', '킬로그램']:
                grams += float(value) * 1000

        return grams
    
    # 문자열에서 숫자와 단위를 분리하는 함수
    def split_volume_unit(self, input_string):
        input_string = input_string.replace(' ','')
        pattern = r'(\d*\.?\d+/\d+|\d*\.?\d+)\s*([^\d\s.]+)'
        matches = re.findall(pattern, input_string)
        
        for match in matches:
            volume = match[0]
            if '/' in volume:
                volume = Fraction(volume)
            unit = match[1]
            return float(volume), unit.lower()
        
        return False, False