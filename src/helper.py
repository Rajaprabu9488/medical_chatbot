import json
import uuid
import asyncio
from datetime import timedelta
from datetime import datetime

queue:list = []
cache:list = []
sessions:dict = {}

async def initial_loader():

    global queue, cache

    try:
        with open('./src/cache_.json','r') as file:
            cache = json.load(file)
        queue = cache[-5:]

    except:
        print("error in file load")
    
    await start_cleanup()


def user_id_provider():
    return uuid.uuid4()

async def cleanup_sessions():
    while True:
        now = datetime.now()

        for session_id in list(sessions.keys()):
            if now - sessions[session_id] > timedelta(minutes=10):
                clear_cache()
                del sessions[session_id]

        await asyncio.sleep(300)


async def start_cleanup():
    asyncio.create_task(cleanup_sessions())

def update_session(session_id):
    sessions[session_id] = datetime.now()
    print(sessions)

def past_string_structure(content):

    past_string_stuct=f"""
    question:
    {content['question']}
    answer:
    {content['answer']}
    """

    return str(past_string_stuct)

def past_question(content):
    past_string_stuct=f"""
    {content['question']}
    """

    return str(past_string_stuct)

def content_retriver():
    final_string=""

    for quest in queue:
        temp = past_string_structure(quest)
        final_string += temp

    return final_string



def json_uploader(question, answer):
    global queue, cache
    
    new_data={'question' : question, 'answer': answer}

    cache.append(new_data)

    queue = cache[-5:]

    with open('./src/cache_.json','w') as file:
        json.dump(cache, file, indent=4)

 
def clear_cache():
    with open('./src/cache_.json','w') as file:
        json.dump([], file, indent=4)


if __name__=='__main__':

    initial_loader()

    print(content_retriver())