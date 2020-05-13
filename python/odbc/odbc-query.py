import pyodbc


def main():
    connection = pyodbc.connect('DSN=MongoDBODBC', autocommit=True)
    run_query(connection, 'show tables')
    run_query(connection, 'describe metadata')
    run_query(connection, 'describe metadata_counties')
    run_query(connection, 'describe metadata_countries')
    run_query(connection, 'describe metadata_iso3s')
    run_query(connection, 'describe metadata_states')
    run_query(connection, 'describe metadata_uids')
    run_query(connection, 'select * from metadata')
    run_query(connection, 'select mc._id, mc.counties, mc.counties_idx from metadata m left outer join metadata_counties mc on m._id = mc._id limit 15')
    run_query(connection, 'select mc._id, mc.countries, mc.countries_idx from metadata m left outer join metadata_countries mc on m._id = mc._id limit 15')
    run_query(connection, 'describe global_and_us')
    run_query(connection, 'describe global_and_us_loc_coordinates')
    run_query(connection, 'select * from global_and_us g left outer join global_and_us_loc_coordinates loc on g._id = loc._id order by g.date DESC limit 15')
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
