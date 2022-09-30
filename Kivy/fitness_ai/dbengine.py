
from cryptography.fernet import Fernet
from sqlite3 import Error
import sqlite3
import os

class DBEngine():
	@classmethod
	def init(cls, filepath):
		return DBEngine(filepath)

	def __init__(self, filepath):
		self._db_file 		= filepath
		self._fernet		= Fernet(b"fLvKlJ8MnCd_DkIPKUeO21L_FXqwk0Kmh1lW2BHECLo=")
	
	def _connect_db(self):
		""" establish connection with database """
		
		if not os.path.exists(self._db_file):
			print("database file does't exists")
			return None
		
		try:
			connection = sqlite3.connect(self._db_file)
		
		except Error as e:
			print(f'[EXCEPTION] {e}')
			return None
		
		else:
			return connection
	
	def _decrypt(self, data_dict):
		""" decrypt data dict using fernet """
		for key, val in data_dict.items():
			data_dict[key] = self._fernet.decrypt( bytes(val, 'utf-8') ).decode("utf-8")
		
		return data_dict

	def _encrypt(self, data_dict):
		""" encrypt data dict using fernet """
		for key, val in data_dict.items():
			data_dict[key] = self._fernet.encrypt( bytes(val, 'utf-8') ).decode("utf-8")
		
		return data_dict

	def read(self, table):
		""" read settings from database table """
		connection = self._connect_db()
		if connection is None:
			print("can't read data - no connection is available")
			return None
		
		cursor	= connection.cursor()
		data 	= None
		try:
			
			query = f'SELECT * FROM {table}'
			cursor.execute(query)
			
			# fetch all records
			data	= cursor.fetchall()[0]
			# read column names from cursor
			cols	= [item[0] for item in cursor.description]
			# convert data to dictionary
			data 	= {key:val for key, val in zip(cols, data)}
			# decrypt data
			data 	= self._decrypt(data)
			return data
		
		except Exception as e:
			print(f'[EXCEPTION] {e}')
		
		finally:
			cursor.close	()
			connection.close()
			return data

	def save(self, table, data):
		""" save encrypted settings to database table """
		connection = self._connect_db()
		if connection is None:
			print("can't save data - no connection available")
			return False
		
		flag 	= False
		cursor 	= connection.cursor()
		try:
			cols    = ", ".join([col for col in data.keys() ])
			qformat	= """INSERT INTO {}({}) VALUES{};"""
			data	= self._encrypt(data)
			query 	= qformat.format(table, cols, tuple([f'{v}' for v in data.values()]) ) 
			cursor.execute(query)
		
		except Exception as e:
			print(f'[EXCEPTION] {e}')
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
		""" update setting in database table """
		connection = self._connect_db()
		if connection is None:
			print("can't update data - no connection available")
			return False
		
		flag 	= False
		cursor 	= connection.cursor()
		try:
			data	= self._encrypt(data)
			query 	= f"UPDATE {table} SET "
			query 	+=  ', '.join([f" {key}='{value}' " for key, value in data.items()])
			cursor.execute(query)
		
		except Exception as e:
			print(f'[EXCEPTION] {e}')
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close	()
			connection.close()
			return flag
