"""
Configuration loading.
"""

import sys
import yaml

def mergeYamlData(yamlData, newYamlData, thePath) :
  """This is a generic Python merge. It is a *deep* merge and handles both
  dictionaries and arrays."""

  if type(yamlData) is None :
    print("ERROR yamlData should NEVER be None ")
    sys.exit(-1)

  if type(yamlData) != type(newYamlData) :
    print("Incompatible types {} and {} while trying to merge YAML data at {}".format(type(yamlData), type(newYamlData), thePath))
    print("Stoping merge at {}".format(thePath))
    return

  if type(yamlData) is dict :
    for key, value in newYamlData.items() :
      if key not in yamlData :
        yamlData[key] = value
      elif type(yamlData[key]) is dict :
        mergeYamlData(yamlData[key], value, thePath+'.'+key)
      elif type(yamlData[key]) is list :
        for aValue in value :
          yamlData[key].append(aValue)
      else :
        yamlData[key] = value
  elif type(yamlData) is list :
    for value in newYamlData :
      yamlData.append(value)
  else :
    print("ERROR yamlData MUST be either a dictionary or an array.")
    sys.exit(-1)

def loadConfig(cliArgs) :
  """Load the CPLogger configuration."""

  config = {
    'natsServer' : {
      'cert' : None,
      'key'  : None,
      'port' : '4222',
      'host' : 'localhost',
      },
    'subjects' : [],
    'rawMessages' : False
  }
  try :
    yamlFile = open(cliArgs.config)
    yamlConfig = yaml.safe_load(yamlFile.read())
    yamlFile.close()
    mergeYamlData(config, yamlConfig, "")
  except Exception as ex :
    print("Could not load the configuration file: [{}]".format(cliArgs.config))
    print(repr(ex))

  config['rawMessages'] = cliArgs.raw

  if cliArgs.send :
    theMsg = " ".join(cliArgs.words)
    if cliArgs.messageFile :
      try :
        msgFile = open(cliArgs.messageFile)
        theMsg = yaml.safe_load(msgFile.read())
        msgFile.close()
      except Exception as ex :
        print("Could not load the message file: [{}]".format(cliArgs.mssageFile))
        print(repr(ex))

    config['send'] = {
      'subject' : cliArgs.send,
      'message' : theMsg
    }

  config['verbose'] = cliArgs.verbose
  if 0 < config['verbose'] :
    print("---------------------------------------------------------------")
    print("Configuration:")
    print(yaml.dump(config))
    print("---------------------------------------------------------------")

  return config
