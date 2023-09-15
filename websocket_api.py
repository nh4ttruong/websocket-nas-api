import argparse
import asyncio
import csv
from datetime import datetime
from aiotruenas_client import CachingMachine as TrueNASMachine

# please remember to check api_key, contact me or read ref: https://github.com/sdwilsh/aiotruenas-client/blob/main/aiotruenas_client/websockets/

async def connect(host, api_key):
    try:
        machine = await TrueNASMachine.create(
            host,
            api_key
        )
        return machine
    except Exception as e:
        print(f"Error connecting to {host}: {str(e)}")
        return None

async def get_datasets(machine, isClean):
    try:
        datasets = await machine.get_datasets()
        dataset_info = []

        for dataset in datasets:
            # isClean equal True, ignore dataset.pool_name == "boot_pool" and ignore dataset.id contain "iocage"
            if isClean:
                if dataset.pool_name == "boot-pool" or "iocage" in dataset.id:
                    continue

            dataset_info.append({
                "+ Pool Name": dataset.pool_name,
                "+ Dataset Name": dataset.id,
                "+ Total": format_bytes(dataset.total_bytes),
                "+ Used": format_bytes(dataset.used_bytes),
                "+ Available": format_bytes(dataset.available_bytes)
            })

        return dataset_info
    except Exception as e:
        print(f"Error retrieving datasets: {str(e)}")
        return []

async def get_disks(machine):
    try:
        disks = await machine.get_disks()
        disk_info = []

        for disk in disks:
            disk_info.append({
                "+ Disk Name": disk.name,
                # "+ Disk Description": disk.description,
                # "Disk Type": disk.type,
                "+ Disk Size": format_bytes(disk.size),
            })

        return disk_info
    except Exception as e:
        print(f"Error retrieving disks: {str(e)}")
        return []

async def get_pools(machine):
    try:
        pools = await machine.get_pools()
        pool_info = []

        for pool in pools:
            pool_info.append({
                "+ Pool ID": pool.id,
                "+ Pool Name": pool.name,
                "+ Pool Status": pool.status
            })

        return pool_info
    except Exception as e:
        print(f"Error retrieving pools: {str(e)}")
        return []

def format_bytes(bytes_value):
    # convert
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    index = 0
    while bytes_value >= 1024 and index < len(units) - 1:
        bytes_value /= 1024.0
        index += 1
    return f"{bytes_value:.2f} {units[index]}"

def datasets2csv(dataset_info, csv_filename):
    try:
        with open(csv_filename, mode='w', newline='') as csv_file:
            fieldnames = ["Pool Name", "Dataset Name", "Total", "Used", "Available"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()

            for item in dataset_info:
                writer.writerow({
                    "Pool Name": item["+ Pool Name"],
                    "Dataset Name": item["+ Dataset Name"],
                    "Total": item["+ Total"],
                    "Used": item["+ Used"],
                    "Available": item["+ Available"]
                })
        
        print(f"Dataset information saved to {csv_filename}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Retrieve information from a TrueNAS instance")
    parser.add_argument("-H", "--host", required=True, help="Hostname or IP address of the TrueNAS instance")
    parser.add_argument("-K", "--api_key", required=True, help="API key for authentication")
    parser.add_argument("--type", required=True, choices=["datasets", "disks", "pools"], help="Choose the type of information to retrieve")
    parser.add_argument("-c", "--clean", required=False, default="False", choices=["True", "False"], help="Clean dataset output information")
    parser.add_argument("--out", required=False, default=False, help="Name of the CSV file to save dataset information (required for 'datasets')")

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    machine = loop.run_until_complete(connect(args.host, args.api_key))

    if machine:
        print(f"Connected to {args.host}!\n")

        if args.type == "disks":
            info = loop.run_until_complete(get_disks(machine))
        elif args.type == "pools":
            info = loop.run_until_complete(get_pools(machine))
        elif args.type == "datasets":
            info = loop.run_until_complete(get_datasets(machine, isClean=args.clean))
        else:
            print("Invalid type specified.")
            return

        for item in info:
            print(f"{args.type.capitalize()} Information:")
            for key, value in item.items():
                print(f"{key}: {value}")
            print("-----")

        if args.type == "datasets":
            if args.out:
                datasets2csv(info, str(args.out + ".csv"))
            else:
                now = datetime.now()
                formatted_date = now.strftime("%Y-%m-%d")
                host_ip_without_dot = args.host.replace('.', '_')
                args.out = f"{formatted_date}_{host_ip_without_dot}_datasets.csv"
                datasets2csv(info, str(args.out))

if __name__ == "__main__":
    # run
    main()
