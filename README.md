Upload
---

ファイルのアップロード  

## 説明  

- $HOST/  
index.html が表示される  
index.html はアップロードサイトのhtml  


- $HOST/resource  
現在のオブジェクト一覧  


- $HOST/upload  
アップロード先  
```sh
curl -X POST localhost:3000/upload -F "upload=@/path/to/your/file"
```

```json
{
  "id": "abcdef43-1111-aaaa-1234-56789abcdb53", 
  "result": "upload OK"
}
```


- $HOST/approve  
アップロード後の処理  
OK とか NG とか  

### OKの場合  
```sh
curl -X POST -H 'Content-Type: application/json' localhost:3000/approve -d '{"approve": "ok", "id": "abcdef43-1111-aaaa-1234-56789abcdb53"}'
```

```json
{
  "id": "abcdef43-1111-aaaa-1234-56789abcdb53", 
  "md5": "b10a8db164e0754105b7a99be72e3fe5", 
  "result": "approve OK"
}
```


### NGの場合  
```sh
curl -X POST -H 'Content-Type: application/json' localhost:3000/approve -d '{"approve": "ng", "id": "abcdef43-1111-aaaa-1234-56789abcdb53"}'
```

```json
{
  "id": "abcdef43-1111-aaaa-1234-56789abcdb53", 
  "result": "approve Cancel"
}
```

