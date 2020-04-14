const MongoClient = require("mongodb").MongoClient;

const uri =
  "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test?retryWrites=true&w=majority";

const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

client.connect((err) => {
  const statistics = client.db("covid19").collection("statistics");

  // // Query to get the last 5 entries for France (continent only)
  statistics
    .find({ country: "France" })
    .sort([["date", -1]])
    .limit(15)
    .toArray(function (err, docs) {
      if (err) {
        console.error(err);
      }
      console.log(docs);
    });

  //Query to get the last day data (limited to 15 docs here).
  statistics
    .find({
      date: {
        $lt: new Date(),
        $gt: new Date(new Date().setDate(new Date().getDate() - 2)),
      },
    })
    .limit(15)
    .toArray((err, docs) => {
      if (err) {
        console.error(err);
      }
      console.log(docs);
    });

  // Query to get the last day data for all the countries within 500km of Paris.
  const lon = 2.341908;
  const lat = 48.860199;
  const earthRadius = 6371; // km
  const searchRadius = 500; // km

  statistics
    .find({
      loc: {
        $geoWithin: {
          $centerSphere: [[lon, lat], searchRadius / earthRadius],
        },
      },
      date: {
        $lt: new Date(),
        $gt: new Date(new Date().setDate(new Date().getDate() - 2)),
      },
    })
    .limit(5)
    .toArray((err, docs) => {
      if (err) {
        console.error(err);
      }
      console.log(docs);
    });
});
