import tkinter as tk
from tkinter import ttk # tipo um CSS para tkinter rs
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from BD import Database# as database
import mysql.connector.errors
import sys

database = Database()

LARGE_FONT = ("verdana", 12)
NORM_FONT = ("verdana", 10)
SMALL_FONT = ("verdana", 8)

def path_finder(entry):
	entry.delete(0,tk.END)
	filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("png files","*.png"),("gif files","*.gif"), ("all files","*.*")))
	# filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("all files","*.*")))
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

def delete_entries(entries):
	try:
		for item in entries:
			if type(item) == tk.ttk.Entry:
				item.delete(0,tk.END)
			else:
				item.set('')
	except TypeError as e:
		pass


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

def cmd_add(listbox = None, entries = None, nome = None, autor = None, capa = None, 
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

	delete_entries(entries)

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
		old.append(listbox.item(curItem).get('values')[0]) # SALVA INDICE DO AUTOR ANTIGO
		old.append(listbox.item(curItem).get('values')[1]) # SALVA NOME DO AUTOR ANTIGO
		old.append(listbox.item(curItem).get('values')[2]) # SALVA NOME DO LIVRO QUE TERÁ SEU AUTOR ALTERADO

	elif tabela == "CATEGORIA":
		old.append(listbox.item(curItem).get('values')[0]) # SALVA INDICE DO GENERO ANTIGO
		old.append(listbox.item(curItem).get('values')[1]) # SALVA NOME DA CATEGORIA ANTIGA
		old.append(listbox.item(curItem).get('values')[2]) # SALVA NOME DO LIVRO QUE TERÁ SUA CATEGORIA ALTERADA

	database.update_one(old, alteracao.upper(), tabela)

	x = listbox.get_children()
	if x != '()': # checks if there is something in the first row
		for child in x:
			listbox.delete(child)
	listbox.insert('','end',values=('0',alteracao.upper()))

def cmd_delete(listbox, entries, tabela, param_id, param):

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

	delete_entries(entries)
	popupmsg("Item apagado com sucesso!")

def quit():
	sys.exit(0)

class mainApp(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		img = Image.open (r".\img\icone.ico")
		icon = ImageTk.PhotoImage(img)
		self.tk.call('wm', 'iconphoto', self._w, icon)	
		
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

def basicListboxScroll(self, gridList, spanList, gridScroll, spanScroll, columnName, text, img = None):

	listbox = ttk.Treeview(self)
	listbox.grid(column = gridList[0], row = gridList[1],
				columnspan = spanList[0], rowspan = spanList[1], sticky=tk.W+tk.E+tk.N+tk.S)
	listbox['columns'] = columnName

	def basicColumn(text = None, stretch = None, width = None, columnName = None):		
		
		listbox.heading("#0", text='Id')
		listbox.column("#0", stretch=tk.NO, width=0)

		for i, column in enumerate(columnName):
			if i == 0 or i > 4:
				listbox.heading(columnName[i], text = text[i])
				listbox.column(columnName[i], stretch = tk.NO, width = 70)
			elif i == 1:
				listbox.heading(columnName[i], text = text[i])
				listbox.column(columnName[i], stretch = tk.NO, width = 330)
			else:
				listbox.heading(columnName[i], text = text[i])
				listbox.column(columnName[i], stretch = tk.NO, width = 150)


	basicColumn(text = text, columnName = columnName)
	scroll = ttk.Scrollbar(self)
	scroll.grid(column = gridScroll[0], row = gridScroll[1], rowspan = spanScroll, sticky=tk.N+tk.S)

	listbox.configure(yscrollcommand = scroll.set)
	scroll.configure(command = listbox.yview)

	return listbox

def basicButton(self, text, grid, pressCommand, width = None, sticky = None):
	button = ttk.Button(self, text = text, 
							command = pressCommand, width = width)
	button.grid(column = grid[0], row = grid[1], sticky = sticky)

def manyButtons(self, frame, nameList, gridList, commandList, widthList, stickyList):
	for i in range(len(nameList)):
		basicButton(self, nameList[i], gridList[i], commandList[i], widthList[i], stickyList[i])

def basicCombobox(self, values, grid):
	box = tk.StringVar()
	combobox = ttk.Combobox(self, textvariable = box, state="readonly", width = 17)
	combobox['values'] = values
	combobox.grid(column = grid[0], row = grid[1])

	return combobox

def basicLabel(self, text, font, grid):
	label = ttk.Label(self, text = text, font = font)
	label.grid(column  = grid[0], row = grid[1])	

def manyLabels(self, frame, nameList, fontList, gridList):
	for i in range(len(nameList)):
		basicLabel(self, nameList[i], fontList[i], gridList[i])	

def basicEntry(self, grid):
	entry = ttk.Entry(self)
	entry.grid(column  = grid[0], row = grid[1])

	return entry

class searchBook(tk.Frame):

	def __init__(self, parent, controller):

		def get_selected_row(event,img):
			try:
				global tupla_escolhida

				indice=listbox.selection()[0]
				# recebendo os valores recebidos com o clique na listbox
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
					img = Image.open (cover)
					img = img.resize ((200, 291))
					photo = ImageTk.PhotoImage(img)
					label_photo = ttk.Label(self, image = photo)
					label.image = photo
					label_photo.grid(column = 7, row = 1, rowspan = 1000, columnspan = 1000)
				except (FileNotFoundError, AttributeError) as err:
					img = Image.open (r".\capas\SEM-IMAGEM.jpg")
					img = img.resize ((200, 291))
					photo = ImageTk.PhotoImage(img)
					label_photo = ttk.Label(self, image = photo)
					label.image = photo
					label_photo.grid(column = 7, row = 1, rowspan = 1000, columnspan = 1000)

			except IndexError:
				pass

		tk.Frame.__init__(self, parent)

		nameList = ['Procurar Livro', "livro", "Autor", "Gênero", "Mídia", "Quantidade", "Lido", "Possuo", "Capa"]
		fontList = [LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT, LARGE_FONT]
		gridList = [[0,0], [0,1], [2,1], [4,1], [0,2], [2,2], [4,2], [0,3], [2,3]]
		manyLabels(self, "searchBook", nameList, fontList, gridList)

		entryNome = basicEntry(self, [1,1])

		entryAutor = basicEntry(self, [3,1])

		entryGenero = basicEntry(self, [5,1])

		values = ['AUDIOBOOK', 'EBOOK', 'FÍSICO']
		combobox_midia = basicCombobox(self, values, [1,2])

		entryQuantidade = basicEntry(self, [3,2])

		values = ['Sim', 'Não']
		combobox_read = basicCombobox(self, values, [5,2])

		values = ['Sim', 'Não']
		combobox_own = basicCombobox(self, values, [1,3])

		entryCapa = basicEntry(self, [3,3])

		entries = [entryNome, entryAutor, entryGenero, entryQuantidade, entryCapa, 
					combobox_midia, combobox_read, combobox_own]

		nameList = ["...", "Procurar livro", "Ver todos", "Alterar cadastro", "Deletar", "Cadastrar", "Limpar campos"]
		gridList = [[4,3], [0,7], [1,7], [2,7], [3,7], [4,7], [5,3]]
		commandList = [lambda: path_finder(entryCapa), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "L.NOME", like = entryNome.get(), tabela = "LIVRO"), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "L.NOME", like = "", tabela = "LIVRO"), 
						lambda: cmd_update(listbox = listbox,
								nome = entryNome.get(), autor = entryAutor.get(), 
								capa = entryCapa.get(), quantidade = entryQuantidade.get(),
								combo_lido = combobox_read.get(), combo_tenho = combobox_own.get(),
								genero = entryGenero.get(), midia = combobox_midia.get()), 
						lambda: cmd_delete(listbox = listbox, entries = entries,
								tabela = "LIVRO", param_id = "IDLIVRO", param = "NOME"), 
						lambda: cmd_add(listbox, entries,
								entryNome.get(), entryAutor.get(), 
								entryCapa.get(), entryQuantidade.get(),
								combobox_read.get(), combobox_own.get(),
								entryGenero.get(), combobox_midia.get(),
								table = "LIVRO"),
						lambda: delete_entries(entries)]

		widthList = [4, 0, 0, 0, 0, 0, 0]
		stickyList = [tk.W, None, None, None, None, None, None]

		manyButtons(self, "searchBook", nameList, gridList, commandList, widthList, stickyList)

		img = "livros.gif"

		columnName = ()
		columnName = ('id','Nome', 'Autor', 'Genero', 'Tipo', 'Tenho', 'Lido', 'Quantidade')
		text = ['ID Livro', 'Nome do livro', 'Autor', 'Gênero', 'Mídia', 'Tenho', 'Lido', 'Quantidade']

		listbox = basicListboxScroll(self, [0,4], [6,3], [6,4], 3, columnName, text, img)

		listbox.bind('<<TreeviewSelect>>',lambda event, img = img: 
			get_selected_row(event, img))

