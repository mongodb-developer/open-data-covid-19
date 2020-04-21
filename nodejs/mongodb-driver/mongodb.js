const MongoClient = require("mongodb").MongoClient;

const uri =
  "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19";

const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

client.connect((err) => {
  const covid19Database = client.db("covid19");
  const statistics = covid19Database.collection("statistics");
  const metadata = covid19Database.collection("metadata");

  // Query to get the last 5 entries for France (continent only)
  statistics
    .find({ country: "France" })
    .sort(["date", -1])
    .limit(15)
    .toArray((err, docs) => {
      if (err) {
        console.error(err);
      }
      console.log(docs);
    });

  //Query to get the last day data (limited to 5 docs here).
  metadata
    .find()
    .toArray((err, docs) => {
      if (err) {
        console.error(err);
      }
      const lastDate = docs[0].last_date;

      statistics
        .find({ date: { $eq: lastDate } })
        .limit(5)
        .toArray((err, docs) => {
          if (err) {
            console.error(err);
          }
          console.log(docs);
        });
    });

  // Query to get the last day data for all the countries within 500km of Paris.
  const lon = 2.341908;
  const lat = 48.860199;
  const earthRadius = 6371; // km
  const searchRadius = 500; // km

  metadata
    .find()
    .toArray((err, docs) => {
      if (err) {
        console.error(err);
      }
      const lastDate = docs[0].last_date;

      statistics
        .find({
          date: { $eq: lastDate },
          loc: {
            $geoWithin: {
              $centerSphere: [[lon, lat], searchRadius / earthRadius],
            },
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
});
