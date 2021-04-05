from tkinter import filedialog, simpledialog, messagebox
from tkinter import *
from PIL import Image, ImageDraw, ImageFont, ImageTk
import glob


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermarking App")
        self.root.geometry("500x500+150+100")
        self.file_path = None
        self.prev_path = None
        self.save_path = None
        self.text = ""
        self.image = None
        self.position = ()

        # Setup Frames
        self.title_frame = Frame(root, height=80, width=1000)
        self.buttons_frame = Frame(root, bg="#4d4d4d")
        self.image_frame = Frame(root)

        # Setup Title & intro
        self.title = Label(self.title_frame, text="Watermarking App", fg="#FFFFFF", font=("Ubuntu", 30, "bold"))
        self.intro_text = Label(self.title_frame, text="Please select an image or folder to begin.", fg="#FFFFFF")

        # Create buttons
        self.select_button = Button(self.buttons_frame, text="Select image", command=self.select_image)
        self.multi_button = Button(self.buttons_frame, text="Watermark multiple", command=self.watermark_multi)
        self.add_text_button = Button(self.buttons_frame, text="Add text", command=self.add_text, padx=5)
        self.clear_button = Button(self.buttons_frame, text="Clear text", command=self.clear_text, padx=5)
        self.save_button = Button(self.buttons_frame, text="Save", command=self.save_to_file, padx=5)
        self.canvas = Canvas(self.image_frame)

        self.show_main_screen()

    def show_main_screen(self):
        """ Loads text and first buttons onto the app screen. """
        self.title_frame.pack(side=TOP)
        self.title_frame.pack_propagate(0)
        self.title.pack()
        self.intro_text.pack(side=TOP)
        self.buttons_frame.pack()
        self.select_button.pack(side=LEFT, padx=50)
        self.multi_button.pack(side=LEFT, padx=50)

    def show_edit_screen(self):
        """ Adds buttons to the app and shows the selected image. """
        self.intro_text.destroy()
        self.save_button.pack(side=RIGHT, padx=100)
        self.save_button["state"] = "disabled"
        self.add_text_button.pack(side=RIGHT, padx=5)
        self.image_frame.pack(side=BOTTOM, fill=BOTH, expand=1)
        self.display_image()

    def select_image(self):
        """ Checks to see if there's an image being edited and displays a warning before selecting a new one. If an
        image is selected, the image is opened.. """
        if self.text == "" or self.save_button["state"] == "disabled" or \
                (self.save_button["state"] == "normal" and
                 messagebox.askokcancel(title="Discard without saving",
                                        message="Select a new image without saving this one?")):
            self.file_path = filedialog.askopenfilename()
            if self.file_path:
                self.prev_path = self.file_path
                # self.prev_path added to save the current image displayed in case of doing Multiple watermarks or
                # other changes to the self.file_path. #prev_path will always have the path of displayed image.
                self.image = Image.open(self.file_path)
                self.show_edit_screen()

    def display_image(self):
        """ Reduces image size if larger than screen and displays the current image. """
        if any(n > MAX_SIZE for n in self.image.size):
            self.image.thumbnail((MAX_SIZE, MAX_SIZE))  # reduce image to fit window
        if not any(n < MIN_SIZE for n in self.image.size):
            w, h = self.image.size
            self.root.geometry(f"{w}x{h + 110}")  # Change app to size of image
        picture = ImageTk.PhotoImage(self.image)
        self.canvas.bg_image = picture
        w, h = self.image.size
        self.canvas.create_image(w/2, h/2, image=self.canvas.bg_image)
        self.canvas.pack(side=TOP, fill=BOTH, expand=1)  # expand to show full image

    def add_text(self):
        """ Accepts text input from user, adds it as watermark to the current image and displays it.
        Enables Save and Clear buttons. """
        self.text = simpledialog.askstring(title="Enter text", prompt="Enter text:")
        self.image = Image.open(self.prev_path)
        self.apply_watermark()
        self.display_image()
        self.clear_button.pack(side=LEFT, padx=5)
        self.save_button["state"] = "normal"
        self.clear_button["state"] = "normal"

    def clear_text(self):
        """ Removes the added watermark text and displays the current image. """
        self.text = ""
        self.image = Image.open(self.prev_path)
        self.display_image()
        self.save_button["state"] = "disabled"
        self.clear_button["state"] = "disabled"

    def apply_watermark(self):
        """ Adds the given text onto the current image as a watermark. """
        w, h = self.image.size
        draw = ImageDraw.Draw(self.image)
        font = ImageFont.truetype(FONT, FONT_SIZE)
        text_w, text_h = draw.textsize(self.text, font)
        x = w - text_w - MARGIN
        y = h - text_h - MARGIN
        c_text = Image.new('RGB', (text_w, text_h), color='#000000')
        drawing = ImageDraw.Draw(c_text)
        drawing.text((0, 0), self.text, fill="#ffffff", font=font)
        c_text.putalpha(100)
        self.image.paste(c_text, (x, y), c_text)

    def save_to_file(self):
        """ Saves the current image to specified directory. Shows feedback stating where image has been saved to.
        Then disables the Save button."""
        directory = filedialog.askdirectory()
        filename = self.prev_path.split("/")[-1]
        self.save_path = f"{directory}/watermark_{filename}"
        self.image.save(self.save_path)
        messagebox.showinfo(title="Image saved", message=f"The file has been saved to: {self.save_path}")
        self.save_button["state"] = "disabled"

    def watermark_multi(self):
        """ Accepts an input directory of images, then asks for a text to add as watermark. Adds the watermark
        to each image in the directory and saves it with a modified filename. Message displayed after saying
        where images are saved. """
        input_directory = filedialog.askdirectory()
        if input_directory:
            list_of_files = glob.glob(f"{input_directory}/*.*")
            self.text = simpledialog.askstring(title="Enter text", prompt="Enter text:")
            for pic in list_of_files:
                filename = pic.split("/")[-1]
                self.save_path = f"{input_directory}/watermark_{filename}"
                self.image = Image.open(pic)
                self.apply_watermark()
                self.image.save(self.save_path)
            messagebox.showinfo(title="Images saved", message=f"The files have been saved to: "
                                                              f"'{input_directory}/'")


MAX_SIZE = 1000
MIN_SIZE = 500
FONT_SIZE = 40
FONT = "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
MARGIN = 10

if __name__ == "__main__":
    window = Tk()
    gui = App(window)
    window.mainloop()
