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
	"go.mongodb.org/mongo-driver/mongo/readpref"
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
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(MDB_URL))
	if err != nil {
		log.Fatalf("Error initializing MongoDB Client: %v\n", err)
	}
	err = client.Ping(ctx, readpref.Primary())
	if err != nil {
		log.Fatalf("No Ping!: %v\n", err)
	}

	// Get references to the main collections:
	database := client.Database("covid19")
	statistics := database.Collection("statistics")
	metadata := database.Collection("metadata")

	recentUKStats(statistics)

	// Get the latest date:
	lastDate := mostRecentDateLoaded(metadata)
	fmt.Printf("\nLast date loaded: %v\n", lastDate)

	highestRecoveries(statistics, lastDate)
	confirmedWithinRadius(statistics, lastDate, 2.341908, 48.860199, 500.0)
}

func confirmedWithinRadius(statistics *mongo.Collection, date time.Time, lat float64, lon float64, radius float64) {
	center := bson.A{lat, lon}

	// Confirmed cases for all countries within 500km of Paris:
	fmt.Println("\nThe last day's confirmed cases for all the countries within 500km of Paris:")
	ctx, _ := context.WithTimeout(context.Background(), 30*time.Second)
	cur, err := statistics.Find(ctx, bson.D{{"date", date}, {"loc", bson.D{{"$geoWithin", bson.D{
		{"$centerSphere", bson.A{center, radius / EARTH_RADIUS}}}}}}})
	if err != nil {
		log.Fatal(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Confirmed))}
	}
	PrintTable([]string{"Country", "Confirmed"}, cur, &ctx, adapter)
}

func recentUKStats(statistics *mongo.Collection) {
	/// Get some results for the UK
	fmt.Println("\nMost recent 10 statistics for the UK:")
	ctx, _ := context.WithTimeout(context.Background(), 30*time.Second)
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
	PrintTable([]string{"Date", "Confirmed", "Recovered", "Deaths"}, cur, &ctx, adapter)
}

func mostRecentDateLoaded(metadata *mongo.Collection) time.Time {
	// Get the latest date:
	var meta Metadata
	if err := metadata.FindOne(context.TODO(), bson.D{}).Decode(&meta); err != nil {
		log.Fatalf("Error loading metadata document: %v\n", err)
	}
	return meta.LastDate
}

func highestRecoveries(statistics *mongo.Collection, date time.Time) {
	// The last day's highest reported recoveries
	fmt.Println("\nThe last day's highest reported recoveries:")
	opts := options.Find().SetSort(bson.D{{"recovered", -1}}).SetLimit(5)
	ctx, _ := context.WithTimeout(context.Background(), 30*time.Second)
	cur, err := statistics.Find(ctx, bson.D{{"date", date}}, opts)
	if err != nil {
		log.Fatal(err)
	}
	defer cur.Close(ctx)
	adapter := func(s Statistic) []string {
		return []string{s.CombinedName, strconv.Itoa(int(s.Recovered))}
	}
	PrintTable([]string{"Country", "Recovered"}, cur, &ctx, adapter)
}

func PrintTable(headings []string, cursor *mongo.Cursor, ctx *context.Context, mapper func(Statistic) []string) {
	table := tablewriter.NewWriter(os.Stdout)
	table.SetHeader(headings)

	for cursor.Next(context.TODO()) {
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
