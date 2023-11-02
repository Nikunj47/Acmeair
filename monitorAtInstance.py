from sdcclient import IbmAuthHelper, SdMonitorClient
import sys


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
    {"id": "kube_deployment_status_replicas_available", "aggregations": {"time": "timeAvg", "group": "avg"}},
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
start = -10
end = 0


sampling = 60
ok, res = sdclient.get_data(metrics,start,end,filter=f"kube_cluster_name='ece750cluster' and kube_namespace_name='acmeair-g11'and kube_workload_name='acmeair-mainservice'")
if not ok:
    print(f"Error fetching metrics: {res}")
    sys.exit(1)


for i in range(0, len(metrics)):
    print(str(metrics[i]['id']) + ': ' + str(res['data'][0]['d'][i]))
