from sqlite3 import Error
import sqlite3
import os

class SQLiteDB():
	@classmethod
	def get_driver(cls, filepath):
		return SQLiteDB(filepath)

	def __init__(self, filepath):
		self.db_file 		= filepath
	
	def connect_db(self):
		""" establish connection with database """
		
		if not os.path.exists(self.db_file):
			print("database file does't exists")
			return None
		
		try:
			connection = sqlite3.connect(self.db_file)
			connection.execute('PRAGMA synchronous=0')
		
		except Error as e:
			Logger.exception(e, 'connect_db', "sdb")
			return None
		
		else:
			return connection
	
	#region direct sql
	def execute_select(self, query, return_dict=False):
		connection = self.connect_db()
		if connection is None:
			print("can't read data because no connection is available")
			return None
		cursor = connection.cursor()
		try:
			# execute query
			cursor.execute(query)
			attrbs= [item[0] for item in cursor.description]
			
			data = cursor.fetchall()
			if return_dict:
				data = [{key:val for key, val in zip(attrbs, row)}
						for row in data]
			
		except Exception as e:
			print(e)
			data = None
		finally:
			cursor.close()
			connection.close()
			return data

	def execute_insert(self, query):
		connection = self.connect_db()
		if connection is None:
			print("can't write data because no connection is available")
			return False
		
		flag = False; redoFlag = False
		cursor = connection.cursor()
		
		try:
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag

	def execute_update(self, query):
		connection = self.connect_db()
		if connection is None:
			print("can't update data because no connection is available")
			return False
		
		flag = False
		cursor = connection.cursor()
		try:
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag

	def execute(self, query):
		connection = self.connect_db()
		if connection is None:
			print("can't Execute Query Because No Connection Is Available")
			return False
		
		flag = False
		cursor = connection.cursor()
		try:
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag

	def execute_transection(self, transaction):
		""" execute a transaction 
			>>> @param:transaction	-> sql quaries separated by  ';' [str] 
		"""
		connection = self.connect_db()
		if connection is None:
			print("can't execute transaction because no connection is available")
			return False
		flag = False;redoFlag=False
		cursor = connection.cursor()
		try:
			cursor.executescript(transaction)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag
    #endregion

	#region functional interface
	def read(self, table=None, columns=None, distinct=False, where=None, orderby=None, 
											limit=None, _join=None, single=False):
		""" read data from a database table 
			>>> @param:table	-> name of table
			>>> @param:columns	-> columns to read, * to read all columns
			>>> @param:distinct	-> select distinct values 
			>>> @param:where	-> where clause for this query
			>>> @param:orderby 	-> orderby clause for this query
			>>> @param:limit	-> limit sample selection
			>>> @param:join		-> dict containing tables{"t1":(c1, c2)}, 
									join_type:[default:JOIN] and on{"t1":"c1"}
			>>> @param:single	-> flag to return single record
					
		"""
		connection = self.connect_db()
		if connection is None:
			print("can't read data - no connection is available")
			return None
		
		cursor = connection.cursor()
		data = None
		try:
			# apply select & from  
			query = ""
			if _join:
				tables 	= _join["tables"]
				assert len(tables.keys()) == 2, "only two tables are allowed in join"
				t1, t2	= tuple(tables.keys()) 
				select	= ", ".join( [ ", ".join([f'{t}.{col}' for col in tables[t] ]) 
																for t in tables.keys()])
				join_type= _join.get("join_type", "JOIN")
				_from	= f" FROM {t1} {join_type} {t2} "
				_on		= f" ON {t1}.{_join['on'][t1]} = {t2}.{_join['on'][t2]}"
				query 	= f" {select} {_from} {_on} "
					
			elif columns == '*':
				query = f" * FROM {table}"
			
			else:
				query = f" {', '.join(columns)} FROM {table}"

			# apply distinct
			if distinct:
				query = f"SELECT DISTINCT {query}"
			
			else:
				query = f"SELECT {query}"

			# apply where
			if where is not None:
				query = query + f" WHERE {where}"
			
			# apply orderby
			if orderby is not None:
				if type(orderby) is tuple:
					query = query + f" ORDER BY {orderby[0]} {orderby[1]}"
				else:
					query = query + f" ORDER BY {orderby}"
			
			# apply limit
			if limit is not None:
				query = query + f" LIMIT {limit}"

			query += ';'
			cursor.execute(query)
			
			# fetch all records
			data	= cursor.fetchall()
			attrbs	= [item[0] for item in cursor.description]
			data 	= [{key:val for key, val in zip(attrbs, row)}
						for row in data]
		
		except Exception as e:
			print(e)
		
		finally:
			cursor.close()
			connection.close()
			if single:
				return data[0] if data and len(data) > 0 else None
			else:
				return data

	def save(self, table, data):
		""" save a dictionary into database table 
			>>> @param:table	-> name of table
			>>> @param:data		-> dict containing column name and respactive 
									value. list of dict in case multiple objects
		"""
		connection = self.connect_db()
		if connection is None:
			print("can't save data - no connection available")
			return False
		
		flag = False
		cursor = connection.cursor()
		try:
			qformat	= """INSERT INTO {}({}) VALUES{};"""
			if type(data) is dict:
				query 	= qformat.format(table, ', '.join(data.keys()), 
									tuple([f'{v}' for v in data.values()]) ) 
				cursor.execute(query)

			else:
				data   = [ {key:val  for key, val in d.items() if val is not None}
																		for d in data ]
				script = [qformat.format(table, ', '.join(d.keys()), 
										tuple([f'{v}' for v in d.values()]) ) for d in data]
				query = "".join(script)
				cursor.executescript(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag

	def update(self, table, data, where=None):
		""" update a database table 
			>>> @param:table	-> name of table
			>>> @param:data		-> dict containing column name and respactive 
									value
			>>> @param:where	-> where clause for this query
		"""
		connection = self.connect_db()
		if connection is None:
			print("can't update data - no connection available")
			return False
		
		flag = False
		cursor = connection.cursor()
		try:
			query = f"UPDATE {table} SET "
			query +=  ', '.join([f" {key}='{value}' " for key, value in data.items()])
			query = query if where is None else f"{query} WHERE {where}"
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag

	def remove(self, table, where):
		""" delet record from database table based on condition 
			>>> @param:table	-> name of table
			>>> @param:where	-> where clause for this query
		"""
		connection = self.connect_db()
		if connection is None:
			print("can't delet record - no connection available")
			return False
		
		flag = False
		cursor = connection.cursor()
		try:
			query = f"DELETE FROM {table} WHERE {where}"
			cursor.execute(query)
		
		except Exception as e:
			print(e)
			try:connection.rollback()
			except Exception:pass
		
		else:
			connection.commit()
			flag = True
		
		finally:
			cursor.close()
			connection.close()
			return flag
    #endregion


""" USAGE 
dbdriver = SQLiteDB("dbfile.db")

dbdriver.execute("INSERT, DELETE or UPDATE query")
data = dbdriver.execute_select("SELECT QUERY", return_dict=True)
dbdriver.execute_insert("INSERT QUERY")
dbdriver.execute_update("UPDATE QUERY")

# You can also use functional interface
dbdriver.read()     # read parameters for this function
dbdriver.remove()   # read parameters
dbdriver.save()     # read parameters
dbdriver.update()   # read parameters
"""