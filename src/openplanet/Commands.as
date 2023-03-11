
namespace Commands
{
    string GetStatus(const string&in route, Json::Value@ data)
    {
        print("GetStatus");

        auto response = Json::Object();
        response["data"] = "Alive";
        response["error"] = "";

        return Json::Write(response);
    }

    string GetDataFolder(const string&in route, Json::Value@ data)
    {
        print("GetDataFolder");

        auto response = Json::Object();
        response["data"] = IO::FromDataFolder("");
        response["error"] = "";

        return Json::Write(response);
    }

    string GetAppFolder(const string&in route, Json::Value@ data)
    {
        print("GetAppFolder");

        auto response = Json::Object();
        response["data"] = IO::FromAppFolder("");
        response["error"] = "";

        return Json::Write(response);
    }

    string LoadOrReloadPlugin(const string&in route, Json::Value@ data)
    {
        print("LoadOrReloadPlugin");

        auto response = Json::Object();
        response["data"] = "";
        response["error"] = "";

        string pluginId = data.Get("id", Json::Value(""));
        string pluginSrc = data.Get("source", Json::Value(""));
        string pluginType = data.Get("type", Json::Value(""));

        auto unloadPluginHandle = Meta::GetPluginFromID(pluginId);
        if (unloadPluginHandle !is null)
        {
            print("Plugin is currently loaded. Unloading...");
            Meta::UnloadPlugin(unloadPluginHandle);
            @unloadPluginHandle = null;
            yield();
        }

        string pluginFileOrDir = pluginId;
        string pluginSubfolder = "Plugins/";
        Meta::PluginType type = Meta::PluginType::Unknown;
        if (pluginType == "folder")
        {
            type = Meta::PluginType::Folder;
            pluginFileOrDir += "/";
        }
        else if (pluginType == "zip")
        {
            type = Meta::PluginType::Zip;
            pluginFileOrDir += ".op";
        }
        else
        {
            string errorText = response["error"];
            errorText += "Unknown plugin_type: " + tostring(pluginType) + "\n";
            response["error"] = errorText;
        }

        string pluginLocation = IO::FromDataFolder("");
        Meta::PluginSource source = Meta::PluginSource::Unknown;
        if (pluginSrc == "app")
        {
            source = Meta::PluginSource::ApplicationFolder;
            pluginLocation = IO::FromAppFolder("Openplanet/");
        }
        else if (pluginSrc == "user")
        {
            source = Meta::PluginSource::UserFolder;
        }
        else
        {
            string errorText = response["error"];
            errorText += "Unknown plugin_src: " + tostring(pluginSrc) + "\n";
            response["error"] = errorText;
        }

        string pluginFullPath = pluginLocation + pluginSubfolder + pluginFileOrDir;
        print(pluginFullPath);
        auto loadPluginHandle = Meta::LoadPlugin(pluginFullPath, source, type);
        if (loadPluginHandle !is null)
        {
            response["data"] = "Plugin loaded";
        }
        else
        {
            string errorText = response["error"];
            errorText += "Plugin not loaded\n";
            response["error"] = errorText;
        }

        return Json::Write(response);
    }

    string UnloadPlugin(const string&in route, Json::Value@ data)
    {
        print("UnloadPlugin");

        auto response = Json::Object();
        response["data"] = "";
        response["error"] = "Not Implemented!";

        return Json::Write(response);
    }
}
