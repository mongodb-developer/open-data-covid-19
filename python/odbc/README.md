# Python & ODBC Code Sample

For some obscure reason, maybe you prefer to use ODBC to access this dataset.

## Run

To access this dataset in [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) through the [BI Connector](https://www.mongodb.com/products/bi-connector), you need to setup the [MongoDB ODBC driver](https://github.com/mongodb/mongo-odbc-driver/releases) and [create a DSN](https://docs.mongodb.com/bi-connector/master/tutorial/create-system-dsn/#).

You can find the DSN in the `odbc.ini` file that usually lives in the `/etc/` folder and you also need to set up an environmental variable `ODBCINI = /etc/odbc.ini`.

As this is a bit complicated to do so I made a Docker container that does all that work for you and also serves as a living documentation of the process.

To use the docker container and run the test simply run: 

```shell script
./docker-build.sh
./docker-run.sh
``` 
