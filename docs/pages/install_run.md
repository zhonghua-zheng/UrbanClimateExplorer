## Install and Run

**Install**: 

- use conda to install the environment

```bash
$ git clone git@github.com:zzheng93/UrbanClimateExplorer.git
$ cd ./UrbanClimateExplorer/binder 
$ conda env create -f environment.yml
$ conda activate aws_urban
```

**Run**:

- Locally:

  ```bash
  $ cd ./UrbanClimateExplorer
  $ git pull
  $ cd ./docs/notebooks 
  $ jupyter notebook
  ```

- HPC:

  e.g., NCAR's [Casper clusters](https://arc.ucar.edu/knowledge_base/70549550) (using a GPU)

  First, create a bash script (see below), and name it as `aws_urban_env.sh`, put it in the same folder with your `UrbanClimateExplorer` folder.

  ```bash
  #!/bin/bash
  source  /glade/work/zhonghua/miniconda3/bin/activate aws_urban
  echo "ssh -N -L 8889:`hostname`:8889 $USER@`hostname`.ucar.edu"
  jupyter notebook --no-browser --ip=`hostname` --port=8889
  ```

  Second, run the commands below

  Note: please use `your own job code` instead of "UIUC0021". You can find more information about execcasper [here](https://arc.ucar.edu/knowledge_base/72581396)

  ```bash
  $ execcasper -A UIUC0021 -l gpu_type=v100 -l walltime=06:00:00 -l $ select=1:ncpus=18:mpiprocs=36:ngpus=1:mem=100GB
  $ bash aws_urban_env.sh
  ```
