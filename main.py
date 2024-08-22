import logging
from niconico import NicoNico
from fastapi import FastAPI
import uuid
from BunnyCDN.Storage import Storage 
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

client = NicoNico()

email = os.environ.get("NICONICO_EMAIL")
password = os.environ.get("NICONICO_PASSWORD")
bunnyKey = os.environ.get("BUNNY_API_KEY")
zoneName = os.environ.get("BUNNY_STORAGE_ZONE")
region = os.environ.get("BUNNY_STORAGE_REGION")
baseURL = os.environ.get("DOWNLOAD_BASE_URL")

print(email, password, bunnyKey)

client.login_with_mail(email, password)

storage = Storage(bunnyKey, zoneName, region)

@app.get("/meta/{video_id}")
def read_item(video_id: str):
    try:
        meta = client.video.watch.get_watch_data(video_id)
        title = meta.video.title
        image = meta.video.thumbnail.player
        return {"title": title, "image": image}
    except Exception as e:
        return {"error": str(e)}

@app.post("/download/{video_id}")
def read_item(video_id: str):
    try:
        meta = client.video.watch.get_watch_data(video_id)
        outputs = client.video.watch.get_outputs(meta)
        output_label = next(iter(outputs))

        randomUUID = str(uuid.uuid4())

        downloaded_path = client.video.watch.download_video(meta, output_label, randomUUID+".%(ext)s")
        print(downloaded_path)
        storage.PutFile(downloaded_path, storage_path="videos/"+downloaded_path)
        url = baseURL + "videos/" + downloaded_path
        os.remove(downloaded_path)
        return {"url": url}
    except Exception as e:
        return {"error": str(e)}

