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

class Database:

	def __init__(self):
		self.connection = mysql.connector.connect(user='root', password = '1234', host = '127.0.0.1', 
											database = 'biblioteca')
		self.cursor = self.connection.cursor()

	# função de busca no banco. Usada pelas buscas para printar na listbox os valores
	# retornados pela querry de consula. A função é divida em três possibilidades
	# já que são três listboxes diferentes que podem ser preenchidas, dependendo de
	# onde foi invocada a querry

	def search_cover(self, name):

		self.cursor.execute("""SELECT IFNULL(L.CAPA, "Sem informação")
							FROM LIVRO L 
							WHERE L.NOME = "%s" """ 
							%(name))

		cover = self.cursor.fetchall()

		return cover


	def search(self, where, like, tabela):

		# invocada pela pesquisa de livros e tipo de mídia
		if tabela == "LIVRO" or tabela == "TIPO" :
			# self.cursor.execute("""SELECT IFNULL(L.CAPA, "Sem informação"), 
			# 					FROM LIVRO L 
			# 					WHERE %s LIKE %s """ 
			# 					%(where , "\"" + "%" +like+ "%" + "\""))
			# photo = self.cursor.fetchall()


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

		return data#, photo

	# Função responsável por linkar as tabelas associativas do BD:
	# Livro -> Livro_Tipo <- Tipo
	# Livro -> Livro_Catagoria <- Categoria
	# Livro -> Autoria <- Autor
	# Sua invocação se dá no cadastro de um novo livro, em que todos
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

	def link_one(self, tabelaAssoc, 
				 idA, tabelaA, paramA, valueA,
				 idB, tabelaB, paramB, valueB):

		return self.cursor.execute("""INSERT IGNORE INTO %s VALUES(NULL,
							(SELECT %s FROM %s
							WHERE %s.%s = "%s"),
							(SELECT %s FROM %s 
							WHERE %s.%s = "%s")
							)""" %(tabelaAssoc, 
								idA, tabelaA, tabelaA, paramA, valueA,
							  	idB, tabelaB, tabelaB, paramB, valueB))


	def insert(self, values, table):

		if table == "LIVRO":
		# A posição das entradas no parâmetro values é: 
		#                nome, autor, genero, midia, qdade, lido, tenho, capa
			try:
				self.cursor.execute("""INSERT INTO LIVRO(IDLIVRO, NOME, CAPA, QUANTIDADE, LIDO, POSSUO, ID_EMPRESTIMO) 
								VALUES (NULL,"%s","%s","%s","%s","%s",NULL) """ 
								%(values[0], 
									values[7], 
									int(values[4]), 
								values[5], 
								values[6]))

				self.cursor.execute("""INSERT IGNORE INTO AUTOR(IDAUTOR, NOME) VALUES (NULL,"%s")""" %(values[1]))

				self.cursor.execute("""INSERT IGNORE INTO TIPO(IDTIPO, TIPO) VALUES (NULL,"%s")""" %(values[3]))			

				self.cursor.execute("""INSERT IGNORE INTO CATEGORIA(IDCATEGORIA, CATEGORIA) VALUES (NULL,"%s")""" 
								%(values[2]))
		

				self.connection.commit()
				self.link_all(values[0], values[1], values[3], values[2])
				
			# Caso o livro já tenha sido cadastrado, levanta o erro de chave duplicada
			# e um pop-up avisa o user que o livro já existe
			except mysql.connector.errors.IntegrityError as e:
				popupmsg("Livro já cadastrado!")
			# O valor do campo quantidade DEVE ser um inteiro
			except ValueError as e:
				popupmsg("Quantidade deve ser um número inteiro!")

		elif table == "AUTOR" or table == "CATEGORIA":
			try:
				self.cursor.execute("""INSERT INTO %s VALUES (NULL,"%s")""" 
								%(table, values[0]))
				self.connection.commit()			

			except mysql.connector.errors.IntegrityError as e:
				popupmsg("O cadastro já existe!")

	def update(self, index, nome_livro, nome_autor, genero, midia, quantidade, 
				combo_lido, combo_tenho, path_capa):

		index_livro_old = index[0]
		autor_old = index[1]
		midia_old = index[2]
		genero_old = index[3]

		# ----------------------- ATUALIZA LIVRO ------------------------
		class ErroSemInfo(Exception):
			def __init__(self, msg):
				print(msg)
		try:
			self.cursor.execute("""UPDATE LIVRO #(IDLIVRO, NOME, CAPA, QUANTIDADE, LIDO, POSSUO, ID_EMPRESTIMO) 
							SET NOME = "%s", CAPA = "%s", QUANTIDADE = "%s",
							LIDO = "%s", POSSUO = "%s", ID_EMPRESTIMO = NULL
							WHERE IDLIVRO = %s""" 
							%(nome_livro, path_capa, int(quantidade), 
							combo_lido, combo_tenho, int(index_livro_old)))
		
		except mysql.connector.errors.IntegrityError as e:
			popupmsg("Livro já cadastrado!")
		except ValueError as e:
			popupmsg("Quantidade deve ser um número inteiro!")	

		# ----------------------- ATUALIZA AUTOR ------------------------
		try:
			self.cursor.execute("""SELECT IDAUTOR FROM AUTOR WHERE NOME = "%s" """
							%(autor_old))

			# recupera o id do velho autor
			index_autor_old = self.cursor.fetchall()
			# print(index_autor_old)

			# o id vem numa tupla que está dentro de uma lis, então, para recuperar
			# seu valor, é preciso acessar a posção 0 da tupla que está na posição
			# 0 da list
			index_autor_old = index_autor_old[0][0]
			# print(index_autor_old)
			
			self.cursor.execute("""SELECT IDAUTOR FROM AUTOR WHERE NOME = "%s" """
							%(nome_autor))
			try:
				index_autor_new = self.cursor.fetchall()
				index_autor_new = index_autor_new[0][0]
			except IndexError as err:
				popupmsg("Por favor, cadastrar a novo autor antes de alterá-lo!")
			
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

			print("""INSERT IGNORE AUTORIA AU 
									VALUES (NULL, "%s", "%s")"""
									%(int(index_livro_old), int(index_autor_new)))

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

			# recupera o id do velho autor
			index_genero_old = self.cursor.fetchall()

			# o id vem numa tupla que está dentro de uma lis, então, para recuperar
			# seu valor, é preciso acessar a posção 0 da tupla que está na posição
			# 0 da list
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
			

				# caso o autor esteja com o nome errado apenas
			self.cursor.execute("""UPDATE CATEGORIA C
							INNER JOIN LIVRO_CATEGORIA LC 
							ON C.IDCATEGORIA = LC.ID_CATEGORIA
							INNER JOIN LIVRO L 
							ON LC.ID_LIVRO = L.IDLIVRO
							SET C.CATEGORIA = "%s"
							WHERE LC.ID_CATEGORIA = "%s" AND LC.ID_LIVRO = "%s" """
							%(genero, int(index_genero_old), int(index_livro_old)))
			
		except (mysql.connector.errors.IntegrityError, IndexError) as err:
				 # caso seja modificado para um autor que já está cadastrado corretamente, 
				 # apenas muda-se a associação na tabela autoria
				# self.cursor.execute("""SELECT IDCATEGORIA FROM CATEGORIA WHERE CATEGORIA = "%s" """
				# 				%(genero))

				# index_genero_new = self.cursor.fetchall()

				# index_genero_new = index_genero_new[0][0]

				self.cursor.execute("""UPDATE LIVRO_CATEGORIA
								SET ID_CATEGORIA = "%s"
								WHERE ID_CATEGORIA = "%s" AND ID_LIVRO = "%s" """
								%(int(index_genero_new), int(index_genero_old), int(index_livro_old)))
		except ErroSemInfo as err:
				self.cursor.execute("""INSERT IGNORE INTO LIVRO_CATEGORIA 
									VALUES (NULL, "%s", "%s")"""
									%(int(index_livro_old), int(index_genero_new)))
		
		self.connection.commit()

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

			# print("apenas atualizando um valor na table")

			index_old = old[0] # indice dos dados que serão modificados
			dado_old = old[1] # nome do dado a ser modificado
			livro_old = old[2] # nome do livro que terá seus dados modificados
			# print(index_old)
			# print(dado_old)
			# print(livro_old)

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
			# print("""UPDATE AUTOR A
			# 		INNER JOIN %s
			# 		ON %s = %s
			# 		INNER JOIN LIVRO L 
			# 		ON %s = L.IDLIVRO
			# 		SET A.NOME = "%s"
			# 		WHERE %s = "%s" AND %s = "%s" """
			# 		%(#tabelaUpdate,
			# 		 tabelaAssoc, idUpdate, idAssoc, idLivro,# paramUpdate,
			# 		str(alteracao), idAssoc, int(index_old), idLivro, int(index_livro_old)))

		except mysql.connector.errors.IntegrityError as err:
			 # caso seja modificado para um autor que já está cadastrado corretamente, 
			 # apenas muda-se a associação na tabela autoria, mantendo-se os dois, ou seja
			 # uma troca de valores nas associações

			# print("\nAqui está havendo uma troca de associações\n")
			# print("""SELECT %s FROM %s %s WHERE %s = "%s" """
			# 				%(idUpdate, tabelaUpdate, letraUpdate, paramUpdate, str(alteracao)))

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
				# está marcado como Sem informação no nome do livro. Isso acontece quanto temos
				# um cadastro de autor e/ou gênero, mas nenhum livro daquele autor e/ou gênero
				# print("\nCampo do nome do livro marcado como Sem informação\n")
				# print("""SELECT %s FROM %s %s WHERE %s = "%s" """
				# 				%(idUpdate, tabelaUpdate, letraUpdate, paramUpdate, dado_old))

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