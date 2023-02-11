
namespace API
{
    funcdef string CallbackMethod(const string&in, const string&in);

    class Router
    {
        dictionary m_routes;

        Router()
        {
        }

        void AddRoute(const string&in name, CallbackMethod@ callback)
        {
            @m_routes[name] = callback;
        }

        string Update(const string&in data)
        {
            string response = "";
            Json::Value@ json = Json::Parse(data);
            string route = json.Get("route", Json::Value(""));
            if (route != "" && m_routes.Exists(route))
            {
                response = cast<CallbackMethod@>(m_routes[route])(route, data);
            }
            return response;
        }
    }

    // Commands
    //  - Load Plugin
    //      -> response
    //  - Unload Plugin
    //      -> response
    //  - Get plugins
    //      -> response
}
