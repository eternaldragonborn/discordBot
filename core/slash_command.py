import requests
from core.wrFiles import writeFile
import os


api = 'https://discord.com/api/v8/'
headers = {"Authorization": f"Bot {os.environ['bot_token']}"}

myID = 384233645621248011
applicationID = 719120395571298336

def edit_permission(ids:str, idType:int, permission:bool, guildID, commandID, oldPermission):
  url = f'/applications/{applicationID}/guilds/{guildID}/commands/{commandID}/permissions'
  
  ids = ids.split(',')
   
  permissions = []
  for id in ids:
      permissions.append({
            'id':int(id),  #role or user id
            'type':idType,   #1:role, 2:user
            'permission':permission   #T/F
          })
  if oldPermission:
    permissions.extend(oldPermission['permissions'])
   
  json = {
    'permissions' : permissions
  }
   
  r = requests.put(f'{api}{url}', headers = headers, json=json)
  if r.status_code != requests.codes.ok:
    return r.reason
  else:
    return '更改成功'
   
def get_commands(guildID:int=None):  #only show id, name, default_permission
   if guildID:
      url = f'/applications/719120395571298336/guilds/{guildID}/commands'
   else:
      url = '/applications/719120395571298336/commands'
   r = requests.get(f'{api}{url}', headers=headers)
   if not r.ok:
      return r.reason
   else:
    filename = 'slash_commands'
    commands = []
    for command in r.json():
        commands.append({'id':command['id'], 'name':command['name'], 'default_permission':command['default_permission']})
    writeFile(filename, commands)
    return f'已寫入至`{filename}.json`檔案內'
      
      
def edit_command(default_permission:bool, commandID:int, guildID:int=None):
   if guildID:
      url = f'/applications/{applicationID}/guilds/{guildID}/commands/{commandID}'
   else:
      url = f'/applications/{applicationID}/commands/{commandID}'
   json = {    #name, description, options, default_permission
           'default_permission':default_permission
      }
   r = requests.patch(f'{api}{url}', json=json, headers=headers)
   if not r.ok:
      return r.reason
   else:
      return '更改成功'
      
def get_command_permissions(guildID:int, commandID:int=None):
  if commandID:
    url = f'/applications/{applicationID}/guilds/{guildID}/commands/{commandID}/permissions'
  else:
    url = f'/applications/{applicationID}/guilds/{guildID}/commands/permissions'
  r = requests.get(f'{api}{url}', headers=headers)
  return r
