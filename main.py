from pytube import YouTube
import firebase_admin
from firebase_admin import credentials, storage, firestore
import requests
import keys

link = 'BL8Oe9oh7mY'
cred = credentials.Certificate(keys.cred_certificate)
firebase_admin.initialize_app(cred, {'storageBucket': keys.storageBucket })


def download_upload(link):
    link = 'https://www.youtube.com/watch?v=' + link
    yt = YouTube(link)
    try:
# download the audio
        yt.streams.get_audio_only().download(filename=yt.video_id+'.mp4')

# get the meta data
        yt_data = {
            "title" : yt.title,
            "description" : yt.description,
            "length" : yt.length,
            "id" : yt.video_id,
            "thumbnail" : yt.thumbnail_url
        }

        print (yt_data)

# audio upload
        filePath = yt_data['id'] + '.mp4'
        fileName = 'audio/'+yt_data["id"]+'.mp4'

        db = firestore.client()
        bucket = storage.bucket()
        blob = bucket.blob(fileName)
        blob.upload_from_filename(filePath)
        blob.make_public()
        videoURL = blob.public_url

# download the thumbnail file
        img_data = requests.get(yt_data['thumbnail']).content
        with open(yt_data['id'] + '.jpg', 'wb') as handler:
            handler.write(img_data)

# thumbnail upload
        thumbnailPath = yt_data['id'] + '.jpg'
        thumbnailName = 'thumbnail/' + yt_data["id"] + '.jpg'

        blob = bucket.blob(thumbnailName)
        blob.upload_from_filename(thumbnailPath)
        blob.make_public()
        thumbnailURL = blob.public_url

# firestore upload
        data = {
            'video_description': yt_data['description'],
            'video_duration' : yt_data['length'],
            'video_file' : videoURL,
            'video_id' : yt_data['id'],
            'video_name': yt_data['title'],
            'video_thumbnail': yt_data['thumbnail']
        }
        doc_ref = db.collection('details').document(yt_data['id'])
        doc_ref.set(data)
 

    except Exception as e:
        print (e)


download_upload(link)







