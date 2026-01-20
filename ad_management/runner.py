import subprocess
import sys

def run_command(command, description):
    """Run a shell command and print status and output."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {description}")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        if result.stderr:
            print("Errors (stderr):")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {description}: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def main():
    print("Starting No-VPN Runner for scripts...")

    # Step 1: Run the scripts sequentially
    scripts = [
        ("python3 1Download_Ads_Sheets.py", "Downloading Ads Sheets"),
        ("python3 2Check_Availability.py", "Checking Availability (Out of Stock)"),
        ("python3 3Check_Availability.py", "Checking Availability (Back in Stock)")
    ]

    for command, description in scripts:
        if not run_command(command, description):
            print(f"Failed to run {description}. Continuing with next script...")

    print("All scripts executed.")

if __name__ == "__main__":
    main()
