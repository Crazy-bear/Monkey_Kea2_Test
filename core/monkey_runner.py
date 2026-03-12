# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
<<<<<<< HEAD

MonkeyRunner 升级版
功能：
1. 执行 adb monkey 随机事件
2. 深度优先解析点击坐标对应的 UI 元素
3. 优先返回可点击元素
4. 输出日志
"""
import subprocess
import re
import uiautomator2 as u2
import xml.etree.ElementTree as ET
import os
import time
from config.logging_config import logger
<<<<<<< HEAD
=======
"""
>>>>>>> bc185e8 (Monkey稳定性测试)
=======
from core.utils import get_timestamp
>>>>>>> a8c8655 (feat: 添加性能监控模块并优化日志处理)


class MonkeyRunner:
    def __init__(self, adb_client, config):
        self.adb_client = adb_client
        self.config = config
<<<<<<< HEAD
        self.d = u2.connect(config.DEVICE_ID)
        # 初始化 LogcatHandler
        from core.logcat_handler import LogcatHandler
        self.logcat_handler = LogcatHandler(config)

    def run_monkey(self, monkey_log_file, max_bytes=10 * 1024 * 1024):
        """
        运行 Monkey 测试并实时解析日志，支持日志轮转
        
        Args:
            monkey_log_file: 日志文件路径
            max_bytes: 日志文件最大大小，默认10MB
            
        Returns:
            None
        """
        try:
            # 创建日志轮转处理器
            class LogRotator:
                def __init__(self, file_path, max_size):
                    self.file_path = file_path
                    self.max_size = max_size
                    self.file = open(file_path, "w", encoding="utf-8")
                    self.closed = False
                    self.last_rotate_time = 0
                
                def write(self, data):
                    if self.closed:
                        return
                    try:
                        # 检查文件大小
                        self.file.write(data)
                        self.file.flush()
                        
                        # 检查是否需要轮转（增加时间间隔，避免频繁轮转）
                        current_time = time.time()
                        if current_time - self.last_rotate_time > 600:  # 每10分钟轮转一次
                            self.file.seek(0, os.SEEK_END)
                            if self.file.tell() > self.max_size:
                                self._rotate()
                                self.last_rotate_time = current_time
                    except Exception as e:
                        logger.error(f"日志写入失败: {e}")
                
                def _rotate(self):
                    if self.closed:
                        return
                    try:
                        # 关闭当前文件
                        self.file.close()
                        
                        # 生成带时间戳的新文件名
                        base, ext = os.path.splitext(self.file_path)
                        timestamp = get_timestamp()
                        new_filename = f"{base}_{timestamp}{ext}"
                        
                        # 重命名当前日志文件
                        if os.path.exists(self.file_path):
                            os.rename(self.file_path, new_filename)
                            logger.info(f"Monkey日志文件已轮转: {new_filename}")
                        
                        # 重新打开日志文件
                        self.file = open(self.file_path, "w", encoding="utf-8")
                    except Exception as e:
                        logger.error(f"日志轮转失败: {e}")
                        # 尝试重新打开文件
                        try:
                            self.file = open(self.file_path, "w", encoding="utf-8")
                        except:
                            pass
                
                def close(self):
                    if not self.closed and self.file:
                        try:
                            self.file.close()
                        except:
                            pass
                        self.closed = True
            
            # 构建 Monkey 命令
            cmd = [
                "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
                "-p", self.config.PACKAGE_NAME,   # 应用包名
                "-s", str(self.config.SEED),    # 随机事件种子
                "--throttle", "500",  # 每次事件之间的间隔（毫秒）
                "--pct-touch", "40",    # 触摸事件百分比
                "--pct-motion", "60",   # 滑动事件百分比
                "--pct-syskeys", "0",   # 系统按键事件百分比
                "--ignore-crashes",  # 忽略应用崩溃
                "--ignore-timeouts",    # 忽略超时错误
                "--monitor-native-crashes",  # 监控原生崩溃
                "-v", "-v", "-v",  # 详细日志（拆分为单独参数）
                str(self.config.EVENT_COUNT),  # 事件数量
            ]
            
            logger.info(f"MonkeyRunner: 执行命令: {' '.join(cmd)}")

            # 创建日志轮转对象
            rotator = LogRotator(monkey_log_file, max_bytes)
            
            # 使用 subprocess.Popen 实时读取日志
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            throttle = 0.5  # throttle延迟（秒），与--throttle 500对应
            try:
                # 读取所有输出
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    rotator.write(line + "\n")
                    # 检测到事件时添加延迟（因为--throttle在该设备上可能不生效）
                    if "Sending" in line:
                        time.sleep(throttle)
                    self.parse_monkey_event(line, rotator)
                
                # 确保等待进程完全结束
                proc.wait(timeout=300)  # 5分钟超时
                
                # 检查进程退出码
                if proc.returncode != 0:
                    logger.warning(f"Monkey 测试执行完成，退出码: {proc.returncode}")
                    rotator.write(f"\nMonkey 测试执行完成，退出码: {proc.returncode}\n")
                else:
                    logger.info("Monkey 测试执行成功")
                    rotator.write("\nMonkey 测试执行成功\n")
            except subprocess.TimeoutExpired:
                logger.error("Monkey 测试执行超时")
                rotator.write("\nMonkey 测试执行超时\n")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except:
                    pass
            finally:
                rotator.close()
                    
        except Exception as e:
            logger.error(f"执行 Monkey 测试时发生错误: {e}")
            if 'rotator' in locals():
                rotator.write(f"\n执行 Monkey 测试时发生错误: {e}\n")
                rotator.close()

    def parse_monkey_event(self, line, log_file_handle):
        """
        解析 Monkey 输出坐标，并查找对应 UI 元素
        """
        match = re.search(r'Sending Touch .*?\(([\d.]+),([\d.]+)\)', line)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            try:
                element_info = self.find_element_by_coord(x, y)
                msg = f"[点击坐标 ({x},{y})] → 元素: {element_info}"
            except Exception as e:
                msg = f"[点击坐标 ({x},{y})] → UI解析异常: {e}"

            # print(msg)  # 输出日志
            log_file_handle.write(msg + "\n")

    def find_element_by_coord(self, x, y):
        """
        深度优先遍历 UI 树，查找包含指定坐标的元素
        优先返回可点击元素，尽量返回最深层节点
        """
        xml = self.d.dump_hierarchy()
        root = ET.fromstring(xml)
        best_node_info = None
        max_depth = -1
        clickable_node_info = None

        def traverse(node, depth=0):
            nonlocal best_node_info, max_depth, clickable_node_info
            bounds = node.attrib.get('bounds')
            if bounds:
                try:
                    # bounds 格式: [left,top][right,bottom]
                    left_top, right_bottom = bounds.split('][')
                    left_top = left_top.strip('[').split(',')
                    right_bottom = right_bottom.strip(']').split(',')
                    left, top = int(left_top[0]), int(left_top[1])
                    right, bottom = int(right_bottom[0]), int(right_bottom[1])
                    if left <= x <= right and top <= y <= bottom:
                        text = node.attrib.get('text', '')
                        rid = node.attrib.get('resource-id', '')
                        clazz = node.attrib.get('class', '')
                        info = f"text={text}, resource-id={rid}, class={clazz}"

                        # 优先保存可点击元素
                        if node.attrib.get('clickable') == 'true':
                            clickable_node_info = info
                        # 更新最深层元素
                        if depth > max_depth:
                            best_node_info = info
                            max_depth = depth
                except Exception as e:
                    # 记录解析错误，但继续执行
                    logger.debug(f"解析UI元素时发生错误: {e}")
                    pass
            for child in node:
                traverse(child, depth + 1)

        traverse(root)

        # 返回优先级：可点击元素 > 最深层元素 > 未找到
        if clickable_node_info:
            return clickable_node_info
        elif best_node_info:
            return best_node_info
        else:
            return "未找到元素"
