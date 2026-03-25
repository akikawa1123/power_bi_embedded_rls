# Power BI Embedded RLS デモ - 再現手順ガイド

このガイドに従うことで、誰でもこのデモを自分の環境で再現できます。

> 📦 **`SampleReport/Artificial Intelligence Sample.pbix` を同梱しています。**  
> レポートを自作することなく、このファイルを発行するだけでデモを開始できます。

---

## 📋 全体の流れ（所要時間: 約20分）

```
[ステップ1] Azure ADアプリ登録（5分）
      ↓
[ステップ2] SampleReport を発行・ID取得・Service Principal 追加（5分）
      ↓
[ステップ3] Python環境のセットアップ（5分）
      ↓
[ステップ4] config.py を設定して実行（5分）
      ↓
[完成] ブラウザで顧客ごとのデータを確認！
```

---

## 🛠️ 事前に必要なもの

| 必要なもの | 備考 |
|----------|------|
| Power BI Pro または Fabric ライセンス | Microsoft 365 / M365 開発者テナント可 |
| Azure AD（Entra ID）へのアクセス | アプリ登録の権限が必要 |
| Python 3.8以上 | https://www.python.org/downloads/ |
| Power BI Desktop | https://aka.ms/pbidesktop （SampleReport の発行に使用） |

> ✅ **Power BI Desktop でレポートを自作する必要はありません。**  
> `SampleReport/Artificial Intelligence Sample.pbix` をそのまま発行してください。

---

## ステップ1: Azure AD アプリの登録

> Service Principal（サービスプリンシパル）を使って Power BI API を呼び出すための認証設定です。

### 1-1. Azure ポータルでアプリを登録

1. https://portal.azure.com にアクセス
2. 左メニュー → **Azure Active Directory**（または **Microsoft Entra ID**）
3. **アプリの登録** → **新規登録** をクリック
4. 以下を入力して **登録**:
   - 名前: `PowerBI-Embedded-Demo`（任意）
   - サポートされているアカウントの種類: **この組織のディレクトリ内のアカウントのみ**
   - リダイレクトURI: 空白のまま可

5. 登録後、以下の値をメモ:
   - **アプリケーション（クライアント）ID** → `CLIENT_ID`
   - **ディレクトリ（テナント）ID** → `TENANT_ID`

### 1-2. クライアントシークレットを作成

1. 左メニュー → **証明書とシークレット**
2. **新しいクライアントシークレット** をクリック
3. 説明: `demo-secret`、有効期限: `24ヶ月`（任意）→ **追加**
4. 作成直後に表示される **値** をコピーしてメモ → `CLIENT_SECRET`
   > ⚠️ この画面を閉じると二度と表示されません！

### 1-3. Power BI API の権限を付与

1. 左メニュー → **APIのアクセス許可**
2. **アクセス許可の追加** → **Power BI Service**
3. **委任されたアクセス許可** を選択
4. 以下を検索して追加:
   - `Report.ReadAll`
   - `Dataset.ReadAll`
   - `Workspace.Read.All`
5. **管理者の同意を与える** をクリック（テナント管理者権限が必要）

### 1-4. Power BI の管理ポータルで設定

1. https://app.powerbi.com にアクセス
2. 右上の歯車アイコン → **管理ポータル**
3. **テナントの設定** → **開発者設定**
4. **サービスプリンシパルによる Power BI API の使用を許可する** → **有効**
5. **変更を適用** をクリック

---

## ステップ2: SampleReport を Power BI Service に発行

> 📦 このリポジトリには `SampleReport/Artificial Intelligence Sample.pbix` が含まれています。  
> レポートを自作する必要はありません。以下の手順でそのまま発行できます。

### 2-1. SampleReport を Power BI Desktop で開く

1. エクスプローラーで `SampleReport/Artificial Intelligence Sample.pbix` をダブルクリック
2. Power BI Desktop が起動してレポートが開く

> Power BI Desktop が未インストールの場合は https://aka.ms/pbidesktop からダウンロードしてください。

### 参考: レポートに含まれる RLS 設定

サンプルレポートには以下の RLS ロールが設定されています:

- ロール名: `CustomerRole`
- DAX 式:

```dax
IF(
    USERNAME() = "customer_a",
    [Category] = "Software",
    IF(
        USERNAME() = "customer_b",
        [Category] = "Hardware",
        TRUE()
    )
)
```

| username | 表示されるデータ |
|----------|----------------|
| `customer_a` | Software のみ |
| `customer_b` | Hardware のみ |
| `customer_c` | すべて |

> 独自のデータや RLS ロールに変更したい場合は、**モデリング** → **ロールの管理** から編集してください。

### 元の手順: Power BI Desktop でレポートを自作する場合（参考）

<details>
<summary>クリックして展開</summary>

### サンプルデータの準備

Power BI Desktopを開いて「データを入力」でサンプルテーブルを作成します。

1. **ホーム** → **データを入力** をクリック
2. テーブル名を `Sales` として以下のデータを入力:

