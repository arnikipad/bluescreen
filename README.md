# ARCHIVE NOTICE

> This repository has been archived as of 2026-09-07 (v6.0 "Autumn").
>
> Meteorological Autumn 2026 begins on 2026-09-01 and the astronomical
> Autumnal Equinox in 2026 begins on 2026-09-22. This release is named
> "Autumn" to reflect the 2026 Autumn timeframe.
>
> References:
> - https://www.metoffice.gov.uk/blog/2026/when-does-autumn-start
> - https://www.timeanddate.com/calendar/autumnal-equinox.html
> - https://www.almanac.com/content/first-day-fall-autumnal-equinox

This repository is archived and will no longer receive feature updates or
upgrades. The project release v6.0 "Autumn" is the final release. The
program can no longer be upgraded from this point — there will be no further
upgrade path provided by the maintainers.

If you need to use the software, treat this repository as read-only. Take
care to only run the code in controlled test environments (virtual machines
or disposable systems) and follow the safety guidance in the README (dry-run
mode and explicit enablement required for destructive actions).

---

```markdown
# BlueScreen Trigger v5.0

Enterprise-grade Windows BSOD (Blue Screen of Death) generator with machine learning analytics, predictive modeling, and advanced system monitoring.

## Overview

**BlueScreen Trigger** is a sophisticated tool for triggering Windows system crashes with progressive versions offering increasingly advanced features:

- **v1**: Basic BSOD trigger with error handling
- **v2**: Async support, enhanced logging, CLI arguments
- **v3**: Recovery mechanisms, system snapshots, multiple trigger methods
- **v4**: Database persistence, REST API, scheduling, telemetry, plugins
- **v5**: Machine learning, anomaly detection, predictive analytics, visualization

## Features

### Core Functionality
- Trigger Windows BSOD via NtRaiseHardError Windows API call
- Multiple error code options (INVALID_IMAGE_FORMAT, FATAL_USER_CALLBACK_EXCEPTION, etc.)
- Dry-run mode for safe testing without actual system effects
- Comprehensive logging and error handling
- Platform verification and privilege escalation

### Version 5 Enhancements
- **Machine Learning Models**
  - Neural network-based success prediction
  - Isolation Forest anomaly detection
  - Model persistence and training

- **Metrics Collection**
  - Real-time CPU, memory, disk, and network monitoring
  - Historical metrics storage in SQLite
  - Automatic baseline collection

- **Analytics Engine**
  - 24-hour trend analysis
  - Optimal trigger time prediction
  - Statistical calculations (mean, std, min, max)
  - System load forecasting

- **Anomaly Detection**
  - Detect unusual system behavior patterns
  - Real-time anomaly scoring
  - Configurable thresholds

- **Predictive Analytics**
  - Forecast trigger success probability
  - Recommend optimal system parameters
  - Confidence scoring

- **Data Visualization**
  - Interactive timeline charts (Plotly)
  - Anomaly detection visualizations
  - Comprehensive analytics dashboards
  - Beautiful HTML reports

## Installation

### Requirements
- Windows OS (7+)
- Python 3.8+
- Administrator privileges (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arnikipad/bluescreen.git
cd bluescreen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install as package:
```bash
pip install -e .
```

## Usage

### Version 5.0

#### Basic Commands

Collect system metrics:
```bash
python bluescreen_v5.py --dry-run --collect
```

Train ML models on historical data:
```bash
python bluescreen_v5.py --train --hours 24
```

Analyze current system metrics:
```bash
python bluescreen_v5.py --analyze
```

Predict trigger outcome:
```bash
python bluescreen_v5.py --predict
```

Generate visualizations:
```bash
python bluescreen_v5.py --visualize
```

Generate analytics report:
```bash
python bluescreen_v5.py --report
```

Show system summary:
```bash
python bluescreen_v5.py --summary
```

Execute trigger (requires no --dry-run):
```bash
python bluescreen_v5.py --trigger
```

#### Advanced Options

```bash
--dry-run              # Run without actual system effects
--hours N              # Specify hours of historical data to use
--collect              # Collect system metrics
--train                # Train ML models
--analyze              # Perform metrics analysis
--predict              # Generate trigger predictions
--visualize            # Create visualization dashboards
--report               # Generate comprehensive report
--summary              # Show system summary
--trigger              # Execute the trigger
```

### Version 4.0

REST API server:
```bash
python bluescreen_v4.py --api
```

Scheduled trigger:
```bash
python bluescreen_v4.py --scheduler
```

Check status:
```bash
python bluescreen_v4.py --status
```

View history:
```bash
python bluescreen_v4.py --history 50
```

### Version 3.0

With recovery points:
```bash
python bluescreen_v3.py --dry-run --method ntraise
```

With event logging:
```bash
python bluescreen_v3.py --event-log --log-file system.log
```

### Version 2.0

With delay:
```bash
python bluescreen_v2.py --delay 5 --error-code PRIVILEGED_INSTRUCTION
```

### Version 1.0

Basic execution:
```bash
python bluescreen_v1.py
```

## Architecture

### Component Hierarchy

```
BlueScreenTriggerV5
├── MetricsCollector
│   └── SystemMetrics
├── AnomalyDetector
│   ├── Isolation Forest Model
│   └── StandardScaler
├── TriggerSuccessPredictor
│   ├── Neural Network (MLP)
│   └── StandardScaler
├── AnalyticsEngine
│   └── Trend Analysis
├── VisualizationEngine
│   ├── Plotly Visualizations
│   └── HTML Dashboards
└── BlueScreenLogger
    └── Multi-Handler Logging
