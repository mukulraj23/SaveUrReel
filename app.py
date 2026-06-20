from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import time
import threading


app = Flask(__name__)


DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)



# AUTO DELETE AFTER 2 MINUTES

def auto_delete_files():

    while True:

        try:

            now = time.time()


            for file in os.listdir(DOWNLOAD_FOLDER):

                path = os.path.join(
                    DOWNLOAD_FOLDER,
                    file
                )


                if os.path.isfile(path):


                    created_time = os.path.getctime(path)



                    if now - created_time > 120:


                        os.remove(path)

                        print(
                            "Deleted:",
                            file
                        )



        except Exception as e:

            print(
                "Delete error:",
                e
            )



        time.sleep(30)






@app.route("/")
def home():

    return render_template(
        "index.html"
    )







@app.route("/download", methods=["POST"])
def download():


    url = request.form["url"]


    filename = str(uuid.uuid4())



    try:



        # GET INFO FIRST

        with yt_dlp.YoutubeDL({}) as ydl:


            info = ydl.extract_info(

                url,

                download=False

            )




        has_video = False



        if "formats" in info:


            for f in info["formats"]:


                if f.get("vcodec") != "none":


                    has_video = True

                    break





        # IMAGE POST

        if not has_video:



            ext = info.get(
                "ext",
                "jpg"
            )



            options = {


                "format":"best",


                "outtmpl":

                f"{DOWNLOAD_FOLDER}/{filename}.%(ext)s"


            }




        # VIDEO REEL / VIDEO POST

        else:



            ext = "mp4"



            options = {



                "format":

                "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best",



                "merge_output_format":

                "mp4",



                "outtmpl":

                f"{DOWNLOAD_FOLDER}/{filename}.mp4"



            }






        # DOWNLOAD

        with yt_dlp.YoutubeDL(options) as ydl:


            ydl.download([url])






        file_path = (

            f"{DOWNLOAD_FOLDER}/{filename}.{ext}"

        )





        return send_file(


            file_path,


            as_attachment=True,


            download_name=

            f"SaveUrReel.{ext}"

        )






    except Exception as e:



        return str(e)







if __name__ == "__main__":



    cleanup_thread = threading.Thread(

        target=auto_delete_files

    )


    cleanup_thread.daemon = True


    cleanup_thread.start()




    app.run(
        debug=False
    )