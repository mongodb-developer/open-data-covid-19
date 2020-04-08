import pyodbc


def main():
    server = 'tcp:covid-19-biconnector.hip2i.mongodb.net,27015'
    database = 'coronavirus'
    username = 'max?source=admin'
    password = 'readonly'
    driver = '/usr/local/lib/libmdbodbcw.so'

    cnxn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM metadata")

    row = cursor.fetchone()
    while row:
        print(row)

    cursor.close()
    cnxn.close()


if __name__ == '__main__':
    main()
