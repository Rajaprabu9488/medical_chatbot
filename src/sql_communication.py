import mysql.connector as sql
import redis
import subprocess
import json

mydb = sql.connect(
    host='localhost',
    user='root',
    password='Raja@2005',
    database='project'
)



r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)
try:
    r.ping()
    print("already running")
except:
    subprocess.run([r"C:\Users\My-PC\OneDrive\Desktop\medical-chatbot\src\start_redis.bat"],shell=True)



r.set('hello','raja')

print(r.get('hello'))
print(r.get('hell'))

cursor = mydb.cursor()

user_id = '134'

try:
    cursor.execute('SELECT * FROM user_log WHERE user_id=%s',([user_id]))
    result = cursor.fetchone()
    if result:
        print('user already exists')
    else:
        cursor.execute("INSERT INTO user_log VALUES(%s , %s , %s ,%s)",('134',"RAJA","raja@gmail.com","94889"))
        

except Exception as e:
    expstr = str(e)
    if('user_log.PRIMARY' in expstr):
        print('issue in id')

    if('user_log.name' in expstr):
        print('same username')

    if('user_log.Email' in expstr):
        print('same email id')

    print(e)

mydb.commit()
