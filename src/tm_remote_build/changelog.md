# 2.1.0
* Add optional --host argument to allow using an address other than localhost
* Add optional -d argument for cases where the default logic cant find the Openplanet.log file
* Fix issue with parsing log file on latest Openplanet version

# 2.0.0
* Rework CLI to simplify internal code and provide more control to the caller
* Add option to load plugins from an ID
* Add option to unload plugins from an ID
* Change output format to match VS Code extension and work with defined problemMatcher
