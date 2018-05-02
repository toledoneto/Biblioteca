import mysql.connector
import tkinter as tk
from tkinter import ttk

def popupmsg(msg):
	popup = tk.Tk()

	popup.wm_title("!")
	label = ttk.Label(popup, text = msg, font = "NORM_FONT")
	label.pack(side = "top", fill="x", pady = 10)
	button1 = ttk.Button(popup, text = "Ok", command = popup.destroy)
	button1.pack()
	popup.mainloop()

# São necessárias cinco operações:
# 1. inserir dados
# 2. atualizar dados
# 3. buscar dados
# 4. deletar dados
# 5. ligar as tabelas associativas

class Database:

	# cria a conexão inicial com o DB e cria um cursor para
	# executar as querries
	def __init__(self):
		self.connection = mysql.connector.connect(user='root', password = '1234', host = '127.0.0.1', 
											database = 'biblioteca')
		self.cursor = self.connection.cursor()

	# função de busca no banco. Usada pelas buscas para printar na listbox os valores
	# retornados pela querry de consula. A função é divida em três possibilidades
	# já que são três listboxes diferentes que podem ser preenchidas, dependendo de
	# onde foi invocada a querry

	# função para buscar as capas dos livros e mostrar quando clicar no lisbox
	# com os dados desejados
	def search_cover(self, name):

		self.cursor.execute("""SELECT IFNULL(L.CAPA, "Sem informação")
							FROM LIVRO L 
							WHERE L.NOME = "%s" """ 
							%(name))

		cover = self.cursor.fetchall()

		return cover


	# função nº 3: buscar dados
	def search(self, where, like, tabela):

		# caso seja invocado pela aba de livros ou tipo de mídia
		# ambas possuem a mesma estrutura de listbox
		if tabela == "LIVRO" or tabela == "TIPO" :
			self.cursor.execute("""SELECT IFNULL(L.IDLIVRO, "Sem informação"), 
									 IFNULL(L.NOME, "Sem informação"), 
									 IFNULL(A.NOME, "Sem informação"), 
									 IFNULL(C.CATEGORIA, "Sem informação"), 
									 IFNULL(T.TIPO, "Sem informação"), 
									 IFNULL(L.POSSUO, "Sem informação"), 
									 IFNULL(L.LIDO, "Sem informação"),  
									 IFNULL(L.QUANTIDADE, "Sem informação")
								FROM LIVRO L 
								LEFT JOIN AUTORIA AU ON AU.ID_LIVRO = L.IDLIVRO
								LEFT JOIN AUTOR A ON A.IDAUTOR = AU.ID_AUTOR 
								LEFT JOIN LIVRO_CATEGORIA LC ON LC.ID_LIVRO = L.IDLIVRO
								LEFT JOIN CATEGORIA C ON C.IDCATEGORIA = LC.ID_CATEGORIA
								LEFT JOIN LIVRO_TIPO LT ON LT.ID_LIVRO = L.IDLIVRO
								LEFT JOIN TIPO T ON T.IDTIPO = LT.ID_TIPO 
								WHERE %s LIKE %s 
								ORDER BY L.IDLIVRO """ 
								%(where , "\"" + "%" +like+ "%" + "\""))
		
		# invocada pela pesquisa de autores
		elif tabela == "AUTOR":
			self.cursor.execute("""SELECT IFNULL(A.IDAUTOR, "Sem informação"), 
									 IFNULL(A.NOME, "Sem informação"), 
									 IFNULL(L.NOME, "Sem informação"), 
									 IFNULL(C.CATEGORIA, "Sem informação")
								FROM LIVRO L 
								RIGHT JOIN AUTORIA AU ON AU.ID_LIVRO = L.IDLIVRO
								RIGHT JOIN AUTOR A ON A.IDAUTOR = AU.ID_AUTOR 
								LEFT JOIN LIVRO_CATEGORIA LC ON LC.ID_LIVRO = L.IDLIVRO
								LEFT JOIN CATEGORIA C ON C.IDCATEGORIA = LC.ID_CATEGORIA
								WHERE %s LIKE %s 
								ORDER BY A.IDAUTOR """
								 %(where , "\"" + "%" +like+ "%" + "\""))

		# invocada pela pesquisa de categorias
		elif tabela == "CATEGORIA":
			self.cursor.execute("""SELECT IFNULL(C.IDCATEGORIA, "Sem informação"), 
									 IFNULL(C.CATEGORIA, "Sem informação"), 
									 IFNULL(L.NOME, "Sem informação"), 
									 IFNULL(A.NOME, "Sem informação")
								FROM LIVRO L 
								LEFT JOIN AUTORIA AU 
								ON AU.ID_LIVRO = L.IDLIVRO
								LEFT JOIN AUTOR A 
								ON A.IDAUTOR = AU.ID_AUTOR 
								RIGHT JOIN LIVRO_CATEGORIA LC 
								ON LC.ID_LIVRO = L.IDLIVRO
								RIGHT JOIN CATEGORIA C 
								ON C.IDCATEGORIA = LC.ID_CATEGORIA
								WHERE %s LIKE %s 
								ORDER BY C.IDCATEGORIA """
								%(where , "\"" + "%" +like+ "%" + "\""))
		
		# retorna os dados a serem mostrados após pesquisa
		data = self.cursor.fetchall()

		return data

	# Função nº 5: responsável por linkar as tabelas associativas do BD:
	# Livro -> Livro_Tipo <- Tipo
	# Livro -> Livro_Catagoria <- Categoria
	# Livro -> Autoria <- Autor
	# Sua invocação se dá no apenas cadastro de um novo livro, em que todos
	# os dados necessários são fornecidos
	def link_all(self, nomeLivro, nomeAutor, nomeTipo, nomeGenero):

		# insere o autor passado, caso já exista, ignora a querry de inserção
		self.cursor.execute("""INSERT IGNORE INTO AUTORIA VALUES(NULL,
							(SELECT IDLIVRO FROM LIVRO
							WHERE LIVRO.NOME = "%s"),
							(SELECT IDAUTOR FROM AUTOR 
							WHERE AUTOR.NOME = "%s")
							)""" %(nomeLivro, nomeAutor))

		# insere o tipo de mídia passado, caso já exista, ignora a querry de inserção
		self.cursor.execute("""INSERT IGNORE INTO LIVRO_TIPO VALUES(NULL,
							(SELECT IDLIVRO FROM LIVRO
							WHERE LIVRO.NOME = "%s"),
							(SELECT IDTIPO FROM TIPO 
							WHERE TIPO.TIPO = "%s")
							)""" %(nomeLivro, nomeTipo))

		# insere a categoria do livro, caso já exista, ignora a querry de inserção
		self.cursor.execute("""INSERT IGNORE INTO LIVRO_CATEGORIA VALUES(NULL,
							(SELECT IDLIVRO FROM LIVRO
							WHERE LIVRO.NOME = "%s"),
							(SELECT IDCATEGORIA FROM CATEGORIA 
							WHERE CATEGORIA.CATEGORIA = "%s")
							)""" %(nomeLivro, nomeGenero))
		self.connection.commit()

	# Função nº 1: inserção de valores. Diversas podem ser as fontes de invocação
	# cada uma foi tratada como uma possibilidade dentro o "if"
	def insert(self, values, table):

		# se tentamos inserir um livro
		if table == "LIVRO":
		# A posição das entradas no parâmetro values é: 
		#                nome, autor, genero, midia, qdade, lido, tenho, capa
			try:
				# caso a quantidade não seja informada, passa-se um
				# valor default igual a 1
				if values[4] == "":
					values[4] = "1"

				# coloca todas as capas como a img "SEM-CAPA" no início
				# if values[7] == "":
				# 	values[7] = r".\capas\SEM-IMAGEM.jpg"
				# print

				self.cursor.execute("""INSERT INTO LIVRO(IDLIVRO, NOME, CAPA, QUANTIDADE, LIDO, POSSUO, ID_EMPRESTIMO) 
								VALUES (NULL,"%s","%s","%s","%s","%s",NULL) """ 
								%(values[0], 
								values[7], 
								int(values[4]), 
								values[5], 
								values[6]))

				# já executamos as querries de autor e categoria, caso eles ainda não estejam
				# cadastrados
				self.cursor.execute("""INSERT IGNORE INTO AUTOR(IDAUTOR, NOME) VALUES (NULL,"%s")""" %(values[1]))

				self.cursor.execute("""INSERT IGNORE INTO TIPO(IDTIPO, TIPO) VALUES (NULL,"%s")""" %(values[3]))			

				self.cursor.execute("""INSERT IGNORE INTO CATEGORIA(IDCATEGORIA, CATEGORIA) VALUES (NULL,"%s")""" 
								%(values[2]))

				self.connection.commit()

				# fazemos o link das tabelas associativas necessárias
				self.link_all(values[0], values[1], values[3], values[2])
				
			# Caso o livro já tenha sido cadastrado, levanta o erro de chave duplicada
			# e um pop-up avisa o user que o livro já existe
			except mysql.connector.errors.IntegrityError as e:
				popupmsg("Livro já cadastrado!")
			# O valor do campo quantidade DEVE ser um inteiro
			# except ValueError as e:
			# 	popupmsg("Quantidade deve ser um número inteiro!")

		# se a inserção for apenas de um novo autor/categoria
		elif table == "AUTOR" or table == "CATEGORIA":
			try:
				self.cursor.execute("""INSERT INTO %s VALUES (NULL,"%s")""" 
								%(table, values[0]))
				self.connection.commit()			

			# caso o novo cadastro já exista
			except mysql.connector.errors.IntegrityError as e:
				popupmsg("O cadastro já existe!")

	# Função nº 2: atualizar os dados. A função mais complicada até então
	# pois envolve uma variedade de tabelas e ligações associativas para
	# se alterar
	def update(self, index, nome_livro, nome_autor, genero, midia, quantidade, 
				combo_lido, combo_tenho, path_capa):

		index_livro_old = index[0]
		autor_old = index[1]
		midia_old = index[2]
		genero_old = index[3]

		# como o padrão do DB é retornar "Sem informação" para alguma querry de busca que
		# não retorne tupla, criou-se esse erro para tratar desses eventos que causam problemas
		# na hora de receber os dados clicados na listbox
		class ErroSemInfo(Exception):
			def __init__(self, msg):
				print(msg)
		# ----------------------- ATUALIZA LIVRO ------------------------

		try:
			self.cursor.execute("""UPDATE LIVRO 
									SET NOME = "%s", 
									CAPA = "%s",
									QUANTIDADE = "%s",
									LIDO = "%s", 
									POSSUO = "%s", 
									ID_EMPRESTIMO = NULL
									WHERE IDLIVRO = %s""" 
									%(nome_livro, path_capa, int(quantidade), 
									  combo_lido, combo_tenho, int(index_livro_old)))
		
		except mysql.connector.errors.IntegrityError as e:
			popupmsg("Livro já cadastrado!")
		except ValueError as e:
			popupmsg("Quantidade deve ser um número inteiro!")	

		# ----------------------- ATUALIZA AUTOR ------------------------
		try:
			# caso a operação troque um autor já cadastrado por um novo, p.e., nome errado
			self.cursor.execute("""SELECT IDAUTOR FROM AUTOR WHERE NOME = "%s" """
									%(autor_old))

			# recupera o id do velho autor
			index_autor_old = self.cursor.fetchall()

			# o id vem numa tupla que está dentro de uma list, então, para recuperar
			# seu valor, é preciso acessar a posição 0 da tupla que está na posição
			# 0 da list
			index_autor_old = index_autor_old[0][0]
			
			# caso estejamos pegando um autor já cadastrado e apontando-o para 
			# uma associação
			self.cursor.execute("""SELECT IDAUTOR FROM AUTOR WHERE NOME = "%s" """
							%(nome_autor))
			try:
				index_autor_new = self.cursor.fetchall()
				index_autor_new = index_autor_new[0][0]
			except IndexError as err:
				popupmsg("Por favor, cadastrar o novo autor antes de alterá-lo!")
			
			# como citado, o retorno "Sem informação" foi tratado com esse erro
			if autor_old == "Sem informação":
				raise ErroSemInfo("autor sem info")
		
			# caso o autor esteja com o nome errado apenas
			self.cursor.execute("""UPDATE AUTOR A
							INNER JOIN AUTORIA AU 
							ON A.IDAUTOR = AU.ID_AUTOR
							INNER JOIN LIVRO L 
							ON AU.ID_LIVRO = L.IDLIVRO
							SET A.NOME = "%s"
							WHERE AU.ID_AUTOR = "%s" AND AU.ID_LIVRO = "%s" """
							%(nome_autor, int(index_autor_old), int(index_livro_old)))
		
		except (mysql.connector.errors.IntegrityError, IndexError) as err:		
			# caso seja modificado para um autor que já está cadastrado corretamente, 
			# apenas muda-se a associação na tabela autoria
			self.cursor.execute("""UPDATE AUTORIA AU
							SET AU.ID_AUTOR = "%s"
							WHERE AU.ID_AUTOR = "%s" AND AU.ID_LIVRO = "%s" """
							%(int(index_autor_new), int(index_autor_old), int(index_livro_old)))
		
		except ErroSemInfo as err:
			# caso a listbox nos retorne um livro com autor "Sem informação" e a alteração 
			# seja colocar um autor já cadastrado nesse livro, o que faz-se apenas é criar
			# a ligação associativa entre livro e autor, pois ambos já estão cadastrados
			self.cursor.execute("""INSERT IGNORE INTO AUTORIA 
									VALUES (NULL, "%s", "%s")"""
									%(int(index_livro_old), int(index_autor_new)))

		# ----------------------- ATUALIZA MÍDIA ------------------------
		self.cursor.execute("""SELECT IDTIPO FROM TIPO WHERE TIPO = "%s" """
						%(midia_old))

		index_midia_old = self.cursor.fetchall()
		index_midia_old = index_midia_old[0][0]

		self.cursor.execute("""SELECT IDTIPO FROM TIPO WHERE TIPO = "%s" """
						%(midia))

		index_midia_new = self.cursor.fetchall()
		index_midia_new = index_midia_new[0][0]
		
		self.cursor.execute("""UPDATE LIVRO_TIPO
						SET ID_TIPO = "%s"
						WHERE ID_TIPO = "%s" AND ID_LIVRO = "%s" """
						%((int(index_midia_new), int(index_midia_old), int(index_livro_old))))			

		# ----------------------- ATUALIZA CATEGORIA ------------------------

		try:
			self.cursor.execute("""SELECT IDCATEGORIA FROM CATEGORIA WHERE CATEGORIA = "%s" """
							%(genero_old))

			index_genero_old = self.cursor.fetchall()

			index_genero_old = index_genero_old[0][0]

			self.cursor.execute("""SELECT IDCATEGORIA FROM CATEGORIA WHERE CATEGORIA = "%s" """
							%(genero))
			try:
				index_genero_new = self.cursor.fetchall()
				index_genero_new = index_genero_new[0][0]
			except IndexError as err:
				popupmsg("Por favor, cadastrar a nova categoria antes de alterá-la!")

			if genero_old == "Sem informação":
				raise ErroSemInfo("autor sem info")
			
			self.cursor.execute("""UPDATE CATEGORIA C
							INNER JOIN LIVRO_CATEGORIA LC 
							ON C.IDCATEGORIA = LC.ID_CATEGORIA
							INNER JOIN LIVRO L 
							ON LC.ID_LIVRO = L.IDLIVRO
							SET C.CATEGORIA = "%s"
							WHERE LC.ID_CATEGORIA = "%s" AND LC.ID_LIVRO = "%s" """
							%(genero, int(index_genero_old), int(index_livro_old)))
			
		except (mysql.connector.errors.IntegrityError, IndexError) as err:

				self.cursor.execute("""UPDATE LIVRO_CATEGORIA
								SET ID_CATEGORIA = "%s"
								WHERE ID_CATEGORIA = "%s" AND ID_LIVRO = "%s" """
								%(int(index_genero_new), int(index_genero_old), int(index_livro_old)))
		except ErroSemInfo as err:
				self.cursor.execute("""INSERT IGNORE INTO LIVRO_CATEGORIA 
									VALUES (NULL, "%s", "%s")"""
									%(int(index_livro_old), int(index_genero_new)))
		
		self.connection.commit()

	# continuação da Função nº 2, mas complementado com a Função nº 5
	def update_one(self, old, alteracao, tabela):

		class ErroSemInfo(Exception):
			def __init__(self, msg):
				print(msg)

		if tabela == "AUTOR":
			tabelaUpdate = "AUTOR"
			letraUpdate = "A"
			idUpdate = "A.IDAUTOR"
			paramUpdate = "A.NOME"
			tabelaAssoc = "AUTORIA"
			letraAssoc = "AU"
			idAssoc = "AU.ID_AUTOR"
			idLivro = "AU.ID_LIVRO"

		elif tabela == "CATEGORIA":
			tabelaUpdate = "CATEGORIA"
			letraUpdate = "C"
			idUpdate = "C.IDCATEGORIA"
			paramUpdate = "C.CATEGORIA"
			tabelaAssoc = "LIVRO_CATEGORIA"
			letraAssoc = "LC"
			idAssoc = "LC.ID_CATEGORIA"
			idLivro = "LC.ID_LIVRO"

		try:
			# tentamos alterar o um regsitro que já exite, p.e. escrevemos errado no cadastro
			# ou seja, apenas vamos atualizar um valor já existente na tabela

			index_old = old[0] # indice dos dados que serão modificados
			dado_old = old[1] # nome do dado a ser modificado
			livro_old = old[2] # nome do livro que terá seus dados modificados

			self.cursor.execute("""SELECT IDLIVRO FROM LIVRO WHERE NOME = "%s" """
							%(livro_old))

			# recupera o id do velho autor
			index_livro_old = self.cursor.fetchall()

			# o id vem numa tupla que está dentro de uma lis, então, para recuperar
			# seu valor, é preciso acessar a posção 0 da tupla que está na posição
			# 0 da list
			index_livro_old = index_livro_old[0][0]

			if livro_old == "Sem informação":
				# para o caso de não ter nenhuma associação, explicado no tratamento mais abaixo
				raise ErroSemInfo("Sem informação")
			else:
				self.cursor.execute("""UPDATE %s %s
						 				INNER JOIN %s %s
						 				ON %s = %s
						 				INNER JOIN LIVRO L 
						 				ON  %s = L.IDLIVRO
						 				SET  %s = "%s"
						 				WHERE  %s = "%s" AND  %s = "%s" """
						 				%(tabela, letraUpdate, tabelaAssoc, letraAssoc, idUpdate, idAssoc, idLivro, paramUpdate,
						 				 str(alteracao), idAssoc, int(index_old), idLivro, int(index_livro_old)))

		except mysql.connector.errors.IntegrityError as err:
			 # caso seja modificado para um autor que já está cadastrado corretamente, 
			 # apenas muda-se a associação na tabela autoria, mantendo-se os dois, ou seja
			 # uma troca de valores nas associações
			self.cursor.execute("""SELECT %s FROM %s %s WHERE %s = "%s" """
							%(idUpdate, tabelaUpdate, letraUpdate, paramUpdate, str(alteracao)))

			index_autor_new = self.cursor.fetchall()

			index_autor_new = index_autor_new[0][0]

			self.cursor.execute("""UPDATE %s %s
							SET %s = "%s"
							WHERE %s = "%s" AND %s = "%s" """
							%(tabelaAssoc, letraAssoc, idAssoc, 
							int(index_autor_new), idAssoc, 
							int(index_old), idLivro, int(index_livro_old)))
		except ErroSemInfo as erro:

			try:
				# nesse caso, o valor está apenas na tabela, mas não tem associações, ou seja,
				# está marcado como "Sem informação" no nome do livro. Isso acontece quanto temos
				# um cadastro de autor e/ou gênero, mas nenhum livro daquele autor e/ou gênero
				self.cursor.execute("""SELECT %s FROM %s %s WHERE %s = "%s" """
								%(idUpdate, tabelaUpdate, letraUpdate, paramUpdate, dado_old))

				index_autor_new = self.cursor.fetchall()

				index_autor_new = index_autor_new[0][0]

				self.cursor.execute("""UPDATE %s %s
								SET %s = "%s"
								WHERE %s = "%s" """
								%(tabelaUpdate, letraUpdate, paramUpdate, 
								str(alteracao), idUpdate, int(index_autor_new)))
			
			except mysql.connector.errors.IntegrityError as err:
				popupmsg("Entrada já cadastrada!")
			
			except IndexError as err:
				popupmsg("Por favor, entrar com o dado que deseja substituir!")

		self.connection.commit()

	def delete(self, tabela, param_id, old_value, param):

		self.cursor.execute("""SELECT %s FROM %s WHERE %s = "%s" """
				%(param_id, tabela, param, old_value))
		
		index_new_value = self.cursor.fetchall()
		index_new_value = index_new_value[0][0]

		if tabela == "LIVRO":
			self.cursor.execute("""DELETE FROM %s WHERE %s = "%s" """
						%(tabela, param_id, index_new_value))
		else:
			self.cursor.execute("""DELETE FROM %s WHERE %s = "%s" """
						%(tabela, param_id, index_new_value))
		
		self.connection.commit()


	def __del__(self):
		try:
			self.cursor.close()
		except (ReferenceError, AttributeError) as e:
			pass
		self.connection.close()