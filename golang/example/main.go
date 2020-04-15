package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/olekukonko/tablewriter"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

const MDB_URL = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19?retryWrites=true&w=majority"
const EARTH_RADIUS = 6371.0

type Metadata struct {
	LastDate time.Time `bson:"last_date"`
}

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

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(MDB_URL))
	if err != nil {
		log.Fatalf("Error initializing MongoDB Client: %v\n", err)
	}

	// Get references to the main collections:
	database := client.Database("covid19")
	statistics := database.Collection("statistics")
	metadata := database.Collection("metadata")

	// Print some interesting results:
	recentUKStats(statistics)
	lastDate := mostRecentDateLoaded(metadata)
	fmt.Printf("\nLast date loaded: %v\n", lastDate)
	highestRecoveries(statistics, lastDate)
	confirmedWithinRadius(statistics, lastDate, 2.341908, 48.860199, 500.0)
}

// Confirmed cases for all countries within 500km of Paris:
func confirmedWithinRadius(statistics *mongo.Collection, date time.Time, lat float64, lon float64, radius float64) {
	center := bson.A{lat, lon}

	fmt.Println("\nThe last day's confirmed cases for all the countries within 500km of Paris:")
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	cur, err := statistics.Find(ctx, bson.D{{"date", date}, {"loc", bson.D{{"$geoWithin", bson.D{
		{"$centerSphere", bson.A{center, radius / EARTH_RADIUS}}}}}}})
	if err != nil {
		log.Fatal(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Confirmed))}
	}
	printTable([]string{"Country", "Confirmed"}, cur, ctx, adapter)
}

// Get some results for the UK
func recentUKStats(statistics *mongo.Collection) {
	fmt.Println("\nMost recent 10 statistics for the UK:")
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	findOptions := options.Find().SetSort(bson.D{{"date", -1}}).SetLimit(10)
	cur, err := statistics.Find(ctx, bson.D{{"country", "United Kingdom"}, {"state", nil}}, findOptions)
	if err != nil {
		log.Fatal(err)
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
	printTable([]string{"Date", "Confirmed", "Recovered", "Deaths"}, cur, ctx, adapter)
}

// mostRecentDateLoaded gets the date of the last data loaded into the database
// from the 'metadata' collection.
func mostRecentDateLoaded(metadata *mongo.Collection) time.Time {
	var meta Metadata
	if err := metadata.FindOne(context.TODO(), bson.D{}).Decode(&meta); err != nil {
		log.Fatalf("Error loading metadata document: %v\n", err)
	}
	return meta.LastDate
}

func highestRecoveries(statistics *mongo.Collection, date time.Time) {
	/// The last day's highest reported recoveries
	fmt.Println("\nThe last day's highest reported recoveries:")
	opts := options.Find().SetSort(bson.D{{"recovered", -1}}).SetLimit(5)
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	cur, err := statistics.Find(ctx, bson.D{{"date", date}}, opts)
	if err != nil {
		log.Fatal(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Recovered))}
	}
	printTable([]string{"Country", "Recovered"}, cur, ctx, adapter)
}

// printTable prints the results of a statistics query in a table.
// headings provides the heading cell contents
// mapper is a funcion which maps Statistic structs to a string array of values to be displayed in the table.
func printTable(headings []string, cursor *mongo.Cursor, ctx context.Context, mapper func(Statistic) []string) {
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader(headings)

	for cursor.Next(ctx) {
		var result Statistic
		err := cursor.Decode(&result)
		if err != nil {
			log.Fatal(err)
		}

		table.Append(mapper(result))
	}
	if err := cursor.Err(); err != nil {
		log.Fatal(err)
	}

	table.Render()
}
