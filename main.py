from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font
from PIL import ImageTk, Image
from exif import Image as Exif
from pprint import pprint
import datetime
import bs4
import xml.etree.ElementTree as ET
import exifread


class App:
    def __init__(self):
        self.root = Tk()

    def set_window_properties(self):
        # Set window title
        self.root.title('GEO Picture')
        # Set window ico
        self.root.iconbitmap('assets/logo.ico')

        # Define title font
        self.title_font = Font(family='Helvetica', size=20)

    def create_widgets(self):
        # Configure grid
        self.root.grid_columnconfigure((0, 1), weight=1)

        # Create header frame
        self.header = ttk.Frame(self.root)
        self.header.grid(column=0, row=0, columnspan=2)

        # Create toolbox frame
        self.toolbox = Frame(self.root)
        self.toolbox.grid(column=0, row=1)

        # Create image preview frame
        self.preview = Frame(self.root)
        self.preview.grid(column=1, row=1)

        # Create canvas to display logo
        self.canvas = Canvas(self.header, width=150, height=150)
        self.canvas.grid(column=0, row=0, sticky=NSEW)

        # Load and resize logo
        self.logo = Image.open('assets/logo.png')
        self.logo = self.logo.resize((150, 150), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(self.logo)

        # Display logo on canvas
        self.canvas.create_image(150/2, 150/2, image=self.logo)

        # Add title on header
        self.title = ttk.Label(
            self.header, text="GEO Picture", font=self.title_font)
        self.title.grid(column=0, row=1)

        # Add title to toolbox
        self.toolbox_label = ttk.Label(
            self.toolbox, text="Toolbox", font=['TkDefaultFont', 15])
        self.toolbox_label.grid(column=0, row=0, columnspan=2)

        # Button to open image
        self.image_btn = ttk.Button(self.toolbox, text="Open image", command=self.open_image)
        self.image_btn.grid(column=0, row=1)

        # Button to bind gpx to image
        self.gpx_btn = ttk.Button(
            self.toolbox, text="Bind GPX", state=DISABLED, command=self.open_gpx)
        self.gpx_btn.grid(column=1, row=1)

        # Create progress bar for display steps of processing
        self.progress_bar = ttk.Progressbar(
            self.toolbox, orient=HORIZONTAL, length=150, mode='determinate')
        self.progress_bar.grid(column=0, row=2, columnspan=2, sticky=NSEW)

        # Separator between toolbox and preview
        self.separator = ttk.Separator(self.root, orient=VERTICAL)
        self.separator.grid(column=1, row=1)

        self.preview_title = ttk.Label(
            self.preview, text='Preview', font=['TkDefaultFont', 15])
        self.preview_title.grid(column=0, row=0, sticky=NSEW)

        # Canvas to have preview of choosen picture
        self.preview_canvas = Canvas(self.preview, width=300, height=300)
        self.preview_canvas.grid(column=0, row=1, sticky=NSEW)

        # Load image if not image is choosen
        self.base_img = Image.open('assets/logo.png')
        self.base_img = self.base_img.resize((300, 300), Image.ANTIALIAS)
        self.base_img = ImageTk.PhotoImage(self.base_img)

        self.preview_canvas.create_image(150, 150, image=self.base_img)

        # Label with image filename
        self.image_label = ttk.Label(
            self.preview, text="Open an image to enable preview")
        self.image_label.grid(column=0, row=2)

    # For read exif date metadatas
    def read_exif(self):
        with open(self.img_file, 'rb') as file:
            self.img_metas = Exif(file)

        if self.img_metas.has_exif:
            print(f'Exif : {self.img_metas.has_exif}')
            date = self.img_metas.datetime_original
            date = bytes(date, 'utf-8')
            date = date.decode('utf-8')
            print(date)
            return date
        else:
            print(f'Exif : {self.img_metas.has_exif}')
            return False

    # For create exif (gps)
    def create_exif(self, coords):
        with open(self.img_file, 'rb') as file:
            file = Exif(file)

            file.gps_latitude = coords['lat']
            file.gps_longitude = coords['lon']

            with open(self.img_file, 'wb') as new_image_file:
                new_image_file.write(file.get_file())


    def open_image(self):
        file = filedialog.askopenfilename(
            title="Select an image", filetype=[("Images Files", ['*.jpg', '*.jpeg', '*.png', '*.gif'])])

        if file:
            self.img_file = file
            self.img_fname = self.img_file.split('/')
            self.img_fname = self.img_fname[len(self.img_fname) - 1]
            self.img_file_url = self.img_file.replace(self.img_fname, '')
            self.image_label.config(text=f'File : {self.img_fname}')

            # Display image on canvas
            self.img_loaded = Image.open(self.img_file)
            self.img_loaded = self.img_loaded.resize(
                (300, 300), Image.ANTIALIAS)
            self.img_loaded = ImageTk.PhotoImage(self.img_loaded)

            self.preview_canvas.create_image(150, 150, image=self.img_loaded)

            # Increase progress bar
            self.progress_bar.step(150)

            # Unlock gpx btn
            self.gpx_btn.config(state=ACTIVE)

    def open_gpx(self):
        file = filedialog.askopenfilename(
            title="Select a GPX", filetype=[("GPX Files", "*.gpx")])

        if file:
            self.gpx_file = file

            # Increase progress bar
            self.progress_bar.step(149)

            # Process
            self.process_gpx()

    def process_gpx(self):
        self.img_hour = self.read_exif()
        self.img_hour = datetime.datetime.strptime(self.img_hour, '%Y:%m:%d %H:%M:%S')

        # Initialize parsing
        xml = ET.parse(self.gpx_file)
        root = xml.getroot()
        nodes = []
        times = []
        print(root.tag)
        
        # Get trkpt tags
        for child in root:
            #  print(child.tag)
             for tag in child:
                # print(tag.tag)
                if tag.tag == '{http://www.topografix.com/GPX/1/1}trkseg':
                    for node in tag:
                        nodes.append(node)
                else:
                    pass

        
        for node in nodes:
            time = node.getchildren()[1]
            time = time.text
            time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')

            delta = self.img_hour - time
            times.append(delta.total_seconds())

        # pprint(times)
        tag_time = min(times, key=abs)
        tag_time = times.index(tag_time)

        coords = nodes[tag_time].attrib
        print(coords)

        app.create_exif(coords)


app = App()

# app.create_exif('1234', '5678')

app.set_window_properties()
app.create_widgets()
# app.open_image()
# app.open_gpx()
app.root.mainloop()
