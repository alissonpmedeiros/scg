import yaml

class ConfigController:
    @staticmethod
    def get_config():
        """ Gets the configuration file from ~/scg/config.yaml """
        
        CONFIG_FILE = '/home/ubuntu/scg/config.yaml'
        
        with open(CONFIG_FILE, 'r') as file:
            CONFIG = yaml.load(file, Loader=yaml.FullLoader)
            return CONFIG