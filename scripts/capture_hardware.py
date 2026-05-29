import platform, psutil, os
import cpuinfo 

# Code writer: Anna Kálmánczhelyi
def capture_hardware():
    """Capture hardware stats, so experiments run on different devices can be compared"""

    pc_stats = {}

    pc_stats["cpu_type"] = cpuinfo.get_cpu_info()["brand_raw"]
    pc_stats["cpu_freq"] = round(cpuinfo.get_cpu_info()["hz_advertised"][0] / 1e9, 2)
    pc_stats["cpu_cores"] = os.cpu_count()
    pc_stats["ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3))
    pc_stats["os_name"] = platform.system()

    return pc_stats


# Code writer: Anna Kálmánczhelyi
""" Write the captured pc stats into a txt file """
if __name__ == "__main__":
    stats = capture_hardware()
    with open("pc_stats.txt", "w", encoding="utf-8") as file:
        for key, value in stats.items():
            file.write(f"{key}: {value}\n")
    print("Wrote pc_stats.txt")