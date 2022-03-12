# Data and code for "Control algorithms underlying the translational optomotor response"

11 Mar 2022

## Overview

### Folder organization

### data folder

- data/expt - experimental data

    - data/expt/or - data from the OMR regulation experiment

    - data/expt/bf - data from the baseline flow experiment

    - data/expt/all - data from both experiments combined

- data/sim - simulation data and model fitting results

### code folder

- code/expts - code for processing experimental data

- code/simulator - Simulator and OMR model code

- code/scripts - simulation scripts

- code/figs - code for generating figures in the article

### figs folder

- generated figures (SVG format)

### Software environment

All code was written using python 3.9 with the following libraries:

- numpy 1.21.x
- pandas 1.2.x
- matplotlib 3.4.x
- scipy 1.7.x
- pillow 8.2.x (required for saving plots as JPG images)
- pyarrow 4.x  (required for feather file format support)

Later versions may also work.

### Processing experimental data, generating simulation data, and creating figures

Ensure that the necessary python version and libraries are available, for example in an activated conda virtual
environment. Then change working directory to the _code_ directory and run one of top-level scripts there, either
gendata.bat for Windows or gendata.sh for Linux etc.

The top-level script

1. processes the tracked data collected from the free swimming experiments to extract information about OMR trajectories
   and swim bouts and to generate data summaries

2. generates synthetic data for the OMR regulation and baseline flow procedures using each of the models discussed in
   the article using the best model parameters found during model fitting

3. generates figures for the article from these data

## Experimental data and data processing pipeline

This section documents the experimental data and describes the data processing steps of OMR trajectory extraction, swim
bout extraction and summarising implemented by packages _expts.trajectory_, _expts.bouts_ and
_expts.analysis_ respectively. The top-level Python script _code/simulator/process_omr_data.py_ runs the experimental
data processing pipeline for both experiments and then combines results of the two experiments.

### Tracked data

The pipeline takes as input data the position of a zebrafish larva for each frame of the original image data where that
position could be determined by the tracking algorithm. This "tracked data" is provided for the OMR regulation (OR) and
baseline flow (BF) experiment in compressed CSV format as file _tracked.csv.gz_ in the
_data/expt/or_ and _data/expt/bf_ directories respectively. Its columns are:

- height - height condition (h1, h4 and h7 for low, medium and high heights respectively)
- stimulus_speed - speed of the moving grid in mm/s
- time - time that the frame was acquired since session start in ms
- id - subject identifier
- xpos - distance of fish from end of its channel in image pixels
- ypos - distance of fish from side of its channel in image pixels (not used for further analysis)

### OMR trajectory extraction

The main processing stages for extracting OMR-consistent trajectories from the tracked data are:

- rescale from pixels to mm and resample at 10 ms fixed frequency, filling gaps up to 120 ms by linear interpolation and
  leaving the rest as missing data

- identify timesteps belonging to forward or backward *traverses*. A *traverse* is a period of time fixed by the
  experimental procedure and independent of behaviour during which the stimulus moves at a fixed velocity either forward
  or backwards. There are two traverses in each *session*, one with the stimulus moving forward and one backward.

- extract *segments* and *OMR trajectories*. A *segment* is a time series of resampled tracking data within a traverse
  with no missing data. An *OMR trajectory* is a time series within a segment during which the direction of swimming is
  consistent with the OMR.

- mark as pruned timesteps within a traverse after the goal boundary has been reached

- mark as pruned segments and trajectories with duration of less than 1s and trajectories with average speed of less
  than 0.5 mm/s

The top-level function for trajectory extraction is _expts.trajectory.extract.extract_trajectories()_

#### Trajectory data columns

The default filename for the OMR trajectory time series is *traj_ts.feather* or *traj_ts.csv*. Output files are
generated in either feather or CSV format depending on the filename extension given.

The columns included are:

- id - subject identifier

- height - height condition.

  This is a categorical factor (e.g. h1, h4, h7); the range of heights associated with each level is given in the
  details for the specific experiment.

