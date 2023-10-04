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
# ok, res = sdclient.get_metrics()
# if not ok:
#     print(f"Error fetching metrics: {res}")
#     sys.exit(1)
# metrics = [{'jmx_jvm_class_loaded'}]
# metrics = [
#     {"id": "jmx_jvm_class_loaded", "aggregations": {"time": "timeAvg", "group": "avg"}}
# ]
metrics = [
    {"id": "jmx_jvm_class_loaded", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_class_unloaded", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_global_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_global_time", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_used", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_used", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_thread_count", "aggregations": {"time": "timeAvg", "group": "avg"}}
]
start = -600
end = 0

# Sampling time:
#   - for time series: sampling is equal to the "width" of each data point (expressed in seconds)
#   - for aggregated data (similar to bar charts, pie charts, tables, etc.): sampling is equal to 0
sampling = 60
ok, res = sdclient.get_data(metrics,start,end)
if not ok:
    print(f"Error fetching metrics: {res}")
    sys.exit(1)


print(res)

# # Filter out JMX metrics
# jmx_metrics = [metric['name'] for metric in res['metrics'] if 'jmx' in metric['name']]

# # Create a list of metric dictionaries for the get_data method
# metrics_to_fetch = [{"id": metric_name, "aggregations": {"time": "timeAvg", "group": "avg"}} for metric_name in jmx_metrics]

# # Time window and sampling settings
# start = -600
# end = 0
# sampling = 60
# filter = None

# # Fetch data for JMX metrics
# for metric in metrics_to_fetch:
#     ok, metric_data = sdclient.get_data([metric], start, end, sampling, filter=filter)
#     if ok:
#         print(metric_data)
#     else:
#         print(f"Error fetching data for metric {metric['id']}: {metric_data}")

