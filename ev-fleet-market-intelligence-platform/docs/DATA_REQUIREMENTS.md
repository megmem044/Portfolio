# MVP Data Requirements

## Purpose

Explaining what data the platform needs, why it is needed, and how it will support analysis.

## Vehicles

### Description

Describing the electric vehicles being operated by each fleet.

### Important Fields

- Vehicle ID
- Manufacturer
- Model
- Model year
- Battery capacity
- Vehicle status

### Business Questions

- Which vehicles are currently active?
- Which vehicle models are included in the fleet?
- How does performance differ between vehicle models?

### Data Source

Not yet selected.

## Fleet Operators

### Description

Describing the organizations managing groups of electric vehicles.

### Important Fields

- Fleet operator ID
- Operator name
- Industry
- City
- Province
- Fleet size
- Operating region
- Operator status

### Business Questions

- How many fleet operators are being analyzed?
- How many vehicles does each operator manage?
- Which industries are represented?
- Where are the fleet operators located?
- How does fleet performance differ between operators?

### Data Source

Synthetic data generated for the project.

## Trips

### Description

Recording individual journeys completed by fleet vehicles, including travelling time, distance, location, and energy usage.

### Important Fields

- Trip ID
- Vehicle ID
- Starting date and time
- Ending date and time
- Starting location
- Ending location
- Distance travelled
- Trip duration
- Energy consumed
- Average speed
- Trip status

### Business Questions

- How many trips is each vehicle completing?
- How far is each vehicle travelling?
- How much energy is being consumed during each trip?
- Which vehicles are operating most frequently?
- How does energy efficiency differ between vehicles and trips?
- When are most trips occurring?

### Data Source

Synthetic data generated for the project using realistic operating ranges informed by NREL Fleet DNA.

## Charging Sessions

### Description

Recording each occasion when a fleet vehicle is connected to a charging station, including charging duration, energy delivered, battery levels, and cost.

### Important Fields

- Charging session ID
- Vehicle ID
- Charging location ID
- Starting date and time
- Ending date and time
- Starting battery percentage
- Ending battery percentage
- Energy delivered
- Charging duration
- Charging cost
- Charging status

### Business Questions

- How often is each vehicle being charged?
- How much energy is being delivered during each session?
- How long is each charging session taking?
- How much is charging costing?
- Which charging locations are being used most frequently?
- Are any charging sessions failing or ending unexpectedly?
- During which times is charging demand highest?

### Data Source

Synthetic data generated for the project.

## Charging Locations

### Description

Recording the physical locations and technical characteristics of charging stations available to fleet vehicles.

### Important Fields

- Charging location ID
- Station name
- Street address
- City
- Province
- Postal code
- Latitude
- Longitude
- Charging network
- Connector type
- Charging level
- Number of charging ports
- Access type
- Station status

### Business Questions

- Where are charging stations located?
- How many charging ports are available at each location?
- Which connector types and charging levels are available?
- Which charging networks operate the stations?
- Which charging locations are available to the public?
- Which locations are being used most frequently by fleet vehicles?
- Are fleet trips occurring within practical reach of charging locations?

### Data Source

Public charging-location data retrieved from the NREL Alternative Fuel Stations API, combined with synthetic fleet-location information where required.

## Vehicle and Battery Telemetry

### Description

Recording time-based sensor readings showing vehicle movement, battery condition, energy usage, and operating conditions.

### Important Fields

- Telemetry reading ID
- Vehicle ID
- Trip ID
- Reading date and time
- Latitude
- Longitude
- Speed
- Battery charge percentage
- Battery temperature
- Outside temperature
- Energy consumption rate
- Odometer reading
- Vehicle operating status

### Business Questions

- How is the battery charge level changing during each trip?
- How much energy is the vehicle consuming over time?
- Are any battery temperatures reaching unusual levels?
- How are outside temperatures affecting energy consumption?
- Where is each vehicle operating?
- Are any telemetry readings showing unusual vehicle behaviour?
- How does vehicle performance differ under different operating conditions?

### Data Source

Synthetic telemetry generated for the project using realistic operating ranges informed by NREL Fleet DNA.

## Operating Costs

### Description

Recording the expenses associated with operating and maintaining each fleet vehicle.

### Important Fields

- Cost record ID
- Vehicle ID
- Cost date
- Cost category
- Cost description
- Energy quantity
- Unit price
- Total cost
- Currency
- Service provider
- Invoice reference

### Business Questions

- What is the total operating cost for each vehicle?
- How much is being spent on charging?
- How much is being spent on maintenance and repairs?
- Which vehicles are the most expensive to operate?
- How are operating costs changing over time?
- What is the operating cost per kilometre?
- Which cost categories account for the most spending?

### Data Source

Synthetic cost data generated for the project using clearly documented assumptions for electricity, maintenance, and other operating expenses.

## EV Market Data

### Description

Recording changes in electric-vehicle adoption across Canadian locations and time periods.

### Important Fields

- Reporting period
- Geography
- Province or territory
- Vehicle type
- Fuel type
- Number of registrations
- Percentage of total registrations
- Quarterly change
- Year-over-year change

### Business Questions

- How many electric vehicles are being registered?
- How are EV registrations changing over time?
- Which provinces or territories have the most EV registrations?
- What percentage of new registrations are electric vehicles?
- How does battery-electric vehicle adoption compare with plug-in hybrid adoption?
- Which geographic areas are experiencing the strongest growth?
- How do fleet trends compare with the wider EV market?

### Data Source

Public quarterly vehicle-registration data from Statistics Canada Table 20-10-0025-01.