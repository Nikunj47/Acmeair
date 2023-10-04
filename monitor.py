from sdcclient import IbmAuthHelper, SdMonitorClient
import sys
# Add the monitoring instance information that is required for authentication
URL = "https://ca-tor.monitoring.cloud.ibm.com"
APIKEY = "ryGqL7Thrn0EvtVjKsAGAXcyPNtPNlFXFDwF4T_Pz-Tk"
GUID = "b92c514a-ca21-4548-b3f0-4d6391bab407"
ibm_headers = IbmAuthHelper.get_headers(URL, APIKEY, GUID)

# Instantiate the Python client
sdclient = SdMonitorClient(sdc_url=URL, custom_headers=ibm_headers)

# Fetch the list of available metrics
ok, res = sdclient.get_metrics()
if not ok:
    print(f"Error fetching metrics: {res}")
    sys.exit(1)

# Filter out JMX metrics
# jmx_metrics = [metric['name'] for metric in res['metrics'] if 'jmx' in metric['name']]
if 'jmx_jvm_class_loaded' in res:
    jmx_metrics = [metric['jmx_jvm_class_loaded'] for metric in res['metrics'] if 'name' in metric and 'jmx' in metric['name']]
else:
    print("The response does not contain a 'jmx_jvm_class_loaded' key.")
    sys.exit(1)

# Create a list of metric dictionaries for the get_data method
metrics_to_fetch = [{"id": metric_name, "aggregations": {"time": "timeAvg", "group": "avg"}} for metric_name in jmx_metrics]

# Time window and sampling settings
start = -600
end = 0
sampling = 60
filter = None

# Fetch data for JMX metrics
for metric in metrics_to_fetch:
    ok, metric_data = sdclient.get_data([metric], start, end, sampling, filter=filter)
    if ok:
        print(metric_data)
    else:
        print(f"Error fetching data for metric {metric['id']}: {metric_data}")

