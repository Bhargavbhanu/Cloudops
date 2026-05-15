terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "right_llm_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  name    = "right-llm"
  cidr    = "10.42.0.0/16"
  azs     = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = ["10.42.1.0/24", "10.42.2.0/24", "10.42.3.0/24"]
  public_subnets  = ["10.42.101.0/24", "10.42.102.0/24", "10.42.103.0/24"]
  enable_nat_gateway = true
}

module "right_llm_eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"
  cluster_name    = "right-llm"
  cluster_version = "1.30"
  subnet_ids      = module.right_llm_vpc.private_subnets
  vpc_id          = module.right_llm_vpc.vpc_id
  eks_managed_node_groups = {
    default = {
      min_size     = 3
      max_size     = 12
      desired_size = 3
      instance_types = ["m6i.large"]
    }
  }
}
