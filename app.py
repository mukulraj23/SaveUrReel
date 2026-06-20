from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid
import time
import threading
import imageio_ffmpeg



app = Flask(__name__)



DOWNLOAD_FOLDER = "downloads"


os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)



ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()





# DELETE FILES AFTER 2 MINUTES

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


                    file_age = now - os.path.getctime(path)



                    if file_age > 120:


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


    url = request.form.get("url")


    filename = str(uuid.uuid4())



    try:


        # GET INFO

        with yt_dlp.YoutubeDL({}) as ydl:


            info = ydl.extract_info(
                url,
                download=False
            )



        is_video = False



        for f in info.get("formats", []):


            if f.get("vcodec") != "none":


                is_video = True

                break





        # VIDEO

        if is_video:


            output_file = (
                f"{DOWNLOAD_FOLDER}/{filename}.mp4"
            )


            options = {


                "format":
                "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best",



                "merge_output_format":
                "mp4",



                "ffmpeg_location":
                ffmpeg_path,



                "outtmpl":
                output_file

            }



            final_ext = "mp4"







        # IMAGE

        else:



            ext = info.get(
                "ext",
                "jpg"
            )



            output_file = (

                f"{DOWNLOAD_FOLDER}/{filename}.{ext}"

            )



            options = {


                "format":
                "best",



                "outtmpl":
                output_file


            }



            final_ext = ext





        # DOWNLOAD


        with yt_dlp.YoutubeDL(options) as ydl:


            ydl.download([url])







        return send_file(

            output_file,

            as_attachment=True,

            download_name=f"SaveUrReel.{final_ext}"

)






    except Exception as e:


        print(e)


        return str(e)









# START CLEANER THREAD

cleanup_thread = threading.Thread(

    target=auto_delete_files

)


cleanup_thread.daemon = True


cleanup_thread.start()








if __name__ == "__main__":


    app.run(
        debug=False
    )
