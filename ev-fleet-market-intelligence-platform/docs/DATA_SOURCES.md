<table>
  <thead>
    <tr>
      <th>Data Area</th>
      <th>Proposed Source</th>
      <th>Source Type</th>
      <th>Format</th>
      <th>Required Fields Available?</th>
      <th>Portfolio Use Allowed?</th>
      <th>Missing Data</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Vehicles</td>
      <td>
        <a href="https://open.canada.ca/data/en/dataset/98f1a129-f628-4ce4-b24d-6f16bf24dd64" target="_blank" rel="noopener noreferrer">
          Natural Resources Canada fuel-consumption ratings
        </a>
      </td>
      <td>Public</td>
      <td>CSV</td>
      <td>Partially</td>
      <td>Yes — Open Government Licence</td>
      <td>Fleet vehicle ID and operational status</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Fleet Operators</td>
      <td>Project-generated synthetic data</td>
      <td>Synthetic</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Trips</td>
      <td>
        <a href="https://www.nrel.gov/transportation/fleettest-fleet-dna.html" target="_blank" rel="noopener noreferrer">
          Synthetic data informed by NREL Fleet DNA
        </a>
      </td>
      <td>Combined</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes &mdash; attribution required under NREL data-use terms</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Charging Sessions</td>
      <td>Project-generated synthetic data</td>
      <td>Synthetic</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Charging Locations</td>
      <td>
        <a href="https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/" target="_blank" rel="noopener noreferrer">
          NREL Alternative Fuel Stations API
        </a>
      </td>
      <td>Public</td>
      <td>CSV, JSON or GeoJSON</td>
      <td>Partially</td>
      <td>Yes &mdash; attribution required under NREL data-use terms</td>
      <td>Internal fleet location and charging-session activity</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Vehicle and Battery Telemetry</td>
      <td>
        <a href="https://www.nrel.gov/transportation/fleettest-fleet-dna.html" target="_blank" rel="noopener noreferrer">
          Synthetic data informed by NREL Fleet DNA
        </a>
      </td>
      <td>Combined</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes &mdash; attribution required under NREL data-use terms</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>Operating Costs</td>
      <td>Project-generated synthetic data</td>
      <td>Synthetic</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
    <tr>
      <td>EV Market Data</td>
      <td>
        <a href="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501" target="_blank" rel="noopener noreferrer">
          Statistics Canada Table 20-10-0025-01
        </a>
      </td>
      <td>Public</td>
      <td>CSV</td>
      <td>Yes</td>
      <td>Yes — Statistics Canada Open Licence</td>
      <td>None</td>
      <td>Selected</td>
    </tr>
  </tbody>
</table>

## Synthetic Data Generation Methods

### Generating Fleet Operator Data

Creating fictional fleet operators using predefined lists of industries, Canadian locations, fleet sizes, and operating regions.

### Generating Trip Data

Creating trips by assigning vehicles realistic starting times, ending times, distances, durations, locations, speeds, and energy consumption values. Using NREL Fleet DNA only for informing realistic operating ranges.

### Generating Charging Session Data

Creating charging sessions linked to vehicles and charging locations. Calculating session duration, energy delivered, battery-level changes, and charging costs using defined rules.

### Generating Vehicle and Battery Telemetry

Creating time-based readings for each trip, including vehicle location, speed, battery level, temperature, energy-consumption rate, and operating status. Keeping readings consistent with their associated trip.

### Generating Operating Cost Data

Creating charging, maintenance, repair, insurance, and other cost records. Calculating costs using documented rates and linking each cost to a vehicle and date.

## Attribution Requirements

When using NREL data, retaining the applicable NREL notice and crediting the U.S. Department of Energy, NREL, and Alliance for Sustainable Energy.

When referring to Fleet DNA, citing the source using the citation guidance published on the Fleet DNA website.
