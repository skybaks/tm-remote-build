
namespace Commands
{
    class ClientCommand
    {
        string Command = "";
        string[] Arguments = {};

        string ToString()
        {
            string concatArgs = "";
            for (uint i = 0; i < Arguments.Length; ++i)
            {
                concatArgs += tostring(Arguments[i]);
                if (i < (Arguments.Length - 1))
                {
                    concatArgs += ", ";
                }
            }

            return tostring(Command) + ": " + concatArgs;
        }
    }

    ClientCommand ParseCommand(const string&in payload)
    {
        ClientCommand newCommand;

        auto json = Json::Parse(payload);
        newCommand.Command = json.Get("command", Json::Value("None"));

        auto argsArray = json.Get("arguments", Json::Array());
        for (uint i = 0; i < argsArray.Length; ++i)
        {
            string argument = argsArray[i];
            newCommand.Arguments.InsertLast(argument);
        }

        return newCommand;
    }

    void HandleClient(Net::Socket@ client)
    {
        int bytes = client.Available();
        if (bytes > 0)
        {
            string payload = client.ReadRaw(bytes);
            auto cmd = ParseCommand(payload);
            if (cmd.Command == "unload_plugin")
            {
                UnloadPlugin(cmd);
            }
            else if (cmd.Command == "load_plugin")
            {
                LoadPlugin(cmd);
            }
        }
    }

    void UnloadPlugin(ClientCommand@ command)
    {
        trace("Executing unload plugin command -> " + tostring(command));
        Meta::Plugin@ target = null;

        if (command.Arguments.Length < 2)
        {
            error("Too few arguments. Expecting 2");
        }

        if (command.Arguments[0] == "id")
        {
            @target = Meta::GetPluginFromID(command.Arguments[1]);
        }
        else if (command.Arguments[0] == "siteID")
        {
            @target = Meta::GetPluginFromSiteID(Text::ParseInt(command.Arguments[1]));
        }

        if (target !is null)
        {
            trace("Unloading plugin '" + target.ID + "' (version " + target.Version + ")");
            Meta::UnloadPlugin(target);
        }
    }

    void LoadPlugin(ClientCommand@ command)
    {
        print("Executing load plugin command -> " + tostring(command));

        if (command.Arguments.Length < 1)
        {
            error("Too few arguments. Expecting 1");
        }

        Meta::LoadPlugin(command.Arguments[0], Meta::PluginSource::UserFolder, Meta::PluginType::Folder);
    }
}