class searchAuthor(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)

		basicLabel(self, "Autor", LARGE_FONT, [0,0])

		entry = basicEntry(self, [1,0])

		nameList = ["Procurar autor", "Ver todos", "Alterar cadastro", "Deletar", "Cadastrar"]
		gridList = [[0,7], [1,7], [2,7], [3,7], [4,7]]
		commandList = [lambda: cmd_search_all(listbox = listbox, 
								where = "A.NOME", like = entry.get(), tabela = "AUTOR"), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "A.NOME", like = "", tabela = "AUTOR"), 
						lambda: cmd_update_one(listbox = listbox,
								alteracao = entry.get(), tabela = "AUTOR"), 
						lambda: cmd_delete(listbox = listbox, entries = None,
								tabela = "AUTOR", param_id = "IDAUTOR", param = "NOME"), 
						lambda: cmd_add(listbox  = listbox, nome = entry.get().upper(), table = "AUTOR")]

		widthList = [0, 0, 0, 0, 0]
		stickyList = [None, None, None, None, None]

		manyButtons(self, "searchAuthor", nameList, gridList, commandList, widthList, stickyList)

		columnName = ()
		columnName = ('id','Autor', 'Nome', 'Genero')
		text = ['ID Livro', 'Autor', 'Nome', 'Gênero']

		listbox = basicListboxScroll(self, [0,4], [6,3], [6,4], 3, columnName, text)