- stimulus_speed - speed of moving grid in mm/s

- time - time in ns since the beginning of the run.

  A run consists of rest period, forward traverse, rest period, and backward traverse. Duration of each period depends
  on the experiment.

- xpos - position in mm relative to the start of the channel

- ypos - position in mm relative to side of channel. This is resampled but otherwise left unchanged and not used here.

- direction - traverse type - F for forward traverse (stimulus moving forward), B for backward traverse (stimulus moving
  backwards), N for neither (stimulus still during rest period before and between trials).

- seg_id - segment id.

  Segments are numbered consecutively from zero within a traverse, with the segment id incrementing after each period of
  missing data. Timesteps with missing data are given a segment id of -1.

- traj_id - trajectory id.

  Trajectories are also numbered consecutively from zero within a segment, or with -1 for timesteps not included in an
  OMR trajectory.

- prune - whether this timestep of an OMR trajectory is identified for pruning

### Bout extraction

Bout extraction follows OMR trajectory extraction. It identifies timesteps at which a bout is considered to have started
and adds statistics for that bout. The top-level function for bout extraction is _expts.bouts.bouts.
extract_trajectories()_. The default filename for the bout time series output is *bout_ts.feather* and the files are
generated in feather format by default (CSV can also be generated).

Note that bout identification is carried out within segments rather than within OMR trajectories. The same bout may have
some timesteps within an OMR trajectory and some outside it, but all will be in the same segment.

#### Bout data columns

The bout extraction process adds the following columns to the OMR trajectory time series data:

_bout_id_ - id numbers for bouts within segments (i.e. periods within a session without missing tracking data after
resampling and interpolation).

Bouts are numbered consecutively from zero within a segment, with the bout id incrementing when the start of a new bout
is detected. Timesteps with missing data are given a bout id of -1.

_bout_num_ - the same as _bout_id_ except that bouts considered invalid are marked by setting _bout_num_ to -1:

- the _span_ of a bout is considered to run from the first timestep of one bout to the timestep before the start of the
  next. For a valid bout these timesteps have the same non-negative _bout_num_

- the last bout in each segment is marked as invalid (_bout_num_ set to -1 for all associated timesteps) as its span and
  therefore its displacement and duration are unknown

- bouts of duration less than 100ms (ten timesteps) are marked invalid as the initial speed cannot be calculated.

- bouts with initial speed (mean speed over the first 100ms) less than 1ms/s are marked invalid

_step_num_ - sequence number for timestep within the bout. Timesteps not belonging to a vaid bout have a _step_num_ of
-1

_swim_speed_ - instantaneous swim speed. This is computed as the gradient of _xpos_ at segment level.

_bout_displacement_ - the change in position from the first to the last timestep of the bout. Note that movement between
the last timestep of one bout and the first timestep of the next is not included.

_bout_peak_speed_ - maximum swim speed over the timesteps in a bout

_bout_duration_ - difference between times for the first and last timestep in a bout. As for displacment, time from the
last timestep of one bout to the first timestep of the next is not included.

_bout_norm_speed_ - normalised speeds. Computed as swim speed divided by sum of swim speeds for up to first 1s (100
timesteps) of the bout.

_bout_initial_speed_ - mean speed over the first 100 ms (ten steps) of the bout

_omr_bout_ - whether the bout is considered an OMR bout. To qualify the bout must be entirely contained within a OMR
trajectory with none of its timesteps marked for pruning.

### Summarising experimental data

Function _expts.analysis.summarise.summarise()_ generates summary data files for a single experiment at the levels of
traverses, sessions and groups.

Default filenames:

- traverse-level summary - _trav_summ.csv_

- session-level summaries - _session.csv_

- group-level summary - _group_summ.csv_

#### Traverse-level summaries

One row for the forward traverse and one for the backward one within each session. Traverses without at least one OMR
trajectory are excluded. Generated by _expts.analysis.travsumm.summarise_traverses()_.

