package com.mongodb.coronavirus;

import java.util.List;
import java.util.Objects;

public class Coordinate {

    private String type;
    private List<Double> coordinates;

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public List<Double> getCoordinates() {
        return coordinates;
    }

    public void setCoordinates(List<Double> coordinates) {
        this.coordinates = coordinates;
    }

    @Override
    public String toString() {
        return "Coordinate{" + "type='" + type + '\'' + ", coordinates=" + coordinates + '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        Coordinate that = (Coordinate) o;
        return Objects.equals(type, that.type) && Objects.equals(coordinates, that.coordinates);
    }

    @Override
    public int hashCode() {
        return Objects.hash(type, coordinates);
    }
}
