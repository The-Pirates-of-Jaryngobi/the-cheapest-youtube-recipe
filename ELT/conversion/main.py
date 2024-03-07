from preprocessor import Preprocessor
from db_connector import DBConnector

if __name__ == '__main__':
    db_connector = DBConnector()
    preprocessor = Preprocessor()
    
    db_connector.set_connect_db()
    
    ingredient_list = db_connector.get_ingredient_data_list()
    for i in range(len(ingredient_list)):
        ingredient_id = ingredient_list[i][0]
        ingredient_name = ingredient_list[i][1]
        ingredient_vague = ingredient_list[i][2]
        print(ingredient_id, ingredient_name, ingredient_vague)
        ingredient_volume = preprocessor.extract_grams_by_regex(ingredient_vague)
        
        if ingredient_volume: # 1. 정규식 표현으로 처리가 가능한 경우.
            db_connector.write_to_ingredient(ingredient_id=ingredient_id, ingredient_volume=ingredient_volume, ingredient_unit='g')
        
        else:
            ingredient_volume, ingredient_unit = preprocessor.split_volume_unit(input_string=ingredient_vague)
            
            if ingredient_volume and ingredient_unit:
                converted_volume, standard_unit = db_connector.get_converted_volume_and_standard_unit(unit_name=ingredient_unit)
                
                if converted_volume and standard_unit:
                    total_volume = ingredient_volume * converted_volume
                    temp_vague = str(total_volume)+standard_unit
                    temp_ingredient_volume = preprocessor.extract_grams_by_regex(input_string=temp_vague)
                    
                    if temp_ingredient_volume: # 정규식 표현으로 1차 확인.
                        db_connector.write_to_ingredient(ingredient_id=ingredient_id, ingredient_volume=temp_ingredient_volume, ingredient_unit='g')
                        continue
                    
                    else:
                        converted_gram = db_connector.get_converted_gram(ingredient_name=ingredient_name, unit_name=standard_unit)
                        db_connector.write_to_ingredient(ingredient_id=ingredient_id, ingredient_volume=total_volume*converted_gram, ingredient_unit='g')
                        continue
                
                else:
                    converted_gram = db_connector.get_converted_gram(ingredient_name=ingredient_name, unit_name=ingredient_unit)
                    db_connector.write_to_ingredient(ingredient_id=ingredient_id, ingredient_volume=ingredient_volume*converted_gram, ingredient_unit='g')
                    continue
            else:
                continue