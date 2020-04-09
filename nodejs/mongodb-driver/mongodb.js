const MongoClient = require("mongodb").MongoClient;

const uri =
  "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority";

const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

client.connect((err) => {
  const statistics = client.db("covid19").collection("statistics");

  // find the latest 15 cases from France
  statistics
    .find({ country: "France" })
    .sort([["a", 1]])
    .limit(15)
    .toArray(function (err, docs) {
      if (err) {
        console.error(err);
      }
      console.log(docs);
      client.close();
    });
});
