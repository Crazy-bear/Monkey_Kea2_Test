# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""
import os
import datetime
import configparser
from settings.logging_config import logger


class Config:
    """
    配置管理类
    支持从环境变量、配置文件和默认值读取配置，实例化时加载，支持 reload()。
    """

    DEFAULT_DEVICE_ID = "192.168.20.81:5555"
    DEFAULT_PACKAGE_NAME = "com.aeke.fitnessmirror"
    DEFAULT_EVENT_COUNT = 100
    DEFAULT_PROFILE = "DEFAULT"
    DEFAULT_TEST_ENGINE = "kea2"

    # 场景别名 -> 属性脚本文件名
    SCENARIO_ALIASES = {
        "main": "test_main_navigation.py",
        "navigation": "test_main_navigation.py",
        "suixinlian": "test_suixinlian.py",
        "course": "test_course.py",
        "profile": "test_profile_plan.py",
        "plan": "test_profile_plan.py",
        "media": "test_media_guide.py",
        "guide": "test_media_guide.py",
    }

    def __init__(self, profile=None, config_file=None, test_engine=None):
        self.profile = profile or os.environ.get("MONKEY_PROFILE", self.DEFAULT_PROFILE)
        self.config_file = config_file or os.environ.get("MONKEY_CONFIG_FILE", "config.ini")
        self.device_version_name = None
        self._firmware_version = None
        self._test_engine_override = test_engine
        self._load()

    def _project_root(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _resolve_path(self, path):
        if os.path.isabs(path):
            return path
        return os.path.join(self._project_root(), path)

    def _load(self):
        """从默认值、环境变量、配置文件加载配置。"""
        self.DEVICE_ID = os.environ.get("MONKEY_DEVICE_ID", self.DEFAULT_DEVICE_ID)
        self.PACKAGE_NAME = os.environ.get("MONKEY_PACKAGE_NAME", self.DEFAULT_PACKAGE_NAME)
        self.EVENT_COUNT = int(os.environ.get("MONKEY_EVENT_COUNT", self.DEFAULT_EVENT_COUNT))

        self.TEST_ENGINE = (
            self._test_engine_override
            or os.environ.get("TEST_ENGINE", self.DEFAULT_TEST_ENGINE)
        ).lower()
        if self.TEST_ENGINE not in ("monkey", "kea2"):
            self.TEST_ENGINE = self.DEFAULT_TEST_ENGINE

        self.KEA2_RUNNING_MINUTES = int(os.environ.get("KEA2_RUNNING_MINUTES", "60"))
        _max_step = os.environ.get("KEA2_MAX_STEP", "").strip()
        self.KEA2_MAX_STEP = int(_max_step) if _max_step else None
        self.KEA2_THROTTLE = int(os.environ.get("KEA2_THROTTLE", "200"))
        self.KEA2_SCENARIOS_DIR = os.environ.get("KEA2_SCENARIOS_DIR", "scenarios")
        self.KEA2_LOG_BUFFER_SECONDS = int(os.environ.get("KEA2_LOG_BUFFER_SECONDS", "120"))

        self.PERF_CPU_THRESHOLD = float(os.environ.get("PERF_CPU_THRESHOLD", 80.0))
        self.PERF_MEM_THRESHOLD = float(os.environ.get("PERF_MEM_THRESHOLD", 512.0))
        self.PERF_FPS_THRESHOLD = float(os.environ.get("PERF_FPS_THRESHOLD", 30.0))
        self.PERF_MEM_LEAK_WINDOW = int(os.environ.get("PERF_MEM_LEAK_WINDOW", 10))
        self.PERF_MEM_LEAK_GROWTH = float(os.environ.get("PERF_MEM_LEAK_GROWTH", 20.0))
        self.PERF_MEM_LEAK_RATE = float(os.environ.get("PERF_MEM_LEAK_RATE", 5.0))
        self.PERF_MEM_LEAK_R2_MIN = float(os.environ.get("PERF_MEM_LEAK_R2_MIN", 0.6))
        self.PERF_MONITOR_INTERVAL = float(os.environ.get("PERF_MONITOR_INTERVAL", 3.0))
        self.PERF_FPS_SAMPLE_EVERY = int(os.environ.get("PERF_FPS_SAMPLE_EVERY", 3))

        self.MONKEY_THROTTLE = int(os.environ.get("MONKEY_THROTTLE", 500))
        self.MONKEY_TOUCH_PERCENT = int(os.environ.get("MONKEY_TOUCH_PERCENT", 40))
        self.MONKEY_MOTION_PERCENT = int(os.environ.get("MONKEY_MOTION_PERCENT", 60))
        self.MONKEY_SYSKEYS_PERCENT = int(os.environ.get("MONKEY_SYSKEYS_PERCENT", 0))
        self.MONKEY_NAV_PERCENT = int(os.environ.get("MONKEY_NAV_PERCENT", 0))
        self.MONKEY_MAJC_PERCENT = int(os.environ.get("MONKEY_MAJC_PERCENT", 0))
        self.MONKEY_FLIP_PERCENT = int(os.environ.get("MONKEY_FLIP_PERCENT", 0))
        self.PARSE_UI_INTERVAL = int(os.environ.get("PARSE_UI_INTERVAL", 0))
        self.DEVICE_CHECK_INTERVAL = int(os.environ.get("DEVICE_CHECK_INTERVAL", 30))
        self.MAX_RECONNECT_ATTEMPTS = int(os.environ.get("MAX_RECONNECT_ATTEMPTS", 3))
        self.MONKEY_TIMEOUT_BUFFER = int(os.environ.get("MONKEY_TIMEOUT_BUFFER", 600))

        self.SEED = int(os.environ.get("MONKEY_SEED", datetime.datetime.now().strftime("%Y%m%d%H%M")))
        self._scenario_filter = None

        if os.path.exists(self.config_file):
            parser = configparser.ConfigParser()
            parser.read(self.config_file, encoding="utf-8")
            section = self.profile if self.profile in parser else "DEFAULT"
            if section in parser:
                sec = parser[section]
                self.DEVICE_ID = sec.get("DEVICE_ID", self.DEVICE_ID)
                self.PACKAGE_NAME = sec.get("PACKAGE_NAME", self.PACKAGE_NAME)
                self.EVENT_COUNT = int(sec.get("EVENT_COUNT", self.EVENT_COUNT))
                self.MONKEY_THROTTLE = int(sec.get("MONKEY_THROTTLE", self.MONKEY_THROTTLE))
                self.MONKEY_TOUCH_PERCENT = int(sec.get("MONKEY_TOUCH_PERCENT", self.MONKEY_TOUCH_PERCENT))
                self.MONKEY_MOTION_PERCENT = int(sec.get("MONKEY_MOTION_PERCENT", self.MONKEY_MOTION_PERCENT))
                self.MONKEY_SYSKEYS_PERCENT = int(sec.get("MONKEY_SYSKEYS_PERCENT", self.MONKEY_SYSKEYS_PERCENT))
                self.PERF_MONITOR_INTERVAL = float(sec.get("PERF_MONITOR_INTERVAL", self.PERF_MONITOR_INTERVAL))
                if sec.get("TEST_ENGINE"):
                    self.TEST_ENGINE = sec.get("TEST_ENGINE", self.TEST_ENGINE).lower()
                if sec.get("KEA2_RUNNING_MINUTES"):
                    self.KEA2_RUNNING_MINUTES = int(sec.get("KEA2_RUNNING_MINUTES", self.KEA2_RUNNING_MINUTES))

    def set_scenario_filter(self, scenarios_csv):
        """设置场景过滤，如 suixinlian,course 或 all。"""
        if not scenarios_csv or str(scenarios_csv).strip().lower() in ("all", "*"):
            self._scenario_filter = None
            return
        names = [s.strip().lower() for s in str(scenarios_csv).split(",") if s.strip()]
        self._scenario_filter = names

    def get_scenarios_dir(self):
        return self._resolve_path(self.KEA2_SCENARIOS_DIR)

    def get_configs_dir(self):
        return os.path.join(self._project_root(), "configs")

    def get_scenario_patterns(self):
        """
        返回 Kea2 discover 用的 -p 模式列表。
        """
        if not self._scenario_filter:
            return ["test_*.py"]
        patterns = []
        for name in self._scenario_filter:
            if name in self.SCENARIO_ALIASES:
                patterns.append(self.SCENARIO_ALIASES[name])
            elif name.startswith("test_") and name.endswith(".py"):
                patterns.append(name)
            else:
                patterns.append(f"test_{name}.py")
        return patterns

    def reload(self, profile=None):
        """重新加载配置，可选切换 profile。"""
        if profile is not None:
            self.profile = profile
        self.device_version_name = None
        self._firmware_version = None
        self._load()
        logger.info(f"配置已重新加载 (profile={self.profile})")

    @classmethod
    def get_profiles(cls, config_file="config.ini"):
        """列出 config.ini 中可用的 profile 名称。"""
        if not os.path.exists(config_file):
            return [cls.DEFAULT_PROFILE]
        parser = configparser.ConfigParser()
        parser.read(config_file, encoding="utf-8")
        return list(parser.sections()) or [cls.DEFAULT_PROFILE]

    def _get_app_info(self):
        """获取应用信息（懒加载，仅在有设备时调用）"""
        try:
            import uiautomator2 as u2
            d = u2.connect(self.DEVICE_ID)
            device_info = d.app_info(self.PACKAGE_NAME)
            self.device_version_name = device_info.get("versionName") or "Unknown"
            logger.info(f"DeviceVersionName: {self.device_version_name}")
        except Exception as e:
            logger.error(f"获取应用信息失败: {e}")
            self.device_version_name = "Unknown"

    def _get_firmware_version(self):
        """通过 adb 获取主板固件版本（ro.build.display.id）"""
        try:
            from core.adb_client import ADBClient
            adb = ADBClient(device_id=self.DEVICE_ID)
            fw = adb.shell("getprop", "ro.build.display.id", timeout=10).strip()
            return fw if fw else "Unknown"
        except Exception as e:
            logger.error(f"获取固件版本失败: {e}")
            return "Unknown"

    @property
    def DeviceVersionName(self):
        if self.device_version_name is None:
            self._get_app_info()
        return self.device_version_name or "Unknown"

    @property
    def FirmwareVersion(self):
        if self._firmware_version is None:
            self._firmware_version = self._get_firmware_version()
        return self._firmware_version

    def get_monkey_timeout_seconds(self):
        """根据事件数与 throttle 估算 Monkey 总超时（秒）。"""
        estimated = self.EVENT_COUNT * (self.MONKEY_THROTTLE / 1000.0)
        return int(estimated + self.MONKEY_TIMEOUT_BUFFER)

    def get_kea2_logcat_max_seconds(self):
        """Kea2 运行期间 logcat 最大捕获时长（秒）。"""
        return self.KEA2_RUNNING_MINUTES * 60 + self.KEA2_LOG_BUFFER_SECONDS

    def validate(self, engine=None):
        """
        校验配置是否可用于执行测试（不连接设备）。
        Returns:
            (bool, list): 是否通过，错误信息列表
        """
        engine = (engine or self.TEST_ENGINE).lower()
        errors = []
        if not getattr(self, "DEVICE_ID", None) or not str(self.DEVICE_ID).strip():
            errors.append("设备ID未配置")
        if not getattr(self, "PACKAGE_NAME", None) or not str(self.PACKAGE_NAME).strip():
            errors.append("应用包名未配置")

        if engine == "monkey":
            try:
                c = int(getattr(self, "EVENT_COUNT", 0))
                if c <= 0:
                    errors.append("事件数量必须大于0")
            except (TypeError, ValueError):
                errors.append("事件数量必须为正整数")

            pct_total = (
                self.MONKEY_TOUCH_PERCENT + self.MONKEY_MOTION_PERCENT
                + self.MONKEY_SYSKEYS_PERCENT + self.MONKEY_NAV_PERCENT
                + self.MONKEY_MAJC_PERCENT + self.MONKEY_FLIP_PERCENT
            )
            if pct_total != 100:
                errors.append(f"Monkey 事件比例之和必须为 100，当前为 {pct_total}")
        elif engine == "kea2":
            if self.KEA2_RUNNING_MINUTES <= 0:
                errors.append("Kea2 运行时长 KEA2_RUNNING_MINUTES 必须大于 0")
            scenarios_dir = self.get_scenarios_dir()
            if not os.path.isdir(scenarios_dir):
                errors.append(f"场景脚本目录不存在: {scenarios_dir}")
            else:
                patterns = self.get_scenario_patterns()
                import glob
                found = []
                for pat in patterns:
                    found.extend(glob.glob(os.path.join(scenarios_dir, pat)))
                if not found:
                    errors.append(f"未找到场景脚本: {patterns} in {scenarios_dir}")
        else:
            errors.append(f"未知测试引擎: {engine}")

        return (len(errors) == 0, errors)


# 向后兼容：模块级默认实例属性（供旧代码 Config.DEVICE_ID 访问）
_default_config = Config()
DEVICE_ID = _default_config.DEVICE_ID
PACKAGE_NAME = _default_config.PACKAGE_NAME
EVENT_COUNT = _default_config.EVENT_COUNT
PERF_CPU_THRESHOLD = _default_config.PERF_CPU_THRESHOLD
PERF_MEM_THRESHOLD = _default_config.PERF_MEM_THRESHOLD
PERF_FPS_THRESHOLD = _default_config.PERF_FPS_THRESHOLD
PERF_MEM_LEAK_WINDOW = _default_config.PERF_MEM_LEAK_WINDOW
PERF_MEM_LEAK_GROWTH = _default_config.PERF_MEM_LEAK_GROWTH
PERF_MEM_LEAK_RATE = _default_config.PERF_MEM_LEAK_RATE
PERF_MEM_LEAK_R2_MIN = _default_config.PERF_MEM_LEAK_R2_MIN
