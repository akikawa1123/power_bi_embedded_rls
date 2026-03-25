# Power BI Embedded - Row-Level Security (RLS) サンプル

1つのレポート・1つのデータセットで、顧客ごとに異なるデータを表示する **Power BI Embedded RLS** のデモアプリです。

> 📦 **`SampleReport/Artificial Intelligence Sample.pbix` を同梱しています。**  
> Power BI Desktop でレポートを自作しなくても、このファイルを Power BI Service に発行するだけでデモを開始できます。

**デモシナリオ:**
| 顧客 | 表示されるデータ |
|------|----------------|
| 顧客A（ソフトウェア事業部） | Category = "Software" のみ |
| 顧客B（家具事業部） | Category = "Furniture" のみ |
| 顧客C（統括本部） | すべてのデータ |

> 🚀 **はじめての方は [DEMO_GUIDE.md](DEMO_GUIDE.md) を参照してください。**  
> Microsoft Entra ID設定・SampleReport の発行・config.py 設定まで、ゼロから再現できる手順書です。

---

## 🎯 主な機能

- 顧客選択ドロップダウンUI
- 顧客ごとに異なるデータを表示（RLS適用）
- 通常レポート表示との切り替え
- 適用中のRLS情報の表示
- サービスプリンシパル認証対応

---

## 🏗️ 仕組み

```
[ブラウザ] 顧客を選択
    ↓  POST /getembedinfo_rls {"customerId": "customer_a"}
[Flask サーバー]
    ↓  config.py から username / roles を取得
    ↓  Microsoft Entra ID → Bearer Token 取得 (MSAL)
    ↓  Power BI GenerateToken API 呼び出し
       EffectiveIdentity: {username: "customer_a", roles: ["CustomerRole"]}
[Power BI API]
    ↓  RLS付き Embed Token を発行
[ブラウザ]
    → USERNAME() = "customer_a" として DAX 評価
    → Software のデータのみ表示
```

---

## 📂 ファイル構成

```
SampleReport/
└── Artificial Intelligence Sample.pbix  ← デモ用サンプルレポート（RLS設定済み）

AppOwnsData/
├── app.py              ← Flask本体・APIエンドポイント (/getembedinfo_rls, /getcustomers)
├── config.py           ← 設定ファイル ★ここを編集
├── models/
│   └── effectiveidentity.py  ← RLS用 EffectiveIdentity モデル
├── services/
│   └── pbiembedservice.py    ← Power BI API 呼び出しロジック
├── templates/
│   └── index.html            ← 顧客選択UI
└── static/js/index.js        ← RLS表示の JavaScript
```

---

## 🔑 RLS 実装のポイント

### username は DAX の USERNAME() と一致させる

```python
# config.py
'username': 'customer_a'   # Power BI の DAX で USERNAME() が返す値と完全一致
```

### roles は Power BI Desktop で定義したロール名と完全一致

```python
'roles': ['CustomerRole']  # 大文字小文字も一致させること
```

### DAX 式の基本パターン

```dax
IF(
    USERNAME() = "customer_a",
    [Category] = "Software",
    IF(
        USERNAME() = "customer_b",
        [Category] = "Furniture",
        TRUE()   // その他のユーザーは全データ表示
    )
)
```

### GenerateToken API に渡す identities の構造

```json
{
  "datasets": [{"id": "dataset-id"}],
  "reports":  [{"id": "report-id"}],
  "identities": [
    {
      "username": "customer_a",
      "roles": ["CustomerRole"],
      "datasets": ["dataset-id"]
    }
  ]
}
```

---

## 🔐 本番環境へのポイント

| 項目 | 開発時 | 本番時 |
|------|--------|--------|
| 認証情報 | `config.py` に直書き | 環境変数 (`os.environ`) |
| 顧客マッピング | `config.py` の `CUSTOMER_MAPPING` | データベースから取得 |
| ユーザー認証 | なし | OAuth / JWT などを実装 |
| Embed Token 更新 | 都度発行 | 有効期限前に更新処理を実装 |
| Service Principal 権限 | Workspace Viewer + Dataset Read | 最小権限・定期的にSecret ローテーション |

---

## 📚 参考リンク

- [Power BI Embedded - 顧客向け埋め込み](https://learn.microsoft.com/ja-jp/power-bi/developer/embedded/embed-sample-for-customers)
- [Row-Level Security (RLS)](https://learn.microsoft.com/ja-jp/power-bi/enterprise/service-admin-rls)
- [GenerateToken API](https://learn.microsoft.com/ja-jp/rest/api/power-bi/embed-token/reports-generate-token-in-group)
- [EffectiveIdentity](https://learn.microsoft.com/ja-jp/rest/api/power-bi/embed-token/reports-generate-token-in-group#effectiveidentity)
