import tkinter as tk
from tkinter import ttk # tipo um CSS para tkinter rs
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from BD import Database# as database
import mysql.connector.errors
import sys
import os

database = Database()

LARGE_FONT = ("verdana", 12)
NORM_FONT = ("verdana", 10)
SMALL_FONT = ("verdana", 8)

def path_finder(entry):
	entry.delete(0,tk.END)
	filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("jpeg files","*.png"),("all files","*.*")))
	entry.insert(0, filename)

def popupmsg(msg):
	popup = tk.Tk()

	popup.wm_title("!")
	label = ttk.Label(popup, text = msg, font = "LARGE_FONT")
	label.pack(side = "top", fill="x", pady = 10)
	button1 = ttk.Button(popup, text = "Ok", command = popup.destroy)
	button1.pack()
	popup.mainloop()

# transforma a saída em S ou N necessário no DB
def sim_nao(param):
	if param == "Sim":
		return "S"
	else:
		return "N"

def delete_listbox(listbox):
	x = listbox.get_children()
	# print ('get_children values: ', x ,'\n')
	if x != '()': # checks if there is something in the first row
		for child in x:
			listbox.delete(child)

def fill_listbox(listbox, values, flag = False):
	
	# caso a Flag = True, a invocação veio do método de ver TODOS os ítens
	if flag == True:
		if len(values) == 8 and isinstance(values, list):
			listbox.insert(parent='',index="end",values = values)
		elif len(values) == 4 and isinstance(values, list):
			listbox.insert(parent='',index="end",values = values)
		# cuida do caso em que o delete só envia uma string: o nome a ser deletado
		elif isinstance(values, str):
			listbox.insert(parent='',index="end",values = values)
	
	# os demais casos caem nesse else
	else:
		if len(values) == 8 and isinstance(values, list):
			listbox.insert('','end',values=('0',values[0].upper(),values[1].upper(),
			values[2].upper(),values[3].upper(),values[6], values[5], values[4].upper()))
		elif len(values) == 3 and isinstance(values, list):
			listbox.insert('','end',values=('0',values[0].upper(),values[1], values[2]))
		elif isinstance(values, str):
			listbox.insert('','end',values=('0',values.upper()))

def cmd_add(listbox = None, nome = None, autor = None, capa = None, 
			quantidade = None, combo_lido = None, 
			combo_tenho = None, genero = None, 
			midia = None, table = None):

	lido = sim_nao(combo_lido)
	tenho = sim_nao(combo_tenho)

	if table == "LIVRO":
		values = [nome.upper(), autor.upper(), genero.upper(),
				 		 midia.upper(), quantidade, lido, tenho, capa]
		write = [nome.upper(), autor.upper(), genero.upper(),
			 		 midia.upper(), quantidade, combo_lido, combo_tenho, capa]
	else:
		values = [nome]
		write = [nome, "Sem informação", "Sem informação"]

	# nome, autor, genero, midia, qdade, lido, tenho, capa
	database.insert(values, table)

	delete_listbox(listbox)
	fill_listbox(listbox, write)

	popupmsg("Cadastro realizado com sucesso!")


def cmd_search_all(listbox, where, like, tabela):

	delete_listbox(listbox)
	for linha in database.search(where = where, like = like, tabela = tabela):
		array = list(linha)
		if array[0] == "1":
			# pula a tupla aux de "sem informação" do DB
			pass
		else:
			for item in range(len(array)):
				if array[item] == 'S':
					array[item] = "Sim"
				elif array[item] == 'N':
					array[item] = "Não"
			fill_listbox(listbox, array, flag = True)


		#---------------------------------
		# Caso consiga arrumar os índices repetidos
		# listbox.insert(parent='',iid=linha[0],index="end",values = linha)
		#---------------------------------


