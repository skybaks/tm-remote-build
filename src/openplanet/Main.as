
Net::Socket@ g_socket = null;
API::Router@ g_router = null;

#if TMNEXT
int g_port = 30000;
#elif MP4
int g_port = 30001;
#elif TURBO
int g_port = 30002;
#endif

void Main()
{
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
