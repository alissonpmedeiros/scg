""" other modules """
import csv 

class CSV:
    @staticmethod
    def create_file(file_dir: str, file_name: str, header: list):
        with open('{}{}'.format(file_dir, file_name), 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    
    @staticmethod
    def save_data(file_dir: str, file_name: str, data: list):
        with open('{}{}'.format(file_dir, file_name), 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(data)


