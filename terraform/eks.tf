data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = "my-cluster"
  kubernetes_version = "1.35"

  addons = {
    coredns = {}
    eks-pod-identity-agent = {
      before_compute = true
    }
    kube-proxy = {}
    vpc-cni = {
      before_compute = true
    }
  }

  enable_cluster_creator_admin_permissions = true

  vpc_id     = data.aws_vpc.default.id
  subnet_ids = data.aws_subnets.default.ids

  # MISCONFIGURATION 1: EKS Secrets Encryption Disabled (AVD-AWS-0038 / Trivy)
  create_kms_key    = false
  encryption_config = null

  # MISCONFIGURATION 2: Public API Endpoint Access Allowed & Unrestricted (AVD-AWS-0039 & AVD-AWS-0040)
  cluster_endpoint_public_access       = true
  cluster_endpoint_private_access      = false
  cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"]

  # MISCONFIGURATION 3: Control Plane Logging Completely Disabled (AVD-AWS-0037)
  cluster_enabled_log_types = []

  # MISCONFIGURATION 4: Overly Permissive Node Group Security Group Rule (AVD-AWS-0104)
  node_security_group_additional_rules = {
    ingress_all = {
      description = "Allow all incoming traffic from anywhere"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  eks_managed_node_groups = {
    example = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 1
      desired_size   = 1

      # MISCONFIGURATION 5: Node EBS Root Volume Unencrypted (AVD-AWS-0131)
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 20
            volume_type           = "gp3"
            encrypted             = false
            delete_on_termination = true
          }
        }
      }
    }
  }

  tags = {
    Environment = "test"
    Terraform   = "true"
  }
}
