# Remote Build

Build and reload openplanet plugins from your IDE.

## Setup

First install the RemoteBuild Openplanet plugin [found here](https://openplanet.dev/plugin/remotebuild) or from the
ingame plugin manager.

Then install the remote build client using pip:

```
python -m pip install --upgrade tm-remote-build
```

## Usage

### Use Case 1 - Plugin Folder in Openplanet\*/Plugins/ Folder

This is the use case if your plugin source code is located in an Openplanet\*/Plugins folder. This use case benefits
from not requiring the overhead of copying the zipped plugin files to the Plugins folder. The drawback is that the
plugin can only be loaded by the game which the Openplanet folder belongs to.

Invoke the remote build client and pass in the path to the folder. A relative path is also valid.

```
tm-remote-build C:\Users\Username\OpenplanetNext\Plugins\Dashboard
```

The client will connect to the running game for this folder location and load the plugin.

### Use Case 2 - Zipped Plugin \*.op

This use case is great if you have external packaging scripts since the input is a pre-existing \*.op file. Another
benefit of this use case is that you can deploy and load in more than one game at a time if multiple are running. The
downside is that you incure the overhead of copying the plugin file to each Openplanet\*/Plugins folder.

Invoke the remote build client and pass in the path to the zipped plugin file. A relative path is also valid.

```
tm-remote-build C:\Users\Username\Code\Dashboard\Dashboard.op
```

The client will find every running game and deploy and load the zipped plugin to all of them.

### Use Case 3 - Package and Deploy Plugin Source

This is for the case where your code is not located in an Openplanet\*/Plugins folder and you would like to use the
remote build client to package and deploy your code.

Invoke the remote build client by passing in the path to your source code, relative or absolute.

```
tm-remote-build C:\Users\Username\Code\Dashboard --zip
```

The client will package the files under the input path. Then deploy and load the zipped plugin to all active games.

You can use the arguments `--zip_out_path`, `--zip_exclude`, and `--zip_plugin_id` to control and tune the packaging.

## Links

* Github: https://github.com/skybaks/tm-remote-build
* Pypi: https://pypi.org/project/tm-remote-build/
* Openplanet: https://openplanet.dev/plugin/remotebuild