Data columns:

- height - height category (h1, h4, h7)

- stimulus_speed - stimulus speed (mm/s)

- id - subject id

- group_id - group identifier - a combination of height and stimulus speed
  (e.g. h1_3.20)

- direction - direction of traverse within a session. *F* for forward,
  *B* for reverse

- displacement - total distance swam over all OMR trajectories within the traverse (mm)

- duration - total time during the OMR trajectories (s)

- swim_speed - mean swim speed over the OMR trajectories (mm/s)

- num_bouts - total number of swim bouts during the OMR trajectories

- bout_rate - mean bout frequency (Hz)

- bout_dist - mean distance travelled per OMR bout (mm)

- bout_init_speed - mean speed over the first 10ms of the OMR bouts (mm/s)

#### Session-level summaries

Function _expts.analysis.sess_summ.summarise_sessions()_ generates session-level summary files. Output file *session.
csv* contains a record for each session that has at least one record in the traverse-level summary. Each summary has one
row per session that combines results from forward and backward traverses as available.

Processing steps include:

- take means over the summary data for forward and backward trajectories for each session

- add derived and additional data (mean height, baseline flow, omr ratio etc)

- various plots can be generated as required

Data columns in addition to those in the traverse-level summary:

- mean_height - midpoint of range of heights for the height category

- baseline_flow - optic flow when not swimming in rad/s assuming fish is at mid height for the condition

- ssbfr_ratio - mean ratio of swim speed to baseline flow over the session

- omr_ratio - mean ratio of observed mean swim speed to stimulus speed over the session

#### Group-level summaries

Function _expts.analysis.group_summ.summarise_groups()_ generates group-level summaries. Means and standard errors for
each dependent variable are taken over all sessions for a given experimental condition
(combination of height and stimulus speed). Column names for mean values are the same as for session and traverse level
summaries, except that *height* is renamed to *height_category*. Standard error column names have suffix *_sem_*, e.g.
*swim_speed_sem* is the standard error for swim speed. Various plots can also be generated.

The top-level script _expts.process_omr_data.py_ then makes versions of the group summary files used for model fitting
that exclude any outlier groups. These are saved with filename _group_summ_pruned.csv_ and are identical to the unpruned
versions except that, for the baseline flow procedure only, the experimental condition with the slowest stimulus speed
is excluded due to the observed anomalous behaviour in that condition.

#### Combining data from both experiments

Timeseries and summary data from both experiments are then combined into single files with path _data/expt/all/bouts_ts.
feather_ etc. A single column _source_ is added to identify the experiment (_OR_ or _BF_) contributing each row.

#### Bout intensity profile extraction

Bout intensity profiles are derived from bout timeseries data combined from the OMR regulation and baseline flow
experiments.

The profile covers a period of 1s (100 timesteps) from the start of a bout. Each step of the profile is computed by
first calculating the mean value of _swim_speed_ over all the valid bouts containing that step and then normalising it
by dividing by the mean of those values. Thus a fish swimming for 1s at the speeds in the intensity profile with
timesteps of 10ms would move a total of 1mm or equivalently be swimming at an average speed of 1 mm/s over that period.

Profiles are computed for all bouts and for OMR bouts only by _expts.bouts.bouts.process_bouts()_ and the results saved
in files *all_profile.csv* and *omr_profile.csv* respectively. Figures can be generated to illustrate the normalised
profiles and to illustrate that they are similar for bouts of widely varying intensity as indicated by initial speed,
peak speed or total displacement.

## OMR model simulation and fitting

### Overview

The OMR simulator consists of core simulation code and a number of models of the OMR in larval zebrafish expressed in
code.

The model-independent simulation code includes services for defining and running simulation "experiments" and reporting
on the results. Data generated by simulation can be compared with observational data and prediction errors computed for
multiple features of the data. Model fitting is assisted by support for systematic search in subregions of parameter
space to find parameters that minimise the prediction errors.

