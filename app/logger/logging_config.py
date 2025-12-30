# -*- coding: utf-8 -*-
"""
日志配置模块

该模块提供了一个自定义的JSON格式日志配置，用于FastAPI后端应用。
主要功能包括：
- JSON格式日志输出，便于日志收集和分析
- 自定义日志字段和格式
- 屏蔽默认UVicorn访问日志，推荐使用中间件自定义
- 支持环境变量配置
"""
import logging
import os
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    自定义JSON日志格式化器
    
    扩展了pythonjsonlogger.JsonFormatter，添加了自定义字段和时间标准化
    """
    def add_fields(self, log_record, record, message_dict):
        """
        添加自定义字段到日志记录
        
        参数:
            log_record: dict - 要输出的日志记录字典
            record: logging.LogRecord - 原始日志记录对象
            message_dict: dict - 消息字典
        """
        # 调用父类方法，处理默认字段
        super().add_fields(log_record, record, message_dict)
        
        # 添加全局固定字段
        log_record["service"] = "fastapi-backend"
        # 从环境变量获取环境信息，默认使用"prod"
        log_record["env"] = os.getenv("ENVIRONMENT", "prod")
        
        # 时间标准化（ISO 8601格式）
        if "asctime" in log_record:
            # 将默认的asctime字段重命名为timestamp
            log_record["timestamp"] = log_record.pop("asctime")


def get_logging_config(debug: bool = False):
    """
    获取日志配置字典
    
    参数:
        debug: bool - 是否启用DEBUG模式
        
    返回符合logging.config.dictConfig格式的配置字典
    """
    # 根据DEBUG模式设置日志级别
    log_level = "DEBUG" if debug else "INFO"
    
    return {
        "version": 1,  # 日志配置版本号
        "disable_existing_loggers": False,  # 保持False，否则会禁用已存在的日志器
        
        "formatters": {
            "json": {
                "()": CustomJsonFormatter,  # 使用自定义格式化器
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(funcName)s %(lineno)d",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601时间格式
            }
        },
        
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",  # 控制台输出
                "formatter": "json",  # 使用json格式化器
                "stream": "ext://sys.stdout",  # 输出到标准输出
            }
        },
        
        "loggers": {
            # Uvicorn主日志器
            "uvicorn": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,  # 不向上传播日志
            },
            # Uvicorn错误日志器
            "uvicorn.error": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            # 屏蔽默认的访问日志，推荐使用中间件自定义
            "uvicorn.access": {
                "handlers": [],
                "level": "CRITICAL",  # 设置为最高级别，实际上禁用了默认访问日志
            },
            # 应用程序自定义日志器
            "app": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            # 支持myapp日志器（保持向后兼容）
            "myapp": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            }
        },
        
        # 根日志器配置
        "root": {
            "handlers": ["console"],
            "level": log_level
        }
    }
