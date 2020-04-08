import pyodbc


def main():
    connection = pyodbc.connect('DSN=MongoDBODBC')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM metadata")
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()


if __name__ == '__main__':
    main()
