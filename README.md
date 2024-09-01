Installations:

conda create -n <env_name> python=3.9.19
conda install -c conda-forge wxpython
conda install pycodestyle pydocstyle pytest

conda install -c conda-forge pyopengl
conda install plyfile
pip install glfw



to run the program as a test:
python main.py "D:\sunny\Codes\IIB_project\data\summer\fitted_otic_capsule.ply" "D:\sunny\Codes\IIB_project\data\summer\JPEG1187.jpg"