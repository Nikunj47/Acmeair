import os
import shutil
from datetime import datetime
from statistics import mean

from sdcclient import IbmAuthHelper, SdMonitorClient
import sys
import time
import matplotlib.pyplot as plt
import threading
import json
from sklearn.linear_model import LinearRegression
import numpy as np
import subprocess

def getData(DURATION):

    folder_name = "./plot"
    URL = "https://ca-tor.monitoring.cloud.ibm.com"
    APIKEY = "ryGqL7Thrn0EvtVjKsAGAXcyPNtPNlFXFDwF4T_Pz-Tk"
    GUID = "b92c514a-ca21-4548-b3f0-4d6391bab407"
    ibm_headers = IbmAuthHelper.get_headers(URL, APIKEY, GUID)

    sdclient = SdMonitorClient(sdc_url=URL, custom_headers=ibm_headers)
    metrics = [
        {"id": "sysdig_container_cpu_cores_used", "aggregations": {"time": "timeAvg", "group": "sum"}},
        {"id": "sysdig_container_cpu_quota_used_percent", "aggregations": {"time": "timeAvg", "group": "sum"}},
        {"id": "sysdig_container_memory_used_bytes", "aggregations": {"time": "timeAvg", "group": "sum"}},
        {"id": "sysdig_container_memory_limit_used_percent", "aggregations": {"time": "timeAvg", "group": "sum"}},
        {"id": "kube_pod_sysdig_restart_count", "aggregations": {"time": "timeAvg", "group": "sum"}},
        {"id": "jmx_jvm_thread_count", "aggregations": {"time": "timeAvg", "group": "sum"}}
    ]

    interval = 3

    # List of kube_workload_names
    workload_names = ['acmeair-flightservice', 'acmeair-mainservice', 'acmeair-bookingservice', 'acmeair-customerservice', 'acmeair-authservice']

    data_storage = {workload: {metric['id']: [] for metric in metrics} for workload in workload_names}

    # Use a timer to fetch data for exactly 10 seconds
    end_time = time.time() + DURATION


    def fetch_data_for_workload(kube_workload_name):
        while time.time() < end_time:
            try:
                start = -10
                end = 0
                ok, res = sdclient.get_data(metrics, start, end,
                                            filter=f"kube_cluster_name='ece750cluster' and kube_namespace_name='acmeair-g11' and kube_workload_name='{kube_workload_name}'")
                if not ok:
                    print(f"Error fetching metrics for {kube_workload_name}: {res}")
                    sys.exit(1)

                for metric in metrics:
                    metric_id = metric['id']
                    data_storage[kube_workload_name][metric_id].append(res['data'][0]['d'][metrics.index(metric)])
            except Exception as e:
                print("Error: Some services are not running!")

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


def selfOptimize():
    while(True):
        interval = 30
        try:
            os.remove('./collected_data.json')
        except Exception as e:
            print(f"An error occurred while deleting './collected_data.json': {e}")
        getData(interval)
        with open('collected_data.json', 'r') as file:
            data = json.load(file)

        print(f'{datetime.now().strftime("%H:%M:%S")}--------------------------------------------------------------------------------------')
        for service in data.keys():
            try:
                service_value = data[service]
                #print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_used_bytes'])}")
                #print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_cores_used'])}")
                print(f'Service {service} restarted {sum(service_value["kube_pod_sysdig_restart_count"])} times!')
                if mean(service_value['sysdig_container_memory_limit_used_percent']) > 80:
                    print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_limit_used_percent'])}% -> Increase memory")
                elif mean(service_value['sysdig_container_memory_limit_used_percent']) < 20:
                    print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_limit_used_percent'])}% -> Decrease memory")
                else:
                    print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_limit_used_percent'])}% -> Memory is good")
                if mean(service_value['sysdig_container_cpu_quota_used_percent']) > 80:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> Increase CPU")
                elif mean(service_value['sysdig_container_cpu_quota_used_percent']) < 20:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> Decrease CPU")
                else:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> CPU is good")
            except Exception as e:
                print(f'Error: {e}')

        # path = ''
        # result = subprocess.run([path + 'switch.sh', path + '/', path], capture_output=True, text=True)
        # result = subprocess.run([path + 'switch.sh', path + '/', path], capture_output=True, text=True)


if __name__ == "__main__":
    #getData(60)
    selfOptimize()
