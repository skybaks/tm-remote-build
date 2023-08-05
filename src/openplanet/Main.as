
Net::Socket@ g_socket = null;
API::Router@ g_router = null;

[Setting category="General" name="Remote Connection Port" description="Port used by the plugin to listen on a TCP socket. If changed the plugin will need to be restarted."]
#if TMNEXT
int Setting_RemoteConnectionPort = 30000;
#elif MP4
int Setting_RemoteConnectionPort = 30001;
#elif TURBO
int Setting_RemoteConnectionPort = 30002;
#endif

int g_port = 0;
string g_menuMessage = "";

void RenderMenu()
{
    UI::TextDisabled(g_menuMessage);
}

void Main()
{
    g_port = Setting_RemoteConnectionPort;
    g_menuMessage = "\\$070" + Icons::Kenney::Cloud + " \\$zRemote Build Port - " + tostring(g_port);
    if (g_port == 0)
    {
        g_menuMessage = "\\$700" + Icons::Kenney::TimesCircle + " \\$zRemote Build Port - OFF";
        error("Configured Remote Connection Port is " + tostring(g_port) + ". Exiting...");
        return;
    }

    @g_socket = Net::Socket();
    g_socket.Listen("localhost", g_port);

    @g_router = API::Router();
    g_router.AddRoute("get_status", @API::GetStatus);
    g_router.AddRoute("get_data_folder", @API::GetDataFolder);
    g_router.AddRoute("get_app_folder", @API::GetAppFolder);
    g_router.AddRoute("load_plugin", @API::LoadOrReloadPlugin);
    g_router.AddRoute("unload_plugin", @API::UnloadPlugin);

    while (true)
    {
        yield();

        Net::Socket@ client = g_socket.Accept();
        if (client !is null)
        {
            startnew(HandleClient, client);
        }
    }
}

void HandleClient(ref@ socket)
{
    Net::Socket@ client = cast<Net::Socket@>(socket);

    while (true)
    {
        yield();

        int bytes = client.Available();
        if (bytes > 0)
        {
            string response = g_router.Update(client.ReadRaw(bytes));
            if (response != "")
            {
                client.Write(response);
            }
        }
        else
        {
            break;
        }
    }
}
