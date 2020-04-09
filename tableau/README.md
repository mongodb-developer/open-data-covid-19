## Using the MongoDB Dataset from Tableau

Tableau is a powerful data visualisation and dashboard tool,
and can be connected to our COVID-19 data in a few short steps.

When you first create a new document in Tableau, you can choose to use 'MongoDB BI Connector' as your data source.
We've enabled the Atlas MongoDB BI Connector for you, so you can use tools like Tableau which expect a relational database as a data source.
The MongoDB BI Connector exposes a MySQL interface to the MongoDB database.

To connect Tableau to the covid19 database, select "MongoDB BI Connector" in the "Connect" panel.

If you haven't used this data source type before, you'll find it by clicking the "More..." button.
In this case you may also need to install an ODBC provider (I needed to install iODBC on my Mac, for example) and the MySQL ODBC connector from Oracle. You'll find instructions to install these by following the link on the connection dialog.

Once you have the necessary components installed,  fill in the form as follows:

TODO: Image

The details are:

Server: covid-19-biconnector.hip2i.mongodb.net
Port: 27015
Database: covid19
Username: readonly
Password: readonly

Once you have connected to the data source, you'll see various tables listed on the left-hand side. Unfortunately, because Tableau works with tables instead of MongoDB's rich documents, we have to flatten the documents into tables which can be rejoined within Tableau.

It's most likely you'll be interested in the data in the "statistics" table, which contains the number of coronavirus statistics for each country (or in the case of the USA, by individual City).