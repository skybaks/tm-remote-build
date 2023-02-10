import socket
import json

def unload_plugin(sock: socket.socket, pluginId: str) -> None:
    sock.send(json.dumps({
        'command': 'unload_plugin',
        'arguments': [
            'id',
            pluginId,
        ]
    }).encode())

def load_plugin(sock: socket.socket, pluginPath: str) -> None:
    sock.send(json.dumps({
        'command': 'load_plugin',
        'arguments': [
            pluginPath
        ]
    }).encode())

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 30000))

    unload_plugin(s, 'Testbed')
    #load_plugin(s, "Testbed\\")
