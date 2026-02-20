import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
import html

from core.logger import logger, ENABLE_FILE_LOGGING, LOG_FILENAME
from logic import ProjectLogic, CACHE_CONFIG

def get_file_content(file_path, last_n_lines=None):
    try:
        if not os.path.exists(file_path):
            return f"File {file_path} not found."
        with open(file_path, "r", encoding="utf-8") as f:
            if last_n_lines:
                return f.readlines()[-last_n_lines:]
            return f.read()
    except Exception as e:
        logger.error(f"[bold red]Error reading file {file_path}:[/] {e}")
        return f"Error reading file: {e}"

@st.dialog("System Configuration", width="large")
def show_config_modal():
    logger.info("[bold cyan]Opening System Configuration Modal[/]")
    st.markdown("### 🛠️ Environment & Logging")
    api_key_status = "✅ Set" if os.getenv("MK_CSM_KEY") else "❌ Missing"
    st.write(f"**API Key (MK_CSM_KEY):** {api_key_status}")
    st.write(f"**Log Level:** `INFO`")
    st.write(f"**File Logging:** `{'Enabled' if ENABLE_FILE_LOGGING else 'Disabled'}`")
    if ENABLE_FILE_LOGGING:
        st.write(f"**Log Filename:** `{LOG_FILENAME}`")
    
    st.divider()
    st.markdown("### ⏱️ Caching Timers (Seconds)")
    st.json(CACHE_CONFIG)

@st.dialog("Application Logs", width="large")
def show_log_modal():
    logger.info("[bold cyan]Opening Application Logs Modal[/]")
    st.markdown(f"**Reading from:** `{LOG_FILENAME}`")
    lines = get_file_content(LOG_FILENAME, last_n_lines=2000)
    
    if isinstance(lines, list):
        full_content = "".join(lines)
        st.download_button(
            label="📥 Download Log File",
            data=full_content,
            file_name="application_log.txt",
            mime="text/plain",
        )
        
        log_html = ["""
        <style>
            .terminal-window {
                background-color: #0e1117; color: #c9d1d9; font-family: monospace;
                font-size: 12px; padding: 15px; border-radius: 8px; border: 1px solid #30363d;
                height: 500px; overflow-y: auto; white-space: pre-wrap; line-height: 1.4;
            }
            .log-line { margin-bottom: 2px; }
            .log-info { color: #3fb950; }
            .log-warn { color: #d29922; }
            .log-error { color: #f85149; }
            .log-meta { color: #8b949e; }
        </style>
        <div class="terminal-window">
        """]

        for line in lines:
            safe_line = html.escape(line.strip())
            css_class = "log-line"
            if "INFO" in safe_line: css_class += " log-info"
            elif "WARNING" in safe_line: css_class += " log-warn"
            elif "ERROR" in safe_line or "CRITICAL" in safe_line: css_class += " log-error"
            
            parts = safe_line.split(" - ", 1)
            if len(parts) > 1:
                log_html.append(f'<div class="{css_class}"><span class="log-meta">{parts[0]} - </span>{parts[1]}</div>')
            else:
                log_html.append(f'<div class="{css_class}">{safe_line}</div>')

        log_html.append("</div>")
        st.markdown("".join(log_html), unsafe_allow_html=True)
    else:
        st.error(lines)

@st.dialog("License", width="large")
def show_license_modal():
    logger.info("[bold cyan]Opening License Modal[/]")
    st.markdown("### Open Source License")
    st.code(get_file_content("LICENSE"), language="text")

@st.dialog("ReadMe", width="large")
def show_readme_modal():
    logger.info("[bold cyan]Opening ReadMe Modal[/]")
    st.markdown(get_file_content("README.md"))

