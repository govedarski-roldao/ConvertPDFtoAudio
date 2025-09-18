from tkinter import *
from main import *
from backstage.convert_book import *
from tkinter import filedialog
from backstage.convert_pdf_to_audio import *
from tkinter import ttk

vozes = [
    "pt-PT-DuarteNeural",
    "pt-PT-RaquelNeural",
    "bg-BG-IvanNeural",
    "bg-BG-KalinaNeural"
]



def browse_files():
    filenames = filedialog.askopenfilenames(
        title="Select files",
        filetypes=(
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("Images", "*.png *.jpg *.jpeg *.gif"),
            ("PDFs", "*.pdf"),
            ("ZIP archives", "*.zip"),
            ("DLT files", "*.dlt"),
            ("Videos", "*.mp4 *.avi *.mov *.mkv")
        )
    )
    if filenames:
        book_location_input.delete(0, END)
        book_location_input.insert(0, "; ".join(filenames))


def browse_destination():
    filenames = filedialog.askopenfilenames(
        title="Select files",
        filetypes=(
            ("All files", "*.*"),
            ("Text files", "*.txt"),
            ("Images", "*.png *.jpg *.jpeg *.gif"),
            ("PDFs", "*.pdf"),
            ("ZIP archives", "*.zip"),
            ("DLT files", "*.dlt"),
            ("Videos", "*.mp4 *.avi *.mov *.mkv")
        )
    )
    if filenames:
        book_location_input.delete(0, END)
        book_location_input.insert(0, "; ".join(filenames))


def start_convert():
    attachments = book_location_input.get().strip().split("; ")[0]
    get_right_format(attachments)
    print(attachments)


# ---------------------------- UI SETUP ------------------------------- #
# Window
root = Tk()
root.title("Jira Bug Tickets")
root.geometry("600x650")  # Initial size
root.config(bg="#f5f5f5", padx=20, pady=20)
root.option_add("*Font", ("Arial", 14))

# Getting the link for the book
Label(root, text="Choose the book", bg="#f5f5f5").grid(column=0, row=0, sticky="W", pady=5)
book_location_input = Entry(root, width=40, bd=2, relief="groove")
book_location_input.grid(column=1, row=0, columnspan=2, sticky="EW", padx=10, pady=5)
book_location_input.focus()

browse_button = Button(text="Browse...", command=browse_files, bg="#007acc", fg="white", relief="raised", padx=10,
                       pady=5)
browse_button.grid(column=1, row=1, padx=10, pady=5, sticky="E")

# Getting the location to drop the audio file
Label(root, text="Choose the book", bg="#f5f5f5").grid(column=0, row=2, sticky="W", pady=5)
audio_location_input = Entry(root, width=40, bd=2, relief="groove")
audio_location_input.grid(column=1, row=2, columnspan=2, sticky="EW", padx=10, pady=5)
audio_location_input.focus()

browse_button = Button(text="Browse...", command=browse_destination, bg="#007acc", fg="white", relief="raised", padx=10,
                       pady=5)
browse_button.grid(column=1, row=3, padx=10, pady=5, sticky="E")

Label(root, text="Choose the Voice", bg="#f5f5f5").grid(column=0, row=4, sticky="W", pady=5)
combo = ttk.Combobox(root, values=vozes)
combo.set(vozes[0])  # valor inicial
combo.grid(column=1, row=4, padx=10, pady=5, sticky="W")

# Starting the process button

start_convert_button = Button(root, text="Start to Convert the book", command=start_convert, bg="#28a745", fg="white",
                              relief="raised", padx=15, pady=8)
start_convert_button.grid(column=0, row=6, columnspan=3, pady=10, sticky="EW")

root.grid_columnconfigure(1, weight=1)  # Make column 1 expandable
root.grid_columnconfigure(2, weight=0)

root.mainloop()
