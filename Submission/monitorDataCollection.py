from sdcclient import IbmAuthHelper, SdMonitorClient
import sys
import time
import matplotlib.pyplot as plt
import threading
import json

folder_name = "./plot"
URL = "https://ca-tor.monitoring.cloud.ibm.com"
APIKEY = "ryGqL7Thrn0EvtVjKsAGAXcyPNtPNlFXFDwF4T_Pz-Tk"
GUID = "b92c514a-ca21-4548-b3f0-4d6391bab407"
ibm_headers = IbmAuthHelper.get_headers(URL, APIKEY, GUID)

sdclient = SdMonitorClient(sdc_url=URL, custom_headers=ibm_headers)

metrics = [
    {"id": "jmx_jvm_class_loaded", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_class_unloaded", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_global_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_global_time", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_scavenge_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_gc_scavenge_time", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_committed", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_init", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_max", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_used", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_heap_used_percent", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_committed", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_init", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_max", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_used", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_nonHeap_used_percent", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_thread_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "jmx_jvm_thread_daemon", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "sysdig_connection_net_request_time", "aggregations": {"time": "timeAvg", "group": "max"}},
    {"id": "sysdig_connection_net_connection_total_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "sysdig_container_cpu_cores_used_percent", "aggregations": {"time": "timeAvg", "group": "avg"}},
    {"id": "sysdig_container_memory_used_percent", "aggregations": {"time": "timeAvg", "group": "avg"}}
]

interval = 3
# ... [Your previous code up to the metrics list]

# List of kube_workload_names
workload_names = ['acmeair-flightservice','acmeair-mainservice','acmeair-bookingservice', 'acmeair-customerservice']

data_storage = {workload: {metric['id']: [] for metric in metrics} for workload in workload_names}

# Use a timer to fetch data for exactly 10 seconds
end_time = time.time() + 600

def fetch_data_for_workload(kube_workload_name):
    while time.time() < end_time:
        start = -10
        end = 0
        ok, res = sdclient.get_data(metrics, start, end, filter=f"kube_cluster_name='ece750cluster' and kube_namespace_name='acmeair-g11' and kube_workload_name='{kube_workload_name}'")
        if not ok:
            print(f"Error fetching metrics for {kube_workload_name}: {res}")
            sys.exit(1)
        
        for metric in metrics:
            metric_id = metric['id']
            data_storage[kube_workload_name][metric_id].append(res['data'][0]['d'][metrics.index(metric)])
        
        # Sleep for the interval duration
        time.sleep(interval)

# Start a thread for each kube_workload_name
threads = []
for kube_workload_name in workload_names:
    thread = threading.Thread(target=fetch_data_for_workload, args=(kube_workload_name,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Plotting each metric in its own figure for each workload
for kube_workload_name, metrics_data in data_storage.items():
    for metric_id, values in metrics_data.items():
        plt.figure(figsize=(10, 5))
        plt.plot(values, marker='o', linestyle='-')
        plt.title(f"{kube_workload_name} - {metric_id}")
        plt.xlabel('Time Intervals')
        plt.ylabel('Metric Value')
        plt.grid(True)
        
        # Save the figure to a file with workload name as prefix
        # filename = f"{kube_workload_name}_{metric_id}.png"
        filename = f"{folder_name}/{kube_workload_name}_{metric_id}.png"
        plt.savefig(filename)
        
        # Close the figure to free up memory
        plt.close()

with open('collected_data.json', 'w') as json_file:
    json.dump(data_storage, json_file, indent=4)