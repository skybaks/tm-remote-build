
Net::Socket@ g_socket = null;
API::Router@ g_router = null;

void Main()
{
    @g_socket = Net::Socket();
    g_socket.Listen("localhost", 30000);

    @g_router = API::Router();
    g_router.AddRoute("load_plugin", @load_pluginTest);

    while (true)
    {
        sleep(10);

        Net::Socket@ client = g_socket.Accept();
        if (client !is null)
        {
            int bytes = client.Available();
            if (bytes > 0)
            {
                string response = g_router.Update(client.ReadRaw(bytes));
                if (response != "")
                {
                    print("Sending response: " + tostring(response));
                    client.Write(response);
                }
            }
        }
    }
}

string load_pluginTest(const string&in route, const string&in payload)
{
    print("called load_pluginTest");
    return "load_plugin not implemented!";
}
