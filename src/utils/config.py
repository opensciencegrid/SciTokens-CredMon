
import os
import ConfigParser

config = None

def ReadConfiguration(config_location):
    global config
    config = ConfigParser.ConfigParser()
    config.read([config_location])
    
    
def GetProviders():
    global config

    providers = []

    if config is None:
        raise Exception("Configuration hasn't been read in yet")

    for section in config.sections():
        if section.startswith("Provider"):
            provider = section.split(" ", 1)
            if len(provider) > 1:
                providers.append(provider[1])

    return providers
    
    
def GetProviderOptions(provider_name, option):
    if not config.has_section("Provider {0}".format(provider_name)):
        raise Exception("Unable to find Provider {0} in configuration file".format(provider_name))
    
    return config.get("Provider {0}".format(provider_name), option)
    
    


