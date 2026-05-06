from fastapi import status
from pydantic_settings import BaseSettings


class Constant(BaseSettings):
    # 权限
    ROLE_ADMIN_DESCRIPTION: str = "系统管理员，管理所有数据"
    ROLE_PROVIDER_DESCRIPTION: str = "数据提供者，上传并管理自己的数据"
    ROLE_CONSUMER_DESCRIPTION: str = "数据使用者，浏览和获取已发布数据"

    # 返回值
    RESP_SUCCESS: dict = {"status": status.HTTP_200_OK, "message": "success"}
    RESP_SERVER_ERROR: dict = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "服务器错误",
    }
    RESP_TOKEN_NOT_MATCH: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token校验失败",
    }
    RESP_TOKEN_VERIFY_ERR: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token解析失败",
    }
    RESP_TOKEN_NOT_EXISTED: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token不存在，请先登录",
    }
    RESP_TOKEN_EXPIRED: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token过期，需要重新登录",
    }

    RESP_USER_FORBIDDEN: dict = {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "当前用户权限不足",
    }
    RESP_USER_INCORRECT_PASSWD: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户名或密码错误",
    }
    RESP_USER_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户名已存在",
    }
    RESP_USER_EMAIL_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "邮箱已被注册",
    }
    RESP_USER_NOT_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户不存在",
    }

    RESP_USER_SESSION_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "会话记录不存在",
    }
    RESP_USER_SESSION_NULL: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "请求发送了一个空会话",
    }
    RESP_INVALID_MODEL: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "无效的模型",
    }
    RESP_DATASET_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "数据资产不存在",
    }
    RESP_DATASET_FORBIDDEN: dict = {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "当前用户无权访问该数据资产",
    }
    RESP_DATASET_UNSUPPORTED_TYPE: dict = {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "当前文件类型暂不支持上传",
    }
    RESP_ANALYSIS_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "数据分析结果不存在",
    }
    RESP_ANALYSIS_JOB_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "数据分析任务不存在",
    }
    RESP_PROFILE_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "数据档案不存在",
    }
    RESP_DATASET_NOT_REVIEWABLE: dict = {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "当前数据资产尚未完成分析，不能审核",
    }
    RESP_DATASET_NOT_PUBLISHABLE: dict = {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "当前数据资产尚未通过审核，不能发布",
    }
    RESP_ACCESS_GRANT_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "数据授权记录不存在",
    }
    RESP_EXPORT_FORMAT_UNSUPPORTED: dict = {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "当前数据资产不支持该导出格式",
    }
    RESP_EXPORT_JOB_NOT_EXISTS: dict = {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "导出任务不存在",
    }
    RESP_EXPORT_JOB_NOT_READY: dict = {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "导出任务尚未完成",
    }


CONSTANT = Constant()
