import os


def resource_path(relative_path):
    """実行ディレクトリを基準にしたリソースの絶対パスを返す"""
    return os.path.join(os.path.abspath("."), relative_path)