def cmd_update(listbox, nome, autor, capa, quantidade, 
			combo_lido, combo_tenho, genero, midia):
	# transforma a saída em S ou N necessário no DB
	# def sim_nao(param):
	# 	if param == "Sim":
	# 		return "S"
	# 	else:
	# 		return "N"

	def selectItem(listbox):
		curItem = listbox.focus()
		old = []
		old.append(listbox.item(curItem).get('values')[0])
		old.append(listbox.item(curItem).get('values')[2])
		old.append(listbox.item(curItem).get('values')[4])
		old.append(listbox.item(curItem).get('values')[3])
		
		return old

	index = selectItem(listbox)

	lido = sim_nao(combo_lido)
	tenho = sim_nao(combo_tenho)

	database.update(index, nome.upper(), autor.upper(), genero.upper(),
			 		 midia.upper(), quantidade, lido, tenho, capa)

	x = listbox.get_children()
	if x != '()': # checks if there is something in the first row
		for child in x:
			listbox.delete(child)
	listbox.insert('','end',values=('0',nome.upper(),autor.upper(),
		genero.upper(),midia.upper(),combo_tenho, combo_lido, quantidade.upper()))

def cmd_update_one(listbox, alteracao, tabela = None):
	# transforma a saída em S ou N necessário no DB

	curItem = listbox.focus()
	
	old = []

	if tabela == "AUTOR":
		# print(listbox.item(curItem).get('values'))
		old.append(listbox.item(curItem).get('values')[0]) # SALVA INDICE DO AUTOR ANTIGO
		old.append(listbox.item(curItem).get('values')[1]) # SALVA NOME DO AUTOR ANTIGO
		old.append(listbox.item(curItem).get('values')[2]) # SALVA NOME DO LIVRO QUE TERÁ SEU AUTOR ALTERADO

	elif tabela == "CATEGORIA":
		# print(listbox.item(curItem).get('values'))
		old.append(listbox.item(curItem).get('values')[0]) # SALVA INDICE DO GENERO ANTIGO
		old.append(listbox.item(curItem).get('values')[1]) # SALVA NOME DA CATEGORIA ANTIGA
		old.append(listbox.item(curItem).get('values')[2]) # SALVA NOME DO LIVRO QUE TERÁ SUA CATEGORIA ALTERADA

	database.update_one(old, alteracao.upper(), tabela)

	x = listbox.get_children()
	if x != '()': # checks if there is something in the first row
		for child in x:
			listbox.delete(child)
	listbox.insert('','end',values=('0',alteracao.upper()))

def cmd_delete(listbox, tabela, param_id, param):

	curItem = listbox.focus()

	#indice do livro a ser deletado
	if tabela == "LIVRO":
		old_value = listbox.item(curItem).get('values')[1]
		nome =  listbox.item(curItem).get('values')[1]
	elif tabela == "AUTOR":
		old_value = listbox.item(curItem).get('values')[1]
		nome =  listbox.item(curItem).get('values')[1]
	elif tabela == "CATEGORIA":
		old_value = listbox.item(curItem).get('values')[1]
		nome =  listbox.item(curItem).get('values')[1]
	# print (index)

	database.delete(tabela, param_id, old_value, param)

	#x = listbox.get_children()
	if tabela == "LIVRO":
		delete_listbox(listbox)
		fill_listbox(listbox, nome)
	elif tabela == "AUTOR":
		delete_listbox(listbox)
		fill_listbox(listbox, nome)
	elif tabela == "CATEGORIA":
		delete_listbox(listbox)
		fill_listbox(listbox ,nome)
	popupmsg("Item apagado com sucesso!")

def quit():
	sys.exit(0)

