from dotenv import load_dotenv
from datetime import datetime, timedelta
import google.generativeai as genai
import re
import os


class YoutubePreprocessor:
    def __init__(self):
        self.GOOGLE_API_KEY = None
        self.gemini = None
    
    def set_gemini_api(self, n):
        load_dotenv('../../../resources/secret.env')
        self.GOOGLE_API_KEY = os.getenv(f'GOOGLE_API_KEY{n}')
        genai.configure(api_key=self.GOOGLE_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-pro')
    
    def convert_to_number(self, text):
        if text is not None:
            try:
                number_string = ''
                for char in text:
                    if char.isdigit() or char == '.':
                        number_string += char
                number = float(number_string)
                if text[-1] == '천':
                    number *= 1000
                if text[-1] == '만':
                    number *= 10000
                if text[-1] == 'K':
                    number *= 1000
                if text[-1] == 'M':
                    number *= 10000
                return int(number)
            except Exception as e:
                print(e)
                print('text:', text)
                return 0
        else:
            return 0

    def convert_to_date(self, text):
        try:
            # '년 전', '개월 전', ... 형식 처리
            if '년' in text:
                num = int(''.join(filter(str.isdigit, text)))
                delta = timedelta(days=num * 365)
                result = datetime.now() - delta
                return result.strftime('%Y-%m-%d')
            if '개월' in text:
                num = int(''.join(filter(str.isdigit, text)))
                delta = timedelta(days=num * 30)
                result = datetime.now() - delta
                return result.strftime('%Y-%m-%d')
            if '주' in text:
                num = int(''.join(filter(str.isdigit, text)))
                delta = timedelta(days=num * 7)
                result = datetime.now() - delta
                return result.strftime('%Y-%m-%d')
            if '일' in text:
                num = int(''.join(filter(str.isdigit, text)))
                delta = timedelta(days=num * 1)
                result = datetime.now() - delta
                return result.strftime('%Y-%m-%d')
            if '시간' in text:
                result = datetime.now()
                return result.strftime('%Y-%m-%d')
            if '분' in text:
                result = datetime.now()
                return result.strftime('%Y-%m-%d')
        except Exception as e:
            print(e)
            print(text)
        
        # '년. 월. 일.' 형식 처리
        try:
            result = datetime.strptime(text, '%Y. %m. %d.')
            return result.strftime('%Y-%m-%d')
        except ValueError:
            print(f'년. 월. 일. 형식 처리 중 에러 발생')
            print(text)
        
        # 그 외의 형식 처리
        try:
            filtered_text = re.findall(r'[\d.]+', text)
            if filtered_text:
                result = datetime.strptime(filtered_text[0], '%Y.%m.%d.')
                return result.strftime('%Y-%m-%d')
        except ValueError:
            print(f'다른 형식 처리 중 에러 발생')
            print(text)
        
        return None

    def query_to_gemini(self, gemini, query_string):
        response = gemini.generate_content(query_string)
        return response.text

    def is_recipe(self, text):
        return '재료' in text

    def is_korean(self, text):
        return re.search('[가-힣]', text)

    def split_text(self, text):
        if ',' in text:
            result = text.split(',')
            if len(result) == 2:
                return result[0].strip(), result[1].strip()
        return None, None
    
    def contains_korean_and_digit(self, text):
        korean_pattern = re.compile('[ㄱ-ㅎㅏ-ㅣ가-힣]')
        digit_pattern = re.compile('[0-9]')

        has_korean = korean_pattern.search(text) is not None
        has_digit = digit_pattern.search(text) is not None

        return has_korean and has_digit

    def contains_english_and_digit(self, text):
        digit_pattern = re.compile('[0-9]')
        english_pattern = re.compile('[a-zA-Z]')

        has_digit = digit_pattern.search(text) is not None
        has_english = english_pattern.search(text) is not None

        return has_digit and has_english

    def convert_to_only_korean(self, text):
        return re.sub('[^ㄱ-ㅎㅏ-ㅣ가-힣]', '', text)
    
    def is_ingredient_and_amount(self, ingredient_name, ingredient_amount):
        if ingredient_name and ingredient_amount and type(ingredient_name) == type('str') and type(ingredient_amount) == type('str'):
            if ingredient_name and '재료' not in ingredient_name and len(ingredient_name) < 128 and len(ingredient_amount) < 128:
                if self.contains_korean_and_digit(ingredient_amount) or self.contains_english_and_digit(ingredient_amount):
                    return True
        return False
                    
    def convert_to_ingredient_and_amount(self, video_text):
        try:
            if self.is_recipe(video_text):
                
                ingredient_and_amount_list = []
                
                query_string = f'"{video_text}"에서 만약 음식재료명과 첨가량에 대한 정보가 있다면 "재료명1,첨가량1\n재료명2,첨가량2\n재료명3,첨가량3,..."와 같은 포맷으로 문자열만 알려줘.'
                gemini_output = self.query_to_gemini(self.gemini, query_string)
                
                text_lines = gemini_output.split('\n')
                for text_line in text_lines:
                    ingredient_name, ingredient_amount = self.split_text(text_line)
                    if self.is_ingredient_and_amount(ingredient_name, ingredient_amount):
                        ingredient_name = self.convert_to_only_korean(ingredient_name)
                        ingredient_and_amount_list.append([ingredient_name, ingredient_amount])
                
                return ingredient_and_amount_list
                
        except Exception as e:
            print('에러 발생')
            print(e)
            raise
        
    def preprocess_text(self, text):
        return str(text).strip()