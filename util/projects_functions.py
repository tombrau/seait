import subprocess
import os
from util.CONSTANTS import *
import requests
import util.installation_status as installation_status
from util.json_tools_projects import get_pref_project_data
from util.path_handler import full_path

def convert_to_backslashes(file_path):
    return file_path.replace("/", "\\")

def get_project_path(project_data):
    if pref_project_path(project_data):
        return convert_to_backslashes(pref_project_path(project_data))
    else:
        # return os.path.abspath(project_data['repo_name'])
        return os.path.join(full_path, project_data['repo_name'])
    
def get_venv_path(project_data):
    return f"{os.path.join(get_project_path(project_data), 'venv')}"

def get_entry_point(project_data, key):
    return os.path.join(get_project_path(project_data), project_data['entry_point'][key])

def get_pref_project_path(project_name, project_pref_path):
    project_path = os.path.join(project_pref_path,project_name)
    return project_path

def pref_project_path(project_data):
    project_id = project_data['id']
    if get_pref_project_data(project_id):
        pref_project_data =get_pref_project_data(project_id)
        if pref_project_data['isSet']:
            return pref_project_data['path']
        else:
            return False

def clone_repo(project_data):
    project_name = project_data['repo_name']
    git_clone_url = project_data['git_clone_url']
    project_path = get_project_path(project_data)
    subprocess.run(["git", "clone", git_clone_url, project_path]) 
    print(f"{project_name} cloned into {project_path}")

def create_virtual_environment(project_data, args=[]):
    project_name = project_data['repo_name']
    venv_path = get_venv_path(project_data)
    print(f"Creating virtual environment for {project_name} at {venv_path} ")
    subprocess.run(["python", "-m", "venv", venv_path], shell=True)         
    print(f"Virtual environment created for {project_name} at {venv_path}")

def update(project_data,args=[]):
    project_path = get_project_path(project_data)
    print(f"Updating {project_data['repo_name']} at {project_path}")
    subprocess.run(["git", "pull"], cwd=project_path)

def uninstall(project_data,args=[]):
    project_path = get_project_path(project_data)
    print(f"Uninstalling {project_data['repo_name']} deleting {project_path} folder.")
    subprocess.run(["rd", "/s", "/q", project_path], shell=True)
    print(f"{project_data['repo_name']} uninstalled {project_path} folder deleted.")

#def launch(project_data, args=[]):
#    project_path = get_project_path(project_data)
#    venv_path = get_venv_path(project_data)
#    launch_path = get_entry_point(project_data, 'launch')
#
#    print(f"launching {project_data['repo_name']} at {project_path}")
#    installation_status_venv = installation_status.check_project_venv(project_data)
#    installation_status_project = installation_status.check_project(project_data)
#
#    if not installation_status_venv:
#        print(f"Virtual environment (venv) not found for {project_data['repo_name']} at {project_path}. Will create a new one.")
#        install(project_data,args=[])
#
#    if installation_status_project:
#        command_len = len(launch_path.split())
#        cmd_launch = project_data['entry_point']['launch']
#        activate_script = f"{venv_path}/Scripts/activate.bat"
#        cmd_command = f'cmd /K ""{activate_script}" && "{venv_path}/Scripts/python" {cmd_launch} {" ".join(args)}"'
#        cmd_command_no_py = f'cmd /K ""{activate_script}" && {cmd_launch} {" ".join(args)}"'
#
#        if launch_path.endswith(".py") and command_len == 1:
#            subprocess.run([f"{venv_path}/Scripts/python", launch_path, *args], cwd=project_path)
#        elif launch_path.endswith(".py") and command_len > 1:
#            subprocess.run(cmd_command, cwd=project_path, shell=True)           
#        elif launch_path.endswith(".bat"):
#            subprocess.run([launch_path, *args], cwd=project_path)
#        else:
#            subprocess.run(cmd_command_no_py, cwd=project_path, shell=True)      
#    else:
#        print(f"Failed to launch {project_data['repo_name']} venv not installed.")

