import numpy as np
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, colorchooser
import random
from scipy.spatial import Voronoi

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global img
        img = Image.open(file_path)

        display_image(img)
    else:
        return None

def save_image(image):
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        image.save(file_path)

def apply_circle_pixelation(image, radius):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, radius * 2):
        for x in range(0, width, radius * 2):
            r, g, b = pixels[x, y]
            draw.ellipse((x, y, x + radius * 2, y + radius * 2), fill=(r, g, b))
    
    return new_image

def apply_square_pixelation(image, size):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, size):
        for x in range(0, width, size):
            r, g, b = pixels[x, y]
            draw.rectangle((x, y, x + size, y + size), fill=(r, g, b))
    
    return new_image

def apply_rectangle_pixelation(image, width, height):
    img_width, img_height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, img_height, height):
        for x in range(0, img_width, width):
            r, g, b = pixels[x, y]
            draw.rectangle((x, y, x + width, y + height), fill=(r, g, b))
    
    return new_image

def apply_triangle_pixelation(image, size):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, size):
        for x in range(0, width, size):
            r, g, b = pixels[x, y]
            points = [(x, y), (x + size, y), (x + size / 2, y + size)]
            draw.polygon(points, fill=(r, g, b))
    
    return new_image

def apply_voronoi_pixelation(image, num_points):
    width, height = image.size
    pixels = image.load()
    points = np.array([[random.randint(0, width), random.randint(0, height)] for _ in range(num_points)])
    vor = Voronoi(points)
    
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for region in vor.regions:
        if not -1 in region and len(region) > 0:
            polygon = [tuple(vor.vertices[i]) for i in region]
            if all(0 <= x < width and 0 <= y < height for x, y in polygon):
                r, g, b = pixels[int(polygon[0][0]), int(polygon[0][1])]
                draw.polygon(polygon, fill=(r, g, b))
    
    return new_image

def display_image(image):
    image_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image = image_tk

def create_gui():
    def update_image():
        if img:
            size = size_slider.get()
            width = width_slider.get()
            height = height_slider.get()
            num_points = points_slider.get()
            pixelation_style = style_var.get()

            if pixelation_style == "Circle":
                pixelated_img = apply_circle_pixelation(img, size)
            elif pixelation_style == "Square":
                pixelated_img = apply_square_pixelation(img, size)
            elif pixelation_style == "Rectangle":
                pixelated_img = apply_rectangle_pixelation(img, width, height)
            elif pixelation_style == "Triangle":
                pixelated_img = apply_triangle_pixelation(img, size)
            elif pixelation_style == "Voronoi":
                pixelated_img = apply_voronoi_pixelation(img, num_points)
            else:
                pixelated_img = img

            display_image(pixelated_img)
    
    root = tk.Tk()
    root.title("Dynamic Pixelation Tool")

    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Import Image", command=open_image)
    file_menu.add_command(label="Save Image", command=lambda: save_image(img))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)

    apply_btn = tk.Button(root, text="Apply Pixelation", command=update_image)
    apply_btn.pack(side=tk.TOP, pady=5)

    controls_frame = tk.Frame(root)
    controls_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

    size_slider = tk.Scale(controls_frame, from_=1, to_=50, orient=tk.HORIZONTAL, label="Shape Size")
    size_slider.pack(side=tk.LEFT, padx=5)

    width_slider = tk.Scale(controls_frame, from_=1, to_=50, orient=tk.HORIZONTAL, label="Rectangle Width")
    width_slider.pack(side=tk.LEFT, padx=5)

    height_slider = tk.Scale(controls_frame, from_=1, to_=50, orient=tk.HORIZONTAL, label="Rectangle Height")
    height_slider.pack(side=tk.LEFT, padx=5)

    points_slider = tk.Scale(controls_frame, from_=10, to_=1000, orient=tk.HORIZONTAL, label="Voronoi Points")
    points_slider.pack(side=tk.LEFT, padx=5)

    style_var = tk.StringVar(value="Circle")
    styles = ["Circle", "Square", "Rectangle", "Triangle", "Voronoi"]
    style_menu = tk.OptionMenu(controls_frame, style_var, *styles)
    style_menu.pack(side=tk.LEFT, padx=5)

    global canvas

    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    img = None
    create_gui()
