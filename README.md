# RPC. gRPC. Protobuf
# Выполнил: Пирюшов Александр

1. Клонируйте репозиторий

2. Установите зависимости

```
pip install -r requirements.txt
```

3. Сгенерируйте файлы proto

```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. glossary.proto
```

4. Соберите и запустите контейнер

```
docker-compose up --build
```