class searchGenre(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		basicLabel(self, 'Categoria', LARGE_FONT, [0,0])

		entry = basicEntry(self, [1,0])

		nameList = ["Procurar categoria", "Ver todos", "Alterar cadastro", "Deletar", "Cadastrar"]
		gridList = [[0,7], [1,7], [2,7], [3,7], [4,7]]
		commandList = [lambda: cmd_search_all(listbox = listbox, 
								where = "C.CATEGORIA", like = entry.get(), tabela = "CATEGORIA"), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "C.CATEGORIA", like = "", tabela = "CATEGORIA"), 
						lambda: cmd_update_one(listbox = listbox,
								alteracao = entry.get(), tabela = "CATEGORIA"), 
						lambda: cmd_delete(listbox = listbox, entries = None,
								tabela = "CATEGORIA", param_id = "IDCATEGORIA", param = "CATEGORIA"), 
						lambda: cmd_add(listbox  = listbox, nome = entry.get().upper(), table = "CATEGORIA")]

		widthList = [0, 0, 0, 0, 0]
		stickyList = [None, None, None, None, None]

		manyButtons(self, "searchAuthor", nameList, gridList, commandList, widthList, stickyList)

		columnName = ()
		columnName = ('id','Categoria', 'Nome', 'AutorAutor')
		text = ['ID Livro', 'Categoria', 'Nome', 'Autor']

		listbox = basicListboxScroll(self, [0,4], [6,3], [6,4], 3, columnName, text)

class searchMidia(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		nameList = ["Procurar tudo", "Procurar E-book", "Procurar Audiobook", "Procurar Físico"]
		gridList = [[0,0], [1,0], [2,0], [3,0]]
		commandList = [lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "", tabela = "TIPO"), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "EBOOK", tabela = "TIPO"), 
						lambda: cmd_search_all(listbox = listbox, 
									where = "T.TIPO", like = "AUDIOBOOK", tabela = "TIPO"), 
						lambda: cmd_search_all(listbox = listbox, 
								where = "T.TIPO", like = "FISICO", tabela = "TIPO")]

		widthList = [0, 0, 0, 0, 0]
		stickyList = [None, None, None, None, None]

		manyButtons(self, "Procurar E-book", nameList, gridList, commandList, widthList, stickyList)

		columnName = ()
		columnName = ('id','Nome', 'Autor', 'Genero')
		text = ['id','Nome', 'Autor', 'Genero']

		listbox = basicListboxScroll(self, [0,4], [6,3], [6,4], 3, columnName, text)

if __name__ == "__main__":
	app = mainApp()
	app.mainloop()