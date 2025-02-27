import os
import sys
import glob
import gzip


def merge(timestamp):
    path = os.path.join(os.path.abspath('.'), "var", timestamp)
    file_list = glob.glob(f"{path}/?????.csv.gz")
    print(f"merging {len(file_list)} files from {path}")

    with gzip.open(f"{path}/merged.csv.gz","wb") as fout:

        # first file
        filename = file_list.pop()
        with gzip.open(filename, "rb") as f:
            fout.write(f.read())
        print(f"appended {filename}")

        # the rest    
        for filename in file_list:
            with gzip.open(filename, "rb") as f:
                next(f) # skip the header
                fout.write(f.read())
            print(f"appended {filename}")


if __name__ == "__main__":
    # parse cli arguments
    if len(sys.argv) == 2:
        timestamp = sys.argv[1]
    else:
        # find the directory with the most recent timestamp
        path = os.path.join(os.path.abspath('.'), "var")
        dirs = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
        timestamp = dirs[-1]

    merge(timestamp)