def launch(project_data, args=[]):
    project_path = get_project_path(project_data)
    venv_path = get_venv_path(project_data)
    launch_path = get_entry_point(project_data, 'launch')

    # if project_data['install_instructions_available']:
    #     install_instructions(project_data)

    print(f"Launching {project_data['repo_name']} at {project_path}")

    installation_status_venv = installation_status.check_project_venv(project_data)
    installation_status_project = installation_status.check_project(project_data)

    if not installation_status_venv:
        print(f"Virtual environment (venv) not found for {project_data['repo_name']} at {project_path}. Will create a new one.")
        install(project_data, args=[])

    if installation_status_project:
        activate_script = f"{venv_path}\\Scripts\\activate.bat"
        python_exe = f"{venv_path}\\Scripts\\python.exe"
        cmd_args = " ".join(args) if args else ""

        # Ensure launch_path is a full path
        if not os.path.isabs(launch_path):
            launch_path = os.path.join(project_path, launch_path)

        if launch_path.endswith(".py"):
            cmd = f'cmd /C "{activate_script} && "{python_exe}" "{launch_path}" {cmd_args}"'
        elif launch_path.endswith(".bat"):
            cmd = f'cmd /C "{activate_script} && call "{launch_path}" {cmd_args}"'
        else:
            cmd = f'cmd /C "{activate_script} && "{launch_path}" {cmd_args}"'

        print(f"Executing command: {cmd}")

        try:
            subprocess.run(cmd, cwd=project_path, shell=True, check=True)
            print(f"Launch of {project_data['repo_name']} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during launch of {project_data['repo_name']}: {e}")
            print(f"Command that failed: {cmd}")
    else:
        print(f"Failed to launch {project_data['repo_name']} venv not installed.")

