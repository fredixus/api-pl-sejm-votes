import json
import boto3
from ast import literal_eval

with open ("secrets.json") as file:
    data = json.load(file)

s3 = boto3.client ('s3')
bucket = data["bucket"]
storage = data["storage"]

def composeResponse(code, body, msg='', ensure_ascii = False):
    return {
        'statusCode': code,
        'body': {
            "message": msg,
            "data": json.dumps(body, ensure_ascii=ensure_ascii)
            }
        }  

def composeJsonResponse(code, body, msg=''):
    return {
        'statusCode': code,
        'body': {
            "message": msg,
            "data": body
            }
        }
        
def composePathToFile(storage, path, requestedFile):
    return storage + path + '/' + requestedFile

def clearPath(path):
    return path.replace('/pl-gov','') if ("/pl-gov" in path) else path
    
def checkIfEmptyString(text):
    if text == '' or None:
        return True
    else:
        return False
        
def validList(text):
    return True if 'list' in text else False
    
def validYear(text):
    return True if int(text) > 1989 else False
    
def validMonth(text):
    return True if int(text) >= 1 and int(text) <= 12 else False
    
def validDay(text):
    return True if int(text) >= 1 and int(text) <= 31 else False

def validPath(path):
    # /9/2023/08/16
    # /9                -- Kandencja sejmu np. 9 (IX)
    # --/2023           -- Rok
    # -------/08        -- Miesiąc
    # ----------/16     -- Dzień
    if(validList(path) == True):
        path = path.replace('/list','')
    
    path = '0'+path
    path_list = path.split("/")
    length = len(path_list)
    emptyPathTextFlag = False

    # Look for empty text
    for el in path_list:
        if checkIfEmptyString(el) == True:
            emptyPathTextFlag = True
    
    if emptyPathTextFlag == True:
        return False
    if length == 1:
        return False
    if length == 2:
        return False
    if length == 3:
        return False
    if length == 4:
        return False
    if length == 5:
        if validYear(path_list[2]) and validMonth(path_list[3]) and validDay(path_list[4]):
            return True
        else:
            return False

def getFileList(path , bucket = bucket, storage=storage, s3=s3):    
    prefix = storage + path + '/'
    limiter='/'
    
    lista = s3.list_objects(Bucket = bucket, Prefix=prefix, Delimiter=limiter)['Contents']

    list_of_files = []
    for file in lista:
        list_of_files.append(str.replace(file['Key'], prefix,''))     
    list_of_files.remove('')
    return list_of_files
    
def getFile(path, bucket = bucket):
    try:
        return s3.get_object(Bucket = bucket, Key = path)["Body"].read().decode('utf')
    except:
        return {'path':path, 'message':'Not exists'}

def getFiles(files, base_path, bucket=bucket, storage=storage):
    print(files, base_path, bucket, storage)
    filesList = []
    for file in files:
        path = composePathToFile(storage, base_path, file)
        print(path)
        filesList.append(literal_eval(getFile(path))[0])
    print (filesList)
    return filesList
    
def replaceEmptyEventObject(eventObject, replacement, event):
    try:
        requestedParameter = event[eventObject]
    except KeyError:
        requestedParameter = replacement
    finally:
        if event is None:
            return replacement
    return requestedParameter

    
def lambda_handler(event, context):
    
    print('Event: ', event)
    path = clearPath(event['path'])
    try:
        body = json.loads(replaceEmptyEventObject('body',"""{"body":{"file":"*"}}""", event))
    except:
        body = replaceEmptyEventObject('body',"""{"body":{"file":"*"}}""", event)
    
    print(body)    
    requestedFile = replaceEmptyEventObject('file', '*', body)
    print(requestedFile)
    
    if(validList(path) == False and (path is not None) and (validPath(path) and (requestedFile != "*")) and (len(body['file']) == 1)):
        # Return one file
        path = composePathToFile(storage, path, body['file'][0])
        return composeJsonResponse(200, getFile(path), 'Success')
        
    elif(validList(path) == False and (path is not None) and (validPath(path) and (requestedFile != "*")) and (len(body['file']) > 1)):
        # Return multiple files
        files = getFiles(body['file'], path)
        return composeResponse(200, files, 'Success')

    elif(validList(path) == False and (path is not None) and (validPath(path) and (requestedFile == '*'))):
        # Return all files
        listFiles = getFileList(path)
        files = getFiles(listFiles, path)
        return  composeJsonResponse(200, files, 'Success')
        
    elif(validList(path) == True and (path is not None) and validPath(path) ):
        # List files
        path = path.replace('/list','')
        listFiles = getFileList(path)
        return  composeResponse(200, listFiles, 'List of files')
    
    else:
        print(validPath(path))
        return composeResponse(400, path, 'Bad request. ')