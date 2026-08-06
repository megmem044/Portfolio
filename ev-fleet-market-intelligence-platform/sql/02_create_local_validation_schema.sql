/*
Creating a local SQLite schema for validating the relational model.

This schema is used only for local testing. The Fabric Warehouse
schema remains in sql/01_create_tables.sql.
*/

PRAGMA foreign_keys = ON;

CREATE TABLE fleet_operator
(
    fleet_operator_id INTEGER      NOT NULL,
    operator_name     VARCHAR(150) NOT NULL,
    industry          VARCHAR(100) NOT NULL,
    city              VARCHAR(100) NOT NULL,
    province          VARCHAR(100) NOT NULL,
    operating_region  VARCHAR(150) NOT NULL,
    operator_status   VARCHAR(20)  NOT NULL,

    CONSTRAINT pk_fleet_operator
        PRIMARY KEY (fleet_operator_id)
);

CREATE TABLE vehicle_model
(
    vehicle_model_id                  INTEGER       NOT NULL,
    manufacturer                      VARCHAR(100)  NOT NULL,
    model_name                        VARCHAR(150)  NOT NULL,
    model_year                        INTEGER       NOT NULL,
    vehicle_class                     VARCHAR(100)  NULL,
    motor_power_kw                    DECIMAL(8, 2) NULL,
    battery_capacity_kwh              DECIMAL(8, 2) NULL,
    electric_range_km                 INTEGER       NULL,
    energy_consumption_kwh_per_100_km DECIMAL(8, 2) NULL,
    recharge_time_hours               DECIMAL(6, 2) NULL,

    CONSTRAINT pk_vehicle_model
        PRIMARY KEY (vehicle_model_id),

    CONSTRAINT uq_vehicle_model
        UNIQUE (manufacturer, model_name, model_year)
);

CREATE TABLE charging_location
(
    charging_location_id INTEGER       NOT NULL,
    station_name         VARCHAR(200)  NOT NULL,
    street_address       VARCHAR(250)  NULL,
    city                 VARCHAR(100)  NOT NULL,
    province             VARCHAR(100)  NOT NULL,
    postal_code          VARCHAR(20)   NULL,
    latitude             DECIMAL(9, 6) NOT NULL,
    longitude            DECIMAL(9, 6) NOT NULL,
    charging_network     VARCHAR(100)  NULL,
    access_type          VARCHAR(50)   NULL,
    station_status       VARCHAR(20)   NOT NULL,

    CONSTRAINT pk_charging_location
        PRIMARY KEY (charging_location_id)
);


CREATE TABLE ev_market_registration
(
    market_registration_id   INTEGER      NOT NULL,
    reference_year           INTEGER      NOT NULL,
    reference_quarter        INTEGER      NOT NULL,
    geography_level          VARCHAR(50)  NOT NULL,
    geography_name           VARCHAR(150) NOT NULL,
    province_or_territory    VARCHAR(100) NULL,
    vehicle_type             VARCHAR(100) NOT NULL,
    fuel_type                VARCHAR(100) NOT NULL,
    registration_count       INTEGER      NOT NULL,
    total_registration_count INTEGER      NOT NULL,

    CONSTRAINT pk_ev_market_registration
        PRIMARY KEY (market_registration_id),

    CONSTRAINT uq_ev_market_registration
        UNIQUE
        (
            reference_year,
            reference_quarter,
            geography_level,
            geography_name,
            vehicle_type,
            fuel_type
        ),

    CONSTRAINT ck_market_reference_quarter
        CHECK (reference_quarter BETWEEN 1 AND 4),

    CONSTRAINT ck_market_registration_count
        CHECK (registration_count >= 0),

    CONSTRAINT ck_market_total_registration_count
        CHECK (total_registration_count >= registration_count)
);


CREATE TABLE fleet
(
    fleet_id          INTEGER      NOT NULL,
    fleet_operator_id INTEGER      NOT NULL,
    fleet_name        VARCHAR(150) NOT NULL,
    fleet_type        VARCHAR(100) NOT NULL,
    city              VARCHAR(100) NOT NULL,
    province          VARCHAR(100) NOT NULL,
    operating_region  VARCHAR(150) NOT NULL,
    fleet_status      VARCHAR(20)  NOT NULL,

    CONSTRAINT pk_fleet
        PRIMARY KEY (fleet_id),

    CONSTRAINT uq_fleet_operator_name
        UNIQUE (fleet_operator_id, fleet_name),

    CONSTRAINT fk_fleet_operator
        FOREIGN KEY (fleet_operator_id)
        REFERENCES fleet_operator (fleet_operator_id)
);

