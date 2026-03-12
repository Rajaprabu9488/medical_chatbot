from fastapi import FastAPI, UploadFile, File, Form, Request 
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from embedding_and_llm import rag_pipeline,rag_initial_loader
from audio_to_text import audio_initial_loader,audio_transcription
from helper import initial_loader, user_id_provider,update_session
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
    os.makedirs("./temp/audio", exist_ok=True)
    os.makedirs("./temp/image", exist_ok=True)


@app.get("/api/session-start")
async def session_start():
    await initial_loader()
    print('new connection')
    session_id=user_id_provider()
    update_session(session_id)
    return {"connection": session_id }


@app.post("/api/session-active")
async def close_session(request:Request):
    data = await request.json()
    session_id = data["session_id"]
    print(session_id)
    update_session(session_id)
    return {'connection':'keep-alive'}



@app.post("/input/")
async def handle_input(
    text:Optional[str]=Form(None),
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):

    result=[]

    if audio is not None:

        audio_path=f'./temp/audio/{audio.filename}'

        with open(audio_path,'wb') as temp:
            shutil.copyfileobj(audio.file, temp)

        audio_text=audio_transcription(audio_path)
        result.append(audio_text)

    if image is not None:
        image_path=f'./temp/image/{image.filename}'

        with open(image_path,'wb') as temp:
            shutil.copyfileobj(image.file, temp)

        image_text=audio_transcription(image_path)
        result.append(image_text)

    if text:
        result.append(text)

    final_combine_text='\n\n'.join(result)
    return StreamingResponse(
        rag_pipeline(final_combine_text),
        media_type="text/plain"
    )

if __name__=='__main__':
    print("server started")
    uvicorn.run(app,port=3000)
    print("server stoped")
