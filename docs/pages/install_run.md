## Install and Run

### **Install**

- use conda to install the environment

```bash
$ git clone git@github.com:zzheng93/UrbanClimateExplorer.git
$ cd ./UrbanClimateExplorer/binder 
$ conda env create -f environment.yml
$ conda activate aws_urban
```

### **Run**

- Locally

  ```bash
  $ cd ./UrbanClimateExplorer
  $ git pull
  $ cd ./docs/notebooks 
  $ jupyter notebook
  ```

- HPC (e.g., NCAR's [Casper clusters](https://arc.ucar.edu/knowledge_base/70549550) with a GPU)

  - First, create a bash script (see below), and name it as `aws_urban_env.sh`, put it in the same folder with your `UrbanClimateExplorer` folder.

    ```bash
    #!/bin/bash
    source  /glade/work/zhonghua/miniconda3/bin/activate aws_urban
    echo "ssh -N -L 8889:`hostname`:8889 $USER@`hostname`.ucar.edu"
    jupyter notebook --no-browser --ip=`hostname` --port=8889
    ```
  
  - Second, run the commands below

    Note: please use `your own job code` instead of "UIUC0021". You can find more information about `execcasper` [here](https://arc.ucar.edu/knowledge_base/72581396)    

    ```bash
    $ execcasper -A UIUC0021 -l gpu_type=v100 -l walltime=06:00:00 -l select=1:ncpus=18:mpiprocs=36:ngpus=1:mem=100GB
    $ bash aws_urban_env.sh
    ```
  
  - Thrid, launch a new terminal, copy and paste the command printed by the "echo" command, and log in. Then open your browser (e.g., Google Chrome), type `https://localhost:8889`.    
  
    Note: Sometimes port `8889` may be used by others. In this case, please adjust your bash script accordingly, e.g., from `8889` to `8892`:
  
    ```bash
    #!/bin/bash
    source  /glade/work/zhonghua/miniconda3/bin/activate aws_urban
    echo "ssh -N -L 8889:`hostname`:8892 $USER@`hostname`.ucar.edu"
    jupyter notebook --no-browser --ip=`hostname` --port=8892
    ```
  
    
  
  
