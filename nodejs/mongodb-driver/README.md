# NodeJS & MongoDB Driver Code Sample

## Quick Start

Next, inside the project, you need to install the project's various NPM dependencies:

    npm install

You should now be ready to make a query on the Open Covid Data Cluster:

    npm start

## How to Connect

```
const MongoClient = require("mongodb").MongoClient;

const uri =
  "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19";

const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

client.connect((err) => {
  const statistics = client.db("covid19").collection("statistics");

  // find the latest 15 cases from France
  statistics
    .find({ country: "France" })
    .limit(15)
    .toArray(function (err, docs) {
      if (err) {
        console.error(err);
      }
      console.log(docs);
      client.close();
    });
});
```

## Related Links

- [MongoDB Node Driver Docs](http://mongodb.github.io/node-mongodb-native/)