| ProductID | ProductName | Category | Price | CustomerID |
|-----------|-------------|----------|-------|------------|
| 1 | Office 365 | Software | 1200 | customer_a |
| 2 | Windows 11 | Software | 2500 | customer_a |
| 3 | Server Rack | Hardware | 5000 | customer_b |
| 4 | Mouse | Hardware | 50 | customer_b |
| 5 | Adobe CC | Software | 3000 | customer_c |
| 6 | Router | Hardware | 800 | customer_c |

3. **読み込む** をクリック

### 2-2. 簡単なビジュアルを作成

- 棒グラフを追加: X軸 = `Category`、Y軸 = `Price`（の合計など）
- 表ビジュアルを追加: `ProductName`、`Category`、`Price` を表示

### 2-3. RLS（行レベルセキュリティ）を設定

1. **モデリング** タブ → **ロールの管理** をクリック
2. **作成** ボタンで新しいロールを作成:
   - ロール名: `CustomerRole`
3. 左のテーブル一覧から **Sales** を選択
4. 右側の「テーブルフィルターのDAX式」に以下を入力:

```dax
IF(
    USERNAME() = "customer_a",
    [Category] = "Software",
    IF(
        USERNAME() = "customer_b",
        [Category] = "Hardware",
        TRUE()
    )
)
```

> このDAX式の意味:
> - `customer_a` → Software のみ表示
> - `customer_b` → Hardware のみ表示
> - `customer_c`（その他）→ すべて表示

5. **保存** をクリック

### RLS の動作をテスト（重要！）

1. **モデリング** → **ロールとして表示** をクリック
2. **CustomerRole** にチェックを入れる
3. **その他のユーザー** に `customer_a` と入力（引用符なし）
4. **OK** をクリック
5. ビジュアルに **Software のみ** 表示されることを確認 ✅
6. `customer_b` でも同様にテスト → **Hardware のみ** 表示を確認 ✅
7. 表示の停止: **ロールとして表示** → **なし** に変更

</details>

### 2-2. レポートを Power BI Service に発行

1. Power BI Desktop で **ホーム** → **発行** をクリック
2. 発行先のワークスペースを選択（または新規作成）
3. 「発行に成功しました」メッセージを確認

### 2-3. Workspace ID と Report ID を取得

1. https://app.powerbi.com（または https://app.fabric.microsoft.com）にアクセス
2. 発行したワークスペースを開く
3. レポートをクリックしてURLを確認:

```
https://app.powerbi.com/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/...
```

4. URL から以下をコピー:
   - `WORKSPACE_ID`: `groups/` の後の `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - `REPORT_ID`: `reports/` の後の `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 2-4. Service Principal をワークスペースに追加

1. ワークスペースの右上 **...** → **ワークスペースのアクセス管理**（または **アクセス**）
2. **ユーザーまたはグループを追加**
3. Azure AD で登録したアプリ名（`PowerBI-Embedded-Demo`）を検索して追加
4. 役割: **メンバー** または **共同作成者** を選択
5. **追加** をクリック

### 2-5. RLS ロールの確認

1. ワークスペースでデータセット（またはセマンティックモデル）を見つける
2. `...` → **セキュリティ** をクリック
3. **CustomerRole** が表示されることを確認（SampleReport を発行すれば自動で反映）
4. **メンバーは空（0）のままでOK** ← Embedded では不要

> ✅ ここが重要ポイント: メンバーにユーザーを追加しなくても、Pythonアプリから動的にユーザーを指定できます。

---

## ステップ3: Python 環境のセットアップ

### 3-1. 依存パッケージのインストール

コマンドプロンプトまたはターミナルを開いて:

```bash
cd "c:\work\embedded\Python\Embed for your customers\AppOwnsData"
pip install -r ../requirements.txt
```

インストールされるパッケージ:
- `flask` - Webフレームワーク
- `requests` - HTTP クライアント
- `msal` - Microsoft 認証ライブラリ

---

## ステップ4: config.py を設定して実行

### 4-1. config.py を編集

[AppOwnsData/config.py](AppOwnsData/config.py) をテキストエディタで開き、以下の値を設定:

```python
class BaseConfig(object):

    AUTHENTICATION_MODE = 'ServicePrincipal'  # ← このまま変更不要

    WORKSPACE_ID = 'xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx'  # ← ステップ2-3でコピーした値
    REPORT_ID = 'xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx'     # ← ステップ2-3でコピーした値
    TENANT_ID = 'xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx'     # ← ステップ1-1でメモした値
    CLIENT_ID = 'xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx'     # ← ステップ1-1でメモした値
    CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' # ← ステップ1-2でメモした値

    # 顧客マッピング（Power BI のDAX式のUSERNAME()と一致させる）
    CUSTOMER_MAPPING = {
        'customer_a': {
            'name': '顧客A - ソフトウェア事業部',
            'username': 'customer_a',    # ← DAX式のUSERNAME()で使われる値
            'roles': ['CustomerRole']    # ← Power BIで定義したロール名（完全一致）
        },
        'customer_b': {
            'name': '顧客B - ハードウェア事業部',
            'username': 'customer_b',
            'roles': ['CustomerRole']
        },
        'customer_c': {
            'name': '顧客C - 統括本部（全データ）',
            'username': 'customer_c',
            'roles': ['CustomerRole']
        }
    }
```