class mainApp(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		img = Image.open (r".\img\icone.ico")
		icon = ImageTk.PhotoImage(img)
		self.tk.call('wm', 'iconphoto', self._w, icon)

		# icon = tk.PhotoImage(file=r'icone.ico')
		# icon.image = icon
		# self.tk.call('wm', 'iconphoto', self._w, icon)	
		
		tk.Tk.wm_title(self, "Biblioteca")
		container = tk.Frame(self)
		container.pack(side="top", fill='both', expand=True)
		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		# adiciona o menu
		menubar = tk.Menu(container)

		procurarMenu = tk.Menu(menubar)
		procurarMenu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label = 'Opções', menu = procurarMenu)
		procurarMenu.add_command(label = "Livro", command = lambda: self.show_frame(searchBook)) #command = lambda: popupmsg("not supported yet!"))
		procurarMenu.add_command(label = "Autor", command = lambda: self.show_frame(searchAuthor))
		procurarMenu.add_command(label = "Mídia", command = lambda: self.show_frame(searchMidia))
		procurarMenu.add_command(label = "Gênero", command = lambda: self.show_frame(searchGenre))
		procurarMenu.add_command(label = "Empréstimo", command = lambda: popupmsg("not supported yet!"))
		procurarMenu.add_command(label = "Loja", command = lambda: popupmsg("not supported yet!"))

		menubar.add_command(label = "Sair", command = quit)

		tk.Tk.config(self, menu = menubar)

		# dic que conterá todas as telas existentes no programa
		self.frames = {}

		# o 'F' representa a palavra Frame, ou seja, para cada
		# Frame carregado, faça...
		for F in (StartPage, searchBook, searchAuthor, searchMidia, 
			searchGenre):	
			frame = F(container, self)

			self.frames[F] = frame

			frame.grid(row = 0, column = 0, sticky = 'nsew')

		self.show_frame(StartPage)

	def show_frame(self, controller):
		frame = self.frames[controller]

		#trás a janela desejada para frente da tela
		frame.tkraise()

