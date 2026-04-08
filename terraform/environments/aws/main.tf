terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # 원격 상태 저장 (S3 + DynamoDB 락) - 협업 시 필수
  # backend "s3" {
  #   bucket         = "devops-starter-tfstate"
  #   key            = "aws/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   dynamodb_table = "devops-starter-tfstate-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}

# ---- VPC (기존 VPC가 있으면 data source로 참조 가능) ----
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true    # 개발 환경: NAT GW 1개 (비용 절감)

  # EKS가 서브넷을 자동 발견하기 위한 태그
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
}

# ---- EKS 클러스터 ----
module "eks" {
  source = "../../modules/eks"

  cluster_name         = var.cluster_name
  vpc_id               = module.vpc.vpc_id
  subnet_ids           = module.vpc.private_subnets
  enable_gpu_nodegroup = var.enable_gpu_nodegroup
}

# ---- ECR 레지스트리 ----
module "ecr_api" {
  source          = "../../modules/ecr"
  repository_name = "devops-starter-api"
}

module "ecr_ray" {
  source          = "../../modules/ecr"
  repository_name = "devops-starter-ray"
}
