import boto3
from io import BytesIO
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pyglet
import speech_recognition as sr
import pyrebase

arr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
       's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

firebaseConfig = {
   #Contains API info
}

firebase = pyrebase.initialize_app(firebaseConfig)

BUCKET_NAME = 'signtranslator'  # replace with your bucket name
s3 = boto3.client('s3')
m = sr.Recognizer()
resource = boto3.resource('s3')


class guestUser:
    folder = ""
    bucket = resource.Bucket(BUCKET_NAME)
    KEY = ""
    text_input = ""
    dir_letters = 'common/letters/'

    def show_image(self, image_object, type):
        image = mpimg.imread(BytesIO(image_object.get()['Body'].read()), type)
        plt.imshow(image)
        plt.pause(0.05)

    def show_letters(self, text):
        for i in range(len(text)):
            if text[i] in arr:
                address = self.dir_letters + text[i] + '.jpg'
                try:
                    image_object = self.bucket.Object(address)
                    self.show_image(image_object, 'jpg')

                except Exception as e:
                    print(e)
            elif text[i] == '.' or text[i] == ' ':
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

    def direct_show_sign(self, image_object):  # Doesnt work
        file_data = image_object.get()['Body'].read()
        '''image = mpimg.imread(BytesIO(image_object.get()['Body'].read()), 'gif')    #This only shows single frame
        imgplot = plt.imshow(image)
        plt.show(imgplot)
        '''
        self.show_gif(file_data)
        print(type(file_data))

    def get_objects(self):
        try:
            self.listen_input()
        except:
            print("Try again")
            return
        self.KEY += self.text_input
        try:
            self.show_letters(self.text_input)
        except:
            print("Token may have expired, try again ")

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


class registeredUser(guestUser):
    def __init__(self, name):
        self.folder = name + '/'

    def get_objects(self):
        try:
            self.listen_input()
        except:
            print("Try again")
            return
        self.KEY = self.folder + self.text_input + ".gif"
        choice = 0
        # image_object = self.bucket.Object(self.KEY)
        try:
            resource.Bucket(BUCKET_NAME).download_file(self.KEY, 'my_image.gif')  # To download gif from cloud
            self.show_gif('my_image.gif')
            choice = 0

        except:
            choice = 1

        if choice == 1:
            try:
                self.show_letters(self.text_input)
            except:
                print("Token may have expired, try again ")

    def put_object(self, filedir):
        dir = self.folder + filedir
        client = boto3.client('s3')
        client.upload_file(filedir, BUCKET_NAME, dir)

class admin(guestUser):

    def put_object(self, filedir):
        dir = self.folder + filedir
        client = boto3.client('s3')
        client.upload_file(filedir, BUCKET_NAME, dir)


class system:
    username = ""
    password = ""
    auth = firebase.auth()

    def sign_in(self):
        self.username = input("Enter your email: ")
        self.password = input("Enter your password: ")
        choice = 3
        try:
            self.user = self.auth.sign_in_with_email_and_password(self.username, self.password)
            print("Logged-in successfully")
            return registeredUser(self.username.partition('@')[0])
        except:
            choice = int(input("Wrong password:\n 1. Try again\n 2. Register\n 3. Login as guest user\n"))

        if choice == 1:
            return self.sign_in()
        elif choice == 2:
            obj = self.sign_up()
            return obj
        elif choice == 3:
            return guestUser()

    def sign_up(self):
        print("Register user")
        self.username = input("Enter your email: ")
        self.password = input("Enter your password: ")
        try:
            self.user = self.auth.create_user_with_email_and_password(self.username, self.password)
            print("User registered successfully")
            return registeredUser(self.username.partition('@')[0])
        except:
            print("Already registered user")
            return -1

def main():
    u1 = system()

    choice = int(input("Already registered ? \n 1.Yes \n 2.No \n 3.Exit \n "))
    obj = -1
    if choice == 1:
        obj = u1.sign_in()
    elif choice == 2:
        choice2 = int(input("Login as guest ? \n 1.Yes \n 2.No \n 3.Exit \n"))

        if choice2 == 1:
            print("Logged in as guest")
            obj = guestUser()
        elif choice2 == 2:
            obj = u1.sign_up()
        else:
            print("Error occurred")
    else:
        print("Try again")

    if obj != -1:
        choice3 = int(input(" 1.Speech to sign translation \n 2.Add signs to database \n 3.Exit \n"))
        if choice3 == 1:
            obj.get_objects()
        elif choice3 == 2:
            print("Function not available yet")
    else:
        print("Not a valid user")


if __name__ == "__main__":
    main()
