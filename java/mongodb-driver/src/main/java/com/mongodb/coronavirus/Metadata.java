package com.mongodb.coronavirus;

import org.bson.codecs.pojo.annotations.BsonProperty;

import java.util.Date;
import java.util.List;
import java.util.Objects;

public class Metadata {

    private String id;
    @BsonProperty("first_date")
    private Date firstDate;
    @BsonProperty("last_date")
    private Date lastDate;
    private List<String> countries;
    private List<String> states;
    private List<String> cities;
    private List<String> iso3s;
    private List<Integer> uids;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Date getFirstDate() {
        return firstDate;
    }

    public void setFirstDate(Date firstDate) {
        this.firstDate = firstDate;
    }

    public Date getLastDate() {
        return lastDate;
    }

    public void setLastDate(Date lastDate) {
        this.lastDate = lastDate;
    }

    public List<String> getCountries() {
        return countries;
    }

    public void setCountries(List<String> countries) {
        this.countries = countries;
    }

    public List<String> getStates() {
        return states;
    }

    public void setStates(List<String> states) {
        this.states = states;
    }

    public List<String> getCities() {
        return cities;
    }

    public void setCities(List<String> cities) {
        this.cities = cities;
    }

    public List<String> getIso3s() {
        return iso3s;
    }

    public void setIso3s(List<String> iso3s) {
        this.iso3s = iso3s;
    }

    public List<Integer> getUids() {
        return uids;
    }

    public void setUids(List<Integer> uids) {
        this.uids = uids;
    }

    @Override
    public String toString() {
        final StringBuffer sb = new StringBuffer("Metadata:").append("\n");
        sb.append("id\t\t\t=> ").append(id).append("\n");
        sb.append("firstDate\t=> ").append(firstDate).append("\n");
        sb.append("lastDate\t=> ").append(lastDate).append("\n");
        sb.append("countries\t=> ").append(countries).append("\n");
        sb.append("states\t\t=> ").append(states).append("\n");
        sb.append("cities\t\t=> ").append(cities).append("\n");
        sb.append("iso3s\t\t=> ").append(iso3s).append("\n");
        sb.append("uids\t\t=> ").append(uids).append("\n");
        return sb.toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Metadata metadata = (Metadata) o;
        return Objects.equals(id, metadata.id) && Objects.equals(firstDate, metadata.firstDate) && Objects.equals(lastDate,
                                                                                                                  metadata.lastDate) && Objects
                .equals(countries, metadata.countries) && Objects.equals(states, metadata.states) && Objects.equals(cities,
                                                                                                                    metadata.cities) && Objects
                .equals(iso3s, metadata.iso3s) && Objects.equals(uids, metadata.uids);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, firstDate, lastDate, countries, states, cities, iso3s, uids);
    }
}
