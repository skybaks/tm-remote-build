import unittest
import logging

from .log import OpenplanetLogMessage

logger = logging.getLogger(__name__)


class TestLogMessageParser(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable logging for test
        logging.basicConfig(level=100)

    def test_read_from_log_system_message(self):
        msg = OpenplanetLogMessage(
            "[        Platform] [  LOG] [18:30:56]  Openplanet for Trackmania Next x64"
        )
        self.assertEqual("Platform", msg.source)
        self.assertEqual("LOG", msg.level)
        self.assertEqual("18:30:56", msg.time)
        self.assertEqual("", msg.subject)
        self.assertEqual("Openplanet for Trackmania Next x64", msg.text)

    def test_read_from_log_plugin_message(self):
        msg = OpenplanetLogMessage(
            "[   ScriptRuntime] [ TRAC] [18:31:09] [PluginManager]  Checking for plugin updates.."
        )
        self.assertEqual("ScriptRuntime", msg.source)
        self.assertEqual("TRAC", msg.level)
        self.assertEqual("18:31:09", msg.time)
        self.assertEqual("PluginManager", msg.subject)
        self.assertEqual("Checking for plugin updates..", msg.text)

    def test_read_malformed_time(self):
        msg = OpenplanetLogMessage("[   ScriptRuntime] [ TRAC] [18:3")
        self.assertEqual("ScriptRuntime", msg.source)
        self.assertEqual("TRAC", msg.level)
        self.assertEqual("", msg.time)
        self.assertEqual("", msg.subject)
        self.assertEqual("", msg.text)

    def test_read_brackets_in_message_text(self):
        msg = OpenplanetLogMessage(
            "[Source] [Level] [Time] [Subject]  [Extra!] Message Text"
        )
        self.assertEqual("Source", msg.source)
        self.assertEqual("Level", msg.level)
        self.assertEqual("Time", msg.time)
        self.assertEqual("Subject", msg.subject)
        self.assertEqual("[Extra!] Message Text", msg.text)
