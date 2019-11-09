import boto3
from io import BytesIO
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import speech_recognition as sr
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pyglet

arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
       's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

BUCKET_NAME = 'signtranslator'  # replace with your bucket name
s3 = boto3.client('s3')
m = sr.Recognizer()
resource = boto3.resource('s3')

class globaluser:
    bucket = resource.Bucket(BUCKET_NAME)
    KEY = ""
    text_input = []
    dir_letters = 'common/letters/'

    def show_image(self, image_object, type):
        image = mpimg.imread(BytesIO(image_object.get()['Body'].read()), type)
        plt.imshow(image)
        plt.pause(0.05)

    def show_letters(self, text):
        for i in range(len(text)):
            if (text[i] in arr):
                address = self.dir_letters + text[i] + '.jpg'
                try:
                    image_object = self.bucket.Object(address)
                    self.show_image(image_object, 'jpg')

                except Exception as e:
                    print(e)
            elif (text[i] == '.' or text[i] == ' '):
                plt.pause(0.1)
                plt.close()
            else:
                continue

    def show_gif(self, dir):
        animation = pyglet.image.load_animation(dir)
        sprite = pyglet.sprite.Sprite(animation)
        w = sprite.width
        h = sprite.height
        window = pyglet.window.Window(width=w, height=h)

        @window.event
        def on_draw():
            sprite.draw()

        pyglet.app.run()

    def get_objects(self, filename):
        self.KEY += filename  # replace with your object key
        image_object = self.bucket.Object(self.KEY)
        type = "gif"
        try:
            self.showsign(image_object, type)
        except:
            print("The object does not exist.")

    def put_objects(self, dir):
        client = boto3.client('s3')
        client.upload_file(dir, BUCKET_NAME, dir)

    def search_text(self):
        self.get_objects(self.text)

    def listen_input(self):
        with sr.Microphone() as source:
            m.adjust_for_ambient_noise(source)
            print('Say Something')
            get = m.listen(source)
        try:
            self.text_input = m.recognize_google(get)
            print('You said ' + self.text_input)

        except Exception:
            print('Could not recognise')


class loggedUser(globaluser):
    def __init__(self, name):
        self.folder = name + '/'

    def get_objects(self, text_input):
        # self.listen_input()
        self.KEY = self.folder + text_input  # replace with your object key
        image_object = self.bucket.Object(self.KEY)
        try:
            resource.Bucket(BUCKET_NAME).download_file(self.KEY + ".gif", 'my_image.gif')
            self.show_gif('my_image.gif')

        except:
            print("The object does not exist.")
            self.show_letters(text_input)

    def put_object(self, filedir):
        dir = self.folder + filedir
        client = boto3.client('s3')
        client.upload_file(filedir, BUCKET_NAME, dir)


def main():
    u1 = loggedUser("user1")
    text = input("Enter text you want to find: ")
    u1.get_objects(text)


if __name__ == "__main__":
    main()
