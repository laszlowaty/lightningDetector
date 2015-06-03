import Image
import urllib
from time import sleep, time
from datetime import datetime
import sys
import Tkinter
import threading


if sys.platform == 'win32':
    import winsound


__author__ = "konrad.wybraniec@gmail.com"


def log(target, info):
    date = datetime.now()
    date = ("%s-%s-%s,%s:%s\t" % (date.year, date.month, date.day,
                                  date.hour, date.minute))
    file = open(target+".txt", "a")
    text = date + info+ "\n"
    file.write(text)
    file.close


class Config:
    default_delay = 60 #czestosc sprawdzanie czy pojawila sie blyskawica. Podawane w sekundach
    current_delay = default_delay #in seconds
    warning_bg_color = "red" # kolor okienka z ostrzezeniem
    destinations = {
                    "suhora": ((440, 475, 480, 515), #wymiary w pixelach poszukiwanego obszaru. Odpowiednio:
                               #lewy gorny rog, gorna krawedz, prawy dolny rog, dolna krawedz. Wyszukiwane na obrazku z blitzortung
                               ("http://images.blitzortung.org/Images/image_b_pl.png"), #link zeby pobrac obrazek z blitzortung. 
                               (255, 255, 255), #kolor na obrazku, na ktory reaguje program. Bazowo bialy
                               ('suhora_temp.png'), #Pod ta nazwa bedzie zapisany obrazek pobrany w blitzortung
                               ('suhora.png'), # Pod ta nazwa bedzie zapisany obszar wyciety z obrazka pobranego z blitzortung.
                               ),
                    "krakow": ((430,435, 475, 475),
                               ("http://images.blitzortung.org/Images/image_b_pl.png"),
                               (255, 255, 255),
                               ('krakow_temp.png'),
                               ('krakow.png')
                               ),
                    "test":   ((0, 0, 925, 925),
                               ("http://images.blitzortung.org/Images/image_b_pl.png"),
                               (255, 255, 255),
                               ('test_temp.png'),
                               ('test.png')),
                    }
    

def play_alert():
    """it takes ~8sec for default file"""
    if sys.platform == 'win32':
        winsound.PlaySound('alarm.wav', winsound.SND_FILENAME)
    else:
        print "Couldn't play music."

    
class Warnings(object):
    
    def __init__(self, img):
        self.running = False
        self.start_warnings()
    
    def quit(self):
        self.running = False
        Config.current_delay = 1260 # czas czekania po kliknieciu w okienko z ostrzezeniem
        self.root.destroy()
    
    def create_box(self):
        self.root = Tkinter.Tk()
        self.root.title("WARNING!")
        self.root.geometry("300x300")
        frame = Tkinter.Frame(self.root, height=300, width=300)
        frame.pack_propagate(0) # don't shrink
        frame.pack()    
        button = Tkinter.Button(frame, text = "WARNING!\nLIGHTNINGS DETECTED!\npress here to close window",
                                     command = self.quit, bg = "red",
                                     activebackground = "red")
        button.pack(fill=Tkinter.BOTH, expand=1)
        self.root.focus_set()
        threading.Thread(target=play_alert).start()
        self.root.after(60000, self.root.destroy) # CZAS ISTNIENIA OKIENKA Z OSTRZEZENIEM W MS. Okienko odswieza sie co
        # minute i odtwarza dzwiek
        self.root.mainloop()
    
    def start_warnings(self):   
        self.running = True
        timer = time()
        while self.running:
            self.create_box()
            if time() - timer >= 1260: # 21 minut istnienia okienka z dzwiekiem
                self.running = False

class Check(object):
    
    @staticmethod
    def cut_image(img, location):
        box = (location[0])
        running = True
        while running:
            try:
                c = img.crop(box)
            except IOError:
                print "IOERROR"
                log("errors", "IOERROR")
            else:
                return c
    
    @staticmethod
    def find_pixels(image, color):
        colors = image.getcolors()
        pixels = 0
        for c in colors:
            if color == c[1]: 
                pixels += c[0]
        return pixels
    
    def __init__(self):
        self.latest_img = None
        self.previous_img = None
        self.location_name = None
        self.location = None
        
    def set_location(self):
        try:
            self.location_name = sys.argv[1]
            self.location = Config.destinations[self.location_name]
        except (KeyError, IndexError):
            print("Incorrect localization. Possible localizations: %s" % Config.destinations.keys())
            sys.exit(1) 
    
    def get_image(self):
        try:
            self.latest_img = urllib.urlopen(self.location[1]).read()
        except:
            print("Error, ignoring")
        open(self.location[3], "wb").write(self.latest_img)
        try:
            self.latest_img = Image.open(self.location[3])
        except IOError:
            print("Error, ignoring")
        self.latest_img = Check.cut_image(self.latest_img, self.location)
        self.latest_img.save(self.location[4])
        
    def start_checking(self):
        while True:
            Config.current_delay = Config.default_delay
            date = datetime.now()
            date = ("%s-%s-%s,%s:%s\t" % (date.year, date.month, date.day,
                                  date.hour, date.minute))
            self.get_image()
            self.pixels = Check.find_pixels(self.latest_img, self.location[2])
            log(self.location_name, str(self.pixels/13))            
            print("%s: %s - possible %s lightnings in last 20 minutes. Pixels: %s" % (date,
                                   self.location_name,
                                   self.pixels/13,
                                   self.pixels))
            if self.pixels > 0:
                Warnings(self.latest_img)
            sleep(Config.current_delay)



if __name__ == '__main__':
    check = Check()
    check.set_location()
    check.start_checking()






