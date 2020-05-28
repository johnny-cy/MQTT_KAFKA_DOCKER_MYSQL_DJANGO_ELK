import shutil

total, used, free = shutil.disk_usage("/")
print(type(total),type(used),type(free))
print("Total: {} GiB".format(total // (2**30)))
print("Used: {} GiB {}%".format(used // (2**30),int(used/total*100)))
print("Available: {} GiB {}%".format(free // (2**30),int(free/total*100)))

