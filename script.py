import urllib.request as urllib2
import requests
import json
import csv
import os
import time

# handle = 'xsanchez'

# list to store all the solutions id and the submitting user with given language, problem id and having verdict as OK
submissions = []
# url to parse the submitted code of a specific contest with submission id
url = 'http://codeforces.com/contest/{ContestId}/submission/{SubmissionId}'
startIndex = 17000
# codeStart is a line after which user's code is written, this is specifically for cpp , for other you can cpp to java etc .
codeStart = '<pre id="program-source-text" class="prettyprint lang-cpp linenums program-source" style="padding: 0.5em;">'
# these are used while cleaning the code
replacer = {'&quot;': '\"', '&gt;': '>', '&lt;': '<', '&amp;': '&', "&apos;": "'"}
keys = replacer.keys()
# this function cleans the code, convert all the tags to original meaning so that we can have comiplable code
def parse(source_code):
    for key in keys:
        source_code = source_code.replace(key, replacer[key])
    return source_code

# this function is finding all the submission of given contest with verdict OK and given problemID
def findSubmissions(contestid,problemid,count):
    # this line retruns Response from requested url
    r = requests.get('https://codeforces.com/api/contest.status?contestId='+str(contestid)+'&from=1&count='+str(count))
    # parse given response to json
    parsed_json = r.json()
    # making a directory named with given cntest id if it doesn't exists already
    Repo = str(contestid)
    if not os.path.exists(Repo):
        os.makedirs(Repo)
        print(" repo made : " + Repo)
    # looping over json to make list of submission
    for i in parsed_json['result']:
        # object of information we need for further steps
        obj = {
            'id':'',
            'programmingLanguage':'',
            'handle':[]
        }
        cnt = 0
        # filling information of our submission
        if i['verdict'] == 'OK' and i['problem']['index'] == problemid:
            obj['id'] = i['id']
            obj['programmingLanguage'] = i['programmingLanguage']
            for j in i['author']['members']:
                obj['handle'].append(j['handle'])
            # Right now only works with GNU C++14
            if i['programmingLanguage'] == 'GNU C++14':
                # this filled up url with given values then read whole page and convert it to utf-8
                data = urllib2.urlopen(url.format(ContestId=contestid, SubmissionId=i['id'])).read().decode('utf-8')
                # start_pos and end_pos are indexes from where actual user code starts and ends respectively
                start_pos = data.find(codeStart, startIndex) + len(codeStart)
                end_pos = data.find("</pre>", start_pos)
                # extract out code
                result = parse(data[start_pos:end_pos]).replace('\r', '')
                print("code extracted of user : " + str(obj['handle']) + " id : " + str(i['id']))
                file = open(Repo + '/' + str(i['id']) + '.cpp', 'w')
                # output code in file which is named using it's submissionID
                file.write(result)
                # inserting this submission in list
                submissions.append(obj)
                cnt+=1

    if len(submissions) != 0:
        execute(submissions,contestid)
    else :
        print("No hacks :(")
    # if list of submissions is empty we don't need to close file
    if cnt!=0:
        file.close()

# this fucntion compiling and checking on testfile for all the parse codes and saving results in newDirectory
def execute(submissions,contestid):
    # new directory to save hacks data
    newDirectory = str(contestid) + '-hacks'
    if not os.path.exists(newDirectory):
        os.makedirs(newDirectory)
        print(" Repo made : " + newDirectory)
    # new directory name
    file1 = open(newDirectory + '/' + newDirectory + '.txt', 'w')
    # for every submission in out list
    for submit in submissions:
        if submit['programmingLanguage'] == 'GNU C++14':
            comm = "cd "+str(contestid)+" g++ "+str(submit['id'])+".cpp"
            # system calls to compile code and saving it output to file1
            os.system(comm)
            # compiling code with given testfile and saving it output in output file to compare it in next step
            os.system("./a.out < testfile.txt > output.txt")
            # checking is both outputs are same or not , if are same do nothing , otherwise save information in ans.txt
            os.system("diff output1.txt output.txt > ans.txt")
            if os.path.getsize("ans.txt") != 0:
                # console output
                print(submit['id'],file = file1)
                for h in submit['handle']:
                    print(h,file = file1)
                print('\n')
    file1.close()

# time and start functions
start_time = time.time()
print("Give input contestID : ")
contestNum = int(input())
print("Give input problemID i.e A,B,C .. :")
problemChar = input()
print("how many solutions to search in : ")
cnt = int(input())
findSubmissions(contestNum,problemChar,cnt)

end_time = time.time()
print ('Execution time %d seconds' % int(end_time - start_time))
