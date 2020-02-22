# -*- coding: utf-8 -*-

import PIL.Image
# import Image
# import PIL 
import PIL.ImageTk as ImageTk
from Tkinter import *  


# poe os index para incrementar de 0 até onde for, e ferifica apenas com o ultimo colocado se ja n existe na mesma imagem


import cv2
import os
from modulos.common import draw_str
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import xml.etree.ElementTree as ET
import shutil
import imutils  
import numpy as np
import random
import json

class TKMarkCoorAnnotation(Frame):
    def __init__(self):
        
        
        self.dist1 = np.Inf
        self.dist2 = np.Inf
        self.TDIST = 4
        
        #inputs-------------------        
        input_data = self.load_config()

        self.switch_class = self.parse_index(input_data['class'])

        dir_data = input_data['dataset']['url']
        img_input = input_data['dataset']['inputs']
        img_data = input_data['dataset']['imagens']
        img_anotation = input_data['dataset']['anotations']

        self.path_input = dir_data + img_input
        self.path_save_img = dir_data + img_data
        self.path_save_anotation = dir_data + img_anotation
        self.path_output = dir_data + '/crops/'
        
        #----------------------------------------------------------------
        
        
        self.id = 0
        self.idImag = 0
        self.idImagGlobal = 0
        self.angulo = 0
        self.frame = None
        self.size_w, self.size_h = 770, 600
        
        self.imgs = os.listdir(os.path.dirname(os.path.realpath(__file__)) + '/' + self.path_input)
        self.imgs = sorted(self.imgs)
        print self.imgs
        
        self.drawing = False  # true if mouse is pressed
        self.mode = True
        
        self.arquivo = open('info.txt', 'w')
        self.salvar = ""
        
        self.name_img = None
        
        
        self.objetos_coo = []
        self.objetos_re_draw = []
        
        self.classe_info()
        
        #---------------------------------------------------------------------
        Frame.__init__(self, master=None, bg='black')
        self.x1, self.y1 = 0, 0
        self.x2, self.y2 = 0, 0
        
        self.canvas = Canvas(self, cursor="cross")
        self.canvas.place(x=160, y=140, width=self.size_w, height=self.size_h)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.master.bind("<KeyPress>", self.key_press)
        
        self.rect = None

        self.start_x = None
        self.start_y = None

        #---------------------------------------------
        
        label_files = Label(self, text="Arquivos", bg='black', fg="white", font=("Arial", 14))
        label_files.place(x=30, y=20)
        
        #------------------
        
        self.list_files = Listbox(self, selectmode=SINGLE, exportselection=False, bg='black', fg="white")
        for item in self.imgs:
            self.list_files.insert(END, item)
        self.list_files.bind('<<ListboxSelect>>', self.file_item_select)
        #-----------------
        self.list_files.select_set(0)
        
        scrollbar = Scrollbar(self.list_files)
        scrollbar.config(command=self.list_files.yview)
        scrollbar.pack(side="right", fill="y")
        self.list_files.config(yscrollcommand=scrollbar.set) 
        self.list_files.place(x=10, y=50, width=140, height=320)
        #-------------------------------------------------------------
        
        
        
        #---------------------------------------------------------------------
        
        
        
        label_list = Label(self, text="Classes", bg='black', fg="white", font=("Arial", 14))
        label_list.place(x=960, y=20)
        
        #------------------
        
        self.listbox = Listbox(self, selectmode=SINGLE, exportselection=False, bg='black', fg="white")
        for item in self.switch_class:
            self.listbox.insert(END, self.switch_class[item])
        # self.listbox.place(x=10, y=480, width=80, height=40)
        self.listbox.bind('<<ListboxSelect>>', self.class_item_select)
        #-----------------
        self.listbox.select_set(0)
        
        scrollbar = Scrollbar(self.listbox)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set) 
        self.listbox.place(x=940, y=50, width=140, height=320)
        # self.listbox.place(x=10, y=140, width=140, height=self.size_h)
        #-------------------------------------------------------------
        
        self.classe = self.switch_class[self.switch_class.keys()[0]]
        
        self.update_img()
    
        #----------------------------------------
        
        
        label_list = Label(self, text="Marcações", bg='black', fg="white", font=("Arial", 14))
        label_list.place(x=30, y=390)
    
    
        self.list_objs = Listbox(self, selectmode=SINGLE, exportselection=False, bg='black', fg="white",)
        
        scrolobj = Scrollbar(self.list_objs)
        scrolobj.config(command=self.list_objs.yview)
        scrolobj.pack(side="right", fill="y")
        self.list_objs.config(yscrollcommand=scrolobj.set) 
        self.list_objs.place(x=10, y=420, width=140, height=320)
        self.list_objs.bind('<<ListboxSelect>>', self.list_objs_event)
            
        
        #-------------------------------------------------------------
        
        label_list = Label(self, text="Rastreio", bg='black', fg="white", font=("Arial", 14))
        label_list.place(x=940, y=390)
        
        
        self.list_track = Listbox(self, selectmode=SINGLE, exportselection=False, bg='black', fg="white",)
        
        scroltrack = Scrollbar(self.list_track)
        scroltrack.config(command=self.list_track.yview)
        scroltrack.pack(side="right", fill="y")
        self.list_track.config(yscrollcommand=scroltrack.set) 
        self.list_track.place(x=940, y=420, width=140, height=320)
        self.list_track.bind('<<ListboxSelect>>', self.list_track_event)
        
        
        #-------------------------------------------------------------
        
        self.img_atual = Label(self, text="Imagem Atual: {}".format(self.imgs[0]), bg='black', fg="white", font=("Arial", 14))
        self.img_atual.place(x=300, y=20)
        
        self.progress = Label(self, text="Progresso: {:0.3f}%".format(float(0)), bg='black', fg="white", font=("Arial", 14))
        self.progress.place(x=300, y=50)
        
        total = Label(self, text="Total: {}".format(len(self.imgs)), bg='black', fg="white", font=("Arial", 14))
        total.place(x=650, y=20)
        
        self.status = Label(self, text="Status: {}".format('Não Salvo'), bg='black', fg="white", font=("Arial", 14))
        self.status.place(x=600, y=50)
    
        #--------------------------------------------------
        lb_track = Label(self, text="Rastreio:", bg='black', fg="white", font=("Arial", 14))
        lb_track.place(x=400, y=90)
        
        
        self.ent_track = Entry(self, name="ent_track")
        self.ent_track.place(x=480, y=90, width=100, height=25)
        
        self.bt_track = Button(self, text='Gravar', bg='black', fg="white", command=self.track_handler)
        self.bt_track.place(x=600, y=90, height=25)
        #--------------------------------------------------
    
        #####
        self.load_xml(self.imgs[self.id])
        
        # reload line
        self.create_line_curso()
        
        #--------------
        
        
    def load_config(self):
        data = None
        try:
            with open('data_config.json') as data_file:    
                data = json.load(data_file)
        except Exception, e:
            print ("Erro load config.json! {}".format(e))
    
        return data

    
    def parse_index(self, data):
        new_class = dict()
        for i in data:
            new_class.update({int(i):data[i]})
        return new_class
    
    def create_line_curso(self):
        self.vertical_line = self.canvas.create_line(0, 0, 0, 0, width=2, dash=(8, 6), fill='#1CF0C3')
        self.horizontal_line = self.canvas.create_line(0, 0, 0, 0, width=2, dash=(8, 6), fill='#1CF0C3')
    
    def file_item_select(self, event):
    
        self.objetos_coo = []
        self.objetos_re_draw = []
        self.list_objs.delete(0, END)       
        self.list_track.delete(0, END)
        self.status.config(text="Status: {}".format('Não Salvo'))
        
        if self.id == len(self.imgs) - 1:
            size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
            self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]                  
            self.arquivo.write(self.salvar)
            
        
        size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
        self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]            

        self.salvar = self.salvar + "\r\n"
        self.idImagGlobal = self.idImag
        self.idImag = 0
        
        
        idx = self.list_files.curselection()[0]
        self.id = idx
        
        # add nova imagem
        self.update_img()


        #####
        self.load_xml(self.imgs[self.id])
    
        
        self.img_atual.config(text="Imagem Atual: {}".format(self.imgs[self.id]))
        percent = float((float(self.id) * 100) / float(len(self.imgs)))
        self.progress.config(text="Progresso: {:0.3f}%".format(percent))
    
    
    def read_index(self):
        with open("index.txt", "a+") as f:
            string = f.read()
            
            f.seek(0)
            f.truncate()
            f.seek(0)
        
            try:
                value = int(string)
            except:
                value = 0
            
            new_value = value + 1
            
            f.write(str(new_value))
            f.close()
            
        return new_value

    def load_xml(self, name_img):  
              
        try:
            file_anot = "{}/{}{}.xml".format(os.path.dirname(os.path.realpath(__file__)), self.path_save_anotation, name_img[:-4])
            tree = ET.parse(file_anot)
            
            
            root = tree.getroot()
    
            for obj in root.findall('object'):
                
                name = obj.find('name').text
                
                try:
                    index = str(obj.find('index').text)
                except Exception, e:
                    print "Generate index!", e
                    # index = str(random.randint(0, 1000))
                    index = str(self.read_index())
                    
                    
                
                self.ent_track.delete(0, END)
                self.ent_track.insert(0, index)
                
                # add new class becase not exists
                select_class = filter(lambda (k, v): v == name, self.switch_class.items())
                
                if len(select_class) == 0:
                    new_id = self.switch_class.keys()[-1] + 1
                    
                    self.switch_class.update({new_id:name})
                    
                    
                    self.listbox.insert(END, self.switch_class[new_id])
                
                bndbox = obj.find('bndbox')
                
                xmin = int(bndbox.find('xmin').text)
                ymin = int(bndbox.find('ymin').text)
                xmax = int(bndbox.find('xmax').text)
                ymax = int(bndbox.find('ymax').text)
                
                x1 = xmin
                y1 = ymin
                x2 = xmax
                y2 = ymax
                
                self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2            
                
                self.objetos_coo.append([name, index, self.x1, self.y1, (self.x2 - self.x1), (self.y2 - self.y1)])
                self.x1, self.y1, self.x2, self.y2 = self.dcon_x(self.x1), self.dcon_y(self.y1), self.dcon_x(self.x2), self.dcon_y(self.y2)
                self.objetos_re_draw.append([name, index, self.x1, self.y1, (self.x2 - self.x1), (self.y2 - self.y1)])
                
                        
                self.list_objs.insert(END, name)
                
                
                self.list_track.insert(END, index)
                
            
            #--------------------
            
            print 'Load:', file_anot        
            
            self.classe_info()
            
            for i, _ in enumerate(self.objetos_coo):
                self.list_objs.selection_clear(i)
                self.list_track.selection_clear(i)
            
            id_end = len(self.objetos_coo) - 1
            
            self.list_objs.select_set(id_end)
            self.list_track.select_set(id_end)
            
            self.redraw_img()
            self.recolor_img(id_end) 
            
            try:
                # seleciona a classe passado o nome da mesma    
                clas_name = self.objetos_coo[id_end][0]
                self.select_class_name(clas_name)
            except Exception, e:
                print e
            
        except Exception, e:
            print "No annotation for the image: ", name_img, e
            
            # reload line
            self.create_line_curso()
        
        
    def recolor_img(self, idx):
        # self.update_img()
        
        c, name_i, x1, y1, x2, y2 = self.objetos_re_draw[idx]
        self.classe, self.name_i, self.x1, self.y1, self.x2, self.y2 = c, name_i, x1, y1, (x2 + x1), (y2 + y1)
        
        self.canvas.create_rectangle(self.x1 - 5, self.y1 - 15, self.x1 + 60, self.y1, fill="yellow", outline='yellow', width=2)
        self.text_class = self.canvas.create_text(self.x1 + 25, self.y1 - 10, font="Arial 10", text=("{} {}").format(self.classe, self.name_i))
        
        
        self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="", outline='yellow', width=2, dash=(8, 6))
        
        b = 8    
        self.canvas.create_oval(self.x1 - b // 2, self.y1 - b // 2, self.x1 + b // 2, self.y1 + b // 2, fill="green", outline='green', width=2)
        self.rect = self.canvas.create_oval(self.x2 - b // 2, self.y2 - b // 2, self.x2 + b // 2, self.y2 + b // 2, fill="green", outline='green', width=2)
  
    def list_objs_event(self, event):
        self.redraw_img()
        idx = self.list_objs.curselection()[0]
        self.recolor_img(idx)
        
        track_value = self.list_track.get(idx)
        self.ent_track.delete(0, END)
        self.ent_track.insert(0, track_value)
        
        # reload line
        self.create_line_curso()
        
        for i, _ in enumerate(self.objetos_coo):
            self.list_track.selection_clear(i)
        self.list_track.select_set(idx)
     
    def list_track_event(self, event):
        self.redraw_img()
        idx_track = self.list_track.curselection()[0]
        

        track_value = self.list_track.get(idx_track)
        self.ent_track.delete(0, END)
        self.ent_track.insert(0, track_value)
        
        
        self.recolor_img(idx_track)

#         # reload line
        self.create_line_curso()
        
        for i, _ in enumerate(self.objetos_coo):
            self.list_track.selection_clear(i)
            self.list_objs.selection_clear(i)
        
        self.list_track.select_set(idx_track)
        self.list_objs.select_set(idx_track)
        
        #------------------------------------
    
    def track_handler(self):
        track_value = self.ent_track.get()
        print "Value: ", track_value
        
        idx = self.list_objs.curselection()[0]
        
        self.objetos_coo[idx][1] = track_value
        self.objetos_re_draw[idx][1] = track_value
        
        
        self.list_track.delete(idx, idx)
        self.list_track.insert(idx, track_value)
        
        for i, _ in enumerate(self.objetos_coo):
            self.list_track.selection_clear(i)
        self.list_track.select_set(idx)
        
        self.list_files.focus()
        
    
    def find_pos(self, key):
        for i, idx in enumerate(self.switch_class.keys()):
            if idx == key:
                return i
        return None
    
    def class_item_select(self, e):
        self.classe = self.listbox.get(self.listbox.curselection())        
        key = [key for key, value in self.switch_class.items() if value == self.classe][0]
        
        # self.canvas.itemconfig(self.text_class, text="{} {}".format(self.classe, self.name_i))

        idx = self.find_pos(key)                        
        for i, _ in enumerate(self.switch_class):
            self.listbox.selection_clear(i)
        
        self.listbox.select_set(idx)
        
        if len(self.objetos_coo) > 0:
            # print 'classe selecionada: ', self.switch_class[key]
            self.classe = self.switch_class[key]
            
            # muda o nome da classe do objeto dinamicamente
            self.canvas.itemconfig(self.text_class, text="{} {}".format(self.classe, self.name_i))
            
            list_select = self.list_objs.curselection()[0]
            
            # muda classe nas listas
            self.objetos_coo[list_select][0] = self.classe
            self.objetos_re_draw[list_select][0] = self.classe
            
            # update list box
            
            self.list_objs.delete(list_select)
            self.list_objs.insert(list_select, self.classe)
            self.list_objs.select_set(list_select)
            
            
            self.list_track.delete(list_select)
            self.list_track.insert(list_select, self.classe)
            self.list_track.select_set(list_select)


        
    # converte resolucao
    def con_x(self, x1):
        # resolucao camera
        xRes1 = self.frame.shape[1]
        # resolucao local
        xRes2 = self.size_w
        0
        a = (xRes1 * x1)
        b = xRes2
        x2 = (a - (a % b)) / b
        
        # x2=(xRes2*x1)/xRes1
        
        return x2
    
    def con_y(self, y1):
        # resolucao camera
        yRes1 = self.frame.shape[0]
        # resolucao local
        yRes2 = self.size_h
        
        a = (yRes1 * y1)
        b = yRes2
        y2 = (a - (a % b)) / b
        
        # y2=(yRes2*y1)/yRes1
        
        return y2
    
    
    # desconverte resolucao
    def dcon_x(self, x1):
        # resolucao camera
        xRes2 = self.frame.shape[1]
        # resolucao local
        xRes1 = self.size_w
        
        a = (xRes1 * x1)
        b = xRes2
        x2 = (a - (a % b)) / b
        
        # x2=(xRes2*x1)/xRes1
        
        return x2
    
    def dcon_y(self, y1):
        # resolucao camera
        yRes2 = self.frame.shape[0]
        # resolucao local
        yRes1 = self.size_h
        
        a = (yRes1 * y1)
        b = yRes2
        y2 = (a - (a % b)) / b
        
        # y2=(yRes2*y1)/yRes1
        
        return y2
    
    
    
    def select_class_name(self, clas_name):
        
        id_select_class = filter(lambda (k, v): v == clas_name, self.switch_class.items())[0][0]
                
        idx = self.find_pos(id_select_class)    
        
        for i, _ in enumerate(self.switch_class):
            self.listbox.selection_clear(i)
         
        self.listbox.select_set(idx)
        
        
        # reload line
        self.create_line_curso()
    
    
    def key_press(self, e):
        
        k = str(e.char)
        
        # para as teclas de atalho n atrapalharem na hora de digitar o track
        is_focus = True if str(self.ent_track.focus_get()).split('.')[-1] == 'ent_track' else False
        if is_focus == False:
            # troca a classe do objecto
            for key in self.switch_class.keys():
                if k == str(key):
                    
                    idx = self.find_pos(key)    
                    
                    for i, _ in enumerate(self.switch_class):
                        self.listbox.selection_clear(i)
                    
                    self.listbox.select_set(idx)
                    
                    
                    
                    if len(self.objetos_coo) > 0:
                        # print 'classe selecionada: ', self.switch_class[key]
                        self.classe = self.switch_class[key]
                        
                        # muda o nome da classe do objeto dinamicamente
                        self.canvas.itemconfig(self.text_class, text="{} {}".format(self.classe, self.name_i))
                        
                        list_select = self.list_objs.curselection()[0]
                        
                        # muda classe nas listas
                        self.objetos_coo[list_select][0] = self.classe
                        self.objetos_re_draw[list_select][0] = self.classe
                        
                        # update list box
                        
                        self.list_objs.delete(list_select)
                        self.list_objs.insert(list_select, self.classe)
                        self.list_objs.select_set(list_select)
                        
                        
                        self.list_track.delete(list_select)
                        self.list_track.insert(list_select, self.classe)
                        self.list_track.select_set(list_select)
                        
                    
        # del 127
        if k == str('c'):
            print "Itens:", len(self.canvas.find_all())
            self.canvas.delete("all")
            
            if len(self.objetos_coo) > 0:
                idx = self.list_objs.curselection()[0]
                
                self.list_objs.delete(idx)
                self.list_track.delete(idx)  
                
                self.objetos_coo.pop(idx)
                self.objetos_re_draw.pop(idx)
                
                self.redraw_img()
            
            
                self.list_objs.select_set(len(self.objetos_coo) - 1)
                self.list_track.select_set(len(self.objetos_coo) - 1)
            
                id_end = len(self.objetos_coo) - 1
                self.list_objs.select_set(id_end)
                self.list_track.select_set(id_end)
            
                
                try:
                    # seleciona a classe passado o nome da mesma    
                    clas_name = self.objetos_coo[id_end][0]
                    self.select_class_name(clas_name)
                    self.recolor_img(id_end) 
                except Exception, e:
                    print e
                
                # reload line
                self.create_line_curso()
            
        
        # grava o objeto
        if k == str('w'):
            print "Itens:", len(self.canvas.find_all())
            self.canvas.delete("all")
            
            h, w, _ = self.frame.shape
            
            print 'Anotação gerada!'
            print 'Nome imagem:', self.imgs[self.id]
            print 'Resolução: ' , (w, h) 
            print 'Objetos: ', self.objetos_coo
            print '-----------------------------------------------------'
            
            
            
            
            string = self.imgs[self.id]
            special = np.array([True if (s.isalnum() or s == "_" or s == "-" or s == ":" \
                          or s == ":" or s == "." or s == "(" or s == ")") else False for s in string])
            
            
            if len(np.where(special == False)[0]) > 0:
                
                self.imgs[self.id] = "".join(s for s in string if s.isalnum() or s == "_" or s == "-" or s == ":" \
                                             or s == ":" or s == "." or s == "(" or s == ")")
            
                os.rename(self.path_input + string, self.path_input + self.imgs[self.id])
                
                self.ge_file_xml(self.path_save_anotation, self.imgs[self.id], w, h, self.objetos_coo)
            
            else:
                self.ge_file_xml(self.path_save_anotation, self.imgs[self.id], w, h, self.objetos_coo)
            
            try:
                shutil.copy2(self.path_input + self.imgs[self.id], self.path_save_img)
            except Exception, e:
                print 'Image already exists! ', e
            
            self.objetos_coo = []
            self.objetos_re_draw = []
            self.list_objs.delete(0, END) 
            self.list_track.delete(0, END)  
            
            self.classe_info()
            
            self.status.config(text="Status: {}".format('Salvo'))
            
            # add nova imagem
            self.update_img()
            
            # reload line
            self.create_line_curso()
            
            
        
        # avanca image
        if k == str('d'):  
            print "Itens:", len(self.canvas.find_all())
            self.canvas.delete("all")
        
            if self.id < len(self.imgs) - 1:
                
                self.objetos_coo = []
                self.objetos_re_draw = []
                self.list_objs.delete(0, END)  
                self.list_track.delete(0, END)       
                self.status.config(text="Status: {}".format('Não Salvo'))
                
                if self.id == len(self.imgs) - 1:
                    size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
                    self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]                  
                    self.arquivo.write(self.salvar)
                    
                
                size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
                self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]            
    
                self.salvar = self.salvar + "\r\n"
                self.idImagGlobal = self.idImag
                self.idImag = 0
                self.id = self.id + 1
                
                # add nova imagem
                self.update_img()
        
        
                #####
                self.load_xml(self.imgs[self.id])
                
                for i, _ in enumerate(self.imgs):
                    self.list_files.selection_clear(i)
                self.list_files.select_set(self.id)
                
                # reload line
                self.create_line_curso()
            
        
        # volta image
        if k == str('a'):
            print "Itens:", len(self.canvas.find_all())
            self.canvas.delete("all")
            
            if self.id > 0:
              
            
                self.objetos_coo = []
                self.objetos_re_draw = []
                self.list_objs.delete(0, END)
                self.list_track.delete(0, END)  
                self.status.config(text="Status: {}".format('Não Salvo'))
                
                if self.id == len(self.imgs) - 1:
                    size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
                    self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]                  
                    self.arquivo.write(self.salvar)
                    
                
                size = self.salvar.find(self.imgs[self.id]) + len(self.imgs[self.id])                    
                self.salvar = self.salvar[:size] + " " + str(self.idImagGlobal) + self.salvar[size:]            
    
                self.salvar = self.salvar + "\r\n"
                self.idImagGlobal = self.idImag
                self.idImag = 0
                self.id = self.id - 1
            
                # add nova imagem
                self.update_img()
        
        
                #####
                self.load_xml(self.imgs[self.id])
                
                for i, _ in enumerate(self.imgs):
                    self.list_files.selection_clear(i)
                self.list_files.select_set(self.id)
            
                # reload line
                self.create_line_curso()
            
        
        self.img_atual.config(text="Imagem Atual: {}".format(self.imgs[self.id]))
        percent = float((float(self.id) * 100) / float(len(self.imgs)))
        self.progress.config(text="Progresso: {:0.3f}%".format(percent))
        
        if k == str('i'):
            print 'Informacoes:'
            print 'Objs:', self.objetos_coo
            print 'Draw: ', self.objetos_re_draw
            print 'Classes: ', self.switch_class
        
    
    def update_img(self):
        
        self.frame = cv2.imread(self.path_input + self.imgs[self.id], 1)
        
        frame_res = cv2.resize(self.frame.copy(), (self.size_w, self.size_h))
        im = cv2.cvtColor(frame_res, cv2.COLOR_BGR2RGB)
        a = PIL.Image.fromarray(im)
        self.tk_im = ImageTk.PhotoImage(image=a)
        
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)
        
    
    def on_button_press(self, event):
        self.redraw_img()
        
        # save mouse drag start position
        self.start_x, self.start_y = (event.x, event.y)
        self.x1, self.y1 = (event.x, event.y)
        
        if self.dist1 < self.TDIST or self.dist2 < self.TDIST:
            
            pass
            
        else:    
            self.canvas.create_rectangle(self.x1 - 5, self.y1 - 15, self.x1 + 60, self.y1, fill="green", outline='green', width=2)
            self.text_class = self.canvas.create_text(self.x1 + 25, self.y1 - 10, font="Arial 10", text=("{} {}").format(self.classe, self.name_i))
            self.rect = self.canvas.create_rectangle(self.x1, self.y1, 1, 1, fill="", outline='green', width=2, dash=(8, 6))
            
        self.status.config(text="Status: {}".format('Não Salvo'))

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
              
        if self.dist1 < self.TDIST:
            self.x1, self.y1 = curX, curY
        else:
            self.x2, self.y2 = curX, curY

        # expand rectangle as you drag the mouse
        # --
        try:
            self.canvas.coords(self.rect, self.x1, self.y1, self.x2, self.y2)
        except Exception, e:
            print e    
        # --
        
        
        if self.dist1 < self.TDIST:
             
            list_select = self.list_objs.curselection()[0]
             
            self.objetos_re_draw[list_select][2] = self.x1
            self.objetos_re_draw[list_select][3] = self.y1
             
            self.objetos_coo[list_select][2] = self.x1
            self.objetos_coo[list_select][3] = self.y1
             
            self.canvas.coords(self.rect, self.x1, self.y1, self.objetos_re_draw[list_select][2] + self.objetos_re_draw[list_select][4], \
                               self.objetos_re_draw[list_select][3] + self.objetos_re_draw[list_select][5])
            
        elif self.dist2 < self.TDIST:
             
            list_select = self.list_objs.curselection()[0]
             
            self.objetos_re_draw[list_select][4] = self.x2 - self.objetos_re_draw[list_select][2]
            self.objetos_re_draw[list_select][5] = self.y2 - self.objetos_re_draw[list_select][3]
             
            self.objetos_coo[list_select][4] = self.x2 - self.objetos_coo[list_select][2]
            self.objetos_coo[list_select][5] = self.y2 - self.objetos_coo[list_select][3]
             
            self.canvas.coords(self.rect, self.objetos_re_draw[list_select][2], self.objetos_re_draw[list_select][3], self.x2, self.y2)
        
    def on_move(self, event):
        
        curX, curY = (event.x, event.y)
              
        self.canvas.coords(self.vertical_line, curX, 0, curX, self.size_h)
        self.canvas.coords(self.horizontal_line, 0, curY, self.size_w, curY)
        
        
        list_select = self.list_objs.curselection()[0]
        
        self.dist1 = np.linalg.norm(np.array([curX, curY]) - \
                              np.array([self.objetos_re_draw[list_select][2], self.objetos_re_draw[list_select][3]]))
        
        
        self.dist2 = np.linalg.norm(np.array([curX, curY]) - \
                              np.array([self.objetos_re_draw[list_select][2] + self.objetos_re_draw[list_select][4],
                                        self.objetos_re_draw[list_select][3] + self.objetos_re_draw[list_select][5]]))
        
        
        b = 8 
        if self.dist1 < self.TDIST:
            self.canvas.create_oval(self.x1 - b // 2, self.y1 - b // 2, self.x1 + b // 2, self.y1 + b // 2, fill="white", outline='white', width=2)
        else:
            self.canvas.create_oval(self.x1 - b // 2, self.y1 - b // 2, self.x1 + b // 2, self.y1 + b // 2, fill="green", outline='green', width=2)
        
        if self.dist2 < self.TDIST:
            self.canvas.create_oval(self.x2 - b // 2, self.y2 - b // 2, self.x2 + b // 2, self.y2 + b // 2, fill="white", outline='white', width=2)
        else:
            self.canvas.create_oval(self.x2 - b // 2, self.y2 - b // 2, self.x2 + b // 2, self.y2 + b // 2, fill="green", outline='green', width=2)
        
    def on_button_release(self, event):
        
        print "Itens:", len(self.canvas.find_all())
        self.canvas.delete("all")
        
        if self.idImag == 0:
            self.salvar = self.salvar + "pos_cap/" + self.imgs[self.id]
        
#         if self.dist1 < self.TDIST or self.dist2 > self.TDIST:
#         
#             if self.y2 < self.y1:
#                 aux = self.y2
#                 self.y2 = self.y1
#                 self.y1 = aux
#             
#             if self.x2 < self.x1:
#                 aux = self.x2
#                 self.x2 = self.x1
#                 self.x1 = aux
#             
        
        if self.dist1 < self.TDIST or self.dist2 < self.TDIST:
            list_select = self.list_objs.curselection()[0]
        else:
            self.objetos_re_draw.append([self.classe, 0, self.x1, self.y1, (self.x2 - self.x1), (self.y2 - self.y1)])
       
        self.x1, self.y1, self.x2, self.y2 = self.con_x(self.x1), self.con_y(self.y1), self.con_x(self.x2), self.con_y(self.y2)
                                         
        self.salvar = self.salvar + " " + str(self.x1) + " " + str(self.y1) + " " + str(self.x2 - self.x1) + " " + str(self.y2 - self.y1)
        # roi = self.frame[self.y1 + 1:self.y2 - 1, self.x1 + 1:self.x2 - 1]        
        self.idImag = self.idImag + 1
        self.idImagGlobal = self.idImag
        # cv2.imwrite(self.path_output + str(self.imgs[self.id])[:-4] + "_" + str(self.idImagGlobal) + ".bmp", roi)
        
        if self.dist1 < self.TDIST:
            self.objetos_coo[list_select][2] = self.x1 
            self.objetos_coo[list_select][3] = self.y1
        
        elif self.dist2 < self.TDIST:
            self.objetos_coo[list_select][4] = self.x2 - self.objetos_coo[list_select][2]
            self.objetos_coo[list_select][5] = self.y2 - self.objetos_coo[list_select][3]
        
        else:
            self.objetos_coo.append([self.classe, 0, self.x1, self.y1, (self.x2 - self.x1), (self.y2 - self.y1)])
            self.list_objs.insert(END, self.classe)
        
        print "Classe: " + str(self.classe) + " | Nome: " + str(self.imgs[self.id])[:-4] + "_" + str(self.idImagGlobal) + " | Coordenadas: " + str(self.x1) + ", " + str(self.y1) + ", " + str(self.x2) + ", " + str(self.y2)
        self.classe_info()
        
        
        if self.dist1 < self.TDIST or self.dist2 < self.TDIST:
            id_end = list_select
        else:
            for i, _ in enumerate(self.objetos_coo):
                self.list_objs.selection_clear(i)
                self.list_track.selection_clear(i)
    
            id_end = len(self.objetos_coo) - 1
        
        self.list_objs.select_set(id_end)
        self.list_track.select_set(id_end)
            
        self.redraw_img()
        self.recolor_img(id_end) 
        
        # reload line
        self.create_line_curso()
        
    def redraw_img(self):
        self.update_img()
        
        for c, name_i, x1, y1, x2, y2  in self.objetos_re_draw:
            
            self.classe, self.name_i, self.x1, self.y1, self.x2, self.y2 = c, name_i, x1, y1, (x2 + x1), (y2 + y1)
            
            
            self.canvas.create_rectangle(self.x1 - 5, self.y1 - 15, self.x1 + 60, self.y1, fill="green", outline='green', width=2)
            self.text_class = self.canvas.create_text(self.x1 + 25, self.y1 - 10, font="Arial 10", text=("{} {}").format(self.classe, self.name_i))
            self.rect = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="", outline='green', width=2, dash=(8, 6))
             
    
    def classe_info(self):
        print '----------------------------------------------'
        print 'Selecione a classe de objeto:'
        print self.switch_class
        print '----------------------------------------------'
    
    def ge_file_xml(self, path_save_anotation, name_img, res_wid, res_hei, objetos_coo):
        annotation = Element('annotation')
        
        folder = SubElement(annotation, 'folder')
        folder.text = 'VOC2007'
        
        filename = SubElement(annotation, 'filename')
        filename.text = str(name_img)
        
        # source--
        source = SubElement(annotation, 'source')
        
        database = SubElement(source, 'database')
        database.text = 'The VOC2007 Database'
        
        annotation1 = SubElement(source, 'annotation')
        annotation1.text = 'PASCAL VOC2007'
        
        image = SubElement(source, 'image')
        image.text = 'flickr'
        
        flickrid = SubElement(source, 'flickrid')
        flickrid.text = '341012865'
        # source...
        
        #owner-----
        owner = SubElement(annotation, 'owner')
        
        flickrid1 = SubElement(owner, 'flickrid')
        flickrid1.text = 'me'
        
        name = SubElement(owner, 'name')
        name.text = 'Mouglas'
        # owner....
        
        
        #size-----
        size = SubElement(annotation, 'size')
        
        width = SubElement(size, 'width')
        width.text = str(res_wid)
        
        height = SubElement(size, 'height')
        height.text = str(res_hei)
        
        depth = SubElement(size, 'depth')
        depth.text = '3'
        # size....
        
        #segmented-----
        segmented = SubElement(annotation, 'segmented')
        segmented.text = '0'
        # segmented....
        
        #object-----
        for obj in objetos_coo:
            
            (type_class, name_index, x, y, w, h) = obj
            
            object = SubElement(annotation, 'object')
            
            name1 = SubElement(object, 'name')
            name1.text = str(type_class)
            
            index = SubElement(object, 'index')
            index.text = str(name_index)
            
            pose = SubElement(object, 'pose')
            pose.text = 'Unspecified'
            
            truncated = SubElement(object, 'truncated')
            truncated.text = '0'
            
            difficult = SubElement(object, 'difficult')
            difficult.text = '0'
            
            bndbox = SubElement(object, 'bndbox')
            
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(x)
            
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(y)
            
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(int(w + x))
            
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(int(h + y))
        
        # object....
            
        
        
        # files
        #==============================================
        nome_save = name_img[:-4]
        
        fileXML = open(path_save_anotation + str(nome_save) + ".xml", "w")
        fileXML.write('')
        
        fileXML = open(path_save_anotation + str(nome_save) + ".xml", "a")
        fileXML.write(tostring(annotation))
        fileXML.close()
        
        # print tostring(annotation)
    
    
    #==========================================================================================

if __name__ == "__main__":
#     root = Tk()
#     app = TKMarkCoorAnnotation(root)
#     root.mainloop()
#     
    
    app = TKMarkCoorAnnotation()
    app.master.geometry("1090x756")
    app.master.title("Marcador de Anotações em Imagens")
    
    
        
    
    app.pack(expand=YES, fill=BOTH)
    app.mainloop()
