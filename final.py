from tkinter import *
import cv2
import face_recognition as fr
import numpy as np
import face_recognition
from datetime import datetime
from PIL import Image,ImageTk
from tkinter import filedialog
import os,shutil

#open the excel sheet
def openExcel():
    os.startfile("attend1.csv")
#clear the excel sheet
def clear():
    filename = "attend1.csv"
    f = open(filename, "w+")
    f.close()
#live attendance
def Live_Attendance():
    #path
    path = 'ImageBasic'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)
    #encoding
    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList
    #mark the attendance in attend1.csv
    def markAttendance(name):
        with open('attend1.csv', 'r+') as f:
            myDatalist = f.readlines()
            nameList = []
            print(myDatalist)
            for line in myDatalist:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now=datetime.now()
                dtstring=now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtstring}')


    encodeListKnown = findEncodings(images)
    #print('encoding complete')

    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()

        cv2.imshow("Test", img)

        if not ret:
            break

        k = cv2.waitKey(1)

        if k % 256 == 27:
            # For Esc key to exit
            print("Close")
            break
        elif k % 256 == 32:
            #space key to capture the attendance
            success, img = cap.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    print(name)

                    y1, x2, y2, x1 = faceLoc
                    # y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
        cap.release
        cv2.destroyAllWindows


#upload attendance
def Upload_Attendance():
    #open file dialog
    root.filename = filedialog.askopenfilename(initialdir="/gui/images", title="Select A file",filetypes=(("png", "*.png"), ("jpg", "*.jpg")))
    def get_encoded_faces():

        encoded = {}

        for dirpath, dnames, fnames in os.walk("./ImageBasic"):
            for f in fnames:
                if f.endswith(".jpg") or f.endswith(".png"):
                    face = fr.load_image_file("ImageBasic/" + f)
                    encoding = fr.face_encodings(face)[0]
                    encoded[f.split(".")[0]] = encoding

        return encoded

    def unknown_image_encoded(img):

        face = fr.load_image_file("ImageBasic/" + img)
        encoding = fr.face_encodings(face)[0]

        return encoding
    #attendance
    def markAttendance(name):
        with open('attend1.csv', 'r+') as f:
            myDatalist = f.readlines()
            nameList = []
            print(myDatalist)
            for line in myDatalist:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtstring = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtstring}')

    def classify_face(im):

        faces = get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())

        img = cv2.imread(im, 1)


        face_locations = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

        face_names = []
        for face_encoding in unknown_face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(faces_encoded, face_encoding)
            name = "Unknown"

            # use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Draw a box around the face
                cv2.rectangle(img, (left - 20, top - 20), (right + 20, bottom + 20), (255, 0, 0), 2)

                # Draw a label with a name below the face
                cv2.rectangle(img, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 2)
                markAttendance(name)

        # Display the resulting image

        while True:

            cv2.imshow('Video', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return face_names

    print(classify_face(root.filename))
#new window for database
def open_window():
    top=Toplevel()
    img1 = Label(top, image=render)
    img1.place(x=0, y=0)
    top.geometry("400x750+120+100")
    heading = Label(top, text="Enter your name",bg="yellow",font="Times 16 bold").pack(padx=10,pady=20)
    name1 = StringVar()
    #get the name
    entry_box = Entry(top, textvariable=name1, width=20,font="Times 20 bold").pack(padx=10,pady=20)
    top.iconbitmap(r'button/test.ico')
    def done():
        #live photo
        import cv2

        cam = cv2.VideoCapture(0)
        while True:
            ret, img = cam.read()

            cv2.imshow("Test", img)

            if not ret:
                break

            k = cv2.waitKey(1)

            if k % 256 == 27:
                # For Esc key
                print("Close")
                break
            elif k % 256 == 32:
                # For Space key

                print("Image " + str(name1.get()) + "saved")#photo saved
                file = 'C:/Users/ramna/PycharmProjects/face/ImageBasic/' + str(name1.get()) + '.jpg'
                cv2.imwrite(file, img)

        cam.release
        cv2.destroyAllWindows


    btn = Button(top, image=img5, command=done).pack()



    def photo():
        #open filedialog and move the photo to the required location
        root.filename = filedialog.askopenfilename(initialdir="/gui/images", title="Select A file",
                                                   filetypes=(("png", "*.png"), ("jpg", "*.jpg")))
        os.chdir('c:\\')
        os.system('C:/Users/ramna/PycharmProjects/face/ImageBasic')
        shutil.move(root.filename, 'C:/Users/ramna/PycharmProjects/face/ImageBasic')


    btn = Button(top, image=img4, command=photo).pack(padx=10,pady=40)
    btn1=Button(top,image=img6,command= top.destroy).pack()

root=Tk()
root.title("Attendance System")
root.iconbitmap(r'button/test.ico')

img4 = PhotoImage(file='button/UploadNewPhoto.png')
img5 = PhotoImage(file='button/TakePhoto.png')
img6 = PhotoImage(file='button/CLOSE.png')

root.geometry("400x750+120+120")

load=Image.open('button/background.png')
render=ImageTk.PhotoImage(load)
img1=Label(root,image=render)
img1.place(x=0,y=0)

img2=PhotoImage(file='button/Live_Attendance.png')
myButton=Button(root,image=img2,command=Live_Attendance)
myButton.place(x=130,y=100)

img3=PhotoImage(file='button/UploadAttendance.png')
myButton3=Button(root,image=img3,bd=0,command=Upload_Attendance)
myButton3.place(x=130,y=200)

img7=PhotoImage(file='button/UploadNewPhoto.png')
myButton3=Button(root,image=img7,bd=0,command=open_window)
myButton3.place(x=130,y=300)

img8=PhotoImage(file='button/showattendance.png')
myButton3=Button(root,image=img8,bd=0,command=openExcel)
myButton3.place(x=130,y=400)

img9=PhotoImage(file='button/clear.png')
myButton3=Button(root,image=img9,bd=0,command=clear)
myButton3.place(x=130,y=500)

btn1=Button(root,image=img6,command= root.destroy)
btn1.place(x=180,y=600)

root.mainloop()