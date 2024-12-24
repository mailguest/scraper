def register(username, passwrord):
    if not username:
        raise ValueError("用户名不能为空")
    elif not passwrord:
        raise ValueError("密码不能为空")
    
    try:
        db.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except db.IntegrityError:
        error = f"User {username} is already registered."
    else:
        return redirect(url_for("auth.login"))