CREATE TABLE charging_port
(
    charging_port_id     INTEGER       NOT NULL,
    charging_location_id INTEGER       NOT NULL,
    port_number          VARCHAR(50)   NOT NULL,
    connector_type       VARCHAR(50)   NOT NULL,
    charging_level       VARCHAR(50)   NOT NULL,
    maximum_power_kw     DECIMAL(8, 2) NULL,
    port_status          VARCHAR(20)   NOT NULL,

    CONSTRAINT pk_charging_port
        PRIMARY KEY (charging_port_id),

    CONSTRAINT uq_charging_location_port
        UNIQUE (charging_location_id, port_number),

    CONSTRAINT fk_charging_port_location
        FOREIGN KEY (charging_location_id)
        REFERENCES charging_location (charging_location_id),

    CONSTRAINT ck_charging_port_power
        CHECK (maximum_power_kw IS NULL OR maximum_power_kw >= 0)
);

CREATE TABLE vehicle
(
    vehicle_id           INTEGER        NOT NULL,
    fleet_id             INTEGER        NOT NULL,
    vehicle_model_id     INTEGER        NOT NULL,
    fleet_vehicle_number VARCHAR(50)    NOT NULL,
    vin                  VARCHAR(17)    NOT NULL,
    licence_plate        VARCHAR(20)    NOT NULL,
    acquisition_date     DATE           NOT NULL,
    in_service_date      DATE           NOT NULL,
    initial_odometer_km  DECIMAL(12, 2) NOT NULL,
    vehicle_status       VARCHAR(20)    NOT NULL,

    CONSTRAINT pk_vehicle
        PRIMARY KEY (vehicle_id),

    CONSTRAINT uq_vehicle_vin
        UNIQUE (vin),

    CONSTRAINT uq_fleet_vehicle_number
        UNIQUE (fleet_id, fleet_vehicle_number),

    CONSTRAINT fk_vehicle_fleet
        FOREIGN KEY (fleet_id)
        REFERENCES fleet (fleet_id),

    CONSTRAINT fk_vehicle_model
        FOREIGN KEY (vehicle_model_id)
        REFERENCES vehicle_model (vehicle_model_id),

    CONSTRAINT ck_vehicle_vin_length
        CHECK (LENGTH(vin) = 17),

    CONSTRAINT ck_vehicle_dates
        CHECK (in_service_date >= acquisition_date),

    CONSTRAINT ck_vehicle_initial_odometer
        CHECK (initial_odometer_km >= 0)
);

CREATE TABLE trip
(
    trip_id             INTEGER        NOT NULL,
    vehicle_id          INTEGER        NOT NULL,
    start_timestamp     DATETIME       NOT NULL,
    end_timestamp       DATETIME       NOT NULL,
    start_latitude      DECIMAL(9, 6)  NOT NULL,
    start_longitude     DECIMAL(9, 6)  NOT NULL,
    end_latitude        DECIMAL(9, 6)  NOT NULL,
    end_longitude       DECIMAL(9, 6)  NOT NULL,
    distance_km         DECIMAL(12, 2) NOT NULL,
    energy_consumed_kwh DECIMAL(12, 3) NOT NULL,
    average_speed_kmh   DECIMAL(8, 2)  NOT NULL,
    trip_status         VARCHAR(20)    NOT NULL,

    CONSTRAINT pk_trip
        PRIMARY KEY (trip_id),

    CONSTRAINT fk_trip_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicle (vehicle_id),

    CONSTRAINT ck_trip_timestamps
        CHECK (end_timestamp > start_timestamp),

    CONSTRAINT ck_trip_start_latitude
        CHECK (start_latitude BETWEEN -90 AND 90),

    CONSTRAINT ck_trip_start_longitude
        CHECK (start_longitude BETWEEN -180 AND 180),

    CONSTRAINT ck_trip_end_latitude
        CHECK (end_latitude BETWEEN -90 AND 90),

    CONSTRAINT ck_trip_end_longitude
        CHECK (end_longitude BETWEEN -180 AND 180),

    CONSTRAINT ck_trip_nonnegative_values
        CHECK
        (
            distance_km >= 0
            AND energy_consumed_kwh >= 0
            AND average_speed_kmh >= 0
        )
);

