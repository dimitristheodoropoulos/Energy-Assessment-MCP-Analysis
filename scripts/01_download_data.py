#!/usr/bin/env python3
\"\"\"Κατέβασμα raw δεδομένων από ERA5/NASA POWER\"\"\"
import os
def main():
    os.makedirs('../data/raw', exist_ok=True)
    # TODO: εδώ βάλε κώδικα με cdsapi ή requests
    print("Download not implemented yet.")
if __name__ == '__main__':
    main()
