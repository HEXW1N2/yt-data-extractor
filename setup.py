import subprocess
import os
import sys
from pathlib import Path
import platform
import shutil
import logging

# Configure logging
logging.basicConfig(filename='setup.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_screen():
    """Clear the terminal screen based on the operating system."""
    os.system('cls' if platform.system() == "Windows" else 'clear')

def get_os_from_user():
    """
    Prompt user to select their operating system.
    Returns: 'linux' or 'windows'
    """
    while True:
        print("Select your operating system:")
        print("1. Linux")
        print("2. Windows")
        choice = input("Enter choice (1/2): ").strip()
        if choice == "1":
            return "linux"
        elif choice == "2":
            return "windows"
        else:
            print("Invalid choice. Please select 1 or 2.")
            input("Press Enter to try again...")
            clear_screen()

def check_existing_installation(directory):
    """
    Check if an installation already exists and handle accordingly.
    Returns: True if ready to proceed, new directory name if creating new, or False on error
    """
    if os.path.exists(directory):
        print(f"\nFound existing installation at: {directory}")
        print("\nOptions:")
        print("1. Remove existing and reinstall")
        print("2. Create new installation with different name")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter choice (1/2/3): ").strip()
            if choice == "1":
                try:
                    print("\nRemoving existing installation...")
                    shutil.rmtree(directory)
                    print("✓ Existing installation removed")
                    return True
                except Exception as e:
                    print(f"Error removing existing installation: {e}")
                    logging.exception("Error removing existing installation")
                    return False
            elif choice == "2":
                counter = 1
                while os.path.exists(f"{directory}_{counter}"):
                    counter += 1
                new_directory = f"{directory}_{counter}"
                print(f"\nWill create new installation at: {new_directory}")
                return new_directory
            elif choice == "3":
                print("\nExiting installation...")
                sys.exit(0)
            else:
                print("Invalid choice. Please select 1, 2, or 3.")

def get_directory():
    """
    Get the installation directory from user input.
    Returns: Valid directory path
    """
    message = """
If you are picking the "(or '.' for current directory)" option, keep in mind that 
this will make a folder for all of the stuff in this app. I hate it when I set 
up something and all of the files are just scrambled around my drive unorganized. 
I am sure a lot of people hate that too. Enjoy the app :)
and also subscribe to HEXW1N2
"""
    print(message)
    
    while True:
        directory = input("\nEnter the full path where you want to install (or '.' for current directory): ").strip()
        if directory == '.':
            directory = os.path.join(os.getcwd(), "yt-data-extractor")
            print(f"\nCreating organized directory structure in: {directory}")
        else:
            directory = os.path.expanduser(directory)
            directory = os.path.abspath(directory)
        
        # Check for existing installation
        if os.path.exists(directory):
            result = check_existing_installation(directory)
            if isinstance(result, str):
                directory = result  # Use new directory name
            elif not result:
                continue  # Try again if removal failed
        
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            if os.access(directory, os.W_OK):
                return directory
            else:
                print("Error: No write permission in this directory.")
        except Exception as e:
            print(f"Error creating directory: {e}")
            logging.exception("Error creating directory")
        input("Press Enter to try again...")
        clear_screen()

def check_directory_permissions(directory):
    """
    Check if we have the necessary permissions on the directory.
    Returns: True if all permissions are correct, False otherwise
    """
    print(f"\nChecking permissions for: {directory}")
    try:
        if os.path.exists(directory):
            # Check read permission
            if os.access(directory, os.R_OK):
                print("✓ Read permission")
            else:
                print("✗ No read permission")
                return False
                
            # Check write permission
            if os.access(directory, os.W_OK):
                print("✓ Write permission")
            else:
                print("✗ No write permission")
                return False
                
            # Check execute permission
            if os.access(directory, os.X_OK):
                print("✓ Execute permission")
            else:
                print("✗ No execute permission")
                return False
                
            return True
        else:
            print("Directory doesn't exist yet, will try to create it")
            return True
    except Exception as e:
        print(f"Error checking permissions: {str(e)}")
        logging.exception("Error checking permissions")
        return False

def check_packages(os_type):
    """
    Check if required system packages are installed.
    Returns: True if all required packages are installed, False otherwise
    """
    if os_type == "linux":
        required_packages = ["python3-venv", "python3-pip"]
        missing_packages = []
        
        print("\nChecking required packages...")
        for package in required_packages:
            try:
                result = subprocess.run(
                    ["dpkg", "-l", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✓ {package} is installed")
                else:
                    missing_packages.append(package)
                    print(f"✗ {package} is missing")
                    logging.error(f"Package {package} is missing")
            except FileNotFoundError:
                print("dpkg command not found. Are you sure you're on a Debian/Ubuntu system?")
                logging.error("dpkg command not found")
                return False
        
        if missing_packages:
            print("\nPlease install missing packages using:")
            print(f"sudo apt-get install {' '.join(missing_packages)}")
            return False
        return True
    
    if os_type == "windows":
        try:
            python_version = platform.python_version()
            print(f"\nPython version: {python_version}")
            
            # Try to install pip if not present
            try:
                import ensurepip
                ensurepip._bootstrap()
                print("✓ pip installed/verified")
                return True
            except Exception as e:
                print("✗ Error with pip installation")
                print("\nPlease run these commands in your terminal:")
                print("1. curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
                print("2. python get-pip.py")
                logging.error(f"Pip installation error: {e}")
                return False

        except Exception as e:
            print(f"Error checking Python installation: {str(e)}")
            logging.error(f"Error checking Python installation: {e}")
            return False

def create_virtual_environment(directory, os_type):
    """Create a virtual environment in the specified directory."""
    print("\nCreating virtual environment...")
    python_cmd = "python" if os_type == "windows" else "python3"
    try:
        result = subprocess.run(
            [python_cmd, "-m", "venv", os.path.join(directory, "venv")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            logging.error(f"Error creating virtual environment: {result.stderr}")
            return False
        print("✓ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {str(e)}")
        logging.exception("Error creating virtual environment")
        return False

def install_dependencies(directory, os_type):
    """Install required Python packages in the virtual environment."""
    print("\nInstalling dependencies...")
    venv_path = Path(directory) / "venv"
    pip_path = venv_path / ("Scripts" if os_type == "windows" else "bin") / "pip"
    
    try:
        # Create requirements.txt
        with open(Path(directory) / "requirements.txt", "w") as f:
            f.write("PySimpleGUI==4.60.5\nyt-dlp==2024.03.10\npyinstaller\n")
        
        # Install dependencies
        result = subprocess.run(
            [str(pip_path), "install", "-r", str(Path(directory) / "requirements.txt")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            logging.error(f"Error installing dependencies: {result.stderr}")
            return False
        print("✓ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {str(e)}")
        logging.exception("Error installing dependencies")
        return False

def create_directories(directory):
    """Create necessary project directories."""
    print("\nCreating project directories...")
    dirs = ["data", "master", "logs", "temp"]
    try:
        # First check if we have write permissions in the parent directory
        if not os.access(directory, os.W_OK):
            print(f"Error: No write permission in {directory}")
            logging.error(f"No write permission in {directory}")
            return False
            
        for dir_name in dirs:
            full_path = os.path.join(directory, dir_name)
            try:
                os.makedirs(full_path, exist_ok=True)
                # Verify the directory was actually created
                if not os.path.exists(full_path):
                    print(f"Error: Failed to create directory {full_path}")
                    logging.error(f"Failed to create directory {full_path}")
                    return False
                print(f"✓ Created {dir_name} directory")
            except PermissionError:
                print(f"Error: Permission denied when creating {full_path}")
                logging.exception(f"Permission denied when creating {full_path}")
                return False
            except Exception as e:
                print(f"Error creating {full_path}: {str(e)}")
                logging.exception(f"Error creating {full_path}")
                return False
        print("✓ All directories created successfully")
        return True
    except Exception as e:
        print(f"Error during directory creation: {str(e)}")
        logging.exception("Error during directory creation")
        return False

def create_package_structure(directory):
    """
    Create the Python package structure and copy source files.
    This includes creating the src directory, __init__.py, and copying main.py and youtube_extractor.py
    """
    print("\nCreating package structure...")
    try:
        # Create src directory structure
        src_dir = os.path.join(directory, 'src', 'yt_data_extractor')
        os.makedirs(src_dir, exist_ok=True)
        
        # Create __init__.py
        init_path = os.path.join(src_dir, '__init__.py')
        with open(init_path, 'w') as f:
            f.write('# YouTube Tool Package\n')
        print("✓ Created __init__.py")
        
        # Copy source files from setup directory
        setup_dir = os.path.dirname(os.path.abspath(__file__))
        source_files = ['main.py', 'youtube_extractor.py']
        
        for filename in source_files:
            source = os.path.join(setup_dir, 'src', 'yt_data_extractor', filename)
            dest = os.path.join(src_dir, filename)
            if os.path.exists(source):
                shutil.copy2(source, dest)
                print(f"✓ Copied {filename}")
            else:
                print(f"✗ Source file not found: {source}")
                return False
        
        return True
    except Exception as e:
        print(f"Error creating package structure: {str(e)}")
        logging.error(f"Error creating package structure: {e}")
        return False

def verify_installation(directory):
    """Verify that the installation was successful."""
    print("\nVerifying installation...")
    venv_path = Path(directory) / "venv"
    python_path = venv_path / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
    try:
        # Verify Python interpreter
        subprocess.run([str(python_path), "-c", "import sys; print(sys.version)"], 
                      check=True, capture_output=True, text=True)
        print("✓ Python interpreter found in virtual environment")
        
        # Verify package structure
        src_dir = os.path.join(directory, 'src', 'yt_data_extractor')
        required_files = ['__init__.py', 'main.py', 'youtube_extractor.py']
        for file in required_files:
            if not os.path.exists(os.path.join(src_dir, file)):
                print(f"✗ Required file missing: {file}")
                return False
            print(f"✓ Found {file}")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        logging.error(f"Error verifying installation: {e}")
        return False
    except FileNotFoundError:
        print(f"Error: Python interpreter not found at {python_path}")
        logging.error(f"Python interpreter not found at {python_path}")
        return False

def main():
    """Main installation function."""
    clear_screen()
    print("YouTube Tool Setup Wizard")
    print("========================")
    
    os_type = get_os_from_user()
    if not check_packages(os_type):
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    directory = get_directory()
    if not check_directory_permissions(directory):
        print("\nPermission issues detected. Please fix permissions and try again.")
        print("You can fix this by running:")
        print(f"sudo chown -R $USER:$USER {directory}")
        print(f"chmod 755 {directory}")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"\nInstalling in: {directory}")
    print(f"Operating System: {os_type.capitalize()}")
    input("\nPress Enter to begin installation...")
    
    steps = [
        (create_virtual_environment, "Creating virtual environment"),
        (install_dependencies, "Installing dependencies"),
        (create_directories, "Creating directories"),
        (create_package_structure, "Creating package structure"),
        (verify_installation, "Verifying installation")
    ]
    
    for step_func, step_name in steps:
        print(f"\n{step_name}...")
        success = step_func(directory, os_type) if 'os_type' in step_func.__code__.co_varnames else step_func(directory)
        
        if not success:
            print(f"\nError during {step_name.lower()}. Installation failed.")
            logging.error(f"Error during {step_name.lower()}")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        # Add explicit success message for each step
        print(f"✓ {step_name} completed successfully")
    
    print("\nInstallation completed successfully!")
    print(f"\nYour YouTube Tool is installed in: {directory}")
    print("\nTo activate the virtual environment:")
    if os_type == "windows":
        print(f"    {directory}\\venv\\Scripts\\activate")
    else:
        print(f"    source {directory}/venv/bin/activate")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        logging.exception("Unexpected error")
        input("\nPress Enter to exit...")
        sys.exit(1)