def run_web():
    st.set_page_config(page_title="Meraki Wireless Clients in Networks", layout="wide", initial_sidebar_state="expanded")
    logger.info("[bold green]Initialising Wireless Clients in Networks Web UI[/]")

    st.markdown(f"""
    <style>
        :root {{
            --primary-accent: #144a90;
            --top-bar-bg: #07172B;
            --white: #FFFFFF;
            --st-light-grey: rgba(49, 51, 63, 0.6);
            --gradient: linear-gradient(to right, #007bff, #6610f2, #e83e8c, #fd7e14);
        }}

        [data-testid="stIconMaterial"] {{ color: var(--primary-accent) !important; }}
        [data-testid="stBaseButton-header"] {{ color: var(--white) !important; }}                
        [data-testid="stMainMenu"] svg {{ fill: var(--white) !important; }}
        .stAppDeployButton {{ display: none !important; }}

        header[data-testid="stHeader"] {{ background-color: transparent; }}
        .top-gradient-bar {{ position: fixed; top: 0; left: 0; width: 100%; height: 4px; background-image: var(--gradient); z-index: 100001; }}
        .top-bar {{ position: fixed; top: 4px; left: 0; width: 100%; height: 56px; background-color: var(--top-bar-bg); z-index: 100000; display: flex; align-items: center; padding-left: 60px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .top-bar-text {{ color: var(--white); font-weight: 600; font-size: 1.1em; }}

        .block-container {{ padding-top: 6rem; }}
    </style>
    <div class="top-gradient-bar"></div>
    <div class="top-bar"><div class="top-bar-text">Wireless Clients in Networks</div></div>
    """, unsafe_allow_html=True)

    try:
        logic = ProjectLogic()
        
        with st.sidebar:
            st.header("1. Scope")
            orgs = logic.get_organizations()
            org_map = {o['name']: o['id'] for o in orgs}
            selected_org = st.selectbox("Organization", options=list(org_map.keys()))
            org_id = org_map[selected_org]
            
            mass_fetch = st.checkbox("Mass Fetch (All Networks)")
            networks = logic.get_networks(org_id)
            net_map = {n['name']: n['id'] for n in networks if 'wireless' in n['productTypes']}
            
            if not mass_fetch:
                selected_nets = st.multiselect("Select Network", options=list(net_map.keys()))
                target_net_ids = [net_map[name] for name in selected_nets]
            else:
                target_net_ids = list(net_map.values())
                logger.info(f"Mass Fetch enabled for Organization: [cyan]{selected_org}[/]")

            st.header("2. Filters")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
            with col2:
                end_date = st.date_input("End Date", datetime.now().date())
            
            today = datetime.now().date()
            date_diff = (end_date - start_date).days
            run_disabled = False
            if (today - start_date).days > 30:
                msg = f"Start date ({start_date}) is older than 30 days."
                st.error(msg)
                logger.warning(f"[bold red]Validation Error:[/] {msg}")
                run_disabled = True
            if date_diff > 30:
                msg = f"Window size ({date_diff} days) exceeds 30-day limit."
                st.error(msg)
                logger.warning(f"[bold red]Validation Error:[/] {msg}")
                run_disabled = True

            resolution = st.radio("Resolution", options=[3600, 86400], format_func=lambda x: "1 Hour" if x == 3600 else "1 Day", horizontal=True)
            split_by_ssid = st.checkbox("Split results by SSID")

            st.divider()
            run_btn = st.button("🚀 Refresh Graph", type="primary", width='stretch', disabled=run_disabled)

            st.divider()
            with st.expander("ℹ️ About", expanded=False):
                st.markdown("### Wireless Clients in Networks")
                st.caption("Report the number of clients in a wireless network.")
                st.markdown("**Author:** SandroN")
                st.markdown("[GitHub Project Repository](https://github.com/SandroNardi/wireless_client_count)")
                st.divider()
                
                if st.button("⚙️ System Configuration", width='stretch'):
                    show_config_modal()
                if ENABLE_FILE_LOGGING:
                    if st.button("📄 Application Logs", width='stretch'):
                        show_log_modal()
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📜 License", width='stretch'):
                        show_license_modal()
                with c2:
                    if st.button("📖 ReadMe", width='stretch'):
                        show_readme_modal()

        if not run_btn:
            st.info("👈 **Please use the sidebar to select your Organization and Networks.**\n\nIf the sidebar is closed, click the **arrow (>>)** in the top-left corner of the screen to open it.")

        if run_btn:
            logger.info(f"[bold cyan]Starting Analysis[/] for Organization: [green]{selected_org}[/]")
            logger.info(f"Parameters: [grey]Networks={len(target_net_ids)}, Resolution={resolution}s, SplitSSID={split_by_ssid}[/]")
            
            progress_bar = st.progress(0); status_text = st.empty()
            total_steps = len(target_net_ids); current_step = 0

            def update_progress(msg):
                nonlocal current_step
                current_step += 1
                progress_bar.progress(min(current_step/total_steps, 1.0))
                status_text.text(f"Processing: {msg}")

            t0, t1 = start_date.strftime("%Y-%m-%dT00:00:00Z"), end_date.strftime("%Y-%m-%dT23:59:59Z")
            all_data = []

            for net_id in target_net_ids:
                net_name = next(k for k, v in net_map.items() if v == net_id)
                if split_by_ssid:
                    update_progress(f"Fetching SSIDs for {net_name}")
                    ssids = logic.get_ssids(net_id)
                    enabled_ssids = [s for s in ssids if s.get('enabled') is True]
                    total_steps += len(enabled_ssids)
                    for s in enabled_ssids:
                        update_progress(f"{net_name} - {s['name']}")
                        df = logic.get_client_history(net_id, t0, t1, resolution, ssid_number=s['number'])
                        if not df.empty:
                            df['Label'] = f"{net_name} ({s['name']})"
                            all_data.append(df)
                else:
                    update_progress(net_name)
                    df = logic.get_client_history(net_id, t0, t1, resolution)
                    if not df.empty:
                        df['Label'] = net_name
                        all_data.append(df)

            status_text.empty(); progress_bar.empty()

            if all_data:
                logger.info(f"Data collection complete. Processing [green]{len(all_data)}[/] data sets.")
                processed_dfs = []
                for df in all_data:
                    if not df.empty:
                        if 'clientCount' not in df.columns:
                            df['clientCount'] = 0
                        df['clientCount'] = pd.to_numeric(df['clientCount'], errors='coerce')
                        df['clientCount'] = df['clientCount'].fillna(0)
                        df = df.infer_objects(copy=False)
                        processed_dfs.append(df)

                if processed_dfs:
                    final_df = pd.concat(processed_dfs, ignore_index=True)
                    st.markdown("**Wireless Client History**")
                    st.caption(f"Split by SSID: {split_by_ssid} | Resolution: {resolution}s")
                    
                    fig = px.line(
                        final_df, 
                        x='startTs', 
                        y='clientCount', 
                        color='Label',
                        labels={'startTs': 'Time', 'clientCount': 'Clients', 'Label': 'Source'}
                    )
                    
                    total_df = final_df.groupby('startTs')['clientCount'].sum().reset_index()
                    fig.add_trace(go.Scatter(
                        x=total_df['startTs'], 
                        y=total_df['clientCount'], 
                        name='TOTAL (Selected)', 
                        line=dict(color='red', width=3, dash='dot'),
                        mode='lines'
                    ))
                    
                    st.plotly_chart(fig, width='stretch', key="client_chart")
                    logger.info("[bold green]Graph rendered successfully.[/]")
                else:
                    logger.warning("[bold yellow]Processed data resulted in an empty set.[/]")
                    st.error("All collected data was empty or invalid.")
            else:
                logger.warning("[bold yellow]No client data found for the selected criteria.[/]")
                st.error("No data found for the selected criteria.")

    except Exception as e:
        logger.error(f"[bold red]Critical Application Error:[/] {e}", exc_info=True)
        st.error(f"Error: {e}")

if __name__ == "__main__":
    run_web()