```

### Database Schema

**Metrics Table:**
- timestamp, cpu_percent, memory_percent, disk_percent
- process_count, network stats, disk I/O
- context switches, interrupts

### ML Models

**AnomalyDetector:**
- Algorithm: Isolation Forest
- Features: 10 system metrics
- Contamination: 10% (configurable)
- Output: Anomaly score [0.0, 1.0]

**TriggerSuccessPredictor:**
- Algorithm: Multi-Layer Perceptron (Neural Network)
- Hidden Layers: 128 → 64 → 32 neurons
- Activation: ReLU
- Output: Success probability [0.0, 1.0]

## Configuration

### Default Configuration (auto-generated)

```yaml
general:
  dry_run: true
  obfuscate: false
  log_file: bluescreen_v4.log

database:
  enabled: true
  path: bluescreen_v4.db

api:
  enabled: false
  host: 127.0.0.1
  port: 8888
  auth_enabled: false

schedule:
  enabled: false
  interval_seconds: 3600

telemetry:
  enabled: false
  endpoint: ""

trigger:
  method: ntraise
  error_code: INVALID_IMAGE_FORMAT
  timeout_seconds: 10
```

## Output Formats

### Analytics Report
```
===== BLUESCREEN V5 ANALYTICS REPORT =====
Generated: 2026-09-05T13:39:45Z

SYSTEM METRICS:
  CPU Usage: 45.2%
  Memory Usage: 62.8%
  Disk Usage: 78.1%
  Process Count: 245

TRENDS (24h):
  CPU: stable (mean: 42.3%, std: 8.5%)
  Memory: increasing (mean: 58.2%, std: 12.1%)
  Disk: stable (mean: 75.9%, std: 2.3%)

PREDICTION:
  Success Probability: 0.89
  Anomaly Score: 0.123
  Recommended Delay: 2.5s
  Confidence: 0.85