The OMR model itself has two top-level objects: the *Agent* representing an individual fish and the *Environment*.

Agents consist of a *Body* and a *Controller*, with a variety of controllers implemented. Each controller includes a
*BoutGenerator* which transforms the result of sensory processing to a sequence of swim bouts.

Three types of environment are modelled:

- natural environment. The fish swims against a stream of water.

- free swimming experimental environment. The fish swims in still water with the OMR evoked by a moving stimulus
  presented below.

- virtual reality (VR) environment. The fish is restrained but swimming can affect the speed of the moving stimulus in
  proportion to its intensity.

Environment and agent components can be mixed and matched by specifying their classnames in a data generation script
along with model parameters and other parameters that specify the different experimental conditions etc.

For the current article only the free swimming experimental environment is used.

### Data generation scripts

Data generation scripts define the agent and environment objects for simulation, the experimental procedure to be
applied, and optionally how to report the results.

The data generation scripts provided in the _code/scripts/sim_ directory follow a naming convention that identifies the
model, the procedure, and how the model was fitted to experimental data.

#### Script filename components identifying the OMR model:

_li_single_ - single factor model

_li_emp_    - model using basic bout generator with mean bout intensity set to observed values

_limi_emp_  - model using enhanced bout generator with mean bout intensity set to observed values

_pmi_li_    - variant A of the dual factor model

_pmi_fbli_  - variant B of the dual factor model

_pmi_fli_   - variant C of the dual factor model (final model)

#### Script filename components identifying the procedure

_o_ - OMR regulation procedure

_b_  - baseline flow procedure

#### Script filename components identifying the features and data used for model fitting:

_sbo_       - minimise swim speed error only and fit to combined data from both experiments

_ribo_      - minimise both bout rate and bout intensity error and fit to combined data from both experiments

_rbo_       - minimise bout rate error only and fit to combined data from both experiments

For example, the _pmi_fli_b_ribo.py_ script generates synthetic data for the final variant of the two-factor OMR model
(_pmi_fli_) using the baseline flow procedure (_b_) with parameters optimised by minimising prediction errors for bout
rate and bout intensity simultaneously while fitting to pooled data from both experiments (_ribo_)

The top level script _gendata_ calls these scripts to generate sample data for all models using the parameters found
during model fitting.

### Model fitting scripts and data

Because each increment of the grid search used for model fitting can take significant time (up to 25 hours for the final
iteration of the variant B of the dual factor model), the results of the final fitting iteration are provided in the _
data/sim_directory for each model alongside the data generation scripts that to find their model parameters. The results
of the most recent fitting iteration are contained in a _fit.csv_ file within a folder named after the model, features
whose errors were minimised in that fitting run, and experimental data used for fitting. For example, the _
pmi_fli_ribo_fit_ folder contains fitting results for variant C of the dual factor model when fitted to both bout rate
and bout intensity values from the combined experimental data.

Each row of the _fit.csv_ file records the result of generating synthetic data and comparing it with the experimental
data for a set of model parameters, and records the model parameters themselves and root mean square prediction errors
for the dependent variables of interest: swim speed, omr ratio, bout rate and bout initial speed.

Model fitting scripts are also provided so that these fitting results can be replicated from experimental data derived
from the original position tracking data. For example, to reproduce the fitting results for the final model, make _code_
the current working directory and run

_python -m scripts.sim.pmi_fli_ribo_fit_

Note that you may want to edit the fitting script to change the number of concurrent processes allowed. This is
specified by the _max_workers_ argument in the call to _grid_search()_

Comments in the fitting scripts show the sequence of search grids leading up to the final one.

### Configuration for data generation

Simulation are controlled by parameters for the session, the environment, and the agent's controller, body and
environment. Default values (shown in square brackets below) are the parameter values used if not overridden in the
experiment script. Global defaults for the model are defined in the *expt.defaultcfg* module, and can be overridden for
a particular project by a *defaultcfg* module placed within the package for that project.

Procedures are expressed in the experiment script by specifying

