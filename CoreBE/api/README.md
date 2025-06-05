# THIẾT LẬP CORE BE FAST API CHATBOT

**Tạo môi trường conda**

```
conda create -n [Tên môi trường] python=3.10 -y
conda activatte [Tên môi trường vừa tạo]
```

**Cài các package dependence**

```
pip install -r requirement.txt
```

**Lệnh chạy project**

```
python -m api.main
```

**Lệnh tạo file schema để định nghĩa csdl**

```
python api/migrations/cli.py create create_users_table
```

**Chạy lệnh để tạo bảng**

```
python api/migrations/cli.py migrate
```