package com.mongodb.coronavirus;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.codecs.configuration.CodecRegistry;
import org.bson.codecs.pojo.PojoCodecProvider;

import java.util.function.Consumer;

import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Sorts.descending;
import static org.bson.codecs.configuration.CodecRegistries.fromProviders;
import static org.bson.codecs.configuration.CodecRegistries.fromRegistries;

public class MongoDB {

    public static void main(String[] args) {
        MongoDatabase db = getMongoClient().getDatabase("coronavirus");
        MongoCollection<Statistic> statsCollection = db.getCollection("statistics", Statistic.class);
        MongoCollection<Metadata> metadataCollection = db.getCollection("metadata", Metadata.class);

        metadataCollection.find().forEach((Consumer<Object>) System.out::println);
        statsCollection.find(eq("country", "France")).sort(descending("date")).limit(10).forEach(System.out::println);
    }

    private static MongoClient getMongoClient() {
        String connectionString = "mongodb+srv://readonly:readonly@covid-19.hip2i.mongodb.net/test";
        CodecRegistry pojoCodecRegistry = fromProviders(PojoCodecProvider.builder().automatic(true).build());
        CodecRegistry codecRegistry = fromRegistries(MongoClientSettings.getDefaultCodecRegistry(), pojoCodecRegistry);
        return MongoClients.create(MongoClientSettings.builder()
                                                      .applyConnectionString(new ConnectionString(connectionString))
                                                      .codecRegistry(codecRegistry)
                                                      .build());
    }
}