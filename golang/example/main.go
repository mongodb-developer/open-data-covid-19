package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

const MDB_URL = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/covid19?retryWrites=true&w=majority"

type Metadata struct {
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

	statistics := client.Database("covid19").Collection("statistics")
	ctx, _ = context.WithTimeout(context.Background(), 30*time.Second)
	findOptions := options.Find().SetSort(bson.D{{"date", -1}})
	cur, err := statistics.Find(ctx, bson.D{{"country", "United Kingdom"}, {"state", nil}}, findOptions)
	if err != nil {
		log.Fatal(err)
	}
	defer cur.Close(ctx)
	for cur.Next(ctx) {
		var result Statistic
		err := cur.Decode(&result)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%v\n", result)
	}
	if err := cur.Err(); err != nil {
		log.Fatal(err)
	}

	fmt.Println("Done")
}