class StartPage(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = tk.Label(self, text = 'Start Page', font = LARGE_FONT)

		photo = tk.PhotoImage(file = r".\img\livros.gif")
		label_photo = tk.Label(self, image = photo)
		label.image = photo
		label_photo.pack()

class searchBook(tk.Frame):

	def __init__(self, parent, controller):

		def get_selected_row(event,img):
			try:
				global tupla_escolhida
				indice=listbox.selection()[0]
				tupla_escolhida=listbox.item(listbox.selection()[0])['values']
				
				entryNome.delete(0,tk.END)
				entryNome.insert(tk.END,tupla_escolhida[1])
				entryAutor.delete(0,tk.END)
				entryAutor.insert(tk.END,tupla_escolhida[2])
				entryGenero.delete(0,tk.END)
				entryGenero.insert(tk.END,tupla_escolhida[3])
				combobox_midia.set(tupla_escolhida[4])
				combobox_read.set(tupla_escolhida[6])
				combobox_own.set(tupla_escolhida[5])
				entryQuantidade.delete(0,tk.END)
				entryQuantidade.insert(tk.END,tupla_escolhida[7])	

				cover = database.search_cover(tupla_escolhida[1])
				cover = cover[0][0]
				img = cover

				entryCapa.delete(0,tk.END)
				entryCapa.insert(tk.END,cover)
				
				label = tk.Label(self, text = 'Start Page', font = LARGE_FONT)

				try:
					# entryCapa.delete(0,tk.END)
					img = Image.open (cover)
					img = img.resize ((200, 291))
					photo = ImageTk.PhotoImage(img)
					label_photo = ttk.Label(self, image = photo)
					label.image = photo
					label_photo.grid(column = 7, row = 1, rowspan = 1000, columnspan = 1000)
				except FileNotFoundError as err:
					# entryCapa.delete(0,tk.END)
					img = Image.open (r".\capas\SEM-IMAGEM.jpg")
					img = img.resize ((200, 291))
					photo = ImageTk.PhotoImage(img)
					label_photo = ttk.Label(self, image = photo)
					label.image = photo
					label_photo.grid(column = 7, row = 1, rowspan = 1000, columnspan = 1000)

			except IndexError:
				pass

		tk.Frame.__init__(self, parent)
		label1 = ttk.Label(self, text = 'Procurar Livro', font = LARGE_FONT)
		label1.grid(column  = 0, row = 0)

		labelNome = ttk.Label(self, text = 'Livro', font = LARGE_FONT)
		labelNome.grid(column  = 0, row = 1)

		entryNome = ttk.Entry(self)
		entryNome.grid(column  = 1, row = 1)

		labelAutor = ttk.Label(self, text = 'Autor', font = LARGE_FONT)
		labelAutor.grid(column  = 2, row = 1)

		entryAutor = ttk.Entry(self)
		entryAutor.grid(column  = 3, row = 1)

		labelGenero = ttk.Label(self, text = 'Gênero', font = LARGE_FONT)
		labelGenero.grid(column  = 4, row = 1)

		entryGenero = ttk.Entry(self)
		entryGenero.grid(column  = 5, row = 1)

		labelMidia = ttk.Label(self, text = 'Mídia', font = LARGE_FONT)
		labelMidia.grid(column  = 0, row = 2)

		box_midia_value = tk.StringVar()
		combobox_midia = ttk.Combobox(self, textvariable = box_midia_value, state="readonly", width = 17)
		combobox_midia['values'] = ('AUDIOBOOK', 'EBOOK', 'FÍSICO')
		combobox_midia.grid(column = 1, row = 2)

		labelQuantidade = ttk.Label(self, text = 'Quantidade', font = LARGE_FONT)
		labelQuantidade.grid(column  = 2, row = 2)

		entryQuantidade = ttk.Entry(self)
		entryQuantidade.grid(column  = 3, row = 2)

		labelLido = ttk.Label(self, text = 'Lido', font = LARGE_FONT)
		labelLido.grid(column  = 4, row = 2)

		box_read_value = tk.StringVar()
		combobox_read = ttk.Combobox(self, textvariable = box_read_value, state="readonly", width = 17)
		combobox_read['values'] = ('Sim', 'Não')
		combobox_read.grid(column = 5, row = 2)

		labelPossuo = ttk.Label(self, text = 'Possuo', font = LARGE_FONT)
		labelPossuo.grid(column  = 0, row = 3)

		box_own_value = tk.StringVar()
		combobox_own = ttk.Combobox(self, textvariable = box_own_value, state="readonly", width = 17)
		combobox_own['values'] = ('Sim', 'Não')

		combobox_own.grid(column = 1, row = 3)

		labelCapa = ttk.Label(self, text = 'Capa', font = LARGE_FONT)
		labelCapa.grid(column  = 2, row = 3)

		entryCapa = ttk.Entry(self)
		entryCapa.grid(column  = 3, row = 3)

		buttonPath = ttk.Button(self, text = "...", 
								command = lambda: path_finder(entryCapa), 
								width = 4)
		buttonPath.grid(column = 4, row = 3, sticky = tk.W)

		buttonBook = ttk.Button(self, text = "Procurar livro", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "L.NOME", like = entryNome.get(), tabela = "LIVRO"))
		buttonBook.grid(column = 0, row = 7)	

		buttonAll = ttk.Button(self, text = "Ver todos", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "L.NOME", like = "", tabela = "LIVRO"))
		buttonAll.grid(column = 1, row = 7)

		buttonUpdate = ttk.Button(self, text = "Alterar cadastro", 
								command = lambda: cmd_update(listbox = listbox,
								nome = entryNome.get(), autor = entryAutor.get(), 
								capa = entryCapa.get(), quantidade = entryQuantidade.get(),
								combo_lido = combobox_read.get(), combo_tenho = combobox_own.get(),
								genero = entryGenero.get(), midia = combobox_midia.get()))
		buttonUpdate.grid(column = 2, row = 7)

		buttonDelete = ttk.Button(self, text = "Deletar", 
								command = lambda: cmd_delete(listbox = listbox,
								tabela = "LIVRO", param_id = "IDLIVRO", param = "NOME"))
		buttonDelete.grid(column = 3, row = 7)

		# nome, autor, capa, quantidade, combo_lido, combo_tenho
		buttonAdd = ttk.Button(self, text = "Cadastrar", 
								command = lambda: cmd_add(listbox,
								entryNome.get(), entryAutor.get(), 
								entryCapa.get(), entryQuantidade.get(),
								combobox_read.get(), combobox_own.get(),
								entryGenero.get(), combobox_midia.get(),
								table = "LIVRO"))
		buttonAdd.grid(column = 4, row = 7)	

		img = "livros.gif"

		listbox = ttk.Treeview(self)
		listbox.grid(row=4,column=0,rowspan=3,columnspan=6,sticky=tk.W+tk.E+tk.N+tk.S)
		
		#L.IDLIVRO, L.NOME, A.NOME,C.CATEGORIA, T.TIPO, L.QUANTIDADE
		listbox['columns'] = ('id','Nome', 'Autor', 'Genero', 'Tipo', 'Tenho', 'Lido', 'Quantidade')

		listbox.heading("#0", text='Id')
		listbox.column("#0", stretch=tk.NO, width=0)

		listbox.heading("id", text='ID Livro')
		listbox.column("id", stretch=tk.NO, width=70)

		listbox.heading('Nome', text='Nome do livro')
		listbox.column("Nome", stretch=tk.NO, width=300)

		listbox.heading('Autor', text='Autor')
		listbox.column("Autor", stretch=tk.NO, width=120)

		listbox.heading('Genero', text='Gênero')
		listbox.column("Genero", stretch=tk.NO, width=120)

		listbox.heading('Tipo', text='Mídia')
		listbox.column("Tipo", stretch=tk.NO, width=120)

		listbox.heading('Tenho', text='Tenho')
		listbox.column("Tenho", stretch=tk.NO, width=70)

		listbox.heading('Lido', text='Lido')
		listbox.column("Lido", stretch=tk.NO, width=70)

		listbox.heading('Quantidade', text='Quantidade')
		listbox.column("Quantidade", stretch=tk.NO, width=70)

		listbox.bind('<<TreeviewSelect>>',lambda event, img = img: 
			get_selected_row(event, img))

		scroll = ttk.Scrollbar(self)
		scroll.grid(row=4,column=6,rowspan=3, sticky=tk.N+tk.S)

		listbox.configure(yscrollcommand=scroll.set)
		scroll.configure(command=listbox.yview)


