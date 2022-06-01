import random
import allure
import pytest
import logging

from tests.common.helpers.assertions import pytest_assert
from tests.common.plugins.loganalyzer import DisableLogrotateCronContext

LOGS_TO_ROTATE = ['/var/log/auth.log',
                  '/var/log/arista.log',
                  '/var/log/cron.log',
                  '/var/log/syslog',
                  '/var/log/teamd.log',
                  '/var/log/telemetry.log',
                  '/var/log/frr/bgpd.log',
                  '/var/log/frr/zebra.log',
                  '/var/log/swss/sairedis.rec',
                  '/var/log/swss/swss.rec',
                  '/var/log/swss/responsepublisher.rec']

logger = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.topology("any"),
    pytest.mark.disable_loganalyzer
]


@pytest.fixture(scope="module", autouse=True)
def check_branch(duthost):
    if duthost.sonic_release in ["201811", "201911", "202006", "202012", "202106"]:
        pytest.skip("Logrotate is not supported on {} and other legacy branches".format(duthost.sonic_release))


class TestLogRotate:
    @pytest.fixture(autouse=True)
    def setup(self, duthost):
        self.duthost = duthost
        self.select_random_log()

    def select_random_log(self):
        random_log = random.choice(LOGS_TO_ROTATE)
        logger.info("Random log is {}".format(random_log))
        self.log_path = random_log

    def get_log_size(self):
        ls_log = self.duthost.shell("ls -l {} | awk '{{print $5}}'".format(self.log_path))
        while "No such file or directory" in ls_log["stderr"]:
            logger.warning("{}".format(ls_log["stderr"]))
            logger.info("Taking another random log")
            self.select_random_log()
            ls_log = self.duthost.shell("ls -l {} | awk '{{print $5}}'".format(self.log_path))
        return int(ls_log["stdout"])

    def set_log_size(self, size):
        if self.size_in_bytes(size) < self.get_log_size():
            # Do backup if the original log size is greater than desired
            self.duthost.shell("cp {} {}.bak".format(self.log_path, self.log_path))
        self.duthost.shell("truncate -s {} {}".format(size, self.log_path))

    @staticmethod
    def size_in_bytes(size):
        try:
            if size.endswith("M"):
                return int(size[:-1]) * 1024 * 1024
            elif size.endswith("K"):
                return int(size[:-1]) * 1024
        except TypeError:
            pytest.fail("Incorrect size value")

    def do_logrotate(self):
        cmd = "/usr/bin/pkill -9 logrotate > /dev/null 2>&1; /usr/sbin/logrotate /etc/logrotate.conf > /dev/null 2>&1"
        self.duthost.shell(cmd)

    @pytest.mark.parametrize("step, size, expected",
                             [("TC1", "16M", True),
                              ("TC2", "10K", False),
                              ("TC3", "8M", False)])
    def test_logrotate(self, setup, step, size, expected):
        steps = {
            "TC1": "Checks if logrotate works when the log size is over the threshold",
            "TC2": "Checks if logrotate doesn't work when the log size is small",
            "TC3": "Checks if logrotate doesn't work when the log size is half of the threshold",
        }
        with DisableLogrotateCronContext(self.duthost):
            with allure.step(steps[step]):
                original_log_size = self.get_log_size()
                logger.info("{} original size is {} bytes".format(self.log_path, original_log_size))
                self.set_log_size(size)
                increased_log_size = self.get_log_size()
                logger.info("{} increased size is {} bytes".format(self.log_path, increased_log_size))
                self.do_logrotate()
                rotated_log_size = self.get_log_size()
                logger.info("{} size after logrotate is {} bytes".format(self.log_path, rotated_log_size))
                pytest_assert((rotated_log_size < increased_log_size) == expected,
                              "Unexpected logrotate behavior detected on {}. Original log size was: {}. Increased to "
                              "{}. The size after logrotate: {}".format(self.log_path, original_log_size,
                                                                        increased_log_size, rotated_log_size))