a) configuration common to all groups and phases. Parameters taking model or project level default values need not be
specified. This is the *cfg* argument to *run()* or *run_expt()*.

b) configuration that varies between the experiment's groups and/or phases. This is the *vcfg* argument to *run()* or
*run_expt()*.

For the data generation scripts provided here, most of the agent configuration parameters are derived from the model
fitting results that are also provided. For example, the _pmi_fli_o_ribo.py_ data generation script uses parameters
found in the corresponding fitting datafile _data/sim/pmi_fli_ribo_fit/fit.csv_.

The link between data generation script and fitting data is created by the line

expt_name = 'pmi_fli_ribo_fit'

near the top of the data generation script. The data generation script merges model parameters from fitting with
parameters specified in the script itself.

The *run()* function creates the data and generates some standard reports.

*run_expt()* just creates data for subsequent reporting. The data is only persisted if the save argument is set to
True (default is False).

*indiv_rpt_expt()*, *group_rpt_expt()* and *summary_rpt_expt()* generate standard figures for individual time
trajectories, group average time trajectories, and group mean variable values. Data generated by *run_expt()* may be
provided as the first argument. This speeds things up as persisting data to disk and then reloading can take significant
time. Alternatively the data may be generated once and persisted, in which case the reporting functions with no data
argument given will find the saved data automatically based on the script name and project.

##### Session parameters.

- dt - timestep in s [0.01]
- nsubjects - number of subjects in each group [20]
- duration - length of an experimental phase [30]

#### Environments (nat, free, vr)

- environment.classname - classname for the environment object

    - natural environment - simulator.environment.natural.NaturalEnvironment

    - free swimming - simulator.environment.freeswim.FreeSwimEnvironment

    - virtual reality - simulator.environment.vr.VREnvironment

        - virtual reality with replay - simulator.environment.vr.VRReplayEnvironment

#### Natural environment (nat)

Simulates the natural environment in which the fish swims against the water stream over a stationary ground image.

- Vs (s) - speed of the water stream in mm/s

- Ke (ke) - effort coefficient. Multiplies instantaneous motor output to determine speed through the water (swim speed)

- height (h) - height of fish eyes above ground in mm

#### Free swimming (free)

Simulates the experimental situation in which the fish swims in still water with a stimulus below moving at a fixed
speed.

- stimulus_speed (s) - speed in mm/s
- Ke - effort coefficient. Multiplies instantaneous motor output to determine speed through the water (swim_speed).
  Always set to 1 for simulations in this article.
- height (h) - height of fish eyes above stimulus in mm

#### Virtual reality (vr, vrreplay)

Simulates the experimental situation in which the fish is restrained with a moving stimulus below. For the basic
implementation stimulus speed varies with motor output (closed loop) to simulate the natural environment. The replay
variant also allows the stimulus history for one phase to be recorded and replayed in a later phase.

- Ke (ke) - effort coefficient. Multiplies instantaneous motor output to determine virtual swim speed swim_speed

- height_vr (h) - actual height of fish eyes above the stimulus in mm [5]

- baseline_speed - speed of the stimulus when the fish is not swimming

- gain - the reduction in stimulus speed per unit swim effort

- recorder (replay VR environment only)

    - 'record': record a new stimlus history record for the current session (closed loop)

    - 'replay': replay the recorded stimulus history (open loop)

    - other : recorder off

## Agent components

### Body module

Represents the sense organs and skeletomuscular system. (The bout generator is modelled as a controller component). The
sense organs generate sensory input from environmental stimulation, perhaps adding sensory noise, and with a fixed
sensory delay. Motor output from the controller is currently relayed to the environment without change. (In the case of
VR when recorded motor neuron activity is taken as an indicator of swim vigour, this is an accurate representation)

#### Body parameters

- sensory_noise - standard deviation of Gaussian zero mean noise (independent of timestep) added to the optic flow
  stimulus to give the sensed flow [0]

- sensory_delay - sensory delay for optic flow perception in seconds [0]