class searchAuthor(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text = 'Author', font = LARGE_FONT)
		label.grid(column  = 0, row = 0)

		entry = ttk.Entry(self)
		entry.grid(column  = 1, row = 0)

		buttonBook = ttk.Button(self, text = "Procurar autor", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "A.NOME", like = entry.get(), tabela = "AUTOR"))
		buttonBook.grid(column = 0, row = 7)	

		buttonAll = ttk.Button(self, text = "Ver todos", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "A.NOME", like = "", tabela = "AUTOR"))
		buttonAll.grid(column = 1, row = 7)

		buttonUpdate = ttk.Button(self, text = "Alterar cadastro", 
								command = lambda: cmd_update_one(listbox = listbox,
								alteracao = entry.get(), tabela = "AUTOR"))
		buttonUpdate.grid(column = 2, row = 7)

		buttonDelete = ttk.Button(self, text = "Deletar", 
								command = lambda: cmd_delete(listbox = listbox,
								tabela = "AUTOR", param_id = "IDAUTOR", param = "NOME"))
		buttonDelete.grid(column = 3, row = 7)

		buttonAdd = ttk.Button(self, text = "Adiciona Autor", 
								command = lambda: cmd_add(listbox  = listbox, nome = entry.get().upper(), table = "AUTOR"))
		buttonAdd.grid(column = 4, row = 7)

		listbox = ttk.Treeview(self)
		listbox.grid(row=4,column=0,rowspan=3,columnspan=100,sticky=tk.W+tk.E+tk.N+tk.S)

		listbox['columns'] = ('id','Autor', 'Nome', 'Genero')

		listbox.heading("#0", text='Id')
		listbox.column("#0", stretch=tk.NO, width=0)

		listbox.heading("id", text='ID Livro')
		listbox.column("id", stretch=tk.NO, width=70)

		listbox.heading('Nome', text='Nome do livro')
		listbox.column("Nome", stretch=tk.NO, width=300)

		listbox.heading('Autor', text='Autor')
		listbox.column("Autor", stretch=tk.NO, width=120)

		listbox.heading('Genero', text='Gênero')
		listbox.column("Genero", stretch=tk.NO, width=120)

		scroll = ttk.Scrollbar(self)
		scroll.grid(row=4,column=101,rowspan=3, sticky=tk.N+tk.S)

		listbox.configure(yscrollcommand=scroll.set)
		scroll.configure(command=listbox.yview)