### 4-2. アプリを起動

```bash
cd "c:\work\embedded\Python\Embed for your customers\AppOwnsData"
python app.py
```

### 4-3. ブラウザで確認

1. http://localhost:5000 を開く
2. ドロップダウンから **顧客A** を選択
3. **「RLS適用でレポートを表示」** をクリック
4. **Software** 製品のみ表示されることを確認 ✅
5. **顧客B** を選択 → **Hardware** のみ表示 ✅
6. **顧客C** を選択 → **すべて** 表示 ✅

---

## ✅ 確認チェックリスト

設定がうまくいかない場合、以下の順番で確認してください:

- [ ] `SampleReport/Artificial Intelligence Sample.pbix` が Power BI Service に発行されている
- [ ] `config.py` の5つのID/Secretが正しく設定されている
- [ ] Service Principal（アプリ）がワークスペースに追加されている（メンバーまたは共同作成者）
- [ ] Power BI管理ポータルで「サービスプリンシパルによるAPI使用」が有効になっている
- [ ] Power BI Serviceにロール「CustomerRole」が存在する（SampleReport を発行すれば自動で反映）
- [ ] ロールの**メンバーは空（0）のまま**（これが正常）

---

## ❓ よくあるエラーと対処法

### `401 Unauthorized`
→ `CLIENT_ID` / `CLIENT_SECRET` / `TENANT_ID` が間違っている

### `403 Forbidden`
→ Service Principal がワークスペースに追加されていない、または管理ポータルの設定が未済

### `404 Not Found`
→ `WORKSPACE_ID` または `REPORT_ID` が間違っている

### RLSが適用されず全データが表示される

**原因1（最多）: DAX式に `USERNAME()` が含まれていない**

```dax
// ❌ 間違い
[Category] = "Software"

// ✅ 正しい
IF(USERNAME() = "customer_a", [Category] = "Software", TRUE())
```

**原因2: カラム名・値のスペルミス**  
→ Power BI Desktop の**データビュー**で実際のカラム名と値を確認する

**原因3: Desktop で修正後に再発行していない**  
→ **ホーム** → **発行** で必ず再発行すること

**原因4: Service Principal がロールのメンバーに含まれている**  
→ データセット → セキュリティ で Service Principal をロールから除外する

### Desktop では動作するが埋め込みアプリでは RLS が適用されない

1. レポートを Power BI Service に**再発行**したか確認
2. ブラウザ F12 → Network タブ → `getembedinfo_rls` レスポンスに `customerInfo` が含まれるか確認
3. Python コンソールで GenerateToken リクエストの `identities` が空でないか確認

```python
# services/pbiembedservice.py に一時追加してデバッグ
print("=== GenerateToken Request ===")
print(json.dumps(request_body.__dict__, indent=2))
```

期待される出力:
```json
{
  "identities": [
    { "username": "customer_a", "roles": ["CustomerRole"], "datasets": ["..."] }
  ]
}
```

### `username` / `roles` に関する間違い

```python
# ❌ 引用符を含めている
'username': '"customer_a"'

# ❌ ロール名の大文字小文字が違う
'roles': ['customerrole']

# ✅ 正しい
'username': 'customer_a'
'roles': ['CustomerRole']
```

### 顧客ドロップダウンが表示されない
→ `config.py` の `CUSTOMER_MAPPING` が正しく設定されているか確認

---

## 📂 ファイル構成

```
SampleReport/
└── Artificial Intelligence Sample.pbix  ← デモ用サンプルレポート（RLS設定済み）

AppOwnsData/
├── app.py                  ← Flaskアプリ本体・APIエンドポイント定義
├── config.py               ← 設定ファイル（★ここを編集）
├── models/
│   ├── effectiveidentity.py ← RLS用EffectiveIdentityモデル
│   └── ...
├── services/
│   └── pbiembedservice.py  ← Power BI API呼び出しロジック
├── templates/
│   └── index.html          ← フロントエンドHTML
└── static/
    └── js/index.js         ← 顧客選択・RLS表示のJavaScript
```

---

## 🔑 このデモの仕組み（技術解説）

```
[ブラウザ]
  ↓ 顧客を選択して「RLS適用で表示」ボタンをクリック
  ↓ POST /getembedinfo_rls {"customerId": "customer_a"}

[Python/Flask サーバー]
  ↓ customer_a の username と roles を config.py から取得
  ↓ Azure AD から Bearer Token を取得（MSAL）
  ↓ Power BI GenerateToken API を呼び出し
     → EffectiveIdentity: {username: "customer_a", roles: ["CustomerRole"]}

[Power BI API]
  ↓ RLS付きの Embed Token を発行

[ブラウザ]
  ↓ Embed Token を使ってレポートを表示
  → Power BI が USERNAME() = "customer_a" として評価
  → DAX式フィルターが適用され Software のみ表示
```

---

*本ガイドで問題が解決しない場合は、[Power BI Embedded ドキュメント](https://learn.microsoft.com/ja-jp/power-bi/developer/embedded/) を参照してください。*
