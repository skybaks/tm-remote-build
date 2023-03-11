
namespace API
{
    funcdef string CallbackMethod(const string&in, Json::Value@);

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

        string Update(const string&in payload)
        {
            string response = "";
            Json::Value@ json = Json::Parse(payload);
            string route = json.Get("route", Json::Value(""));
            if (route != "" && m_routes.Exists(route))
            {
                response = cast<CallbackMethod@>(m_routes[route])(route, json["data"]);
            }
            else
            {
                auto jsonResp = Json::Object();
                jsonResp["data"] = "";
                jsonResp["error"] = "Not implemented: " + tostring(route);
                response = Json::Write(jsonResp);
            }
            return response;
        }
    }
}
