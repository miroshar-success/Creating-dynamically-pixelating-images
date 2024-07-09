import numpy as np
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import random
from scipy.spatial import Voronoi

# Variables globales
history = []
redo_stack = []
img = None

def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global img
        img = Image.open(file_path).convert('RGB')
        add_to_history(img.copy())
        display_image(img)
    else:
        return None

def save_image(image):
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if file_path:
        image.save(file_path)

def get_nearest_color(color, color_palette):
    r, g, b = color
    min_distance = float('inf')
    closest_color = None

    for palette_color in color_palette:
        cr, cg, cb = palette_color
        color_diff = np.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        if color_diff < min_distance:
            min_distance = color_diff
            closest_color = palette_color

    return closest_color

def apply_circle_pixelation(image, radius, color_palette):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, radius * 2):
        for x in range(0, width, radius * 2):
            original_color = pixels[x, y]
            if len(color_palette) >= 4:
                fill_color = get_nearest_color(original_color, color_palette)
            else:
                fill_color = original_color
            draw.ellipse((x, y, x + radius * 2, y + radius * 2), fill=fill_color)
    
    return new_image

def apply_square_pixelation(image, size, color_palette):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, size):
        for x in range(0, width, size):
            original_color = pixels[x, y]
            if len(color_palette) >= 4:
                fill_color = get_nearest_color(original_color, color_palette)
            else:
                fill_color = original_color
            draw.rectangle((x, y, x + size, y + size), fill=fill_color)
    
    return new_image

def apply_rectangle_pixelation(image, width, height, color_palette):
    img_width, img_height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, img_height, height):
        for x in range(0, img_width, width):
            original_color = pixels[x, y]
            if len(color_palette) >= 4:
                fill_color = get_nearest_color(original_color, color_palette)
            else:
                fill_color = original_color
            draw.rectangle((x, y, x + width, y + height), fill=fill_color)
    
    return new_image

def apply_triangle_pixelation(image, size, color_palette):
    width, height = image.size
    pixels = image.load()
    new_image = Image.new("RGB", image.size)
    draw = ImageDraw.Draw(new_image)
    
    for y in range(0, height, size):
        for x in range(0, width, size):
            original_color = pixels[x, y]
            if len(color_palette) >= 4:
                fill_color = get_nearest_color(original_color, color_palette)
            else:
                fill_color = original_color
            points = [(x, y), (x + size, y), (x + size / 2, y + size)]
            draw.polygon(points, fill=fill_color)
    
    return new_image

def apply_voronoi_pixelation(image, num_points, color_palette):
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
                original_color = pixels[int(polygon[0][0]), int(polygon[0][1])]
                if len(color_palette) >= 4:
                    fill_color = get_nearest_color(original_color, color_palette)
                else:
                    fill_color = original_color
                draw.polygon(polygon, fill=fill_color)
    
    return new_image

def display_image(image):
    canvas_width, canvas_height = 500, 500
    canvas.config(width=canvas_width, height=canvas_height)
    image_tk = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
    canvas.image = image_tk

