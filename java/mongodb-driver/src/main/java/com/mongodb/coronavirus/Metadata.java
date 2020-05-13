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
    private List<String> counties;
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

    public List<String> getCounties() {
        return counties;
    }

    public void setCounties(List<String> counties) {
        this.counties = counties;
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
        sb.append("firstDate => ").append(firstDate).append("\n");
        sb.append("lastDate  => ").append(lastDate).append("\n");
        sb.append("countries => List of ").append(countries.size()).append(" countries.\n");
        sb.append("states    => List of ").append(states.size()).append(" states.\n");
        sb.append("counties  => List of ").append(counties.size()).append(" counties.\n");
        sb.append("iso3s     => List of ").append(iso3s.size()).append(" iso3s.\n");
        sb.append("uids      => List of ").append(uids.size()).append(" uids.\n");
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
                .equals(countries, metadata.countries) && Objects.equals(states, metadata.states) && Objects.equals(counties,
                                                                                                                    metadata.counties) && Objects
                .equals(iso3s, metadata.iso3s) && Objects.equals(uids, metadata.uids);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, firstDate, lastDate, countries, states, counties, iso3s, uids);
    }
}
