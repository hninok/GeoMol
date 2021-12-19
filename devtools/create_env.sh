# Developed by Kevin A. Spiekermann
# This script does the following tasks:
# 	- creates the conda
# 	- prompts user for desired CUDA version
# 	- installs PyTorch with specified CUDA version in the environment
# 	- installs torch torch-geometric in the environment


# get OS type
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=MacOS;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac
echo "Running ${machine}..."


# request user to select one of the supported CUDA versions
# source: https://pytorch.org/get-started/locally/
PS3='Please enter 1, 2, 3, 4, or 5 to specify the desired CUDA version from the options above: '
options=("9.2" "10.1" "10.2" "11.1" "cpu" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "9.2")
            CUDA="cudatoolkit=9.2"
            CUDA_VERSION="cu92"
            break
            ;;
        "10.1")
			CUDA="cudatoolkit=10.1"
            CUDA_VERSION="cu101"
            break
            ;;
        "10.2")
			CUDA="cudatoolkit=10.2"
            CUDA_VERSION="cu102"
            break
            ;;
        "11.1")
			CUDA="cudatoolkit=11.1"
            CUDA_VERSION="cu111"
            break
            ;;
        "cpu")
			# "cpuonly" works for Linux and Windows
			CUDA="cpuonly"
			# Mac does not use "cpuonly"
			if [ $machine == "Mac" ]
			then
				CUDA=" "
			fi
            CUDA_VERSION="cpu"
            break
            ;;
        "Quit")
            exit
            ;;
        *) echo "invalid option $REPLY";;
    esac
done

echo "Creating conda environment..."
echo "Running: conda env create -f environment.yml"
conda env create -f devtools/environment.yml

# activate the environment to install torch-geometric
source activate GeoMol

echo "Installing PyTorch with requested CUDA version..."
echo "Running: conda install pytorch torchvision $CUDA -c pytorch"
if [ $CUDA_VERSION == "cu111" ]; then
  conda install pytorch torchvision torchaudio $CUDA -c pytorch -c nvidia -c conda-forge
else
  conda install pytorch torchvision $CUDA -c pytorch
fi

echo "Installing torch-geometric..."
echo "Using CUDA version: $CUDA_VERSION"
# get PyTorch version
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
echo "Using PyTorch version: $TORCH_VERSION"

pip install torch-scatter==2.0.8 -f https://pytorch-geometric.com/whl/torch-${TORCH_VERSION}+${CUDA_VERSION}.html
pip install torch-sparse==0.6.11 -f https://pytorch-geometric.com/whl/torch-${TORCH_VERSION}+${CUDA_VERSION}.html
pip install torch-cluster==1.5.9 -f https://pytorch-geometric.com/whl/torch-${TORCH_VERSION}+${CUDA_VERSION}.html
pip install torch-spline-conv==1.2.1 -f https://pytorch-geometric.com/whl/torch-${TORCH_VERSION}+${CUDA_VERSION}.html
pip install torch-geometric==1.7.2

conda install -c conda-forge tensorboard

