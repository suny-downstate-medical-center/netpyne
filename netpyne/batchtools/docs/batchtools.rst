Running a Batch Job
===================

The NetPyNE batchtools subpackage provides a method of automating job submission and reporting::


 batch<-->\               /---> configuration_0 >---\
           \             /                         specs---\
           \<--->dispatcher_0                               sim_0
           \             \                         comm ---/
           \              \---<    results_0    <---/
            \
            \               /---> configuration_1 >---\
            \              /                         specs---\
            \<--->dispatcher_1                                sim_1
             \             \                         comm ---/
             \              \---<    results_1    <---/
             \
             \
             ...


1. Retrieving batch configuration values through the ``specs`` object
-----
Each simulation is able to retrieve relevant configurations through the ``specs`` object, and communicate with
the dispatcher through the ``comm`` object.

importing the relevant objects::

     from netpyne.batchtools import specs, comm
     cfg = specs.SimConfig()  # create a SimConfig object
     netParams = specs.NetParams()  # create a netParams object

``netpyne.batchtools.specs`` behaves similarly to ``netpyne.sim.specs`` except in the following cases:

* ``netpyne.batchtools.specs`` automatically captures relevant configuration mappings created by the ``dispatcher`` upon initialization

   * these mappings can be retrieved via ``specs.get_mappings()``

* the SimConfig object created by ``netpyne.batch.specs.SimConfig()`` will update itself with relevant configuration mappings through the ``update()`` method::

    from netpyne.batchtools import specs # import the custom batch specs
    cfg = specs.SimConfig()              # create a SimConfig object
    cfg.update()                         # update the cfg object with any relevant mappings for this particular batch job

The ``update`` method will update the ``SimConfig`` object with the configuration mappings captured in ``specs`` (see: ``specs.get_mappings()``)

This replaces the previous idiom for updating the SimConfig object with mappings from the batched job submission::

    try:
        from __main__ import cfg  # import SimConfig object with params from parent module
    except:
        from cfg import cfg  # if no simConfig in parent module, import directly from tut8_cfg module



2. Communicating results to the ``dispatcher`` with the ``comm`` object
-----

Prior batched simulations relied on ``.pkl`` files to communicate data. The ``netpyne.batch`` subpackage uses a specific ``comm`` object to send custom data back
The ``comm`` object determines the method of communication based on the batch job submission type.

In terms of the simulation, the following functions are available to the user:

* **comm.initialize()**: establishes a connection with the batch ``dispatcher`` for sending data

* **comm.send(<data>)**: sends ``<data>`` to the batch ``dispatcher``

* **comm.close()**: closes and cleans up the connection with the batch ``dispatcher``

3. Specifying a batch job
-----
Batch job handling is implemented with methods from ``netpyne.batchtools.search``

**search**::

    def search(job_type: str, # the submission engine to run a single simulation (e.g. 'sge', 'sh')
               comm_type: str, # the method of communication between host dispatcher and the simulation (e.g. 'socket', 'filesystem')
               run_config: Dict,  # batch configuration, (keyword: string pairs to customize the submit template)
               params: Dict,  # search space (dictionary of parameter keys: tune search spaces)
               algorithm: Optional[str] = "variant_generator", # search algorithm to use, see SEARCH_ALG_IMPORT for available options
               label: Optional[str] = 'search',  # label for the search
               output_path: Optional[str] = '../batch',  # directory for storing generated files
               checkpoint_path: Optional[str] = '../ray',  # directory for storing checkpoint files
               max_concurrent: Optional[int] = 1,  # number of concurrent trials to run at one time
               batch: Optional[bool] = True,  # whether concurrent trials should run synchronously or asynchronously
               num_samples: Optional[int] = 1,  # number of trials to run
               metric: Optional[str] = "loss", # metric to optimize (this should match some key: value pair in the returned data
               mode: Optional[str] = "min",  # either 'min' or 'max' (whether to minimize or maximize the metric
               algorithm_config: Optional[dict] = None,  # additional configuration for the search algorithm
               ) -> tune.ResultGrid: # results of the search

The basic search implemented with the ``search`` function uses ``ray.tune`` as the search algorithm backend, returning a ``tune.ResultGrid`` which can be used to evaluate the search space and results. It takes the following parameters;

