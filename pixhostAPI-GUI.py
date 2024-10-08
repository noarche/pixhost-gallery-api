import tkinter as tk
from tkinter import ttk  # Import ttk for ProgressBar and other widgets
from tkinter import filedialog, messagebox
import requests
import pyperclip
import time


# File paths for saving gallery and image information
save_file_path = "galleries_info.txt"
image_links_file = "image_links.txt"

# Function to create a gallery and auto-fill hash fields
def create_gallery():
    gallery_name = gallery_name_entry.get()
    nsfw = nsfw_var.get()
    content_type = "1" if nsfw else "0"

    if not gallery_name:
        messagebox.showwarning("Input Required", "Please enter a gallery name.")
        return

    url = "https://api.pixhost.to/galleries"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "application/json"
    }
    params = {
        "gallery_name": gallery_name
    }

    response = requests.post(url, headers=headers, data=params)

    if response.status_code == 200:
        data = response.json()
        gallery_info.set(f"Gallery Created:\nName: {data['gallery_name']}\nHash: {data['gallery_hash']}\nURL: {data['gallery_url']}")

        # Auto-fill Gallery Hash and Gallery Upload Hash
        gallery_hash_entry.delete(0, tk.END)
        gallery_hash_entry.insert(0, data['gallery_hash'])

        gallery_upload_hash_entry.delete(0, tk.END)
        gallery_upload_hash_entry.insert(0, data['gallery_upload_hash'])

        # Store gallery info for later use
        root.gallery_url = data['gallery_url']
        root.gallery_name = data['gallery_name']
        root.gallery_hash = data['gallery_hash']
        root.gallery_upload_hash = data['gallery_upload_hash']

    else:
        messagebox.showerror("Error", f"Error creating gallery: {response.status_code}")

# Function to finalize a gallery and save details to a file
def finalize_gallery():
    gallery_hash = gallery_hash_entry.get()
    upload_hash = gallery_upload_hash_entry.get()

    if not gallery_hash or not upload_hash:
        messagebox.showwarning("Input Required", "Please provide both gallery hash and upload hash.")
        return

    url = f"https://api.pixhost.to/galleries/{gallery_hash}/finalize"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "application/json"
    }
    params = {
        "gallery_upload_hash": upload_hash
    }

    response = requests.post(url, headers=headers, data=params)

    if response.status_code == 200:
        messagebox.showinfo("Success", "Gallery finalized successfully!")

        # Save gallery URL and name to a file
        gallery_url = root.gallery_url
        gallery_name = root.gallery_name
        with open(save_file_path, "a") as file:
            file.write(f"{gallery_url},{gallery_name}\n")

        # Copy the gallery URL to clipboard
        pyperclip.copy(gallery_url)
        messagebox.showinfo("Clipboard", f"Gallery URL copied to clipboard: {gallery_url}")

    else:
        messagebox.showerror("Error", f"Error finalizing gallery: {response.status_code}")

# Function to upload images one by one (queue system)
def upload_images():
    image_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.webp *.gif *.jpg *.jpeg *.png")])
    if not image_paths:
        return

    gallery_hash = gallery_hash_entry.get()
    upload_hash = gallery_upload_hash_entry.get()

    if not gallery_hash or not upload_hash:
        messagebox.showwarning("Input Required", "Please enter both gallery hash and upload hash.")
        return

    url = "https://api.pixhost.to/images"
    headers = {
        "Accept": "application/json"
    }

    progress_bar['value'] = 0
    progress_bar['maximum'] = len(image_paths)

    # Upload images one by one
    for idx, image_path in enumerate(image_paths):
        try:
            with open(image_path, "rb") as image_file:
                files = {"img": image_file}
                params = {"content_type": "0", "gallery_hash": gallery_hash, "gallery_upload_hash": upload_hash, "max_th_size": "420"}

                response = requests.post(url, headers=headers, files=files, data=params)

                if response.status_code == 200:
                    data = response.json()
                    upload_info.set(f"Uploaded Image {idx+1}: {data['show_url']}")

                    # Save image link to file
                    with open(image_links_file, "a") as file:
                        file.write(f"{data['show_url']}\n")

                    # Update progress bar
                    progress_bar['value'] += 1
                else:
                    messagebox.showerror("Error", f"Failed to upload image: {image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Exception occurred: {str(e)}")

        # Adding slight delay to simulate real-time upload
        time.sleep(1)

    messagebox.showinfo("Upload Complete", "All images uploaded successfully.")

