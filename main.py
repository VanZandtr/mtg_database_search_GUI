import tkinter as tk
from tkinter import *
from tkinter import ttk
import pandas as pd
from PIL import ImageTk, Image
import urllib.request
import requests
import sys
import os
import shutil

fields = 'Card Name', 'Set', 'Mana Cost (1U)', 'CMC'

#get cards
json_df = pd.read_json('AllPrintings.json', encoding='UTF-8')

def quit_window():
    global root
    root.destroy()
    shutil.rmtree("./images")
    sys.exit()
    
def display_images(folder, root):       
    filenames = os.listdir(folder)
    columns = 6
    image_count = 0
    window = Toplevel(root)
    window.geometry("1900x800")
    canvas = Canvas(window, width = 1900, height = 800)
    canvas.grid(row=0, column=1, sticky= "news")
    #canvas.place(x=0, y=0)
    
    vsb = Scrollbar(window,orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=0, sticky="ns")
    
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    frame_image = Frame(canvas)
    frame_image.pack(expand=True, fill="both")
    #frame_image.grid_rowconfigure(0, weight = 1)
    #frame_image.grid_columnconfigure(0, weight = 1)
    canvas.create_window((0,0), window=frame_image, anchor="nw")
    
    for name in filenames:
      image_count += 1
      r, c = divmod(image_count - 1, columns)
      im = Image.open(os.path.join(folder, name))
      resized = im.resize((300,300), Image.ANTIALIAS)
      tkimage = ImageTk.PhotoImage(resized)
      myvar = Label(frame_image, image = tkimage)
      myvar.image = tkimage
      myvar.grid(row=r, column = c)
      #print "here"
    window.mainloop()

def fetch(entries):
    card_name = entries[0][1].get()
    set_abbr = entries[1][1].get()
    urls = []
    save_names = []
    #all_labels = []
    
    ret = find_cards(card_name,set_abbr)
    
    if not ret:
        print("list is empty")
        return
    else:
        #create image folder
        if os.path.isdir('images') is False:
            os.mkdir("images")
    
    #not looking for a specific name --> return all cards
    if len(ret) > 1 and card_name == "":
        test_limit = 0
        for card in ret:
            card_id = card['identifiers']['scryfallId']
            url = 'https://api.scryfall.com/cards/' + card_id
            response = requests.get(url)
            url = (response.json())['image_uris']['large'] #small,normal,large
            urls.append(url)
            save_name = "./images/" + card['name'] + ".png"
            save_names.append(save_name)
            test_limit += 1
            
            
            if test_limit == 50:
                break
    
    #else return the first card given
    #if card set is specified will give only one card anyway
    else:
        first_card_identifer = ret[0]['identifiers']['scryfallId']
        url = 'https://api.scryfall.com/cards/' + first_card_identifer
        
        response = requests.get(url)
        url = (response.json())['image_uris']['larege'] #small,normal,large
        urls.append(url)
        save_name = "./images/" +  card['name'] + ".png"
        save_names.append(save_name)
    
    print("Got all URLs")
    
    #add all images to file
    name_index =  0
    for url in urls:
        print(name_index)
        urllib.request.urlretrieve(url, save_names[name_index])
        name_index += 1
    
    if len(ret) > 1 and card_name == "":       
        #display all images
        display_images("./images/", root)
    else:
        print("add for single card!!!!!")
  

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=15, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries

def find_cards(name=None, set_abbr=None):
    cards = []
    for row in json_df['data']:
        if str(row) == "nan":
           continue
        try:
            for card in row['cards']:
                if name == card['name'] and set_abbr == card['setCode']:
                    cards.append(card)
                    return cards
                elif name == card['name'] and set_abbr == "":
                    cards.append(card)
                    return cards
                elif name == "" and set_abbr == card['setCode']:
                    cards.append(card)
        except Exception:
            pass
    return cards

if __name__ == '__main__':
    root = tk.Tk()
    #root.protocol("WM_DELETE_WINDOW", root.destroy())
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
    b1 = tk.Button(root, text='Search', command=(lambda e=ents: fetch(e)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)

    root.mainloop()

###############################################################################



