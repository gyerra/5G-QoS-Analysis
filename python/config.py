"""Shared configuration for the QoS analysis pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "python" / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "python" / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "python" / "output"
PLOTS_DIR = OUTPUT_DIR / "plots"
MODELS_DIR = OUTPUT_DIR / "models"
FRONTEND_DATA_DIR = PROJECT_ROOT / "public" / "data"

CSV_SEARCH_DIRS = [PROJECT_ROOT / "QOS Analysis", PROJECT_ROOT]

COL_TIMESTAMP = "Timestamp"
COL_LOCATION = "Location"
COL_SIGNAL = "Signal Strength (dBm)"
COL_DOWNLOAD = "Download Speed (Mbps)"
COL_UPLOAD = "Upload Speed (Mbps)"
COL_LATENCY = "Latency (ms)"
COL_JITTER = "Jitter (ms)"
COL_NETWORK = "Network Type"
COL_DEVICE = "Device Model"
COL_CARRIER = "Carrier"
COL_BAND = "Band"
COL_BATTERY = "Battery Level (%)"
COL_TEMP = "Temperature (°C)"
COL_DURATION = "Connected Duration (min)"
COL_HANDOVER = "Handover Count"
COL_DATA_USAGE = "Data Usage (MB)"
COL_VIDEO = "Video Streaming Quality"
COL_VONR = "VoNR Enabled"
COL_CONGESTION = "Network Congestion Level"
COL_PING = "Ping to Google (ms)"
COL_DROPPED = "Dropped Connection"

QOS_NUMERIC = [COL_SIGNAL, COL_DOWNLOAD, COL_UPLOAD, COL_LATENCY, COL_JITTER, COL_PING]
QOS_CATEGORICAL = [COL_LOCATION, COL_NETWORK, COL_CARRIER, COL_BAND, COL_CONGESTION, COL_DEVICE]
QOS_BOOLEAN = [COL_VONR, COL_DROPPED]

TARGET_DOWNLOAD = COL_DOWNLOAD
TARGET_LATENCY = COL_LATENCY
TARGET_UPLOAD = COL_UPLOAD

PRIMARY_TARGETS = [TARGET_DOWNLOAD, TARGET_LATENCY]

RANDOM_STATE = 42
TEST_SIZE = 0.2