### Controller

The controller object implements flow integration and uses a bout generator object to generate the motor output.

- controller.classname - classname for the controller object
    - single factor controller - simulator.agent.controller.PIController
    - dual factor controller with bout intensity specified separately - simulator.agent.controller.
      DualControllerSpecifiedIntensity
    - dual factor controller - simulator.agent.controller.DualFactorController

#### Parameters for single factor controller (_simulator.agent.controller.PIController_)

- tau (&tau;<sub>f</sub>) - time constant for leaky integration if positive. "None" or negative tau for no leak. If tau
  is less than the timestep _dt_ then the PI controller acts as a proportional controller with Ki specifying the gain (
  this is for convenience when grid fitting as integral control, leaky integral control and proportional control can all
  be expressed using tau and Ki alone)
- Ki - integral gain (always set to 1 for scripts in this article)
- Kp - proportional gain (always set to 0 here)

#### Parameters for controller with specified bout intensity (_simulator.agent.controller.DualControllerSpecifiedIntensity_)

As for the single factor controller with the addition of

- u_intensity - required bout intensity. Set to mean observed value for the corresponding experimental condition.

#### Parameters for dual factor controller (_simulator.agent.controller.DualFactorController_)

- kfi (k<sub>f</sub>) - gain for forward component of input to flow integrator
- kbi (k<sub>b</sub>) - gain for backward component of input to flow integator
- tau_intensity (&tau;<sub>f</sub>) - time constant for leaky integration of optic flow. Integral control and
  proportional control are specified in the same way as for the other controllers.

### Bout generator

A single bout generator class _simulator.agent.bouts.BoutGenerator_ implements both basic and enhanced bout generators.

#### Bout generator parameters

- krate (k<sub>r</sub>) - gain parameter for the Poisson generator input (default 1)
- kintensity (k<sub>i</sub>) - gain parameter for bout intensity (default 1)
- kmotor (k<sub>m</sub>) - gain parameter for motor inhibition of bout initiation (default 0)
- tau_motor (&tau;<sub>m</sub>) - time constant for motor integration leak
- bout_profile - intensity bout profile.

### Package structure for the simulator and model code

#### Core simulation infrastructure

- **sessrun** - simulation framework for running agent-based experiments and model fitting

- **report** - generic support for reports and figures

- **test** - some unit tests, mostly for the simulation infrastructure

#### OMR model

- **expt** - package containing three model-specific modules that interact directly with the simulation framework:

    - defaultcfg - default configuration for experiments and reporting. Also specifies the base folder for the data
      store.

    - run - convenience function for running an OMR simulation with standard reporting

    - session - factory class that allows the session runner to create and configure simulation objects specific to this
      model and collect data from them.

      The session object must support the API defined by the session runner. Model objects may use a similar API
      themselves (for the OMR model this is sometimes the case) but this is a requirement only for the session object.

- **environment** - package for environmental components.

- **agent** - package for the OMR agent and its components

- **analysis** - data analysis and reporting specific to the OMR model

### Data storage for simulation data and model fitting results

Data is generated in a folder structure whose root is given by the _base_data_folder_ parameter. This parameter may
include an initial ~ to specify the user's home directory. The default base data folder here is ../data as the working
directory should be code/ when running python modules.

Within the base folder, there is a folder for each project with the same name as that of the corresponding python
package for that project. This allows you to separate data for multiple projects by creating scripts in different
package. Within the project folder is a folder for each experiment script whose name by default is the same as that of
the script.

The results of simulation runs are stored and retrieved as two items: metadata and data. The metadata in JSON format
records the experimental configuration and some model-specific defaults for reporting and model fitting. Generated data
is stored in a binary format (Apache Arrow feather) by default for high i/o performance, but CSV format is also
available with a header giving the column names. The *data* objects returned by *run_expt()* and *get_data()* are tuples
whose first element is the metadata represented as an object of class *sessrun.md.MD* and the second a pandas
*DataFrame*.
