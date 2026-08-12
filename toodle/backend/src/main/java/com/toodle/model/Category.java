package com.toodle.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import java.util.UUID;

@Entity
public class Category {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    private String name;
    private String color;
    @ManyToOne
    @JoinColumn(name = "owner_id")
    private AppUser owner;

    protected Category() {
    }

    public Category(String name, String color, AppUser owner) {
        this.name = name;
        this.color = color;
        this.owner = owner;
    }

    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getColor() { return color; }

    public void update(String name, String color) {
        this.name = name;
        this.color = color;
    }
}