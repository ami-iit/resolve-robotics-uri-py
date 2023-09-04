# resolve-robotics-uri-py

Pure Python package (that only depends on Python stdlib) to resolve a package:// (ROS-style) or model:// (Gazebo-style) URI to an absolute filename.

## Installation

Install using onle one of the following commands to install in an existing environment:

### Installation from conda-forge

```bash
mamba install -c conda-forge resolve-robotics-uri-py
```

### Installation from PyPI

```bash
python -m pip install resolve-robotics-uri-py
```

## Usage in Python

Add `import resolve_robotics_uri_py` to your Python file, then take inspiration from the following examples.

If you want to get the location of the `iCubGazeboV2_7` iCub model installed from [`icub-models`](https://github.com/robotology/icub-models):

~~~python
absolute_path = resolve_robotics_uri_py.resolve_robotics_uri("package://iCub/robots/iCubGazeboV2_7/model.urdf")
~~~

If you want to get the location of the `ergoCubSN00`  model installed from [`ergocub-software`](https://github.com/icub-tech-iit/ergocub-software):

~~~python
absolute_path = resolve_robotics_uri_py.resolve_robotics_uri("package://ergoCub/robots/ergoCubSN000/model.urdf")
~~~

If you want to get the location of the `panda`  model installed by [`moveit_resources_panda_description`](https://index.ros.org/p/moveit_resources_panda_description/):

~~~python
absolute_path = resolve_robotics_uri_py.resolve_robotics_uri("package://moveit_resources_panda_description/urdf/panda.urdf")
~~~


## Command Line usage

`resolve_robotics_uri_py` also install a command line tool called `resolve-robotics-uri-py` for use in scripts, that can be used as:

~~~
resolve-robotics-uri-py package://iCub/robots/iCubGazeboV2_7/model.urdf
~~~

For example,  on bash this can be used to easily convert the a urdf specified via `package://` to an sdf (assuming you have Gazebo installed), using the [backtick operator](https://www.redhat.com/sysadmin/backtick-operator-vs-parens):
~~~
gz sdf -p `resolve-robotics-uri-py package://iCub/robots/iCubGazeboV2_7/model.urdf`
~~~

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html)