CREATE TABLE charging_session
(
    charging_session_id         INTEGER        NOT NULL,
    vehicle_id                  INTEGER        NOT NULL,
    charging_port_id            INTEGER        NOT NULL,
    start_timestamp             DATETIME       NOT NULL,
    end_timestamp               DATETIME       NOT NULL,
    starting_battery_percentage DECIMAL(5, 2)  NOT NULL,
    ending_battery_percentage   DECIMAL(5, 2)  NOT NULL,
    energy_delivered_kwh        DECIMAL(12, 3) NOT NULL,
    price_per_kwh               DECIMAL(10, 4) NOT NULL,
    additional_fee              DECIMAL(10, 2) NOT NULL,
    charging_status             VARCHAR(20)    NOT NULL,

    CONSTRAINT pk_charging_session
        PRIMARY KEY (charging_session_id),

    CONSTRAINT fk_charging_session_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicle (vehicle_id),

    CONSTRAINT fk_charging_session_port
        FOREIGN KEY (charging_port_id)
        REFERENCES charging_port (charging_port_id),

    CONSTRAINT ck_charging_session_timestamps
        CHECK (end_timestamp > start_timestamp),

    CONSTRAINT ck_charging_session_battery_range
        CHECK
        (
            starting_battery_percentage BETWEEN 0 AND 100
            AND ending_battery_percentage BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_charging_session_nonnegative_values
        CHECK
        (
            energy_delivered_kwh >= 0
            AND price_per_kwh >= 0
            AND additional_fee >= 0
        )
);

CREATE TABLE telemetry_reading
(
    telemetry_reading_id        INTEGER        NOT NULL,
    vehicle_id                  INTEGER        NOT NULL,
    trip_id                     INTEGER        NOT NULL,
    reading_timestamp           DATETIME       NOT NULL,
    latitude                    DECIMAL(9, 6)  NOT NULL,
    longitude                   DECIMAL(9, 6)  NOT NULL,
    speed_kmh                   DECIMAL(8, 2)  NOT NULL,
    battery_percentage          DECIMAL(5, 2)  NOT NULL,
    battery_temperature_celsius DECIMAL(6, 2)  NOT NULL,
    outside_temperature_celsius DECIMAL(6, 2)  NOT NULL,
    energy_consumption_rate_kw  DECIMAL(10, 3) NOT NULL,
    odometer_km                 DECIMAL(12, 2) NOT NULL,
    operating_status            VARCHAR(20)    NOT NULL,

    CONSTRAINT pk_telemetry_reading
        PRIMARY KEY (telemetry_reading_id),

    CONSTRAINT uq_trip_reading_timestamp
        UNIQUE (trip_id, reading_timestamp),

    CONSTRAINT fk_telemetry_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicle (vehicle_id),

    CONSTRAINT fk_telemetry_trip
        FOREIGN KEY (trip_id)
        REFERENCES trip (trip_id),

    CONSTRAINT ck_telemetry_latitude
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT ck_telemetry_longitude
        CHECK (longitude BETWEEN -180 AND 180),

    CONSTRAINT ck_telemetry_battery_range
        CHECK (battery_percentage BETWEEN 0 AND 100),

    CONSTRAINT ck_telemetry_nonnegative_values
        CHECK (speed_kmh >= 0 AND odometer_km >= 0)
);

CREATE TABLE operating_cost
(
    operating_cost_id   INTEGER        NOT NULL,
    vehicle_id          INTEGER        NOT NULL,
    charging_session_id INTEGER        NULL,
    cost_date           DATE           NOT NULL,
    cost_category       VARCHAR(50)    NOT NULL,
    cost_description    VARCHAR(250)   NULL,
    quantity            DECIMAL(12, 3) NULL,
    unit_price          DECIMAL(12, 4) NULL,
    total_cost          DECIMAL(12, 2) NOT NULL,
    currency_code       VARCHAR(3)     NOT NULL,
    service_provider    VARCHAR(150)   NULL,
    invoice_reference   VARCHAR(100)   NULL,

    CONSTRAINT pk_operating_cost
        PRIMARY KEY (operating_cost_id),

    CONSTRAINT fk_operating_cost_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicle (vehicle_id),

    CONSTRAINT fk_operating_cost_charging_session
        FOREIGN KEY (charging_session_id)
        REFERENCES charging_session (charging_session_id),

    CONSTRAINT ck_operating_cost_quantity
        CHECK (quantity IS NULL OR quantity >= 0),

    CONSTRAINT ck_operating_cost_unit_price
        CHECK (unit_price IS NULL OR unit_price >= 0),

    CONSTRAINT ck_operating_cost_total
        CHECK (total_cost >= 0),

    CONSTRAINT ck_operating_cost_currency
        CHECK (LENGTH(currency_code) = 3)
);
