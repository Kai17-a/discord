# ---------------------------
# プロバイダ設定
# ---------------------------
# AWS
provider "aws" {
  region     = "ap-northeast-1"
}

# 自分のパブリックIP取得用
provider "http" {}