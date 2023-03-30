import os
from tkinter import filedialog, Tk, Label, Button, Text, StringVar, Frame, Scrollbar, Canvas
from PIL import Image, ImageTk

class App:
    def __init__(self, master):

        self.master = master
        self.master.geometry("800x600")
        self.folder_path = StringVar()

        self.browse_button = Button(self.master, text="Browse", command=self.browse)
        self.browse_button.grid(row=0, column=0)

        self.folder_label = Label(self.master, textvariable=self.folder_path)
        self.folder_label.grid(row=1, column=0)

        self.scroll_frame = Frame(self.master)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(2, weight=1)

        self.canvas = Canvas(self.scroll_frame)
        self.scrollbar = Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.table_frame = Frame(self.canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>", self.update_scroll_region)
        # Add this line after creating the canvas
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.table = []
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def browse(self):
        folder = filedialog.askdirectory()
        self.folder_path.set(folder)

        if folder:
            self.populate_table(folder)
            
    def clear_table(self):
        for widget in self.table:
            for item in widget:
                item.destroy()
        self.table = []

    def populate_table(self, folder):
        self.clear_table()

        def file_number(file):
            number = file.split(" ")[-1].split(".")[0][1:-1]
            return int(number) if number.isdigit() else float('inf')

        files = sorted(os.listdir(folder), key=file_number)
        serial_number = 1
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                number = int(file.split(" ")[-1].split(".")[0][1:-1])

                img = Image.open(os.path.join(folder, file))
                original_img_size = img.size
                img.thumbnail((100, 100))
                img = ImageTk.PhotoImage(img)

                serial_label = Label(self.table_frame, text=serial_number)
                serial_label.grid(row=number, column=0)

                img_label = Label(self.table_frame, image=img)
                img_label.image = img
                img_label.grid(row=number, column=1)

                img_size_label = Label(self.table_frame, text=f"{original_img_size[0]}x{original_img_size[1]}")
                img_size_label.grid(row=number, column=2)

                with open(os.path.join(folder, f"{file.split('.')[0]}.txt"), "r") as txt_file:
                    txt_content = txt_file.read()

                txt_entry = Text(self.table_frame, wrap="word", height=5, width=30)
                txt_entry.insert("1.0", txt_content)
                txt_entry.config(state="disabled")
                txt_entry.grid(row=number, column=3)

                def create_edit_command(row_number, file_base_name):
                    return lambda: self.edit_text(row_number, file_base_name)

                edit_button = Button(self.table_frame, text="Edit", command=create_edit_command(serial_number, file.split('.')[0]))
                edit_button.grid(row=number, column=4)

                self.table.append((serial_label, img_label, img_size_label, txt_entry, edit_button))
                serial_number += 1

    def edit_text(self, number, file_name):
        entry = self.table[number - 1][3]
        edit_button = self.table[number - 1][4]

        button_text = edit_button.config("text")[-1]
        if button_text == "Edit":
            entry.config(state="normal")
            edit_button.config(text="Save")
        else:
            entry.config(state="disabled")
            edit_button.config(text="Edit")
            txt_content = entry.get("1.0", "end-1c")
            with open(os.path.join(self.folder_path.get(), f"{file_name}.txt"), "w") as txt_file:
                txt_file.write(txt_content)

    def update_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()

