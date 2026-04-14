from fastapi import FastAPI, UploadFile, File, Form, Request , HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from embedding_and_llm import rag_pipeline,rag_initial_loader
from audio_to_text import audio_initial_loader,audio_transcription
from image_to_text import ocr_initial_loader, ocr_pipeline
from helper import initial_loader,update_session,chat_id_provider, search_session_id,upadate_user,validate_user , find_Email,verify_OTP ,update_password, user_profile,edit_user_profile,signup_verified
import warnings
from typing import Optional
import shutil
import os



warnings.filterwarnings('ignore')

app=FastAPI()

app.add_middleware(CORSMiddleware,allow_origins=["*"],
                   allow_methods=['*'],
                   allow_headers=['*'],
                   allow_credentials=True)



@app.on_event("startup")
async def startup_event():
    rag_initial_loader()
    audio_initial_loader()
    ocr_initial_loader()
    initial_loader()
    os.makedirs("./temp/audio", exist_ok=True)
    os.makedirs("./temp/image", exist_ok=True)



@app.get("/api/session-start")
async def session_start():
    print('new connection')
    session_id=chat_id_provider()
    update_session(session_id)
    return {"connection": session_id }


@app.post("/api/session-active")
async def close_session(request:Request):
    data = await request.json()
    if data["session_id"] is None:
        raise HTTPException(status_code=401,detail="refresh page to get token")
    session_id = data["session_id"]
    update_session(session_id)
    return {'connection':True}



@app.post("/auth/signup/")
async def signup(username:Optional[str] = Form(None),
        email:Optional[str] = Form(None),
        password: Optional[str] = Form(None)                 
):
    try:
        user_id = upadate_user(username,email,password)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    return {'identity': user_id,"usermail": email}

@app.post("/auth/signup_verification/")
async def signup_verification(userid:Optional[str]=Form(None),mail:Optional[str]=Form(None),OTP:Optional[str]=Form(None)):
    try:
        result = signup_verified(userid,OTP)
        return result
    except Exception as e:
        if("Request Timeout" in str(e)):
            raise HTTPException(status_code=401,detail=str(e))
        if("Too many attempts" in str(e)):
            raise HTTPException(status_code=429, detail=str(e))
        
        raise HTTPException(status_code=404,detail=str(e))





@app.post("/auth/login/")
async def signup(username:Optional[str] = Form(None),
        password: Optional[str] = Form(None)                 
):
    try:
        user_id = validate_user(username,password)
        update_session(user_id[2])
        return {'identity': user_id[0],"session":user_id[2] ,"username": username,'usermail':user_id[1] }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post('/auth/get_usermail/')
async def get_usermail(username:Optional[str]=Form(None)):
    try:
        usrmail = find_Email(username)
    except Exception as e:
        if("Too many attempts" in str(e)):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"usrmail":usrmail[0], "reset_key":usrmail[1]}

@app.post('/auth/OTP_verification/')
async def otp_verification(mail:Optional[str]=Form(None),reset_key:Optional[str]=Form(None) ,OTP:Optional[str]=Form(None)):
    
    try:
        success_data = verify_OTP(mail,reset_key,OTP)
    except Exception as e:
        if("Too many attempts" in str(e)):
            raise HTTPException(status_code=429, detail=str(e))

        raise HTTPException(status_code=401, detail=str(e))
    
    return {'reset_key':success_data[0],"content":success_data[1]}


@app.post('/auth/reset_password/')
async def reset_password(usrmail:Optional[str]=Form(None), reset_key:Optional[str]=Form(None), new_password:Optional[str]=Form(None)):
    try:
        status = update_password(usrmail, reset_key,new_password)

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    return {'reset_status': status} 

@app.post('/auth/Edit_profile/')
async def Edit_profile(user_id:Optional[str]=Form(None)):
    if user_id is None:
        raise HTTPException(status_code=401,detail='user_id did not provided')
    try:
        
        user_details = user_profile(user_id)
        return user_details
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))

@app.post('/auth/profile_update/')
async def update_user_profile(userid:Optional[str]=Form(None) , username:Optional[str]=Form(None) , Email:Optional[str]=Form(None) , key:Optional[str]=Form(None)):
    try:
        data = edit_user_profile(userid,username,Email,key)
        return data
    except Exception as e:
        if("Too many change" in str(e)):
            raise HTTPException(status_code=429, detail=str(e))
        if("unauthorized request" in str(e)):
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=404,detail=str(e))
    
     

@app.post("/input/")
async def handle_input(
    user_id:Optional[str]=Form(None),
    session_id:Optional[str]=Form(None),
    text:Optional[str]=Form(None),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    if(not search_session_id(session_id)):
        print(search_session_id(session_id))
        raise HTTPException(status_code=404,detail='session is invalid, please reload the page')
    
    result=[]

    if image is not None:
        image_path=f'./temp/image/{image.filename}'

        with open(image_path,'wb') as temp:
            shutil.copyfileobj(image.file, temp)
        try:
            image_text=ocr_pipeline(image_path)
            result.append(image_text)
        except Exception as e:
            raise HTTPException(status_code=503,detail='OCR failed to Connect, try again')

    if audio is not None:

        audio_path=f'./temp/audio/{audio.filename}'

        with open(audio_path,'wb') as temp:
            shutil.copyfileobj(audio.file, temp)
        try:
            audio_text=audio_transcription(audio_path)
            result.append(audio_text)
        except Exception as e:
            raise HTTPException(status_code=503,detail='STT failed to Connect, try again')

    if text:
        result.append(text)

    final_combine_text='\n\n'.join(result)
    return StreamingResponse(
        rag_pipeline(user_id,session_id,final_combine_text),
        media_type="text/plain"
    )

if __name__=='__main__':
    print("server started")
    uvicorn.run(app,port=3000)
    print("server stoped")
