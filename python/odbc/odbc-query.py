import pyodbc


def main():
    connection = pyodbc.connect('DSN=MongoDBODBC', autocommit=True)
    run_query(connection, 'show tables')
    run_query(connection, 'describe metadata')
    run_query(connection, 'describe metadata_cities')
    run_query(connection, 'describe metadata_countries')
    run_query(connection, 'describe metadata_iso3s')
    run_query(connection, 'describe metadata_states')
    run_query(connection, 'describe metadata_uids')
    run_query(connection, 'select * from metadata')
    run_query(connection, 'select mc._id, mc.cities, mc.cities_idx from metadata m left outer join metadata_cities mc on m._id = mc._id limit 15')
    run_query(connection, 'select mc._id, mc.countries, mc.countries_idx from metadata m left outer join metadata_countries mc on m._id = mc._id limit 15')
    run_query(connection, 'describe statistics')
    run_query(connection, 'describe statistics_loc_coordinates')
    run_query(connection, 'select * from statistics s left outer join statistics_loc_coordinates loc on s._id = loc._id order by s.date DESC limit 15')
    connection.close()


def run_query(connection, query):
    print('\n' + query)
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()
    cursor.close()


if __name__ == '__main__':
    main()
