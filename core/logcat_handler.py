# -*- coding: utf-8 -*-
"""
@author: Junxiong Huang
@date: 2025/1/10
"""

import subprocess
import threading
import time
import os
from config.logging_config import logger
from core.utils import get_timestamp


class LogcatHandler:
    def __init__(self, config):
        """
        初始化 LogcatHandler
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.process = None
        self.crash_callback = None
    
    def start_logcat(self, output_file, buffers=None, max_bytes=10 * 1024 * 1024):
        """
        启动 Logcat 日志捕获，支持日志轮转。
        
        Args:
            output_file: 日志输出文件路径
            buffers: 要捕获的日志缓冲区列表，默认包括 main、events、crash
            max_bytes: 日志文件最大大小，默认10MB
            
        Returns:
            subprocess.Popen: 日志捕获进程
        """
        if buffers is None:
            buffers = ["main", "events", "crash"]
        
        # 构建命令
        cmd = ["adb", "-s", self.config.DEVICE_ID, "logcat"]
        for buffer in buffers:
            cmd.extend(["-b", buffer])
        
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
                            logger.info(f"日志文件已轮转: {new_filename}")
                        
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
            
            # 创建日志轮转对象
            rotator = LogRotator(output_file, max_bytes)
            
            # 启动子进程并处理输出
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            
            # 启动线程处理输出
            def handle_output():
                try:
                    for line in process.stdout:
                        rotator.write(line)
                except Exception as e:
                    logger.error(f"处理日志输出时发生错误: {e}")
                finally:
                    rotator.close()
            
            output_thread = threading.Thread(target=handle_output)
            output_thread.daemon = True
            output_thread.start()
            
            self.process = process
            logger.info(f"Logcat 日志捕获已启动，输出到: {output_file}")
            return process
        except Exception as e:
            logger.error(f"启动 Logcat 失败: {e}")
            return None

    def stop_logcat(self):
        """
        停止 Logcat 捕获。
        """
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("Logcat 日志捕获已停止")
            except Exception as e:
                logger.error(f"停止 Logcat 失败: {e}")
            finally:
                self.process = None

    def detect_crashes(self, log_file):
        """
        检测日志中的崩溃信息。
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            list: 崩溃信息列表
        """
        crashes = []
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as file:
                # 增加更多崩溃类型检测
                crash_keywords = [
                    "FATAL EXCEPTION",
                    "ANR",
                    "NullPointerException",
                    "OutOfMemoryError",
                    "IllegalStateException",
                    "RuntimeException",
                    "ClassCastException",
                    "IndexOutOfBoundsException",
                    "IOException",
                    "Error",
                    "Crash"
                ]
                
                # 读取并分析日志
                for line in file:
                    if any(keyword in line for keyword in crash_keywords):
                        crashes.append(line.strip())
        except FileNotFoundError:
            logger.error(f"错误: 日志文件 {log_file} 未找到。")
        except IOError as e:
            logger.error(f"IO 错误: {e}")
        except Exception as e:
            logger.error(f"检测崩溃时发生错误: {e}")
        
        return crashes
    
    def analyze_logs(self, log_file):
        """
        分析日志文件，提供详细分析和崩溃分类。
        
        Args:
            log_file: 日志文件路径
            
        Returns:
            dict: 日志分析结果，包含崩溃分类和分析结论
        """
        analysis_result = {
            "crash_categories": {},
            "total_crashes": 0,
            "analysis_conclusion": "",
            "crash_details": []
        }
        
        try:
            logger.info(f"开始分析日志文件: {log_file}")
            
            with open(log_file, "r", encoding="utf-8", errors="ignore") as file:
                # 崩溃类型分类
                crash_categories = {
                    "NullPointerException": [],
                    "OutOfMemoryError": [],
                    "IllegalStateException": [],
                    "RuntimeException": [],
                    "ClassCastException": [],
                    "IndexOutOfBoundsException": [],
                    "IOException": [],
                    "ANR": [],
                    "Other": []
                }
                
                # 读取并分析日志
                line_count = 0
                for line in file:
                    line_count += 1
                    line = line.strip()
                    # 检测崩溃类型
                    if "NullPointerException" in line:
                        crash_categories["NullPointerException"].append(line)
                    elif "OutOfMemoryError" in line:
                        crash_categories["OutOfMemoryError"].append(line)
                    elif "IllegalStateException" in line:
                        crash_categories["IllegalStateException"].append(line)
                    elif "RuntimeException" in line:
                        crash_categories["RuntimeException"].append(line)
                    elif "ClassCastException" in line:
                        crash_categories["ClassCastException"].append(line)
                    elif "IndexOutOfBoundsException" in line:
                        crash_categories["IndexOutOfBoundsException"].append(line)
                    elif "IOException" in line:
                        crash_categories["IOException"].append(line)
                    elif "ANR" in line:
                        crash_categories["ANR"].append(line)
                    elif any(keyword in line for keyword in ["FATAL EXCEPTION", "Error", "Crash"]):
                        crash_categories["Other"].append(line)
                
                logger.info(f"日志文件分析完成，共分析 {line_count} 行")
                
                # 统计崩溃数量
                total_crashes = 0
                crash_details = []
                for category, crashes in crash_categories.items():
                    count = len(crashes)
                    if count > 0:
                        analysis_result["crash_categories"][category] = count
                        total_crashes += count
                        crash_details.extend([{"category": category, "message": crash} for crash in crashes])
                
                analysis_result["total_crashes"] = total_crashes
                analysis_result["crash_details"] = crash_details
                
                # 生成分析结论
                if total_crashes == 0:
                    analysis_result["analysis_conclusion"] = "未检测到崩溃，应用稳定性良好。"
                else:
                    # 找出最常见的崩溃类型
                    most_common_category = max(analysis_result["crash_categories"].items(), key=lambda x: x[1])
                    analysis_result["analysis_conclusion"] = f"共检测到 {total_crashes} 次崩溃，其中最常见的崩溃类型是 {most_common_category[0]}，发生了 {most_common_category[1]} 次。\n\n"
                    
                    # 针对不同崩溃类型提供分析
                    if "NullPointerException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"NullPointerException：{analysis_result['crash_categories']['NullPointerException']}次\n原因分析：空指针异常可能是由于未正确初始化对象或调用了空对象的方法导致。在代码中应增加空值检查，确保对象在使用前已正确初始化。\n\n"
                    if "OutOfMemoryError" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"OutOfMemoryError：{analysis_result['crash_categories']['OutOfMemoryError']}次\n原因分析：内存溢出错误可能是由于应用内存使用过高或内存泄漏导致。建议检查大对象的使用，及时释放不再需要的资源，并考虑使用内存分析工具检测泄漏。\n\n"
                    if "ANR" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"ANR：{analysis_result['crash_categories']['ANR']}次\n原因分析：应用无响应可能是由于主线程执行了耗时操作导致。应将网络请求、数据库操作等耗时任务移至后台线程执行。\n\n"
                    if "IOException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"IOException：{analysis_result['crash_categories']['IOException']}次\n原因分析：IO异常可能是由于文件操作、网络连接或其他IO操作失败导致。应增加异常处理，确保IO操作的健壮性。\n\n"
                    if "IllegalStateException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"IllegalStateException：{analysis_result['crash_categories']['IllegalStateException']}次\n原因分析：非法状态异常可能是由于对象处于不适合执行请求操作的状态导致。应确保在调用方法前检查对象的状态是否正确。\n\n"
                    if "RuntimeException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"RuntimeException：{analysis_result['crash_categories']['RuntimeException']}次\n原因分析：运行时异常可能是由于代码逻辑错误或意外情况导致。应增加异常处理和错误检查，提高代码的健壮性。\n\n"
                    if "ClassCastException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"ClassCastException：{analysis_result['crash_categories']['ClassCastException']}次\n原因分析：类型转换异常可能是由于尝试将对象转换为不兼容的类型导致。应在转换前使用instanceof检查类型兼容性。\n\n"
                    if "IndexOutOfBoundsException" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"IndexOutOfBoundsException：{analysis_result['crash_categories']['IndexOutOfBoundsException']}次\n原因分析：索引越界异常可能是由于访问数组、集合或字符串时使用了无效的索引导致。应在访问前检查索引的有效性。\n\n"
                    if "Other" in analysis_result["crash_categories"]:
                        analysis_result["analysis_conclusion"] += f"Other：{analysis_result['crash_categories']['Other']}次\n原因分析：其他类型的崩溃可能由多种原因导致，建议查看具体的崩溃日志以确定详细原因。\n\n"
                
                logger.info(f"日志分析结果: {analysis_result}")
                    
        except FileNotFoundError:
            logger.error(f"错误: 日志文件 {log_file} 未找到。")
            analysis_result["analysis_conclusion"] = "无法分析日志，文件未找到。"
        except IOError as e:
            logger.error(f"IO 错误: {e}")
            analysis_result["analysis_conclusion"] = f"无法分析日志，IO错误: {e}"
        except Exception as e:
            logger.error(f"分析日志时发生错误: {e}")
            analysis_result["analysis_conclusion"] = f"分析日志时发生错误: {e}"
        
        return analysis_result
    
    def start_real_time_crash_detection(self, log_file, callback=None):
        """
        启动实时崩溃检测
        
        Args:
            log_file: 日志文件路径
            callback: 崩溃检测回调函数
        """
        self.crash_callback = callback
        
        def monitor_logs():
            """监控日志文件的变化"""
            last_position = 0
            crash_keywords = [
                "FATAL EXCEPTION",
                "ANR",
                "NullPointerException",
                "OutOfMemoryError",
                "IllegalStateException",
                "RuntimeException"
            ]
            
            while self.process and self.process.poll() is None:
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                        
                        for line in new_lines:
                            if any(keyword in line for keyword in crash_keywords):
                                if self.crash_callback:
                                    self.crash_callback(line.strip())
                                logger.warning(f"实时检测到崩溃: {line.strip()}")
                except Exception as e:
                    logger.error(f"监控日志时发生错误: {e}")
                
                time.sleep(1)  # 每秒检查一次
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_logs)
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("实时崩溃检测已启动")


