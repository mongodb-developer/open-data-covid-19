package com.mongodb.coronavirus;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.codecs.configuration.CodecRegistry;
import org.bson.codecs.pojo.PojoCodecProvider;
import org.bson.conversions.Bson;

import java.util.Date;

import static com.mongodb.client.model.Filters.*;
import static com.mongodb.client.model.Sorts.descending;
import static org.bson.codecs.configuration.CodecRegistries.fromProviders;
import static org.bson.codecs.configuration.CodecRegistries.fromRegistries;

public class MongoDB {

    public static void main(String[] args) {
        try (MongoClient client = MongoClients.create(getMongoClient())) {
            int earthRadius = 6371;
            MongoDatabase db = client.getDatabase("covid19");
            MongoCollection<Stat> statsCollection = db.getCollection("statistics", Stat.class);
            MongoCollection<Metadata> metadataCollection = db.getCollection("metadata", Metadata.class);

            System.out.println("Query to get the last 5 entries for France (continent only)");
            Bson franceFilter = eq("country", "France");
            Bson noStateFilter = eq("state", null);
            statsCollection.find(and(franceFilter, noStateFilter)).sort(descending("date")).limit(5).forEach(System.out::println);

            System.out.println("\nQuery to get the last day data (limited to 5 docs here).");
            Metadata metadata = metadataCollection.find().first();
            Date lastDate = metadata.getLastDate();
            Bson lastDayFilter = eq("date", lastDate);
            statsCollection.find(lastDayFilter).limit(5).forEach(System.out::println);

            System.out.println("\nQuery to get the last day data for all the countries within 500km of Paris.");
            Bson aroundParisFilter = geoWithinCenterSphere("loc", 2.341908, 48.860199, 500.0 / earthRadius);
            statsCollection.find(and(lastDayFilter, aroundParisFilter)).forEach(System.out::println);

            System.out.println("\nPrint the Metadata summary.");
            metadataCollection.find().forEach(System.out::println);
        }
    }

    private static MongoClientSettings getMongoClient() {
        String connectionString = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test";
        CodecRegistry pojoCodecRegistry = fromProviders(PojoCodecProvider.builder().automatic(true).build());
        CodecRegistry codecRegistry = fromRegistries(MongoClientSettings.getDefaultCodecRegistry(), pojoCodecRegistry);
        return MongoClientSettings.builder()
                                  .applyConnectionString(new ConnectionString(connectionString))
                                  .codecRegistry(codecRegistry)
                                  .build();
    }
}