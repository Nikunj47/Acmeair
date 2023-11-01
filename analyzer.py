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

    # metrics = [
    #     {"id": "sysdig_container_net_request_time", "aggregations": {"time": "timeAvg", "group": "avg"}},
    #     {"id": "sysdig_container_cpu_cores_used", "aggregations": {"time": "timeAvg", "group": "avg"}},
    #     {"id": "sysdig_container_memory_used_bytes", "aggregations": {"time": "timeAvg", "group": "avg"}},
    #     {"id": "sysdig_program_net_connection_total_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    #     {"id": "jmx_jvm_thread_count", "aggregations": {"time": "timeAvg", "group": "avg"}},
    #     {"id": "jmx_jvm_heap_used", "aggregations": {"time": "timeAvg", "group": "sum"}}
    # ]

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


def analyze():
    with open('collected_data.json', 'r') as file:
        data = json.load(file)

    # for service in data.values():
    #     metric = service['sysdig_container_memory_used_bytes']
    #     for i in range(1, len(metric)):
    #         metric[i] = metric[i] - metric[i - 1]
    #     metric[0] = 0

    # for service in data.values():
    #     for metric in service.values():
    #         maxi = 0
    #         mini = 9999999999
    #         for x in metric:
    #             maxi = max(maxi, x)
    #             mini = min(mini, x)
    #         for i in range(0, len(metric)):
    #             if maxi != mini:
    #                 metric[i] = (metric[i] - mini) / (maxi - mini)

    # for service in data.keys():
    #     service_value = data[service]
    #     X = np.array([service_value['sysdig_container_cpu_cores_used'], service_value['sysdig_container_memory_used_bytes'],
    #                   service_value['sysdig_program_net_connection_total_count'], service_value['jmx_jvm_thread_count'],service_value['jmx_jvm_heap_used']]).T
    #     model = LinearRegression()
    #     model.fit(X, service_value['sysdig_container_net_request_time'])
    #     coefficients = model.coef_
    #     intercept = model.intercept_
    #     print(f"Regression Func for {service}: U = {intercept} + {coefficients[0]}*cpu + {coefficients[1]}*memory + {coefficients[2]}*requests + {coefficients[3]}*thread + {coefficients[2]}*heap")

    for service in data.keys():
        service_value = data[service]
        x_list = [
            np.array(service_value['sysdig_container_cpu_quota_used_percent']),
        np.array(service_value['sysdig_container_memory_limit_used_percent'])]
        name_list = ['sysdig_container_cpu_quota_used_percent','sysdig_container_memory_limit_used_percent']
        for i, x in enumerate(x_list, start=1):
            x_reshaped = x.reshape(-1, 1)
            model = LinearRegression()
            model.fit(x_reshaped, service_value['jmx_jvm_thread_count'])
            y_pred = model.predict(x_reshaped)
            plt.scatter(x, service_value['jmx_jvm_thread_count'], color='blue')
            plt.plot(x, y_pred, color='red')
            plt.title(f'Regression for {name_list[i-1]}')
            plt.xlabel('threads')
            plt.ylabel(f'{name_list[i-1]}')
            plt.savefig("./plots/" + service + "_regression_x" + str(i) + ".png")
            plt.clf()
            print(f"{service}: U = {model.intercept_} + {model.coef_} * {name_list[i-1]}")

def selfOptimize():

    path = './../Acmeair/acmeair-mainservice-java/scripts/buildAndDeployToOpenshift.sh'

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
                    modify_memory_value(f'./{service}-java/chart/{service}-java/values.yaml', 'd')
                elif mean(service_value['sysdig_container_memory_limit_used_percent']) < 20:
                    print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_limit_used_percent'])}% -> Decrease memory")
                    modify_memory_value(f'./{service}-java/chart/{service}-java/values.yaml', 'd')
                else:
                    print(f"Service {service} -> Memory: {mean(service_value['sysdig_container_memory_limit_used_percent'])}% -> Memory is good")
                if mean(service_value['sysdig_container_cpu_quota_used_percent']) > 80:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> Increase CPU")
                    modify_cpu_value(f'./{service}-java/chart/{service}-java/values.yaml', 'i')
                elif mean(service_value['sysdig_container_cpu_quota_used_percent']) < 20:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> Decrease CPU")
                    modify_cpu_value(f'./{service}-java/chart/{service}-java/values.yaml', 'd')
                else:
                    print(f"Service {service} -> CPU: {mean(service_value['sysdig_container_cpu_quota_used_percent'])}% -> CPU is good")
            except Exception as e:
                print(f'Error while monitoring metrics: {e}')

        try:
            subprocess.run('./../Acmeair/acmeair-mainservice-java/scripts/buildAndDeployToOpenshift.sh', shell=True)
        except Exception as e:
            print(f'Error while redeploy pods: {e}')

        # path = ''
        # result = subprocess.run([path + 'switch.sh', path + '/', path], capture_output=True, text=True)
        # result = subprocess.run([path + 'switch.sh', path + '/', path], capture_output=True, text=True)

def modify_cpu_value(file_path, action):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if 'cpu:' in line:
                parts = line.split('cpu:')
                try:
                    number_part = parts[1].strip().rstrip('m')
                    number = int(number_part)
                    if action == 'i':
                        number *= 2
                    else:
                        number /= 2
                    line = f"      cpu: {number}m\n"
                except ValueError:
                    pass
            file.write(line)

def modify_memory_value(file_path, action):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if 'memory:' in line:
                parts = line.split('memory:')
                try:
                    number_part = parts[1].strip().rstrip('m')
                    number = int(number_part)
                    if action == 'i':
                        number *= 2
                    else:
                        number /= 2
                    line = f"      memory: {number}m\n"
                except ValueError:
                    pass
            file.write(line)

# def UtilityF(service, heap_usage, heap_percent):
#     workload_names = ['acmeair-flightservice', 'acmeair-mainservice', 'acmeair-bookingservice', 'acmeair-customerservice']
#     if heap_percent > 0.8:
#         return 1
#     elif heap_percent < 0.2:
#         return -1
#     else:
#         return 0
#     # intercept = [-48697451, 0, -8046373, -707591167]
#     # cpu = [11347404, 0, 10870970, -37740221]
#     # memory = [0.5075522, 0, -0.00200957, 3.469551059]
#     # requests = [1346, 0, 412, -2126996]
#     # thread = [-134281, 0, 167582, 5531956]
#     # heap = [1346, 0, 412, -2126996]
#     # i=0
#     # for name in workload_names:
#     #     if name == service:
#     #         return intercept[i] + cpu[i] * cpu_usage + memory[i] * memory_usage + requests[i] * request_usage + thread[i] * thread_usage + heap[i] * heap_usage
#
# def clear_directory(directory_path):
#     try:
#         shutil.rmtree(directory_path)
#         os.makedirs(directory_path)
#     except Exception as e:
#         print(f"Failed to clear directory {directory_path}. Reason: {e}")


if __name__ == "__main__":
    #getData(60)
    #analyze()
    selfOptimize()
