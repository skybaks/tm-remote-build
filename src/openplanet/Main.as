
Net::Socket@ g_socket = null;

void Main()
{
    @g_socket = Net::Socket();
    g_socket.Listen("localhost", 30000);

    while (true)
    {
        sleep(10);

        Net::Socket@ client = g_socket.Accept();
        if (client !is null)
        {
            Commands::HandleClient(client);
        }
    }
}
