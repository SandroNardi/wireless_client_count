# Meraki Wireless Clients in Netwoks 📡

A specialized dashboard for visualizing and analyzing wireless client density across Cisco Meraki networks. Built with **Streamlit**, **Plotly**, and the **Meraki Dashboard API**, this tool allows administrators to monitor usage trends, compare network loads, and drill down into specific SSID performance.

---

## 📂 Project Structure

```text
wireless_clients_networks/
├── .streamlit/
│   └── config.toml       # Streamlit theme and server configuration
├── core/
│   ├── __init__.py
│   ├── api.py            # Singleton session management for Meraki SDK
│   └── logger.py         # Rich logging configuration (Console + File)
├── logic.py              # Backend logic, API calls, caching, and data processing
├── web.py                # Frontend UI, layout, and visualization
├── application.log       # Runtime logs (auto-generated)
├── requirements.txt      # Python dependencies
├── LICENSE               # MIT License file
└── README.md             # Project documentation
```

---

## ✨ Key Features

*   **Dual Operation Modes**:
    *   **Single/Multi-Network**: Select specific networks to compare client counts over time.
    *   **Mass Fetch**: One-click aggregation of client data across every wireless network in the organization.
*   **SSID Granularity**: 
    *   Toggle **"Split results by SSID"** to break down network totals into individual broadcasted SSIDs.
    *   Automatically filters for **Enabled SSIDs only** to optimize API efficiency.
*   **Strict Data Validation**:
    *   Enforces a **30-day maximum window** for analysis.
    *   Enforces a **30-day retention limit** (Start Date cannot be older than 30 days from the current time).
*   **Interactive Visualizations**:
    *   High-performance time-series graphs powered by **Plotly**.
    *   **Total Aggregation Line**: A dynamic dotted red line showing the sum of all selected sources.
*   **Smart Caching**: Uses `@st.cache_data` with configurable TTLs to minimize redundant API hits.
*   **Terminal-Style Logging**: A built-in UI log viewer that simulates a terminal environment with color-coded severity (INFO, WARNING, ERROR).

---

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.9 or higher.
*   A Cisco Meraki API Key.

### 2. Installation
Install the required dependencies:

```bash
pip install streamlit pandas plotly meraki rich
```

### 3. Environment Configuration
The application requires your Meraki API key to be set as an environment variable.

*   **Windows (PowerShell)**:
    ```powershell
    $env:MK_CSM_KEY = "your_api_key_here"
    ```
*   **Mac/Linux**:
    ```bash
    export MK_CSM_KEY="your_api_key_here"
    ```

### 4. Launching the App
```bash
streamlit run web.py
```

---

## ⚙️ Customization & Configuration

### Caching Timers (`logic.py`)
Control how long data is stored in memory:
*   **Short (300s)**: Real-time metrics.
*   **Medium (3600s)**: Device and Network lists.
*   **Long (86400s)**: Organization structure.

### Logging (`core/logger.py`)
*   **ENABLE_FILE_LOGGING**: Set to `True` to persist logs to `application.log`.
*   **Terminal Renderer**: Accessible via the **"Application Logs"** button in the **About** section.

---

## ⚠️ API Usage & Limitations

*   **30-Day Constraint**: This tool is optimized for Meraki's standard data retention. Requests exceeding 30 days are blocked in the UI to prevent API errors.
*   **SSID Splitting**: Enabling SSID split increases the number of API calls (1 call per enabled SSID). For large organizations, use this feature selectively.
*   **Mass Fetch Mode**: In Mass Fetch mode, the app iterates through all networks. The progress bar provides real-time feedback on the collection status.

---

## 📝 License

This project is licensed under the **MIT License**. See the LICENSE file for details.

**Author**: SandroN