class searchGenre(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		label = ttk.Label(self, text = 'Genre', font = LARGE_FONT)
		label.grid(column  = 0, row = 0)

		entry = ttk.Entry(self)
		entry.grid(column  = 1, row = 0)

		buttonBook = ttk.Button(self, text = "Procurar gênero", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "C.CATEGORIA", like = entry.get(), tabela = "CATEGORIA"))
		buttonBook.grid(column = 0, row = 7)	

		buttonAll = ttk.Button(self, text = "Ver todos", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "C.CATEGORIA", like = "", tabela = "CATEGORIA"))
		buttonAll.grid(column = 1, row = 7)

		buttonUpdate = ttk.Button(self, text = "Alterar cadastro", 
								command = lambda: cmd_update_one(listbox = listbox,
								alteracao = entry.get(), tabela = "CATEGORIA"))
		buttonUpdate.grid(column = 2, row = 7)

		buttonDelete = ttk.Button(self, text = "Deletar", 
								command = lambda: cmd_delete(listbox = listbox,
								tabela = "CATEGORIA", param_id = "IDCATEGORIA", param = "CATEGORIA"))
		buttonDelete.grid(column = 3, row = 7)

		buttonAdd = ttk.Button(self, text = "Adiciona Gênero", 
								command = lambda: cmd_add(listbox  = listbox, nome = entry.get().upper(), table = "CATEGORIA"))
		buttonAdd.grid(column = 4, row = 7)

		listbox = ttk.Treeview(self)
		listbox.grid(row=4,column=0,rowspan=3,columnspan=100,sticky=tk.W+tk.E+tk.N+tk.S)

		listbox['columns'] = ('id','Categoria', 'Livro', 'Autor')

		listbox.heading("#0", text='Id')
		listbox.column("#0", stretch=tk.NO, width=0)

		listbox.heading("id", text='ID Categoria')
		listbox.column("id", stretch=tk.NO, width=100)

		listbox.heading('Categoria', text='Categoria')
		listbox.column("Categoria", stretch=tk.NO, width=140)

		listbox.heading('Livro', text='Nome do livro')
		listbox.column("Livro", stretch=tk.NO, width=300)

		listbox.heading('Autor', text='Autor')
		listbox.column("Autor", stretch=tk.NO, width=120)

		scroll = ttk.Scrollbar(self)
		scroll.grid(row=4,column=101,rowspan=3, sticky=tk.N+tk.S)

		listbox.configure(yscrollcommand=scroll.set)
		scroll.configure(command=listbox.yview)
		
class searchMidia(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		buttonAll = ttk.Button(self, text = "Search All Midia", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "", tabela = "TIPO"))
		buttonAll.grid(column = 0, row = 0)

		buttonEbook = ttk.Button(self, text = "Search E-book", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "EBOOK", tabela = "TIPO"))
		buttonEbook.grid(column = 1, row = 0)	

		buttonAudiobook = ttk.Button(self, text = "Search Audiobook", 
									command = lambda: cmd_search_all(listbox = listbox, 
									where = "T.TIPO", like = "AUDIOBOOK", tabela = "TIPO"))
		buttonAudiobook.grid(column = 2, row = 0)	

		buttonBook = ttk.Button(self, text = "Search Book", 
								command = lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "FISICO", tabela = "TIPO"))
		buttonBook.grid(column = 3, row = 0)

		listbox = ttk.Treeview(self)
		listbox.grid(row=4,column=0,rowspan=3,columnspan=100,sticky=tk.W+tk.E+tk.N+tk.S)

		listbox['columns'] = ('id','Nome', 'Autor', 'Genero')#, 'Tipo', 'Quantidade')

		listbox.heading("#0", text='Id')
		listbox.column("#0", stretch=tk.NO, width=0)

		listbox.heading("id", text='ID Livro')
		listbox.column("id", stretch=tk.NO, width=70)

		listbox.heading('Nome', text='Nome do livro')
		listbox.column("Nome", stretch=tk.NO, width=300)

		listbox.heading('Autor', text='Autor')
		listbox.column("Autor", stretch=tk.NO, width=120)

		listbox.heading('Genero', text='Gênero')
		listbox.column("Genero", stretch=tk.NO, width=120)

		scroll = ttk.Scrollbar(self)
		scroll.grid(row=4,column=101,rowspan=3, sticky=tk.N+tk.S)

		listbox.configure(yscrollcommand=scroll.set)
		scroll.configure(command=listbox.yview)


if __name__ == "__main__":
	app = mainApp()
	app.mainloop()