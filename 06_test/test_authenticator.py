import pytest
# 同じディレクトリにある authenticator.py から Authenticatorクラスをインポート
from authenticator import Authenticator

# 1. register() メソッドで、ユーザーが正しく登録されるか
def test_register_success():
    auth = Authenticator()
    auth.register("test_user", "password123")
    # 辞書内に正しくデータが入っているかを確認
    assert auth.users["test_user"] == "password123"

# 2. register() メソッドで、すでに存在するユーザー名で登録を試みた場合にエラーが出るか
def test_register_duplicate_error():
    auth = Authenticator()
    auth.register("test_user", "password123")
    # pytest.raises を使って、指定したエラーが発生することを確認
    with pytest.raises(ValueError) as excinfo:
        auth.register("test_user", "new_password")
    
    # エラーメッセージの内容も確認
    assert str(excinfo.value) == "エラー: ユーザーは既に存在します。"

# 3. login() メソッドで、正しいユーザー名とパスワードでログインできるか
def test_login_success():
    auth = Authenticator()
    auth.register("test_user", "password123")
    result = auth.login("test_user", "password123")
    # 戻り値が期待通りかを確認
    assert result == "ログイン成功"

# 4. login() メソッドで、誤ったパスワードでエラーが出るか
def test_login_failure_error():
    auth = Authenticator()
    auth.register("test_user", "password123")
    # 誤ったパスワードで ValueError が発生することを確認
    with pytest.raises(ValueError) as excinfo:
        auth.login("test_user", "wrong_pass")
    
    assert str(excinfo.value) == "エラー: ユーザー名またはパスワードが正しくありません。"