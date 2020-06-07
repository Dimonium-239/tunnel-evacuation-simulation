from tkinter import *
from settings import *

class Menu:
    def __init__(self):

        self.path_len = 40
        self.tunnel_len = self.meters_to_pixels(800)  #1377.5
        self.exit_size = self.meters_to_pixels(2)
        self.car_margin = self.meters_to_pixels(1)
        self.cell_size = int(self.car_margin/3)
        self.num_of_pathes = 4
        self.margin = 30
        self.car_quantity = 100

        self.window = Tk()
        self.window.title("Welcome to LikeGeeks app")
        self.window.geometry('500x500')
        
        self.path_len_i = self.line('Length of path', 0)
        self.tunnel_len_i = self.line('Length of tunnel', 1)
        self.num_of_pathes_i = self.line('Number of path', 2)
        self.exit_size_i = self.line('Exit size', 3)
        self.car_margin_i = self.line('Margin of car', 4)
        self.car_quantity_i = self.line('Car quantity', 5)
        self.margin_i = self.line('Global margin (auxity)', 6)

        self.btn = Button(self.window, text="Subbmit", command=self.clicked)
        self.btn.grid(column=1, row=7)
        self.window.mainloop()
    

    def line(self, text, row):
        self.lbl = Label(self.window, text=text)
        self.lbl.grid(column=0, row=row)
        self.txt = Entry(self.window, width=25)
        self.txt.grid(column=1, row=row)
        return self.txt
    
    def get_settings(self):
        return self.path_len, \
                self.tunnel_len, \
                self.exit_size, \
                self.car_margin, \
                self.cell_size, \
                self.num_of_pathes, \
                self.margin,    \
                self.car_quantity

    def clicked(self):
        if self.path_len_i.get():
            self.path_len = int(self.path_len_i.get())
        if self.tunnel_len_i.get():
            self.tunnel_len = self.meters_to_pixels(int(self.tunnel_len_i.get()))
        if self.num_of_pathes_i.get():
            self.num_of_pathes = int(self.num_of_pathes_i.get())
        if self.exit_size_i.get():
            self.exit_size = self.meters_to_pixels(int(self.exit_size_i.get()))
        if self.car_margin_i.get():
            self.car_margin = self.meters_to_pixels(int(self.car_margin_i.get()))
        if self.car_quantity_i.get():
            self.car_quantity = int(self.car_quantity_i.get())
        if self.margin_i.get():
            self.margin = int(self.margin_i.get())
        self.window.destroy()

    def meters_to_pixels(self, meters):
        return int((meters*self.path_len)/2.55)

    def pixels_to_meters(self, pixels):
        return int((pixels*2.55)/self.path_len)
        
