import streamlit as st
import pandas as pd
import meraki
from core.api import session
from core.logger import logger

API_CALL_COUNTER = 0

def _increment_counter(endpoint):
    global API_CALL_COUNTER
    API_CALL_COUNTER += 1
    logger.info(f"[bold cyan][API CALL #{API_CALL_COUNTER}][/] Fetching: [green]{endpoint}[/]")

CACHE_CONFIG = {
    'short': 300,
    'medium': 3600,
    'long': 86400
}

class ProjectLogic:
    def __init__(self):
        """Initializes the Meraki Dashboard API session."""
        self.dashboard = session.get_dashboard()

    @st.cache_data(ttl=CACHE_CONFIG['medium'])
    def get_organizations(_self):
        _increment_counter("organizations.getOrganizations")
        return _self.dashboard.organizations.getOrganizations()

    @st.cache_data(ttl=CACHE_CONFIG['medium'])
    def get_networks(_self, organization_id):
        _increment_counter("organizations.getOrganizationNetworks")
        return _self.dashboard.organizations.getOrganizationNetworks(organization_id)

    @st.cache_data(ttl=CACHE_CONFIG['medium'])
    def get_ssids(_self, network_id):
        _increment_counter(f"wireless.getNetworkWirelessSsids ({network_id})")
        return _self.dashboard.wireless.getNetworkWirelessSsids(network_id)
    
    @st.cache_data(ttl=CACHE_CONFIG['short'])
    def get_client_history(_self, network_id, t0, t1, resolution, ssid_number=None):
        """
        Fetches wireless client count history.
        """
        try:
            kwargs = {
                "networkId": network_id,
                "t0": t0,
                "t1": t1,
                "resolution": resolution
            }
            
            if ssid_number is not None:
                kwargs["ssid"] = int(ssid_number)
                _increment_counter(f"wireless.getNetworkWirelessClientCountHistory (Net: {network_id}, SSID: {ssid_number})")
            else:
                _increment_counter(f"wireless.getNetworkWirelessClientCountHistory (Net: {network_id})")

            history = _self.dashboard.wireless.getNetworkWirelessClientCountHistory(**kwargs)
            
            if not history:
                return pd.DataFrame()
            
            df = pd.DataFrame(history)
            df['startTs'] = pd.to_datetime(df['startTs'])
            return df

        except Exception as e:
            logger.error(f"[bold red]API Error on {network_id}: {e}[/]")
            return pd.DataFrame()