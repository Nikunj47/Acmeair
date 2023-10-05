import json
import csv

# Load the JSON data
with open('collected_data.json', 'r') as json_file:
    data_storage = json.load(json_file)

# Convert the JSON data to CSV and save it
with open('collected_data.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write the header
    header = ['kube_workload_name', 'metric_id'] + [f'value_{i}' for i in range(len(next(iter(data_storage.values()))['jmx_jvm_class_loaded']))]
    writer.writerow(header)
    
    # Write the data
    for kube_workload_name, metrics_data in data_storage.items():
        for metric_id, values in metrics_data.items():
            row = [kube_workload_name, metric_id] + values
            writer.writerow(row)