# About function to display instructions
def show_about():
    about_message = (
        "How to Use the PiXhost API GUI:\n\n"
        "1. Create a Gallery:\n"
        "- Enter a name and check 'NSFW' if necessary. Click 'Create Gallery'.\n\n"
        "2. Upload Images to the Gallery:\n"
        "- After creating the gallery, you can click 'Upload Images' to select and upload images sequentially.\n\n"
        "3. Finalize the Gallery:\n"
        "- Once images are uploaded, click 'Finalize Gallery' to make the gallery public.\n"
        "- The gallery information (URL, Name) will be saved to a file, and the URL copied to clipboard.\n\n"
        "Note: Upload images before finalizing the gallery."
    )
    messagebox.showinfo("About", about_message)

# GUI Setup
root = tk.Tk()
root.title("PiXhost API GUI")
root.geometry("350x475")
root.config(bg="#2E2E2E")  # Dark theme background
root.attributes("-alpha", 0.92)  # Slight transparency

# Initialize variables to store gallery info
root.gallery_url = ""
root.gallery_name = ""
root.gallery_hash = ""
root.gallery_upload_hash = ""

# Gallery creation section
gallery_name_label = tk.Label(root, text="Gallery Name:", bg="#2E2E2E", fg="white")
gallery_name_label.pack(pady=5)
gallery_name_entry = tk.Entry(root, bg="#444444", fg="white")
gallery_name_entry.pack(pady=5)

# NSFW checkbox
nsfw_var = tk.IntVar()
nsfw_checkbox = tk.Checkbutton(root, text="Public Access", variable=nsfw_var, bg="#2E2E2E", fg="white", selectcolor="#444444")
nsfw_checkbox.pack(pady=5)

create_gallery_button = tk.Button(root, text="1. Create Gallery", bg="#444444", fg="white", command=create_gallery)
create_gallery_button.pack(pady=10)

gallery_info = tk.StringVar()
gallery_info_label = tk.Label(root, textvariable=gallery_info, bg="#2E2E2E", fg="white")
gallery_info_label.pack(pady=10)

# Upload image button
upload_image_button = tk.Button(root, text="2. Upload Images", bg="#444444", fg="white", command=upload_images)
upload_image_button.pack(pady=10)

# Finalize gallery button
finalize_gallery_button = tk.Button(root, text="3. Finalize Gallery", bg="#444444", fg="white", command=finalize_gallery)
finalize_gallery_button.pack(pady=10)

# Gallery hash section (for uploading and finalizing)
gallery_hash_label = tk.Label(root, text="Gallery Hash:", bg="#2E2E2E", fg="white")
gallery_hash_label.pack(pady=5)
gallery_hash_entry = tk.Entry(root, bg="#444444", fg="white")
gallery_hash_entry.pack(pady=5)

gallery_upload_hash_label = tk.Label(root, text="Gallery Upload Hash:", bg="#2E2E2E", fg="white")
gallery_upload_hash_label.pack(pady=5)
gallery_upload_hash_entry = tk.Entry(root, bg="#444444", fg="white")
gallery_upload_hash_entry.pack(pady=5)




# Progress bar for image uploads
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

upload_info = tk.StringVar()
upload_info_label = tk.Label(root, textvariable=upload_info, bg="#2E2E2E", fg="white")
upload_info_label.pack(pady=5)

# Menu bar with About option
menu_bar = tk.Menu(root)
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

root.mainloop()
