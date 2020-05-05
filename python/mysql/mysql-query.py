import mysql.connector


def main():
    connection = mysql.connector.connect(user='readonly', password='readonly',
                                         host='covid-19-biconnector.hip2i.mongodb.net',
                                         port='27015',
                                         database='covid19',
                                         auth_plugin='mysql_native_password')
    cursor = connection.cursor()
    query = "SELECT * from global_and_us limit 20"
    cursor.execute(query)

    for i in cursor:
        print(i)

    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
