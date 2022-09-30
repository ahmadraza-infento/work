
import os
import sqlite3
from cryptography.fernet import Fernet

class EncryptedDB():
	""" SQLITE based database with ability to store and load encrypted data to insure
		that only specific app can read app data
	"""
	def __init__(self, dbfile, encryption_key):
		self._db_file 		= dbfile
		self._encrypter		= Fernet(encryption_key)
	
	def _connect_file(self):
		""" establish connection with database """
		
		if not os.path.exists(self._db_file):
			print("db file not found")
			return None
		
		try:
			connection = sqlite3.connect(self._db_file)
		
		except Exception as e:
			print(e)
			return None
		
		else:
			return connection
	
	def decrypt(self, data_dict):
		for key, val in data_dict.items():
			data_dict[key] = self._encrypter.decrypt( bytes(val, 'utf-8') ).decode("utf-8")
		
		return data_dict

	def encrypt(self, data_dict):
		for key, val in data_dict.items():
			data_dict[key] = self._encrypter.encrypt( bytes(val, 'utf-8') ).decode("utf-8")
		
		return data_dict

	def read(self, query):
		connection = self._connect_file()
		if connection is None:
			return None
		
		cursor	= connection.cursor()
		data 	= None
		try:
			
			cursor.execute(query)
			
			# fetch all records
			data	= cursor.fetchall()[0]
			# read column names from cursor
			cols	= [item[0] for item in cursor.description]
			# convert data to dictionary
			data 	= {key:val for key, val in zip(cols, data)}
			# decrypt data
			data 	= self.decrypt(data)
			return data
		
		except Exception as e:
			print(e)
		
		finally:
			cursor.close	()
			connection.close()
			return data

	def save(self, table, data):
		connection = self._connect_file()
		if connection is None:
			return False
		
		flag 	= False
		cursor 	= connection.cursor()
		try:
			cols	= ", ".join([c for c in data.keys() ] )
			qformat	= """INSERT INTO {}({}) VALUES{};"""
			data	= self.encrypt(data)
			query 	= qformat.format(table, cols, tuple([f'{v}' for v in data.values()]) ) 
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close	()
			connection.close()
			return flag

	def update(self, table, data):
		connection = self._connect_file()
		if connection is None:
			return False
		
		flag 	= False
		cursor 	= connection.cursor()
		try:
			data	= self.encrypt(data)
			query 	= f"UPDATE {table} SET "
			query 	+=  ', '.join([f" {key}='{value}' " for key, value in data.items()])
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close	()
			connection.close()
			return flag