========================================
```

### Visualizations Generated
- `metrics_timeline.html` - Interactive CPU/Memory timeline
- `anomaly_detection.html` - Anomaly scores over time
- `dashboard.html` - Comprehensive analytics dashboard

## API Endpoints (v4.0)

### Health Check
```bash
GET /api/health
```

### Trigger History
```bash
GET /api/history
```

### Statistics
```bash
GET /api/stats
```

### Available Plugins
```bash
GET /api/plugins
```

### Execute Trigger
```bash
POST /api/trigger
Authorization: Bearer <token>
```

## Development

### Project Structure
```
bluescreen/
├── bluescreen_v1.py          # Basic version
├── bluescreen_v2.py          # Async version
├── bluescreen_v3.py          # Recovery version
├── bluescreen_v4.py          # Enterprise version
├── bluescreen_v5.py          # ML version
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
├── bluescreen_config.yaml    # Configuration
└── README.md                 # This file
```

### Adding ML Models

To add custom ML models to v5:

```python
from bluescreen_v5 import BlueScreenTriggerV5

trigger = BlueScreenTriggerV5()

# Train models
trigger.train_models(hours=24)

# Make predictions
metrics = trigger.metrics_collector.collect_metrics()
prediction = trigger.predict_trigger_outcome(metrics)
print(prediction.success_probability)
```

## Compilation to EXE

### Using PyInstaller

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build single-file executable:
```bash
pyinstaller --onefile --windowed bluescreen_v5.py
```

3. Build with all dependencies:
```bash
pyinstaller --onefile --hidden-import=sklearn --hidden-import=plotly bluescreen_v5.py
```

4. Executable will be in `dist/` directory

### Using cx_Freeze

```bash
pip install cx_Freeze
cxfreeze bluescreen_v5.py --target-dir dist
```

## Performance Metrics

### Metrics Collection Time
- Collection: ~200ms
- Storage: ~50ms
- Total: ~250ms per cycle

### Model Training Time
- Anomaly Detector: ~2-5 seconds (100+ samples)
- Success Predictor: ~3-8 seconds (100+ samples)
- Combined: ~5-13 seconds

### Prediction Time
- Per metric: ~10-20ms
- Batch (100): ~200-400ms

## Error Codes

Supported NTSTATUS error codes:
- `0xC000007B` - INVALID_IMAGE_FORMAT (default)
- `0xC000013B` - FATAL_USER_CALLBACK_EXCEPTION
- `0xC0000096` - PRIVILEGED_INSTRUCTION
- `0x00000050` - PAGE_FAULT_IN_NONPAGED_AREA

## Troubleshooting

### Models Not Training
- Ensure at least 20 historical metrics are collected
- Check that metrics database exists and has data
- Verify sklearn version is 1.0+

### Visualizations Not Generating
- Install plotly: `pip install plotly`
- Check that matplotlib is installed for fallback
- Ensure dashboards/ directory is writable

### API Server WON'T START
- Verify port 8888 is not in use
- Check firewall settings
- Ensure admin privileges if needed

### Trigger Execution Fails
- Run with administrator privileges
- Verify Windows platform (not WSL)
- Check that ntdll.dll is accessible
- Review log files for detailed errors

## Security Considerations

⚠️ **WARNING**: This tool can cause immediate system failure without saving data. Use only in:
- Testing environments
- Virtual machines
- Systems with full backups
- Development/research contexts

### Sensitive Data
- Model files are stored unencrypted
- Metrics database contains performance data
- API tokens should use strong authentication
- Enable encryption at rest for production

## License

This project is provided for educational and authorized testing purposes only.

## Disclaimer

By using this tool, you accept full responsibility for:
- System damage or data loss
- Unauthorized system access or modification
- Compliance with applicable laws and regulations
- Authorized use only in environments you own or have permission to test

**This tool should only be used by authorized administrators on systems where you have explicit permission.**

## References

- [Windows NTSTATUS Codes](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/)
- [Isolation Forest Algorithm](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Plotly Python](https://plotly.com/python/)

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the detailed logs in bluescreen_v*.log
- Check the configuration in bluescreen_config.yaml
- Consult the inline code documentation

---

**BlueScreen Trigger v5.0** - Enterprise BSOD Generator with ML Analytics
```