* **job_type**: either "``sge``" or "``sh``", specifying how the job should be submitted, "``sge``" will submit batch jobs through the Sun Grid Engine. "``sh``" will submit bach jobs through the shell on a local machine
* **comm_type**: either "``socket``" or "``filesystem``", specifying how the job should communicate with the dispatcher
* **run_config**: a dictionary of keyword: string pairs to customize the submit template, the expected keyword: string pairs are dependent on the job_type::

    =======
    sge
    =======
    queue: the queue to submit the job to (#$ -q {queue})
    cores: the number of cores to request for the job (#$ -pe smp {cores})
    vmem: the amount of memory to request for the job (#$ -l h_vmem={vmem})
    realtime: the amount of time to request for the job (#$ -l h_rt={realtime})
    command: the command to run for the job

    example:
    run_config = {
        'queue': 'cpu.q',       # request job to be run on the 'cpu.q' queue
        'cores': 8,             # request 8 cores for the job
        'vmem': '8G',           # request 8GB of memory for the job
        'realtime': '24:00:00', # set timeout of the job to 24 hours
        'command': 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'
    } # set the command to be run to 'mpiexec -n $NSLOTS -hosts $(hostname) nrniv -python -mpi init.py'

    =======
    sh
    =======
    command: the command to run for the job

    example:
    run_config = {
        'command': 'mpiexec -n 8 nrniv -python -mpi init.py'
    } # set the command to be run

* **params**: a dictionary of config values to perform the search over. The keys of the dictionary should match the keys of the config object to be updated. Lists or numpy generators >2 values will force a grid search over the values; otherwise, a list of two values will create a uniform distribution sample space.

    **usage 1**: updating a constant value specified in the ``SimConfig`` object ::

        # take a config object with the following parameter ``foo``
        cfg = specs.SimConfig()
        cfg.foo = 0
        cfg.update()

        # specify a search space for ``foo`` such that a simulation will run with:
        # cfg.foo = 0
        # cfg.foo = 1
        # cfg.foo = 2
        # ...
        # cfg.foo = 9

        # using:
        params = {
            'foo': range(10)
        }

    **usage 2**: updating a nested object in the ``SimConfig`` object::

        # to update a nested object, the package uses the `.` operator to specify reflection into the object.
        # take a config object with the following parameter object ``foo``
        cfg = specs.SimConfig()
        cfg.foo = {'bar': 0, 'baz': 0}
        cfg.update()

        # specify a search space for ``foo['bar']`` with `foo.bar` such that a simulation will run:
        # cfg.foo['bar'] = 0
        # cfg.foo['bar'] = 1
        # cfg.foo['bar'] = 2
        # ...
        # cfg.foo['bar'] = 9

        # using:
        params = {
            'foo.bar': range(10)
        }

        # this reflection works with nested objects as well...
        # i.e.
        # cfg.foo = {'bar': {'baz': 0}}
        # params = {'foo.bar.baz': range(10)}

* **algorithm** : the search algorithm (supported within ``ray.tune``)

    **Supported algorithms**::

        * "variant_generator": grid and random based search of the parameter space (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "random": grid and random based search of the parameter space (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "axe": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "bayesopt": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "hyperopt": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "bohb": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "nevergrad": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "optuna": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "hebo": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "sigopt": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)
        * "zoopt": optimization algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)

* **label**: a label for the search, used for output file naming

* **output_path**: the directory for storing generated files, can be a relative or absolute path

* **checkpoint_path**: the directory for storing checkpoint files in case the search needs to be restored, can be a relative or absolute path

* **max_concurrent**: the number of concurrent trials to run at one time, it is recommended to keep in mind the resource usage of each trial to avoid overscheduling

* **batch**: whether concurrent trials should run synchronously or asynchronously

* **num_samples**: the number of trials to run, for any grid search, each value in the grid will be sampled ``num_samples`` times.

* **metric**: the metric to optimize (this should match some key: value pair in the returned data)

* **mode**: either 'min' or 'max' (whether to minimize or maximize the metric)

* **algorithm_config**: additional configuration for the search algorithm (see: https://docs.ray.io/en/latest/tune/api/suggestion.html)

