package main

import (
	"context"
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/olekukonko/tablewriter"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

const mdbURL = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19"
const earthRadius = 6371.0

// Metadata represents (a subset of) the data stored in the metadata
// collection in a single document.
type Metadata struct {
	LastDate time.Time `bson:"last_date"`
	// There are other fields in this document, but this sample code doesn't
	// use them.
}

// Statistic represents the document structure of documents in the
// 'statistics' collection.
type Statistic struct {
	ID  primitive.ObjectID `bson:"_id"`
	UID int32

	// Location:
	CombinedName string `bson:"combined_name"`
	City         string
	State        string
	Country      string
	CountryCode  int32  `bson:"country_code"`
	CountryISO2  string `bson:"country_iso2"`
	CountryISO3  string `bson:"country_iso3"`
	FIPS         int32
	Loc          struct {
		Type        string
		Coordinates []float64
	}

	Date time.Time

	// Statistics:
	Confirmed  int32
	Deaths     int32
	Population int32
	Recovered  int32
}

// main is the entrypoint for this binary.
// It connects to MongoDB but most of the interesting code is in other functions.
func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(mdbURL))
	if err != nil {
		panic(fmt.Sprintf("Error initializing MongoDB Client: %v", err))
	}
	defer client.Disconnect(ctx)

	// Get references to the main collections:
	database := client.Database("covid19")
	statistics := database.Collection("statistics")
	metadata := database.Collection("metadata")

	// Print some interesting results:
	fmt.Println("\nMost recent 10 statistics for United Kingdom:")
	recentCountryStats(statistics, "United Kingdom")
	lastDate := mostRecentDateLoaded(metadata)
	fmt.Printf("\nLast date loaded: %v\n", lastDate)
	fmt.Println("\nThe last day's highest reported recoveries:")
	highestRecoveries(statistics, lastDate)
	fmt.Println("\nThe last day's confirmed cases for all the countries within 500km of Paris:")
	confirmedWithinRadius(statistics, lastDate, 2.341908, 48.860199, 500.0)
}

// recentCountryStats prints the most recent 10 stats for a country.
// Note that this won't work for "US" because that data is broken down by city & state.
func recentCountryStats(statistics *mongo.Collection, country string) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	findOptions := options.Find().SetSort(bson.D{{"date", -1}}).SetLimit(10)
	cur, err := statistics.Find(ctx, bson.D{{"country", country}, {"state", nil}}, findOptions)
	if err != nil {
		panic(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{
			s.Date.String(),
			strconv.Itoa(int(s.Confirmed)),
			strconv.Itoa(int(s.Recovered)),
			strconv.Itoa(int(s.Deaths)),
		}
	}
	printTable(ctx, []string{"Date", "Confirmed", "Recovered", "Deaths"}, cur, adapter)
}

// mostRecentDateLoaded gets the date of the last data loaded into the database
// from the 'metadata' collection.
func mostRecentDateLoaded(metadata *mongo.Collection) time.Time {
	var meta Metadata
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	if err := metadata.FindOne(ctx, bson.D{}).Decode(&meta); err != nil {
		panic(fmt.Sprintf("Error loading metadata document: %v", err))
	}
	return meta.LastDate
}

// highestRecoveries prints the top 5 countries with the most recoveries.
func highestRecoveries(statistics *mongo.Collection, date time.Time) {
	/// The last day's highest reported recoveries
	opts := options.Find().SetSort(bson.D{{"recovered", -1}}).SetLimit(5)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	cur, err := statistics.Find(ctx, bson.D{{"date", date}}, opts)
	if err != nil {
		panic(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Recovered))}
	}
	printTable(ctx, []string{"Country", "Recovered"}, cur, adapter)
}

// Confirmed cases for all countries within radius km of a lon/lat coordinate:
func confirmedWithinRadius(statistics *mongo.Collection, date time.Time, lon float64, lat float64, radius float64) {
	center := bson.A{lon, lat}
	locationExpr := bson.E{
		"loc", bson.D{{
			"$geoWithin", bson.D{{
				"$centerSphere", bson.A{center, radius / earthRadius},
			}},
		}},
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	cur, err := statistics.Find(ctx, bson.D{{"date", date}, locationExpr})
	if err != nil {
		panic(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Confirmed))}
	}
	printTable(ctx, []string{"Country", "Confirmed"}, cur, adapter)
}

// printTable prints the results of a statistics query in a table.
// headings provides the heading cell contents
// mapper is a function which maps Statistic structs to a string array of values to be displayed in the table.
func printTable(ctx context.Context, headings []string, cursor *mongo.Cursor, mapper func(Statistic) []string) {
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader(headings)

	for cursor.Next(ctx) {
		var result Statistic
		err := cursor.Decode(&result)
		if err != nil {
			panic(err)
		}

		table.Append(mapper(result))
	}
	if err := cursor.Err(); err != nil {
		panic(err)
	}

	table.Render()
}