=======

    def run_monkey(self, monkey_log_file):
        cmd = [
            "adb", "-s", self.config.DEVICE_ID, "shell", "monkey",
            "-p", self.config.PACKAGE_NAME,   # 应用包名
            # "-c", "android.intent.category.LAUNCHER",  # 启动器类别
            # "-c", ".activity.HealthListActivity",  # 启动器类别
            "-s", str(self.config.SEED),    # 随机事件种子
            "--throttle", "200",  # 每次事件之间的间隔（毫秒）
            "--ignore-crashes",  # 忽略应用崩溃
            "--ignore-timeouts",    # 忽略超时错误
            "--pct-touch", "40",    # 触摸事件百分比
            "--pct-motion", "60",   # 滑动事件百分比
            "--pct-syskeys", "0",   # 系统按键事件百分比
            "--monitor-native-crashes",  # 监控原生崩溃
            # "--monitor-native-exceptions",  # 监控原生异常
            # "--ignore-security-exceptions",  # 忽略安全异常
            "-v -v -v",  # 详细日志
            str(self.config.EVENT_COUNT),  # 事件数量
        ]
        # cmd = [str(arg) for arg in cmd]  # 确保 cmd 列表中的每个元素都是字符串
        print(f"MonkeyRunner: {cmd}")
        return self.adb_client.run_command(cmd, monkey_log_file)
>>>>>>> bc185e8 (Monkey稳定性测试)
