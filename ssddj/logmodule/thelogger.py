import logging
import logging.config
import yaml
class theLogger:
    def __init__(self, moduleName, configFile='logconfig.yml'):
        fH = open(configFile,'r')
        logging.config.dictConfig(yaml.load(fH))
        fH.close()
        self.logger = logging.getLogger(moduleName)

if __name__=="__main__":
    l = theLogger("powerclass")
    l.logger.info("This is an info of the root logger")
