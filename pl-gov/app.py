import json
import math
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
        "headers" : {
            "Content-Type" : "application/json"
        },
        'body': json.dumps(body, ensure_ascii=ensure_ascii)
        
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
    
def validDeputiesVotes(text):
    return True if 'deputiesVotes' in text else False
    
def validYear(text):
    return True if int(text) > 1989 else False
    
def validMonth(text):
    return True if int(text) >= 1 and int(text) <= 12 else False
    
def validDay(text):
    return True if int(text) >= 1 and int(text) <= 31 else False
    
def validTermOfOffice(text):
    terms = [7, 8, 9, 10]
    return True if int(text) in terms else False

def validPath(path):
    # /9/2023/08/16
    # /9                -- Kandencja sejmu np. 9 (IX)
    # --/2023           -- Rok
    # -------/08        -- Miesiąc
    # ----------/16     -- Dzień
    if(validList(path) == True):
        path = path.replace('/list','')
    
    if(validDeputiesVotes(path) == True):
        path = path.replace('/deputiesVotes','')
    
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
        return True if validTermOfOffice(path_list[1]) else False
    if length == 3:
        return True if validTermOfOffice(path_list[1]) and validYear(path_list[2]) else False
    if length == 4:
        return True if validTermOfOffice(path_list[1]) and validYear(path_list[2]) and validMonth(path_list[3]) else False
    if length == 5:
        return True if validTermOfOffice(path_list[1]) and validYear(path_list[2]) and validMonth(path_list[3]) and validDay(path_list[4]) else False

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
    return filesList
    
def replaceEmptyEventObject(eventObject, replacement, event):
    try:
        requestedParameter = event[eventObject]
    except KeyError:
        requestedParameter = replacement
    except TypeError:
        requestedParameter = replacement
    finally:
        if ((event is None) or (requestedParameter is None)):
            requestedParameter = replacement
    return requestedParameter

def getFilesPerPages(files, event, page_size, path):
    root = '/default/pl-gov'
    total_pages = math.ceil(len(files) / page_size)
    total_pages = 1 if total_pages == 0 else total_pages
    page_num = int(replaceEmptyEventObject('queryStringParameters', {'page':1}, event)['page'])
    
    if page_num < 1 or page_num > total_pages:
        return composeResponse(404, 'Page not found. ' + path)
    
    start = (page_num - 1) * page_size
    end = min(page_num * page_size, len(files))
    
    next_link = None
    if page_num < total_pages:
        next_link = f"{root}{path}?page={page_num + 1}"
    
    prev_link = None
    if page_num > 1:
        prev_link = f"{root}{path}?page={page_num - 1}"
        
    return {
            "files": files[start:end],
            "next": next_link,
            "previous": prev_link,
            "total_pages": total_pages
        }
    
def lambda_handler(event, context):
    page_size = 10
    print('Event: ', event)
    path = clearPath(event['path'])
    try:
        body = json.loads(replaceEmptyEventObject('body',"""{"body":{"file":"*"}}""", event))
    except:
        body = replaceEmptyEventObject('body',"""{"body":{"file":"*"}}""", event)
    
    print(body)    
    requestedFile = replaceEmptyEventObject('file', '*', body)
    print(requestedFile)
        
    if(validList(path) == False and (path is not None) and (validPath(path) and (requestedFile != "*")) and (len(body['file']) >= 1)):
        # Return multiple files
        files = getFiles(body['file'], path)
        #return composeResponse(200, files)
        body = getFilesPerPages(files, event, page_size, path)
        return composeResponse(200, body, True)

    elif(validList(path) == False and (path is not None) and (validPath(path) and (requestedFile == '*'))):
        # Return all files
        listFiles = getFileList(path)
        files = getFiles(listFiles, path)
        #return  composeResponse(200, files)
        body = getFilesPerPages(files, event, page_size, path)
        return composeResponse(200, body, True)
        
    elif(validList(path) == True and (path is not None) and validPath(path) ):
        # List files
        path = path.replace('/list','')
        listFiles = getFileList(path)
        return  composeResponse(200, listFiles)
        
    elif(validList(path) == False and (path is not None) and path == "/"):
        return composeResponse(200, {
            "message":'I am alive, it is working.'
        })
    
    else:
        print(validPath(path))
        return composeResponse(400, 'Bad request. ' + path)