def install(project_data, args=[]):
    project_path = get_project_path(project_data)
    print(f"Installing {project_data['repo_name']} at {project_path}")
    
    clone_repo(project_data)
    create_virtual_environment(project_data)
    
    venv_path = get_venv_path(project_data)
    install_path = get_entry_point(project_data, 'install')
    activate_script = f"{venv_path}\\Scripts\\activate.bat"
    python_exe = f"{venv_path}\\Scripts\\python.exe"

    if project_data['install_requirements']:
        install_requirements(project_data)
    
    if project_data['install_instructions_available']:
        install_instructions(project_data)

    cmd_args = " ".join(args) if args else ""

    if install_path.endswith(".py"):
        cmd = f'cmd /C "{activate_script} && "{python_exe}" "{install_path}" {cmd_args}"'
    elif install_path.endswith(".bat"):
        cmd = f'cmd /C "{activate_script} && "{install_path}" {cmd_args}"'
    else:
        cmd = f'cmd /C "{activate_script} && {install_path} {cmd_args}"'

    print(f"Executing command: {cmd}")
    
    try:
        print(f"Installation of {project_data['repo_name']} completed successfully.")
        subprocess.run(cmd, cwd=project_path, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during installation of {project_data['repo_name']}: {e}")
        print(f"Command that failed: {cmd}")



def delete_virtual_environment(project_data,args=[]):
    venv_path = get_venv_path(project_data)
    print(f"Deleting virtual environment for {project_data['repo_name']} at {venv_path}")
    subprocess.run(["rd", "/s", "/q", venv_path], shell=True)
    print(f"virtual environment deleted for {project_data['repo_name']}")
    
def install_cuda(project_data):
    project_path = get_project_path(project_data)
    venv_path = get_venv_path(project_data)
    print(f"installing cuda")
    cmd = f"{venv_path}/Scripts/python -m pip install torch==1.13.1 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117"
    subprocess.run(cmd, shell=True, cwd=project_path)
    print(f"cuda installed")

# def install_requirements(project_data):
#     project_path = get_project_path(project_data)
#     venv_path = get_venv_path(project_data)
#     print(f"Installing requirements for {project_data['repo_name']} at {venv_path}")
#     if project_data['install_cuda']:
#         install_cuda(project_data)
# 
#     try: subprocess.run([f"{venv_path}/Scripts/python","-m", "pip","install","-r","requirements.txt"], cwd=project_path)
#     except: print("Oops")
#     try: subprocess.run([f"{venv_path}/Scripts/python","-m", "pip","install","-r","requirements_versions.txt"], cwd=project_path)
#     except:print("Oops 2")
#     
#     print(f"{project_data['repo_name']} requirements installed at {venv_path}")

def install_requirements(project_data):
    project_path = get_project_path(project_data)
    venv_path = get_venv_path(project_data)
    print(f"Installing requirements for {project_data['repo_name']} at {venv_path}")
    if project_data['install_cuda']:
        install_cuda(project_data)

    # Get the requirements file name, default to "requirements.txt" if not specified
    requirements_file = project_data.get("requirements_file", "requirements.txt")

    try:
        subprocess.run([f"{venv_path}/Scripts/python", "-m", "pip", "install", "-r", requirements_file], cwd=project_path, check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to install requirements from {requirements_file}")
    
    # If the first attempt fails, try the alternate file name
    if requirements_file != "requirements.txt":
        try:
            subprocess.run([f"{venv_path}/Scripts/python", "-m", "pip", "install", "-r", "requirements.txt"], cwd=project_path, check=True)
        except subprocess.CalledProcessError:
            print("Failed to install requirements from requirements.txt")
    
    print(f"{project_data['repo_name']} requirements installed at {venv_path}")



def install_instructions(project_data):
    project_path = get_project_path(project_data)
    venv_path = get_venv_path(project_data)
    print(f"Executing install instructions for {project_data['repo_name']}")

    for command in project_data["install_instructions"]:
        subprocess.run([f"{venv_path}/Scripts/python"] + command.split(), cwd=project_path)
        print(f"{project_data['repo_name']} Instructed installation completed")

def install_webui_extension(project_data,args=[]):
    print(f"installing {project_data['repo_name']}")
    subprocess.run(["git","clone",project_data["git_clone_url"],f"{full_path}\{project_data['webui_path']}\extensions\{project_data['repo_name']}"]) 
    # print(["git","clone",project_data["git_clone_url"],f"{full_path}\{project_data['webui_path']}\extensions\{project_data['repo_name']}"])

    print(f"{project_data['repo_name']} installed")
    download_models(project_data, skip_existing=True)

def update_webui_extension(project_data,args=[]):
    print(f"updating {project_data['repo_name']}")
    subprocess.run(["git","pull"], cwd=f"{project_data['webui_path']}\extensions\{project_data['repo_name']}")

def uninstall_webui_extension(project_data,args=[]):
    print(f"uninstalling {project_data['repo_name']}")
    subprocess.run(["rd", "/s", "/q", f"{project_data['webui_path']}\extensions\{project_data['repo_name']}"], shell=True)
    print(f"{project_data['repo_name']} uninstalled")

def download_models(project_data, skip_existing=True):
    # base_url = "https://huggingface.co/datasets/disty/seait_ControlNet-modules-safetensors/resolve/main/"
    base_url = "https://huggingface.co/datasets/disty/seait_ControlNet1-1-modules-safetensors/resolve/main/"

    download_folder = os.path.join(full_path,project_data['webui_path'], 'models', 'ControlNet')
    # print(download_folder)
    os.makedirs(download_folder, exist_ok=True)

    for model in CN_MODELS_11:
        file_path = os.path.join(download_folder, model)
        
        if skip_existing and os.path.exists(file_path):
            print(f"{model} already exists. Skipping download.")
            continue

        url = base_url + model
        response = requests.get(url)

        if response.status_code == 200:
            model_size_mb = int(response.headers.get("Content-Length", 0)) / (1024 * 1024)
            print(f"Downloading {model} ({model_size_mb:.2f} MB)")
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"{model} downloaded.")
        else:
            print(f"Error: Failed to download {model}. Status code: {response.status_code}")

    print("All models downloaded.")

def download_comfyui_models(project_data):
    if project_data["id"] == 2:
        # print(f"downloading models for {project_data['repo_name']}")
        project_path = get_project_path(project_data) 
        checkpoints_path = os.path.join(f"{project_path}/{project_data['checkpoints_path']}")
        # subprocess.run(["git","clone",project_data["models_path"],f"{project_data['webui_path']}\models\ControlNet"]) 
        # download_file(project_data["download_models_path"], project_data['checkpoints_path']) 
        # print(checkpoints_path) 
        # download_file(project_data['download_models_path'],f"C:/repos/seai/ComfyUI/models/checkpoints/{project_data['download_models_path']}")     
        print(f"{project_data['repo_name']} models downloaded")    

methods = {
    "clone": clone_repo,
    "update": update,
    "delete_venv": delete_virtual_environment,
    "create_venv": create_virtual_environment,
    "uninstall": uninstall,
    "launch": launch,
    "install": install,
    "install_webui_extension": install_webui_extension,
    "uninstall_webui_extension": uninstall_webui_extension,
    "update_webui_extension": update_webui_extension,
    "download_models": download_models,
}
