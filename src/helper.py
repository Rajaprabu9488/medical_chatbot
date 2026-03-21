import json
import os
import uuid 
import random
import secrets
from datetime import timedelta
from datetime import datetime
import redis
import bcrypt
import subprocess
from dotenv import load_dotenv
import mysql.connector as sql

redis_object = None
mydb = None
cursor = None
sessions:dict = {}

load_dotenv()

PEPPER = os.getenv("PEPPER_TEXT")

def initial_loader():
    global redis_object, mydb, cursor

    redis_object = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
    )

    try:
        redis_object.ping()
        print("already running")
    except:
        subprocess.run([r"C:\Users\My-PC\OneDrive\Desktop\medical-chatbot\src\start_redis.bat"],shell=True)

    try:
        mydb = sql.connect(
            host='localhost',
            user='root',
            password='Raja@2005',
            database='project'
        )

        cursor = mydb.cursor()
    except Exception as e:
        print('database is not connected....')
    
    # await start_cleanup()

# ---------------------------------------------------------------------
#                         session controller
# --------------------------------------------------------------------

def user_id_provider():
    return str(uuid.uuid4())

def chat_id_provider():
    return str(uuid.uuid4())

# async def cleanup_sessions():
#     while True:
#         now = datetime.now()

#         for session_id in list(sessions.keys()):
#             if now - sessions[session_id] > timedelta(minutes=10):
#                 clear_cache(session_id)
#                 del sessions[session_id]

#         await asyncio.sleep(300)


# async def start_cleanup():
#     asyncio.create_task(cleanup_sessions())

def update_session(session_id):
    session_cache=redis_object.get(session_id)
    if(session_cache is not None):
        redis_object.expire(session_id,600)
    else:
        redis_object.setex(session_id,600,'active')


def search_session_id(session_id:str):
    if(session_id is None):
        return False
    
    active_session = redis_object.get(session_id)
    if(active_session == 'active'):
        redis_object.expire(session_id,600)
        return True
    return False

def generate_OTP():
    return ''.join(random.choices('0123456789',k=6))

# ---------------------------------------------------------------------
#                 database usage
# --------------------------------------------------------------------
def hash_password(password: str):

    password_peppered = (password + PEPPER).encode()

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(password_peppered, salt)

    return hashed

def verify_password(password: str, stored_hash: bytes):
    password_peppered = (password + PEPPER).encode()
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_peppered, stored_hash)

def generate_reset_secret():
    return secrets.token_urlsafe(32)


def Redis_uploader(session_id,question, answer):

    history=redis_object.get(f'chat:{session_id}')

    if history:
        history = json.loads(history)
    else:
        history = []

    new_data={'question' : question, 'answer': answer}

    history.append(new_data)
    history = history[-5:]

    redis_object.set(f'chat:{session_id}',json.dumps(history))


 
def clear_cache(session_id):
    redis_object.delete(session_id)
    

def upadate_user(username:str , email:str , password:str):
    user_id = user_id_provider()
    chat_session_id = chat_id_provider()
    username = username.lower()
    email = email.lower()
    password = hash_password(password)

    cursor.execute('SELECT user_id FROM user_log WHERE name=%s AND Email=%s LIMIT 1',(username,email))
    result = cursor.fetchone()
    if result:
        raise Exception('User Already Exists')
    
    try:
        cursor.execute("INSERT INTO user_log VALUES(%s , %s , %s ,%s)",(user_id,username,email,password))
    
    except Exception as e:
        expstr = str(e)
        if('user_log.PRIMARY' in expstr):
            raise Exception('Issue In ID Generation : Submit Again')

        if('user_log.name' in expstr):
            raise Exception('Username Already Exists')

        if('user_log.Email' in expstr):
            raise Exception('E-mail ID Already Exists')

    mydb.commit()

    return [user_id,chat_session_id]

def find_Email(username:str):
    cursor.execute('SELECT Email FROM user_log WHERE name=%s LIMIT 1',([username]))
    result = cursor.fetchone()
    if(result is None):
        raise Exception("User Not Found")
    
    reset_key= generate_reset_secret()
    otp = generate_OTP()

    store_otp_key={'reset_key':reset_key,'otp':otp}
    redis_object.setex(result[0],600,json.dumps(store_otp_key))

    return [result[0],reset_key]


def validate_user(username:str, password:str):
    username = username.lower()
    chat_session_id = chat_id_provider()
    cursor.execute('SELECT user_id,Email,password FROM user_log WHERE name=%s LIMIT 1',([username]))
    result = cursor.fetchone()
    if result is None:
        raise Exception('User Not Exists, Please sign in')
    
    if(verify_password(password, result[2])):
        return [*result[:-1],chat_session_id]
    else:
        raise Exception('Invalid Password')



# --------------------------------------------------------------------
#                 query usage
# --------------------------------------------------------------------


def past_string_structure(content):

    past_string_stuct=f"""
    question:
    {content['question']}
    answer:
    {content['answer']}
    """

    return str(past_string_stuct)

def question_retriver(session_id, question):
    question_string=""
    queue = redis_object.get(f'chat:{session_id}')
    if queue:
        queue = json.loads(queue)
    else:
        queue = []
    for quest in queue:
        question_string += quest['question']
        question_string += ", "

    question_string +=question

    return question_string

def content_retriver(session_id):
    final_string=""
    queue = redis_object.get(f'chat:{session_id}')
    if queue:
        queue = json.loads(queue)
    else:
        queue = []
    for quest in queue:
        temp = past_string_structure(quest)
        final_string += temp

    return final_string




if __name__=='__main__':

    initial_loader()
    demo_id=chat_id_provider()
    ss_demo_id=chat_id_provider()
    # user_demo_id=upadate_user('RAJAPRABHU','raja@123','2345')
    # print(content_retriver(demo_id))
    # print("user id:",user_demo_id)
    # print("chat id:",demo_id)
    # sessions[demo_id]=datetime.now()
    # update_session(demo_id)
    # print(search_session_id(demo_id))
    # print(redis_object.ttl(demo_id))
    # print(sessions)

    # print(validate_user('rajaprabhu','94889'))

    # email= find_Email('rajaprabhu')
    # print(email)

    # x=json.loads(redis_object.get(email[0]))
    # print(f"reset key: {x['reset_key']}, otp : {x['otp']}")

    # print(generate_OTP())

    # scrt=generate_reset_secret()
    # print(scrt)

