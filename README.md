# DVC Recorder
> Making DVC a little more DRY


I love DVC and when using it I found that I had to repeat myself more often than I'd like. Parameter names and file names often appeared in two or three different places, in code and in config files.  Let's DRY up DVC and give it a single source of truth.

## Install

Make sure you have virtualenv and then

```bash
git clone https://github.com/talosiot-will/dvcrecord.git
cd dvcrecord
make env
```

## Walkthrough

We'll pick up where the tutorial on [data pipelines](https://dvc.org/doc/start/data-pipelines) left off.  Since the point of this exercise is not to show off DVC's nifty large dataset handling abilities, we'll use a very truncated `data.xml` that's part of this repository.  Below is a snippet of `prepare.py`

```python
#<A bunch of imports> 

# =============================
#load your params, input, and output files
params = yaml.safe_load(open('params.yaml'))['prepare']

if len(sys.argv) != 2:
    sys.stderr.write("Arguments error. Usage:\n")
    sys.stderr.write("\tpython prepare.py data-file\n")
    sys.exit(1)

# Test data set split ratio
split = params['split']
random.seed(params['seed'])

input = sys.argv[1]
output_train = os.path.join('data', 'prepared', 'train.tsv')
output_test = os.path.join('data', 'prepared', 'test.tsv')

def process_posts(fd_in, fd_out_train, fd_out_test, target_tag):
    # << function logic goes here.  I skipped it >>
    pass

## read and write files
os.makedirs(os.path.join('data', 'prepared'), exist_ok=True)

with io.open(input, encoding='utf8') as fd_in:
    with io.open(output_train, 'w', encoding='utf8') as fd_out_train:
        with io.open(output_test, 'w', encoding='utf8') as fd_out_test:
            process_posts(fd_in, fd_out_train, fd_out_test, '<python>')

```

Which if you run with the command 
```bash
dvc run -n prepare \
          -p prepare.seed,prepare.split \
          -d src/prepare.py -d data/data.xml \
          -o data/prepared \
          python src/prepare.py data/data.xml
```

will yield the `dvc.yaml` file
```yaml
stages:
  prepare:
    cmd: python src/prepare.py data/data.xml
    deps:
    - data/data.xml
    - src/prepare.py
    params:
    - prepare.seed
    - prepare.split
    outs:
    - data/prepared
```

There's a lot of repetition there.  The single source of truth for which parameters you need is your python source code file.  You have to repeat that information in the `dvc run` command, which then gets logged in the `dvc.yaml` file.  Similarly with the output folder, the path appears both in code and again in the command line argument.  Let's try to clean that up a bit.

Copy `prepare.py` to a new file we'll call `prepare-dvcr.py` and let's edit the new file.  We'll introduce a tiny bit of machinery to manage this stage of the pipeline.

```python
from dvcrecord import PipelineStage
stage = PipelineStage('prepare')
```

That object will help us load our parameters

```python
split = stage.params.load('prepare.split')
random.seed(stage.params.load('prepare.seed'))
```

We can load the input_file straight from the command line argument.
```python
input_file = stage.deps.from_cli()[0]
```
And we register our output folder.
```python
output_folder = stage.outputs.register('data', 'prepared')
output_test = os.path.join(output_folder, 'test.tsv')
output_train = os.path.join(output_folder, 'train.tsv')
```

That's it.  Now we don't have to repeat outselves in the `dvc run` command.  Instead you can just run it like a normal python program, with a few special command line arguments.  Specify the dependent file directly with the flag `--dvc_dep`.  Specify that you'd like the output sent to a `dvc.yaml` file with `--dvc_record`.

```
>> python prepare-dvcr.py --dvc_dep data/data.xml --dvc_record
```

It automatically knows that your code is dependent on the original source file (the one being run in the command line) as well as any paramater files you've used.
