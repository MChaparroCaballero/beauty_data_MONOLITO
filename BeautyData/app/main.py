from fastapi import FastAPI
app= FastAPI()
@app.get("/ping")
def ping():
    return {"message" :"pong"}


@app.get("/")
def holla_mundo():
    return{"message": "Holla mundo"}