def choose_color():
    color_code = colorchooser.askcolor(title="Choose color")[1]
    if color_code:
        custom_color = tuple(int(color_code.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        if len(custom_color) == 3:  # Ensure it's a valid RGB color
            color_palette.append(custom_color)
            update_color_display()

def update_color_display():
    color_display.delete(0, tk.END)
    for idx, color in enumerate(color_palette):
        color_display.insert(tk.END, f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
        color_display.itemconfig(idx, bg=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")

def delete_color():
    selected_index = color_display.curselection()
    if selected_index:
        color_palette.pop(selected_index[0])
        update_color_display()

def add_to_history(image):
    history.append(image)
    if len(history) > 10:  # Limit history to last 10 actions
        history.pop(0)

def undo():
    if history:
        redo_stack.append(history.pop())
        if history:
            display_image(history[-1])
        else:
            canvas.delete("all")

def redo():
    if redo_stack:
        last_image = redo_stack.pop()
        add_to_history(last_image)
        display_image(last_image)

def create_gui():
    def update_image():
        if img:
            size = size_slider.get()
            width = width_slider.get()
            height = height_slider.get()
            num_points = points_slider.get()
            pixelation_style = style_var.get()

            if pixelation_style == "Circle":
                pixelated_img = apply_circle_pixelation(img, size, color_palette)
            elif pixelation_style == "Square":
                pixelated_img = apply_square_pixelation(img, size, color_palette)
            elif pixelation_style == "Rectangle":
                pixelated_img = apply_rectangle_pixelation(img, width, height, color_palette)
            elif pixelation_style == "Triangle":
                pixelated_img = apply_triangle_pixelation(img, size, color_palette)
            elif pixelation_style == "Voronoi":
                pixelated_img = apply_voronoi_pixelation(img, num_points, color_palette)
            else:
                pixelated_img = img

            add_to_history(pixelated_img)
            display_image(pixelated_img)

    root = tk.Tk()
    root.title("Dynamic Pixelation Tool")

    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", command=open_image)
    file_menu.add_command(label="Save", command=lambda: save_image(img))
    menubar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(menubar, tearoff=0)
    edit_menu.add_command(label="Undo", command=undo)
    edit_menu.add_command(label="Redo", command=redo)
    menubar.add_cascade(label="Edit", menu=edit_menu)

    # Create main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create canvas
    global canvas
    canvas = tk.Canvas(main_frame)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Create controls frame
    controls_frame = tk.Frame(root)
    controls_frame.pack(fill=tk.X)

    # Pixelation style selection
    style_label = tk.Label(controls_frame, text="Pixelation Style:")
    style_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    style_var = tk.StringVar(value="Square")
    style_options = ["Circle", "Square", "Rectangle", "Triangle", "Voronoi"]
    style_menu = tk.OptionMenu(controls_frame, style_var, *style_options)
    style_menu.pack(side=tk.LEFT, padx=5, pady=5)

    # Size slider for circle, square, and triangle
    size_label = tk.Label(controls_frame, text="Size:")
    size_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    size_slider = tk.Scale(controls_frame, from_=1, to=100, orient=tk.HORIZONTAL)
    size_slider.set(10)
    size_slider.pack(side=tk.LEFT, padx=5, pady=5)

    # Width slider for rectangle
    width_label = tk.Label(controls_frame, text="Width:")
    width_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    width_slider = tk.Scale(controls_frame, from_=1, to=100, orient=tk.HORIZONTAL)
    width_slider.set(10)
    width_slider.pack(side=tk.LEFT, padx=5, pady=5)

    # Height slider for rectangle
    height_label = tk.Label(controls_frame, text="Height:")
    height_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    height_slider = tk.Scale(controls_frame, from_=1, to=100, orient=tk.HORIZONTAL)
    height_slider.set(10)
    height_slider.pack(side=tk.LEFT, padx=5, pady=5)

    # Points slider for Voronoi
    points_label = tk.Label(controls_frame, text="Points:")
    points_label.pack(side=tk.LEFT, padx=5, pady=5)
    
    points_slider = tk.Scale(controls_frame, from_=10, to=1000, orient=tk.HORIZONTAL)
    points_slider.set(100)
    points_slider.pack(side=tk.LEFT, padx=5, pady=5)

    # Update button
    update_button = tk.Button(controls_frame, text="Update", command=update_image)
    update_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Color palette
    color_palette_frame = tk.Frame(root)
    color_palette_frame.pack(fill=tk.X)

    add_color_button = tk.Button(color_palette_frame, text="Add Color", command=choose_color)
    add_color_button.pack(side=tk.LEFT, padx=5, pady=5)

    delete_color_button = tk.Button(color_palette_frame, text="Delete Color", command=delete_color)
    delete_color_button.pack(side=tk.LEFT, padx=5, pady=5)

    global color_display
    color_display = tk.Listbox(color_palette_frame, height=5, width=30)
    color_display.pack(side=tk.LEFT, padx=5, pady=5)
    
    global color_palette
    color_palette = []

    root.mainloop()

create_gui()
