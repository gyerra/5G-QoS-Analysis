# 5G Network Dataset — Data Profile Report

**Generated:** 2026-08-07T15:00:04.496328+00:00
**Inspection script:** `python/inspect_dataset.py`

## 1. Files Found

- `5g_network_data.csv` — **50,000** rows × **21** columns

## 2. Merge Recommendation

A single CSV file was found. **Analyse as a standalone dataset** — no merge required.

## 3. Column Overview

### 5g_network_data.csv

| Column | Type | Category | Missing | Unique | QoS Roles |
| --- | --- | --- | --- | --- | --- |
| Timestamp | str | datetime_candidate | 0 (0.0%) | 50000 | timestamp |
| Location | str | categorical | 0 (0.0%) | 8 | location |
| Signal Strength (dBm) | float64 | numerical | 0 (0.0%) | 501 | signal_strength |
| Download Speed (Mbps) | float64 | numerical | 0 (0.0%) | 38384 | download_speed |
| Upload Speed (Mbps) | float64 | numerical | 0 (0.0%) | 12738 | upload_speed |
| Latency (ms) | float64 | numerical | 0 (0.0%) | 191 | latency |
| Jitter (ms) | float64 | numerical | 0 (0.0%) | 491 | jitter |
| Network Type | str | categorical | 0 (0.0%) | 3 | network_technology |
| Device Model | str | categorical | 0 (0.0%) | 5 | — |
| Carrier | str | categorical | 0 (0.0%) | 7 | carrier |
| Band | str | categorical | 0 (0.0%) | 5 | — |
| Battery Level (%) | int64 | numerical | 0 (0.0%) | 90 | — |
| Temperature (°C) | float64 | numerical | 0 (0.0%) | 251 | — |
| Connected Duration (min) | int64 | numerical | 0 (0.0%) | 59 | — |
| Handover Count | int64 | numerical | 0 (0.0%) | 5 | — |
| Data Usage (MB) | float64 | numerical | 0 (0.0%) | 31385 | — |
| Video Streaming Quality | int64 | numerical | 0 (0.0%) | 5 | — |
| VoNR Enabled | bool | boolean | 0 (0.0%) | 2 | — |
| Network Congestion Level | str | categorical | 0 (0.0%) | 3 | — |
| Ping to Google (ms) | float64 | numerical | 0 (0.0%) | 901 | — |
| Dropped Connection | bool | boolean | 0 (0.0%) | 2 | dropped_connection |

## 4. QoS Metrics Availability

- **Download Speed**: Available (`Download Speed (Mbps)`)
- **Upload Speed**: Available (`Upload Speed (Mbps)`)
- **Latency**: Available (`Latency (ms)`)
- **Jitter**: Available (`Jitter (ms)`)
- **Packet Loss**: **NOT AVAILABLE**
- **Dropped Connection**: Available (`Dropped Connection`)
- **Signal Strength**: Available (`Signal Strength (dBm)`)
- **Network Technology**: Available (`Network Type`)
- **Carrier**: Available (`Carrier`)
- **Location**: Available (`Location`)
- **Timestamp**: Available (`Timestamp`)

## 5. Data Quality

### 5g_network_data.csv
- Duplicate rows: **0**
- No missing values detected.

## 6. Recommended ML Targets

- **download_speed** → `Download Speed (Mbps)`
- **latency** → `Latency (ms)`
- **upload_speed** → `Upload Speed (Mbps)`

## 7. Potential ML Features

- `Signal Strength (dBm)` (signal_strength)
- `Jitter (ms)` (jitter)
- `Dropped Connection` (dropped_connection)
- `Network Type` (network_technology)
- `Carrier` (carrier)
- `Location` (location)
- `Timestamp` (timestamp)
- `Battery Level (%)` (other_numeric)
- `Temperature (°C)` (other_numeric)
- `Connected Duration (min)` (other_numeric)
- `Handover Count` (other_numeric)
- `Data Usage (MB)` (other_numeric)
- `Video Streaming Quality` (other_numeric)
- `Ping to Google (ms)` (other_numeric)

## 8. Data Quality Impact on Project

- Dataset contains 50,000 records — sufficient for EDA and ML.
- Unavailable QoS metrics (packet_loss) will be excluded from analysis.
- Timestamp column present — chronological train/test split recommended for ML.
- No continuous packet-loss percentage column; 'Dropped Connection' (boolean) is available as a drop-event indicator only.
