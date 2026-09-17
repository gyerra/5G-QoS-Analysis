# Review 2 — Dataset Documentation

## Dataset Location and Discovery

To preserve data integrity and prevent redundant storage in the repository, the Review 2 analysis module does not duplicate the 50,000-row primary dataset.

Instead, the analysis scripts dynamically discover and load `5g_network_data.csv` from the repository root using Python's `pathlib.Path`:

- **Primary File**: `5g_network_data.csv` (located at repository root: `../5g_network_data.csv`)
- **Dataset Size**: ~6.5 MB (50,000 observations × 21 attributes)
- **Data Integrity**: The original CSV file is treated as strictly read-only and is never modified, overwritten, or subsetted destructively.

## Dataset Features

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `Timestamp` | Datetime / Object | Timestamp of the network telemetry measurement |
| `Location` | Categorical (String) | Geographic zone (Urban, Suburban, Rural, etc.) |
| `Signal Strength (dBm)` | Numerical (Float) | Received signal power in decibel-milliwatts |
| `Download Speed (Mbps)` | Numerical (Float) | Downlink throughput in Megabits per second |
| `Upload Speed (Mbps)` | Numerical (Float) | Uplink throughput in Megabits per second |
| `Latency (ms)` | Numerical (Float) | Round-trip time in milliseconds |
| `Jitter (ms)` | Numerical (Float) | Packet delay variation in milliseconds |
| `Network Type` | Categorical (String) | Telephony generation (5G, 4G LTE, 3G, etc.) |
| `Device Model` | Categorical (String) | User equipment smartphone model |
| `Carrier` | Categorical (String) | Cellular network service provider |
| `Band` | Categorical (String) | Radio frequency operational band |
| `Battery Level (%)` | Numerical (Integer) | Remaining device battery percentage |
| `Temperature (°C)` | Numerical (Float) | Device operating temperature |
| `Connected Duration (min)` | Numerical (Integer) | Session connection duration |
| `Handover Count` | Numerical (Integer) | Number of cell tower handovers during session |
| `Data Usage (MB)` | Numerical (Float) | Total data transferred in Megabytes |
| `Video Streaming Quality` | Categorical / Discrete | Discrete streaming quality index / resolution |
| `VoNR Enabled` | Boolean | Voice over New Radio (5G voice) activation status |
| `Network Congestion Level` | Categorical (String) | Traffic load status (Low, Medium, High) |
| `Ping to Google (ms)` | Numerical (Float) | Internet destination ping latency in milliseconds |
| `Dropped Connection` | Boolean | Whether connection was dropped / failure event |
